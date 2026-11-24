# System Architecture & Technical Design

## 1. High-Level Architecture

The Visitor Counter application is designed as a cloud-native, containerized microservice running on Kubernetes with an in-memory Redis database.

```mermaid
flowchart TD
    subgraph ClientLayer["Client Layer"]
        User["User Web Browser"]
    end

    subgraph K8sCluster["Kubernetes Cluster (visitor-app namespace)"]
        subgraph IngressRouting["Ingress / Service Layer"]
            SVC["flask-service (NodePort :30080)"]
        end

        subgraph ApplicationWorkload["Flask Deployment (Stateless)"]
            Pod1["Flask Pod 1 (256Mi / 500m)"]
            Pod2["Flask Pod 2 (256Mi / 500m)"]
            PodHPA["Autoscaled Pods 3-6 (Dynamic)"]
        end

        subgraph AutoscalingSystem["Autoscaling Subsystem"]
            HPA["Horizontal Pod Autoscaler (flask-hpa)"]
            MetricsSvc["Metrics Server (kubelet stats)"]
        end

        subgraph DatabaseTier["Database Tier (Stateful)"]
            RedisSvc["redis-service (ClusterIP :6379)"]
            RedisPod["Redis Pod (redis:7-alpine)"]
            RedisVol[("Volume (emptyDir / PV)")]
        end
    end

    User -->|HTTP Requests| SVC
    SVC -->|Round-Robin Load Balancing| Pod1
    SVC -->|Round-Robin Load Balancing| Pod2
    SVC -.->|Traffic on Scale-Up| PodHPA

    Pod1 -->|INCR visitor_count| RedisSvc
    Pod2 -->|INCR visitor_count| RedisSvc
    PodHPA -.->|INCR visitor_count| RedisSvc

    RedisSvc --> RedisPod
    RedisPod --> RedisVol

    MetricsSvc -->|Scrapes CPU/RAM metrics| ApplicationWorkload
    HPA -->|Queries CPU metrics| MetricsSvc
    HPA -->|Scales Replicas 2-6| ApplicationWorkload
```

---

## 2. Hybrid Cloud & Failover Architecture

For Task 4, the application architecture demonstrates dual-environment resilience across two isolated cluster profiles or namespaces:

```mermaid
flowchart LR
    Client["Traffic Ingress / Gateway"]

    subgraph PrivateEnv["Private On-Premise Cluster (:30081)"]
        PrivFlask["Flask Deployment (2 Replicas)"]
        PrivRedis["Redis Stateful Backend"]
        PrivFlask --> PrivRedis
    end

    subgraph PublicEnv["Simulated Public Cloud Cluster (:30082)"]
        PubFlask["Flask Deployment (2 Replicas)"]
        PubRedis["Redis Stateful Backend"]
        PubFlask --> PubRedis
    end

    Client -->|Primary Traffic (Normal State)| PrivateEnv
    Client -.->|Failover Traffic (On Outage)| PublicEnv
```

### Failover Mechanics
1. **Primary Active:** User traffic is routed to the Private Cluster running on local port `30081`.
2. **Failure Injection:** Simulating private outage by scaling replicas to 0 or stopping private cluster services.
3. **Automated Redirection:** Traffic switches instantly to the Simulated Public Cloud Cluster (`30082`), ensuring zero application downtime.
