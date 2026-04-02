"""
Task 3 (HARD): Multi-Root-Cause with Red Herrings
Simultaneous issues:
- Memory leak in search-service
- Misconfigured deployment in recommendation-service
- Scheduled cron job consuming excess CPU
- Noisy logs with red herrings
Agent must identify ALL root causes, prioritize, and fix each one.
"""

TASK_CONFIG = {
    "id": "multi_root_cause",
    "name": "Multi-Root-Cause Incident",
    "difficulty": "hard",
    "description": "Multiple simultaneous issues with misleading logs. Identify all root causes and fix them.",
    "target_resolution_time": 35.0,  # minutes
    "base_score": 1.0,
    "time_limit": 35.0,
}

VARIANTS = [
    {
        "name": "Multi-Root-Cause System Failure",
        "root_causes": [
            "search-service memory leak",
            "recommendation-service pod misconfiguration",
            "scheduled cron job consuming excess CPU",
        ],
        "affected_services": [
            "search-service",
            "recommendation-service",
            "api-gateway",
            "user-service",
        ],
        "resolution": [
            "rollback_deploy:recommendation-service",
            "run_diagnostic:search-service",
            "restart_service:search-service",
            "run_diagnostic:system-cron",
            "update_config:system-cron,schedule=disabled",
        ],
    },
]
