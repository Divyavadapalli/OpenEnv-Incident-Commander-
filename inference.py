"""
Baseline inference agent for IncidentCommander.
Uses OpenAI LLM to make decisions about incident response.

Environment variables required:
- API_BASE_URL: Base URL for the OpenEnv environment server
- MODEL_NAME: Name of the LLM model to use
- HF_TOKEN: Hugging Face token (used as API key)
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from openai import OpenAI
import time

# Initialize environment variables
api_base = os.environ.get("API_BASE_URL", "http://localhost:7860")
model_name = os.environ.get("MODEL_NAME", "meta-llama/Llama-2-7b-chat-hf")
hf_token = os.environ.get("HF_TOKEN", "")

# Client will be initialized in main() when actually needed
client = None

# Global state
current_observation = None
current_state = None
step_count = 0
max_steps = 100


def reset_environment(task_id: str = "single_service_outage", difficulty: str = "easy") -> None:
    """Reset the environment and start a new episode."""
    global current_observation, current_state, step_count
    
    try:
        response = requests.post(
            f"{api_base}/reset",
            params={"task_id": task_id, "difficulty": difficulty},
            timeout=30,
        )
        response.raise_for_status()
        
        data = response.json()
        current_observation = data["observation"]
        current_state = data["state"]
        step_count = 0
        
        print(f"✓ Environment reset: {task_id} ({difficulty})")
        print(f"  Incident ID: {current_state['incident_id']}")
        print(f"  Severity: {current_observation['severity_level']}")
        return True
    except Exception as e:
        print(f"✗ Failed to reset environment: {e}")
        return False


def take_action(action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Take an action in the environment."""
    global current_observation, current_state, step_count
    
    try:
        response = requests.post(
            f"{api_base}/step",
            json={"action": action},
            timeout=30,
        )
        response.raise_for_status()
        
        data = response.json()
        current_observation = data["observation"]
        
        # Get updated state
        state_response = requests.get(f"{api_base}/state", timeout=30)
        state_response.raise_for_status()
        current_state = state_response.json()
        
        step_count += 1
        
        return {
            "observation": data["observation"],
            "reward": data["reward"],
            "done": data["done"],
            "info": data["info"],
        }
    except Exception as e:
        print(f"✗ Failed to take action: {e}")
        return None


