"""
Pre-built incident scenarios for all three task difficulties.
"""

from typing import Dict, List, Any

EASY_SCENARIOS = [
    {
        "name": "Payment Service 500 Errors",
        "root_causes": ["payment-service crashed"],
        "affected_services": ["payment-service"],
        "initial_status": {
            "payment-service": "DOWN",
            "api-gateway": "DEGRADED",
            "user-service": "HEALTHY",
        },
        "error_signature": "payment-service: fatal error in payment processor - OOM Kill",
        "resolution": ["restart_service:payment-service"],
        "time_limit": 15.0,  # minutes
    },
    {
        "name": "Search Service Config Error",
        "root_causes": ["incorrect elasticsearch config deployment"],
        "affected_services": ["search-service"],
        "initial_status": {
            "search-service": "DEGRADED",
            "api-gateway": "DEGRADED",
            "user-service": "HEALTHY",
        },
        "error_signature": "search-service: Failed to connect to Elasticsearch cluster",
        "resolution": ["rollback_deploy:search-service"],
        "time_limit": 15.0,
    },
    {
        "name": "Cache Service Memory Exhaustion",
        "root_causes": ["cache not evicting expired keys"],
        "affected_services": ["cache-layer"],
        "initial_status": {
            "cache-layer": "DEGRADED",
            "auth-service": "DEGRADED",
            "api-gateway": "HEALTHY",
        },
        "error_signature": "cache-layer: Memory usage critical, key eviction failing",
        "resolution": ["restart_service:cache-layer"],
        "time_limit": 15.0,
    },
]

MEDIUM_SCENARIOS = [
    {
        "name": "Database Connection Pool Cascade",
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
        "initial_status": {
            "database": "HEALTHY",
            "auth-service": "DOWN",
            "api-gateway": "DOWN",
            "payment-service": "DEGRADED",
            "user-service": "DEGRADED",
        },
        "error_signature": "Connection pool exhausted, cascading timeouts",
        "resolution": [
            "check_dependencies:auth-service",
            "restart_service:auth-service",
            "scale_service:auth-service,replicas=3",
        ],
        "time_limit": 25.0,
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
        "initial_status": {
            "database": "DEGRADED",
            "user-service": "DEGRADED",
            "payment-service": "DEGRADED",
            "recommendation-service": "DOWN",
        },
        "error_signature": "Replication lag detected, read-heavy services timing out",
        "resolution": [
            "run_diagnostic:database",
            "update_config:database,analytics_job=disabled",
        ],
        "time_limit": 25.0,
    },
]

HARD_SCENARIOS = [
    {
        "name": "Multi-Root-Cause System Failure",
        "root_causes": [
            "search-service memory leak",
            "recommendation-service pod misconfiguration",
            "scheduled cron job consuming excess CPU",
            "unrelated: old warning logs from yesterday",
        ],
        "affected_services": [
            "search-service",
            "recommendation-service",
            "api-gateway",
            "user-service",
        ],
        "initial_status": {
            "search-service": "DOWN",
            "recommendation-service": "DEGRADED",
            "api-gateway": "DEGRADED",
            "user-service": "DEGRADED",
            "notification-service": "HEALTHY",
        },
        "error_signature": "Multiple simultaneous issues with misleading logs",
        "resolution": [
            "rollback_deploy:recommendation-service",
            "run_diagnostic:search-service",
            "restart_service:search-service",
            "run_diagnostic:system-cron",
            "update_config:system-cron,schedule=disabled",
        ],
        "time_limit": 35.0,
    },
]

def get_scenario(difficulty: str, scenario_index: int = 0) -> Dict[str, Any]:
    """Get a scenario by difficulty and index."""
    if difficulty == "easy":
        return EASY_SCENARIOS[scenario_index % len(EASY_SCENARIOS)]
    elif difficulty == "medium":
        return MEDIUM_SCENARIOS[scenario_index % len(MEDIUM_SCENARIOS)]
    elif difficulty == "hard":
        return HARD_SCENARIOS[scenario_index % len(HARD_SCENARIOS)]
    else:
        return EASY_SCENARIOS[0]
