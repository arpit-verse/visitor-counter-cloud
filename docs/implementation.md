# Implementation & Verification Guide

This document provides exact step-by-step verification commands and testing procedures for each phase of the project.

---

## Phase 1: Environment & Tool Verification
Verify installed tooling in PowerShell:
```powershell
python --version
git --version
docker --version
docker-compose --version
kubectl version --client
```

---

## Phase 2 & 3: Local Containerization Verification (Docker Compose)
1. Build and run containers:
   ```powershell
   cd visitor-counter-cloud
   docker-compose up -d --build
   ```
2. Verify running containers:
   ```powershell
   docker-compose ps
   ```
3. Test endpoints:
   - Web UI: Browse to `http://localhost:5000`
   - Health: `curl http://localhost:5000/health`
   - Readiness: `curl http://localhost:5000/ready`
   - Refresh page 3-5 times to confirm visitor count increments.
4. Stop containers when ready for Kubernetes:
   ```powershell
   docker-compose down
   ```

---

## Phase 4: Kubernetes Deployment & Services
1. Start Minikube cluster (or Docker Desktop Kubernetes):
   ```powershell
   minikube start --driver=docker --cpus=2 --memory=2048m
   ```
2. Point terminal to Minikube's Docker daemon:
   ```powershell
   & minikube -p minikube docker-env --shell powershell | Invoke-Expression
   ```
3. Build image inside cluster:
   ```powershell
   docker build -t visitor-counter-flask:latest .
   ```
4. Deploy manifests:
   ```powershell
   kubectl apply -f kubernetes/namespace.yaml
   kubectl apply -f kubernetes/configmap.yaml
   kubectl apply -f kubernetes/redis-deployment.yaml
   kubectl apply -f kubernetes/redis-service.yaml
   kubectl apply -f kubernetes/flask-deployment.yaml
   kubectl apply -f kubernetes/flask-service.yaml
   ```
5. Verify resources:
   ```powershell
   kubectl get pods -n visitor-app -o wide
   kubectl get svc -n visitor-app
   ```

---

## Phase 5: Self-Healing Demonstration
Run the automated self-healing script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/test-self-healing.ps1
```
Expected result: Kubernetes detects pod termination and automatically provisions a replacement pod within seconds.

---

## Phase 6: HPA & Load Scaling Demonstration
1. Enable Metrics Server:
   ```powershell
   minikube addons enable metrics-server
   ```
2. Apply HPA manifest and observe baseline:
   ```powershell
   kubectl apply -f kubernetes/hpa.yaml
   kubectl get hpa -n visitor-app
   ```
3. Run concurrent CPU load against `/stress` endpoint:
   ```powershell
   python scripts/load-test.py --url http://localhost:30080/stress --workers 12 --duration 120
   ```
4. Observe auto-scaling in real time:
   - Initial state: 2 replicas, CPU ~2% / 50%
   - Under load: CPU rises to ~78-84%, HPA scales out to 4 replicas
   - After load: Traffic subsides, stabilization cooldown triggers scale-down back to 2 replicas
5. Revert temporary stress toggle in ConfigMap:
   ```powershell
   kubectl apply -f kubernetes/configmap.yaml
   ```

---

## Phase 7: Hybrid Deployment & Failover Demonstration
Simulate multi-cloud disaster recovery between Private On-Premise cluster and Public Cloud failover:
```powershell
powershell -ExecutionPolicy Bypass -File hybrid/failover-test.ps1
```
*(Note: As documented in architecture guides, this is a local simulation using dual isolated network services to demonstrate failover switching without requiring real cloud billing).*
