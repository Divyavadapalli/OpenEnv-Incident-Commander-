"""
Task 2 (MEDIUM): Cascading Failure
Database connection pool exhaustion causes auth-service slowdown,
which causes API gateway timeouts, triggering user-facing errors.
Agent must trace the chain backward and fix in correct order.
"""

TASK_CONFIG = {
    "id": "cascading_failure",
    "name": "Cascading Failure",
    "difficulty": "medium",
    "description": "Multiple services are failing due to a cascading effect. Trace the chain and fix the root cause.",
    "target_resolution_time": 25.0,  # minutes
    "base_score": 1.0,
    "time_limit": 25.0,
}

VARIANTS = [
    {
        "name": "Database Connection Pool Exhaustion",
        "root_causes": [
            "database connection pool exhausted",
            "auth-service consuming all connections",
        ],
        "affected_services": [
            "database",
            "auth-service",
            "api-gateway",
            "payment-service",
            "user-service",
        ],
        "resolution": [
            "check_dependencies:auth-service",
            "restart_service:auth-service",
            "scale_service:auth-service,replicas=3",
        ],
    },
    {
        "name": "Slow Database Downstream Effects",
        "root_causes": [
            "database replication lag",
            "heavy analytics job running",
        ],
        "affected_services": [
            "database",
            "user-service",
            "payment-service",
            "recommendation-service",
        ],
        "resolution": [
            "run_diagnostic:database",
            "update_config:database,analytics_job=disabled",
        ],
    },
]
