"""
Simulated metric patterns for incident scenarios.
"""

from typing import Dict, Any
import random


def get_healthy_metrics() -> Dict[str, float]:
    """Metrics for a healthy service."""
    return {
        "error_rate": round(random.uniform(0.001, 0.005), 4),
        "p99_latency_ms": round(random.uniform(50, 150), 1),
        "cpu_percent": round(random.uniform(20, 40), 1),
        "memory_percent": round(random.uniform(30, 50), 1),
        "request_rate": round(random.uniform(100, 500), 0),
        "throughput_rps": round(random.uniform(50, 250), 1),
    }


def get_degraded_metrics(severity: float = 0.5) -> Dict[str, float]:
    """Metrics for a degraded service (0.0=healthy, 1.0=critical)."""
    return {
        "error_rate": round(random.uniform(0.05 * severity, 0.2 * severity), 4),
        "p99_latency_ms": round(random.uniform(200, 800) * severity, 1),
        "cpu_percent": round(random.uniform(60, 85) * severity, 1),
        "memory_percent": round(random.uniform(60, 85) * severity, 1),
        "request_rate": round(random.uniform(50, 200), 0),
        "throughput_rps": round(random.uniform(10, 50) * (1 - severity), 1),
    }


def get_critical_metrics() -> Dict[str, float]:
    """Metrics for a critical/down service."""
    return {
        "error_rate": round(random.uniform(0.8, 1.0), 4),
        "p99_latency_ms": round(random.uniform(2000, 5000), 1),
        "cpu_percent": round(random.uniform(90, 100), 1),
        "memory_percent": round(random.uniform(90, 100), 1),
        "request_rate": round(random.uniform(10, 50), 0),
        "throughput_rps": 0.0,
    }


SERVICE_DEPENDENCIES = {
    "api-gateway": [
        "auth-service",
        "payment-service",
        "user-service",
        "search-service",
    ],
    "auth-service": ["database"],
    "payment-service": ["database", "notification-service"],
    "user-service": ["database", "cache-layer"],
    "search-service": ["elasticsearch", "cache-layer"],
    "recommendation-service": ["database", "ml-models"],
    "notification-service": ["message-queue"],
    "cache-layer": [],
    "database": [],
    "elasticsearch": [],
    "message-queue": [],
    "ml-models": [],
}


def get_service_metrics_for_status(status: str) -> Dict[str, float]:
    """Get realistic metrics for a given service status."""
    if status == "healthy":
        return get_healthy_metrics()
    elif status == "degraded":
        return get_degraded_metrics(0.5)
    else:  # down
        return get_critical_metrics()
