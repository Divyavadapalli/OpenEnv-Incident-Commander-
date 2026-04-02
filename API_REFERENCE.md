# IncidentCommander API Quick Reference

## Base URL
```
http://localhost:7860
```

## Endpoints

### 1. Health Check (GET)
```bash
curl http://localhost:7860/health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "available_tasks": [
    "single_service_outage",
    "cascading_failure",
    "multi_root_cause"
  ]
}
```

### 2. Reset Environment (POST)
```bash
curl -X POST "http://localhost:7860/reset?task_id=single_service_outage&difficulty=easy"
```
**Query Parameters:**
- `task_id` (string): single_service_outage | cascading_failure | multi_root_cause
- `difficulty` (string): easy | medium | hard

**Response:**
```json
{
  "observation": {
    "timestamp": "2024-01-15T10:30:00",
    "active_alerts": [...],
    "recent_logs": [...],
    "metrics_snapshot": {...},
    "service_status": {...},
    "team_messages": [...],
    "incident_timeline": [...],
    "time_elapsed": 0.0,
    "severity_level": "P1",
    "available_services": [...],
    "service_dependencies": {...}
  },
  "state": {
    "incident_id": "abc12345",
    "task_id": "single_service_outage",
    "task_name": "Single Service Outage",
    "difficulty": "easy",
    "current_step": 0,
    "max_steps": 50,
    "services": {...},
    "root_causes": [...],
    "identified_causes": [],
    "applied_fixes": [],
    "score": 0.0,
    "is_done": false,
    "resolution_status": "ongoing",
    "total_reward": 0.0,
    "time_elapsed": 0.0
  }
}
```

### 3. Step / Execute Action (POST)
```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "action_type": "check_logs",
      "target_service": "payment-service",
      "parameters": null,
      "message": null
    }
  }'
```

**Action Types:**
- `check_logs` (target_service required)
- `check_metrics` (target_service optional)
- `run_diagnostic` (target_service optional)
- `restart_service` (target_service required)
- `rollback_deploy` (target_service required)
- `scale_service` (target_service required, parameters required)
- `update_config` (target_service required, parameters required)
- `escalate` (no parameters)
- `communicate` (message required)
- `mark_resolved` (no parameters)
- `check_dependencies` (target_service required)
- `check_recent_deploys` (target_service optional)

**Response:**
```json
{
  "observation": {...},
  "reward": 0.05,
  "done": false,
  "info": {
    "step": 1,
    "action_result": {
      "success": true,
      "message": "Retrieved 20 logs for payment-service",
      "data": [...]
    },
    "time_elapsed": 0.5,
    "identified_causes": [],
    "applied_fixes": []
  }
}
```

### 4. Get Environment State (GET)
```bash
curl http://localhost:7860/state
```

**Response:** Complete EnvironmentState (includes ground truth)
```json
{
  "incident_id": "abc12345",
  "task_id": "single_service_outage",
  "task_name": "Single Service Outage",
  "difficulty": "easy",
  "current_step": 1,
  "max_steps": 50,
  "services": {
    "payment-service": {
      "name": "payment-service",
      "status": "down",
      "error_rate": 0.98,
      "p99_latency_ms": 5000.0,
      "cpu_percent": 95.0,
      "memory_percent": 92.0,
      "running_replicas": 0,
      "desired_replicas": 3,
      "last_deployment": null,
      "config_version": "1.0"
    },
    ...
  },
  "root_causes": ["payment-service crashed"],
  "identified_causes": [],
  "applied_fixes": [],
  "score": 0.05,
  "is_done": false,
  "resolution_status": "ongoing",
  "total_reward": 0.05,
  "time_elapsed": 0.5
}
```

### 5. Episode Result (POST)
```bash
curl -X POST http://localhost:7860/episode-result
```

**Response:**
```json
{
  "incident_id": "abc12345",
  "task_id": "single_service_outage",
  "task_name": "Single Service Outage",
  "difficulty": "easy",
  "final_score": 0.85,
  "root_causes": ["payment-service crashed"],
  "identified_causes": ["payment-service crashed"],
  "applied_fixes": ["restart_service:payment-service"],
  "time_elapsed_minutes": 3.2,
  "steps_taken": 5,
  "total_reward": 1.15
}
```

## Example Agent Loop

```python
import requests
import json

api_url = "http://localhost:7860"

# Reset
reset_response = requests.post(f"{api_url}/reset?task_id=single_service_outage&difficulty=easy")
observation = reset_response.json()["observation"]

done = False
while not done:
    # Decide action (your RL agent would do this)
    action = {
        "action_type": "check_logs",
        "target_service": "payment-service"
    }
    
    # Step
    step_response = requests.post(
        f"{api_url}/step",
        json={"action": action}
    )
    
    observation = step_response.json()["observation"]
    reward = step_response.json()["reward"]
    done = step_response.json()["done"]
    
    print(f"Reward: {reward:.3f}, Done: {done}")

# Get final result
result = requests.post(f"{api_url}/episode-result").json()
print(f"Final Score: {result['final_score']:.2f}")
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- **200 OK** - Success
- **400 Bad Request** - Invalid input
- **500 Internal Server Error** - Server error

Error responses include detail:
```json
{
  "detail": "Invalid task_id: unknown_task"
}
```

## Performance Notes

- Reset: ~100ms
- Step: ~50ms (excluding LLM latency)
- State: ~10ms
- Health: ~10ms

With LLM inference (Llama2-7b): ~1-2 seconds per action
