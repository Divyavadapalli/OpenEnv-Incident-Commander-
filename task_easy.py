"""
Task 1 (EASY): Single Service Outage
A single microservice is throwing 500 errors.
Agent must: check logs → identify error → apply correct fix (restart, rollback, or config change).
"""

TASK_CONFIG = {
    "id": "single_service_outage",
    "name": "Single Service Outage",
    "difficulty": "easy",
    "description": "A single microservice is experiencing critical errors. Diagnose and fix the issue.",
    "target_resolution_time": 15.0,  # minutes
    "base_score": 1.0,
    "time_limit": 15.0,
}

VARIANTS = [
    {
        "name": "Payment Service 500 Errors",
        "root_causes": ["payment-service crashed"],
        "affected_services": ["payment-service"],
        "resolution": ["restart_service:payment-service"],
    },
    {
        "name": "Search Service Config Error",
        "root_causes": ["incorrect elasticsearch config deployment"],
        "affected_services": ["search-service"],
        "resolution": ["rollback_deploy:search-service"],
    },
    {
        "name": "Cache Service Memory Issue",
        "root_causes": ["cache not evicting expired keys"],
        "affected_services": ["cache-layer"],
        "resolution": ["restart_service:cache-layer"],
    },
]
