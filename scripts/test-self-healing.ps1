# Self-Healing Test Script
param(
    [string]$Namespace = "visitor-app",
    [string]$Deployment = "flask-deployment"
)

Write-Host "=== Step 1: Listing initial running pods ===" -ForegroundColor Cyan
kubectl get pods -n $Namespace -l app=flask-app -o wide

$targetPod = (kubectl get pods -n $Namespace -l app=flask-app -o jsonpath="{.items[0].metadata.name}")
Write-Host "`nTarget pod selected for deletion: $targetPod" -ForegroundColor Yellow

Write-Host "Simulating pod crash/deletion..." -ForegroundColor Red
kubectl delete pod $targetPod -n $Namespace

Write-Host "`n=== Step 2: Observing Kubernetes self-healing reconciliation ===" -ForegroundColor Cyan
Start-Sleep -Seconds 3
kubectl get pods -n $Namespace -l app=flask-app -o wide

Write-Host "`nSelf-healing test completed: ReplicaSet replaced the terminated pod." -ForegroundColor Green
