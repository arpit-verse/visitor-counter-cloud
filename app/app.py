import os
import socket
import time
import hashlib
from flask import Flask, render_template, jsonify, request
import redis

app = Flask(__name__)

# Configuration from Environment Variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME", "Development (Local)")
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")

# Stress endpoint toggle: set ENABLE_STRESS_ENDPOINT=true to enable
ENABLE_STRESS = os.getenv("ENABLE_STRESS_ENDPOINT", "false").lower() == "true"
# Hard cap: each /stress request burns CPU for at most this many seconds
STRESS_MAX_SECONDS = min(int(os.getenv("STRESS_DURATION_S", "2")), 5)

# Start time for uptime calculation
START_TIME = time.time()

# Pod / Host Identification
HOSTNAME = socket.gethostname()

def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        socket_connect_timeout=2,
        socket_timeout=2,
        decode_responses=True
    )

@app.route("/")
def index():
    visitor_count = "Unavailable"
    redis_connected = False
    error_message = None

    try:
        r = get_redis_client()
        # Atomic counter increment via Redis INCR
        visitor_count = r.incr("visitor_count")
        redis_connected = True
    except redis.ConnectionError as e:
        error_message = f"Cannot connect to Redis at {REDIS_HOST}:{REDIS_PORT}. Error: {str(e)}"
    except Exception as e:
        error_message = f"Redis operation error: {str(e)}"

    return render_template(
        "index.html",
        visitor_count=visitor_count,
        redis_connected=redis_connected,
        error_message=error_message,
        hostname=HOSTNAME,
        environment=ENVIRONMENT_NAME,
        version=APP_VERSION,
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT,
        uptime_seconds=int(time.time() - START_TIME)
    )

@app.route("/health")
def health():
    """
    Liveness probe endpoint. Verifies that the Flask web server is alive and responding.
    """
    return jsonify({
        "status": "healthy",
        "hostname": HOSTNAME,
        "environment": ENVIRONMENT_NAME,
        "uptime_seconds": int(time.time() - START_TIME)
    }), 200

@app.route("/ready")
def ready():
    """
    Readiness probe endpoint. Verifies that both the web application and Redis dependency are ready.
    Returns HTTP 200 if Redis responds to PING, otherwise returns HTTP 503 Service Unavailable.
    """
    try:
        r = get_redis_client()
        if r.ping():
            return jsonify({
                "status": "ready",
                "redis": "connected",
                "redis_host": REDIS_HOST,
                "hostname": HOSTNAME
            }), 200
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "redis": "disconnected",
            "error": str(e),
            "hostname": HOSTNAME
        }), 503

@app.route("/metrics")
def metrics():
    """
    Application metrics endpoint for observability and load monitoring.
    """
    visitor_count = -1
    redis_ok = False
    try:
        r = get_redis_client()
        val = r.get("visitor_count")
        visitor_count = int(val) if val else 0
        redis_ok = True
    except Exception:
        pass

    return jsonify({
        "app_uptime_seconds": int(time.time() - START_TIME),
        "total_visitors": visitor_count,
        "redis_connected": redis_ok,
        "hostname": HOSTNAME,
        "environment": ENVIRONMENT_NAME
    }), 200

@app.route("/stress")
def stress():
    """
    CPU stress endpoint for HPA autoscaling demonstration.
    ONLY enabled when ENABLE_STRESS_ENDPOINT=true environment variable is set.
    Hard-capped at STRESS_MAX_SECONDS (default 2s, max 5s) per request.
    Burns CPU via iterative SHA-256 hashing to trigger Kubernetes HPA scale-out.
    """
    if not ENABLE_STRESS:
        return jsonify({
            "error": "Stress endpoint disabled. Set ENABLE_STRESS_ENDPOINT=true to enable.",
            "hostname": HOSTNAME
        }), 403

    deadline = time.time() + STRESS_MAX_SECONDS
    iterations = 0
    data = b"visitor-counter-hpa-stress-seed"
    while time.time() < deadline:
        data = hashlib.sha256(data).digest()
        iterations += 1

    return jsonify({
        "status": "ok",
        "hostname": HOSTNAME,
        "iterations": iterations,
        "duration_seconds": STRESS_MAX_SECONDS,
        "environment": ENVIRONMENT_NAME
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
