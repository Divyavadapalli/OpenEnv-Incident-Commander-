"""
FastAPI server implementing OpenEnv specification.
Serves as the OpenEnv environment endpoint for agent training.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

from env.environment import IncidentCommanderEnv
from env.models import (
    Action,
    StepRequest,
    ResetResponse,
    Observation,
    EnvironmentState,
    HealthResponse,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IncidentCommander",
    description="AI agent training environment for production incident management",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = IncidentCommanderEnv()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns HTTP 200 if service is operational.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        available_tasks=[
            "single_service_outage",
            "cascading_failure",
            "multi_root_cause",
        ],
    )


@app.post("/reset", response_model=ResetResponse)
async def reset_env(request: Request):
    """
    Reset environment and start new episode.
    
    Query parameters:
    - task_id: Which task to run (single_service_outage/cascading_failure/multi_root_cause)
    - difficulty: Task difficulty (easy/medium/hard)
    
    Returns:
    - Initial observation
    - Initial environment state
    """
    try:
        # Get query parameters
        task_id = request.query_params.get("task_id", "single_service_outage")
        difficulty = request.query_params.get("difficulty", "easy")
        
        # Validate inputs
        valid_tasks = [
            "single_service_outage",
            "cascading_failure",
            "multi_root_cause",
        ]
        valid_difficulties = ["easy", "medium", "hard"]
        
        if task_id not in valid_tasks:
            raise ValueError(f"Invalid task_id: {task_id}")
        if difficulty not in valid_difficulties:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        
        # Reset environment
        observation = env.reset(task_id=task_id, difficulty=difficulty)
        state = env.state()
        
        logger.info(f"Reset environment: task={task_id}, difficulty={difficulty}, incident_id={env.incident.incident_id}")
        
        return ResetResponse(
            observation=observation,
            state=state,
        )
    
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
async def step_env(step_req: StepRequest):
    """
    Execute one action in the environment.
    
    Request body:
    - action: Action object with action_type, target_service, parameters, etc.
    
    Returns:
    - observation: New observation after action
    - reward: Reward for this step
    - done: Whether episode is finished
    - info: Additional metadata
    """
    try:
        action = step_req.action
        
        # Validate action
        if not action.action_type:
            raise ValueError("action_type is required")
        
        # Execute step
        observation, reward, done, info = env.step(action)
        
        logger.info(f"Step {env.current_step}: action={action.action_type}, reward={reward:.3f}, done={done}")
        
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info,
        }
    
    except Exception as e:
        logger.error(f"Step error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state", response_model=EnvironmentState)
async def get_state():
    """
    Get current environment state.
    Includes ground truth information (root causes, etc.)
    """
    try:
        state = env.state()
        return state
    except Exception as e:
        logger.error(f"State error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/episode-result")
async def episode_result():
    """
    Get final episode result and scoring.
    Called after episode is done.
    """
    try:
        state = env.state()
        
        # Calculate final score using grader
        final_score = env.grader.grade(
            identified_causes=state.identified_causes,
            applied_fixes=state.applied_fixes,
            time_elapsed=state.time_elapsed,
            num_wasted_actions=env.wasted_actions,
            no_false_positives=True,
            communication_sent=env.communication_count > 0,
        )
        
        return {
            "incident_id": state.incident_id,
            "task_id": state.task_id,
            "task_name": state.task_name,
            "difficulty": state.difficulty,
            "final_score": final_score,
            "root_causes": state.root_causes,
            "identified_causes": state.identified_causes,
            "applied_fixes": state.applied_fixes,
            "time_elapsed_minutes": state.time_elapsed,
            "steps_taken": state.current_step,
            "total_reward": state.total_reward,
        }
    except Exception as e:
        logger.error(f"Episode result error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IncidentCommander OpenEnv Environment",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
            "episode_result": "/episode-result",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
