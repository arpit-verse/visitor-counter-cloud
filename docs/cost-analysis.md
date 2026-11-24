# Cloud Resource & Cost Optimization Analysis

## 1. Overview of Implemented Optimizations

This project implements three key cloud optimization strategies:

1. **Docker Container Image Optimization:** Multi-stage build transitioning from bloated standard Python images (`python:3.11`, ~1.02 GB) to an optimized Debian slim runtime (`python:3.11-slim`, ~145 MB).
2. **Kubernetes Resource Right-Sizing:** Explicit definition of CPU/Memory requests and limits preventing cluster resource starvation and runaway overprovisioning.
3. **Horizontal Pod Autoscaling (HPA):** Elastic scaling based on actual CPU utilization (target 50%) with dynamic scaling between 2 and 6 replicas, eliminating idle replica waste.

---

## 2. Before vs. After Quantitative Comparison

The following table contrasts the baseline unoptimized setup against the optimized cloud-native deployment using actual measured metrics:

| Metric / Dimension | Baseline (Unoptimized) | Optimized Implementation | Measured / Calculated Impact | Evidence File |
| :--- | :--- | :--- | :--- | :--- |
| **Docker Base Image** | `python:3.11` (Full Debian Bookworm) | `python:3.11-slim` (Multi-stage build) | **85.8% image size reduction** | `09-cost-image-optimization.txt` |
| **Measured Image Size** | **1,020 MB (1.02 GB)** | **145 MB** | **875 MB saved per container pull** | `09-cost-image-optimization.txt` |
| **Container User Security** | `root` (UID 0) | `appuser` (Non-root UID 1000) | Hardened least-privilege compliance | `Dockerfile` |
| **Pod CPU Request / Limit** | Unbounded (Cluster default) | Request: 100m / Limit: 500m | Guaranteed QoS, burst capped | `kubernetes/flask-deployment.yaml` |
| **Pod Memory Request / Limit** | Unbounded (OOM risk) | Request: 128Mi / Limit: 256Mi | Predictable cluster scheduling | `kubernetes/flask-deployment.yaml` |
| **Replica Strategy** | Static 6 Replicas 24/7 | HPA: 2 (idle) to 6 (peak load, 50% CPU target) | **66.7% compute idle capacity saved** | `05-hpa-status.txt` |
| **Idle Cluster Memory** | $6 \times 256\text{ MiB} = 1.536\text{ GiB}$ | $2 \times 128\text{ MiB} = 256\text{ MiB}$ | **1.28 GiB freed during low traffic** | `07-hpa-scaling-results.txt` |
| **Idle Cluster CPU** | $6 \times 500\text{m} = 3.0\text{ vCPU}$ | $2 \times 100\text{m} = 0.2\text{ vCPU}$ | **2.8 vCPU reclaimed for other workloads** | `07-hpa-scaling-results.txt` |
| **Peak Observed Scale** | 6 Static Replicas | 4 Replicas dynamically under sustained load | Matched real-time demand without over-provisioning | `07-hpa-scaling-results.txt` |

---

## 3. Resource Allocation and Cost Impact

The following comparison illustrates the reduction in allocated Kubernetes resources through right-sizing and autoscaling. These figures represent configured resource allocations, not actual cloud billing measurements.

| Resource | Baseline Scenario | Optimized Scenario | Impact |
|---|---:|---:|---|
| Flask replicas during idle periods | 6 | 2 | 66.7% fewer replicas |
| CPU requests | 3.0 vCPU | 0.2 vCPU | 2.8 vCPU lower requested capacity |
| Memory requests | Based on baseline assumption of 256 MiB per replica | 256 MiB total | Lower reserved memory |
| CPU limits | 3.0 vCPU | 1.0 vCPU | Reduced maximum configured capacity |
| Container image size | 1,020 MB | 145 MB | 85.8% reduction |

### Cost Optimization Interpretation

1. **Image optimization:** Smaller container images reduce registry storage requirements and image transfer volume.
2. **Resource right-sizing:** Explicit CPU and memory requests and limits improve resource allocation and reduce unnecessary reservation.
3. **Horizontal Pod Autoscaling:** The application scales from 2 replicas to 4 during the demonstrated load test and returns to 2 replicas after the load ends.

These optimizations can reduce infrastructure expenditure in a cloud environment. Actual monetary savings depend on the cloud provider, region, instance pricing, storage charges and workload duration. No real cloud billing measurements were performed because this project uses a local Minikube environment.

The financial impact is therefore discussed qualitatively rather than presented as an actual cloud cost reduction.