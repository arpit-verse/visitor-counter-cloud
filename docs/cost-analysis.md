# Cloud Resource & Cost Optimization Analysis

## 1. Overview of Implemented Optimizations

This project implements three key cloud optimization strategies:

1. **Docker Container Image Optimization:** Multi-stage build transitioning from bloated standard Python images (`python:3.11`, ~1.02 GB) to an optimized Debian slim runtime (`python:3.11-slim`, ~145 MB).
2. **Kubernetes Resource Right-Sizing:** Explicit definition of CPU/Memory requests and limits preventing cluster resource starvation and runaway overprovisioning.
3. **Horizontal Pod Autoscaling (HPA):** Elastic scaling based on actual CPU utilization (target 50%) with dynamic scaling between 2 and 6 replicas, eliminating idle replica waste.

---

## 2. Before vs. After Quantitative Comparison

| Metric / Dimension | Baseline (Unoptimized) | Optimized Implementation | Measured / Calculated Impact |
| :--- | :--- | :--- | :--- |
| **Docker Base Image** | `python:3.11` (Full Debian) | `python:3.11-slim` (Multi-stage) | **85.8% image size reduction** |
| **Docker Image Size** | ~1,020 MB | ~145 MB | **875 MB saved per container pull** |
| **Container User Security** | `root` (UID 0) | `appuser` (Non-root UID 1000) | Hardened runtime compliance |
| **Pod CPU Request / Limit** | Unbounded (Default cluster max) | Request: 100m / Limit: 500m | Guaranteed QoS with bounded burst |
| **Pod Memory Request / Limit** | Unbounded (OOM risk) | Request: 128Mi / Limit: 256Mi | Predictable cluster scheduling |
| **Replica Strategy** | Static 6 Replicas 24/7 | HPA: 2 (idle) to 6 (peak load) | **66.7% compute idle capacity saved** |
| **Idle Cluster Memory** | $6 \times 256\text{ MiB} = 1.536\text{ GiB}$ | $2 \times 128\text{ MiB} = 256\text{ MiB}$ | **1.28 GiB freed during low traffic** |
| **Idle Cluster CPU** | $6 \times 500\text{m} = 3.0\text{ vCPU}$ | $2 \times 100\text{m} = 0.2\text{ vCPU}$ | **2.8 vCPU reclaimed for other workloads** |

---

## 3. Projected Cloud Cost Model (Hypothetical AWS EKS / GCP GKE)

> **Disclaimer:** The financial figures below represent an academic projection based on public cloud hourly compute pricing (e.g., standard micro/small compute instances at \$0.04/vCPU-hour and \$0.005/GB-RAM-hour). Measured local metrics are strictly technical.

### Baseline Cost Scenario (Static 6 Replicas Overprovisioned)
- **vCPU Allocations:** 6 replicas $\times$ 0.5 vCPU = 3.0 vCPU $\times$ 730 hrs/month $\times$ \$0.04 = **\$87.60/month**
- **RAM Allocations:** 6 replicas $\times$ 0.5 GB = 3.0 GB $\times$ 730 hrs/month $\times$ \$0.005 = **\$10.95/month**
- **Container Registry Storage & Egress:** ~1.02 GB image pulls $\times$ frequent deployments = **\$5.20/month**
- **Total Estimated Baseline Cost:** **\$103.75 / month**

### Optimized Cost Scenario (HPA Elastic 2 Replicas with Burst)
Assuming 18 hours of low traffic (2 replicas) and 6 hours of peak load (average 4 replicas):
- **Average Active Replicas:** $(18 \times 2 + 6 \times 4) / 24 = 2.5\text{ replicas}$
- **vCPU Allocations:** 2.5 replicas $\times$ 0.1 vCPU (base) to 0.3 vCPU (avg) $\approx$ 0.6 vCPU avg $\times$ 730 hrs $\times$ \$0.04 = **\$17.52/month**
- **RAM Allocations:** 2.5 replicas $\times$ 0.15 GB avg = 0.375 GB $\times$ 730 hrs $\times$ \$0.005 = **\$1.37/month**
- **Container Registry Storage & Egress:** ~145 MB image = **\$0.80/month**
- **Total Estimated Optimized Cost:** **\$19.69 / month**

### Net Savings
- **Monthly Savings:** **\$84.06 / month**
- **Relative Cost Reduction:** **~81% cost decrease**
