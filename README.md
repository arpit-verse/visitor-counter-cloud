# Scalable Cloud-Native Visitor Counter Application
### Flask, Redis, Docker & Kubernetes with Horizontal Pod Autoscaling (HPA) and Hybrid Cloud Deployment

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![Redis 7](https://img.shields.io/badge/Redis-7--alpine-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5.svg)](https://kubernetes.io/)

---

## 1. Project Overview

This project implements a complete, submission-ready Cloud Computing college project demonstrating microservice containerization, cloud orchestration, self-healing, automated horizontal pod autoscaling (HPA), hybrid cloud deployment simulation, and measurable cost optimization techniques.

### Core Objectives & Deliverables
1. **Task 1: Containerization:** Python Flask application coupled with an in-memory Redis database using Docker and Docker Compose.
2. **Task 2: Kubernetes Deployment:** Deployments for Flask (2 initial replicas) and Redis, ClusterIP & NodePort services, resource requests/limits, readiness/liveness probes, and pod self-healing demonstration.
3. **Task 3: Horizontal Pod Autoscaling (HPA):** Metrics Server integration, dynamic scaling between 2 and 6 replicas targeted at 50% CPU utilization, and simulated load generation.
4. **Task 4: Hybrid Cloud Deployment:** Resilient multi-environment setup (Private on-premise cluster + Simulated public cloud cluster) with zero-downtime failover demonstration.
5. **Task 5: Cost & Resource Optimization:** Measured 85.8% Docker image reduction, CPU/memory right-sizing, and autoscaling resource reclaim analysis.

---

## 2. Project Directory Structure

```
visitor-counter-cloud/
├── app/
│   ├── app.py                     # Flask application with Redis INCR logic
│   ├── requirements.txt           # Python application dependencies
│   ├── templates/
│   │   └── index.html             # Responsive telemetry dashboard UI
│   └── static/
│       └── style.css              # Modern stylesheet
│
├── Dockerfile                     # Optimized multi-stage Python 3.11-slim build
├── Dockerfile.unoptimized         # Baseline image for optimization comparison
├── docker-compose.yml             # Local multi-container Docker composition
├── .dockerignore                  # Docker build context exclusions
├── .gitignore                     # Git tracking exclusions
│
├── kubernetes/
│   ├── namespace.yaml             # Dedicated visitor-app namespace
│   ├── configmap.yaml             # Application environment configurations
│   ├── redis-deployment.yaml      # Redis deployment with probes and limits
│   ├── redis-service.yaml         # Internal Redis ClusterIP service (:6379)
│   ├── flask-deployment.yaml      # Multi-replica Flask deployment with probes
│   ├── flask-service.yaml         # NodePort ingress service (:30080)
│   └── hpa.yaml                   # HorizontalPodAutoscaler configuration
│
├── hybrid/
│   └── failover-test.ps1          # Hybrid cloud failover verification script
│
├── scripts/
│   ├── test-self-healing.ps1      # Automatic pod deletion & replacement test
│   └── load-test.py               # Concurrent multi-threaded traffic generator
│
├── docs/
│   ├── architecture.md            # Detailed architecture and flow diagrams
│   ├── cost-analysis.md           # Before/after quantitative cost comparison
│   └── implementation.md          # Step-by-step verification guide
│
└── README.md                      # Complete documentation and quickstart
```

---

## 3. Technology Stack

- **Application:** Python 3.11, Flask 3.0.3, Gunicorn 22.0, Redis Py 5.0
- **Database:** Redis 7 (Alpine Linux)
- **Containerization:** Docker Engine, Docker Compose
- **Orchestration:** Kubernetes (Minikube / Docker Desktop), kubectl, Metrics Server
- **Telemetry & Probes:** Liveness (`/health`), Readiness (`/ready`), Metrics (`/metrics`)

---

## 4. Quickstart: Local Docker Compose (Task 1)

1. Launch application stack:
   ```bash
   docker-compose up -d --build
   ```
2. Verify running containers:
   ```bash
   docker-compose ps
   ```
3. Open in browser:
   - Dashboard: `http://localhost:5000`
   - Health Probe: `http://localhost:5000/health`
   - Readiness Probe: `http://localhost:5000/ready`
4. Tear down stack:
   ```bash
   docker-compose down
   ```

---

## 5. Kubernetes Orchestration & Verification (Tasks 2 & 3)

### Deploying the Workload
```powershell
# 1. Load local Docker image into Minikube cluster
docker tag visitor-counter-cloud-flask-app:latest visitor-counter-flask:latest
minikube image load visitor-counter-flask:latest
minikube image load redis:7-alpine

# 2. Apply Kubernetes configurations in dependency order
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/redis-deployment.yaml
kubectl apply -f kubernetes/redis-service.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-service.yaml

# 3. Verify pods, services, and endpoints
kubectl get pods -n visitor-app -o wide
kubectl get svc -n visitor-app
kubectl get endpoints -n visitor-app

# 4. Access the application in browser
# Option A (Recommended): Port-forward to NodePort 30080
kubectl port-forward -n visitor-app svc/flask-service 30080:5000

# Option B: Minikube tunnel URL
minikube service flask-service -n visitor-app --url

# 5. Verify health, readiness, and metrics endpoints
curl http://localhost:30080/health
curl http://localhost:30080/ready
curl http://localhost:30080/metrics
```

### Self-Healing Demonstration
```powershell
powershell -ExecutionPolicy Bypass -File scripts/test-self-healing.ps1
```

### Horizontal Pod Autoscaling (HPA) Demonstration
```powershell
# Apply HPA policy
kubectl apply -f kubernetes/hpa.yaml

# Generate simulated load (25 concurrent workers for 120s)
python scripts/load-test.py --url http://localhost:30080/ --workers 25 --duration 120

# Observe auto-scaling in real time
kubectl get hpa -n visitor-app -w
```

---

## 6. Hybrid Cloud Failover Demonstration (Task 4)

Simulate disaster recovery failover between private on-premise cluster and public cloud cluster:
```powershell
powershell -ExecutionPolicy Bypass -File hybrid/failover-test.ps1
```

---

## 7. Cost & Resource Optimization Results (Task 5)

| Dimension | Baseline (Unoptimized) | Optimized Implementation | Improvement |
| :--- | :--- | :--- | :--- |
| **Docker Base Image** | `python:3.11` (Full Debian) | `python:3.11-slim` (Multi-stage) | **85.8% Size Reduction** |
| **Image Size** | 1,020 MB | 145 MB | **875 MB Saved** |
| **CPU / RAM Allocation** | Unbounded (No limits) | Request: 100m, 128Mi / Limit: 500m, 256Mi | Predictable QoS |
| **Idle Capacity Policy** | Static 6 Replicas | HPA 2 to 6 Replicas | **66.7% Idle Compute Saved** |
| **Estimated Monthly Cost** | \$103.75 | \$19.69 | **~81% Cost Reduction** |

Detailed breakdown available in [`docs/cost-analysis.md`](docs/cost-analysis.md).

---

## 8. Screenshot Submission Checklist

- [x] 1. Flask application homepage displaying total visitor count (`http://localhost:5000`).
- [x] 2. `docker-compose ps` showing healthy `flask` and `redis` containers.
- [x] 3. `kubectl get pods -n visitor-app -o wide` showing 2 active Flask replicas and 1 Redis pod.
- [x] 4. `kubectl get svc -n visitor-app` showing `NodePort` and `ClusterIP` services.
- [x] 5. Self-healing test output showing automatic pod recreation after deletion.
- [ ] 6. `kubectl get hpa -n visitor-app` during traffic spike displaying replica scale-up.
- [ ] 7. HPA scale-down confirmation after traffic cessation.
- [ ] 8. Hybrid failover script output demonstrating switch to public cloud tier.
- [ ] 9. `docker images` comparing unoptimized vs. optimized image sizes.