def get_llm_suggestion(prompt: str) -> str:
    """Get suggestion from LLM for next action."""
    try:
        messages = [
            {
                "role": "system",
                "content": """You are an expert Site Reliability Engineer (SRE) responding to production incidents.
Your goal is to:
1. Investigate the incident by checking logs and metrics
2. Identify root causes
3. Apply appropriate fixes
4. Communicate with stakeholders
5. Mark the incident as resolved when all issues are fixed

You respond ONLY with a JSON object containing the action to take. No explanations, just JSON.
Example: {"action_type": "check_logs", "target_service": "payment-service"}

Available action types:
- check_logs (target_service required)
- check_metrics (target_service optional)
- run_diagnostic (target_service optional)
- restart_service (target_service required)
- rollback_deploy (target_service required)
- scale_service (target_service required, parameters required)
- update_config (target_service required, parameters required)
- communicate (message required)
- escalate
- mark_resolved
- check_dependencies (target_service required)
- check_recent_deploys (target_service optional)
"""
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=200,
            temperature=0.3,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"✗ LLM error: {e}")
        return "{}"


def build_context_prompt() -> str:
    """Build a detailed context prompt from current observation and state."""
    if not current_observation or not current_state:
        return ""
    
    # Extract key information
    alerts = current_observation.get("active_alerts", [])
    recent_logs = current_observation.get("recent_logs", [])[-5:]
    service_status = current_observation.get("service_status", {})
    messages = current_observation.get("team_messages", [])
    time_elapsed = current_observation.get("time_elapsed", 0)
    
    prompt = f"""
Current Incident Status:
- Time Elapsed: {time_elapsed:.1f} minutes
- Severity: {current_observation.get('severity_level', 'UNKNOWN')}
- Incident ID: {current_state['incident_id']}

Active Alerts ({len(alerts)}):
"""
    
    for alert in alerts[:3]:
        prompt += f"\n- [{alert['severity']}] {alert['service']}: {alert['title']}"
    
    prompt += f"\n\nService Status:"
    for service, status in list(service_status.items())[:5]:
        prompt += f"\n- {service}: {status}"
    
    prompt += f"\n\nRecent Logs:"
    for log in recent_logs:
        prompt += f"\n- [{log['service']}] {log['message']}"
    
    prompt += f"\n\nRoots Causes Found So Far: {current_state.get('identified_causes', [])}"
    prompt += f"\nFixes Applied: {current_state.get('applied_fixes', [])}"
    
    prompt += "\n\nWhat is your next action?"
    
    return prompt


def parse_action_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse LLM response into action dict."""
    try:
        # Extract JSON from response
        response_text = response_text.strip()
        
        # Handle cases where LLM wraps JSON in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        action = json.loads(response_text)
        
        # Validate required fields
        if "action_type" not in action:
            return None
        
        return action
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"✗ Parse error: {e}")
        return None


def run_agent(task_id: str = "single_service_outage", difficulty: str = "easy") -> Dict[str, Any]:
    """Run the agent for one complete episode."""
    global step_count, max_steps
    
    print(f"\n{'='*60}")
    print(f"Starting IncidentCommander Episode")
    print(f"Task: {task_id} | Difficulty: {difficulty}")
    print(f"{'='*60}\n")
    
    # Reset environment
    if not reset_environment(task_id, difficulty):
        return {"success": False, "error": "Failed to reset environment"}
    
    max_steps = {"easy": 50, "medium": 75, "hard": 150}.get(difficulty, 100)
    
    # Agent loop
    done = False
    episode_reward = 0.0
    
    while not done and step_count < max_steps:
        print(f"\n[Step {step_count + 1}/{max_steps}]")
        
        # Build context and get LLM suggestion
        context_prompt = build_context_prompt()
        llm_response = get_llm_suggestion(context_prompt)
        
        # Parse action
        action = parse_action_response(llm_response)
        
        if not action:
            print(f"✗ Failed to parse action from LLM")
            print(f"  LLM response: {llm_response[:100]}...")
            continue
        
        print(f"→ Action: {action['action_type']}", end="")
        if action.get("target_service"):
            print(f" ({action['target_service']})", end="")
        if action.get("message"):
            print(f": {action['message'][:40]}...", end="")
        print()
        
        # Execute action
        result = take_action(action)
        
        if result:
            reward = result["reward"]
            done = result["done"]
            episode_reward += reward
            
            print(f"  Reward: {reward:+.3f} | Total: {episode_reward:+.3f}")
            
            if done:
                print(f"\n✓ Episode finished!")
                break
        else:
            print(f"  Failed to execute action")
        
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    # Get final result
    try:
        result_response = requests.post(f"{api_base}/episode-result", timeout=30)
        result_response.raise_for_status()
        final_result = result_response.json()
    except Exception as e:
        print(f"✗ Failed to get episode result: {e}")
        final_result = {}
    
    return {
        "success": True,
        "task_id": task_id,
        "difficulty": difficulty,
        "steps_taken": step_count,
        "total_reward": episode_reward,
        "final_score": final_result.get("final_score", 0.0),
        "identified_causes": final_result.get("identified_causes", []),
        "applied_fixes": final_result.get("applied_fixes", []),
        "time_elapsed": final_result.get("time_elapsed_minutes", 0),
    }


def main():
    """Run agent on all three tasks."""
    global client
    
    # Initialize OpenAI client (required for LLM calls)
    if not client:
        if not hf_token:
            raise ValueError("HF_TOKEN environment variable must be set")
        client = OpenAI(
            base_url=api_base,
            api_key=hf_token,
        )
    
    print("\n" + "="*60)
    print("IncidentCommander Baseline Agent")
    print("="*60)
    
    results = {}
    
    # Task 1: Easy
    print("\nRunning EASY task...")
    results["easy"] = run_agent("single_service_outage", "easy")
    
    # Task 2: Medium
    print("\n\nRunning MEDIUM task...")
    results["medium"] = run_agent("cascading_failure", "medium")
    
    # Task 3: Hard
    print("\n\nRunning HARD task...")
    results["hard"] = run_agent("multi_root_cause", "hard")
    
    # Print summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    for difficulty, result in results.items():
        if result.get("success"):
            print(f"\n{difficulty.upper()} Task:")
            print(f"  Final Score: {result.get('final_score', 0):.2f}")
            print(f"  Steps Taken: {result.get('steps_taken', 0)}")
            print(f"  Time: {result.get('time_elapsed', 0):.1f} min")
            print(f"  Root Causes Found: {len(result.get('identified_causes', []))}")
            print(f"  Fixes Applied: {len(result.get('applied_fixes', []))}")
        else:
            print(f"\n{difficulty.upper()} Task: FAILED")
    
    print("\n" + "="*60)
    
    # Return results
    return results


if __name__ == "__main__":
    import sys
    
    # Check for required environment variables
    if not os.environ.get("HF_TOKEN"):
        print("Error: HF_TOKEN environment variable not set")
        sys.exit(1)
    
    # Run agent
    results = main()
    
    # Exit with success if all tasks ran
    sys.exit(0)
