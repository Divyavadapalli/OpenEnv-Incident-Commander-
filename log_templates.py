"""
Realistic log templates for incident generation.
These templates are used to generate believable production logs.
"""

LOG_TEMPLATES = {
    "error": [
        "{timestamp} ERROR [auth-service] Request ID {req_id}: Connection pool exhausted. Available: {value}/100",
        "{timestamp} ERROR [payment-service] Processing payment {req_id} failed: Timeout after {value}ms",
        "{timestamp} ERROR [search-service] Memory usage critical: {value}MB / {max_value}MB. GC pressure rising.",
        "{timestamp} ERROR [api-gateway] Backend health check failed for {service}: {status_code}",
        "{timestamp} ERROR [recommendation-service] Failed to load model weights: {error_message}",
        "{timestamp} ERROR [database] Connection refused: {service} unable to reach primary database",
        "{timestamp} ERROR [notification-service] Queue backup detected: {value} messages pending",
        "{timestamp} ERROR [cache-layer] Redis connection timeout after {value}ms",
        "{timestamp} ERROR [deployment-controller] Rollback for {service} failed: {reason}",
        "{timestamp} ERROR [monitoring] Alert channel failure: Slack webhook timeout",
    ],
    "warning": [
        "{timestamp} WARNING [auth-service] Pool utilization at {value}%. Approaching limits.",
        "{timestamp} WARNING [payment-service] P99 latency at {value}ms (SLA: {sla}ms)",
        "{timestamp} WARNING [search-service] CPU usage trending up: {value}% (current)",
        "{timestamp} WARNING [database] Replication lag detected: {value}ms",
        "{timestamp} WARNING [api-gateway] Request rate spike detected: {value} req/s",
        "{timestamp} WARNING [cache-layer] Eviction rate elevated: {value} keys/min",
        "{timestamp} WARNING [recommendation-service] Model inference latency: {value}ms",
        "{timestamp} WARNING [notification-service] Queue size growing: {value} messages",
        "{timestamp} WARNING [deployment-controller] Pending deployments: {value}",
        "{timestamp} WARNING [monitoring] Scrape timeout on {service} metrics endpoint",
    ],
    "info": [
        "{timestamp} INFO [deployment/controller] Deployment started for {service}: {version}",
        "{timestamp} INFO [auth-service] Authentication token cache hit rate: {value}%",
        "{timestamp} INFO [payment-service] Transaction processed: ID={req_id}, amount=${value}",
        "{timestamp} INFO [search-service] Index rebuild progress: {value}%",
        "{timestamp} INFO [database] Backup completed: {size}GB in {duration}s",
        "{timestamp} INFO [api-gateway] Rate limit applied for client {client_id}: {reason}",
        "{timestamp} INFO [cache-layer] Cache warming complete for {cache_name}",
        "{timestamp} INFO [notification-service] Message delivered: {notification_id}",
        "{timestamp} INFO [recommendation-service] Model update initiated: {version}",
        "{timestamp} INFO [monitoring] Health check passed for {service}",
    ],
    "debug": [
        "{timestamp} DEBUG [auth-service] Token validation for request {req_id} completed in {value}ms",
        "{timestamp} DEBUG [payment-service] Processing transaction branch: {branch_name}",
        "{timestamp} DEBUG [search-service] Query execution plan: {query_type}",
        "{timestamp} DEBUG [database] SQL query executed in {value}ms",
        "{timestamp} DEBUG [api-gateway] Header validation: allowed={allowed}, received={received}",
        "{timestamp} DEBUG [cache-layer] Cache lookup: key={key}, hit={hit}",
        "{timestamp} DEBUG [notification-service] Message serialization: {format}",
        "{timestamp} DEBUG [recommendation-service] Feature vector computation: {dimensions}d",
        "{timestamp} DEBUG [deployment-controller] Kubernetes event: {event_type}",
        "{timestamp} DEBUG [monitoring] Metric collection completed: {count} samples",
    ],
}

# Specific error messages for incidents
INCIDENT_ERRORS = {
    "memory_leak": [
        "Memory usage critical: 8945MB / 8192MB. Process scheduled for OOMKill.",
        "Heap size exceeded: {value}% of max heap. GC unable to keep up.",
        "Memory pressure: {value} page faults/sec. Potential memory leak detected.",
        "Process {pid} requesting memory beyond limits. Container restart imminent.",
    ],
    "connection_pool_exhaustion": [
        "Connection pool exhausted. Available: 0/100. Max retries exceeded.",
        "No idle connections available. Queued requests: {value}. Timeout threshold reached.",
        "Database connection pool saturated. New connections rejected.",
        "Connection acquisition timeout after {value}ms. Pool limit: 100.",
    ],
    "deployment_issue": [
        "Config mismatch detected on pod {pod_id}. Expected: {expected}, Actual: {actual}",
        "Deployment rollout stuck: {value}% complete. Waiting for {reason}",
        "Image pull failed: {image_hash}. Registry unreachable or image missing.",
        "Pod crash loop detected: {crashes} crashes in last {duration}s.",
    ],
    "cascading_failure": [
        "Upstream service {service} returned {status_code}. Cascading timeout impact detected.",
        "Dependency chain failure: A → B → C → D. Root cause at: {root}",
        "Service timeout triggered chain reaction across {count} dependent services.",
    ],
    "cpu_spike": [
        "Unexpected CPU usage spike: {value}%. Current threshold: {threshold}%",
        "Cron job {job_name} consuming {value}% CPU. Scheduled execution conflict detected.",
        "Runaway goroutine detected. Goroutine count: {count}. Normal baseline: {baseline}.",
    ],
}

def get_log_template(level: str) -> str:
    """Get a random log template for a given level."""
    import random
    if level in LOG_TEMPLATES:
        return random.choice(LOG_TEMPLATES[level])
    return "{timestamp} {level} [unknown] {message}"
