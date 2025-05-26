#!/bin/bash

# ======================
# Kubernetes Deployment Script (Bash)
# ======================

# Default environment
ENV=${1:-prod}
K8S_PATH="./k8s/$ENV"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOG_FILE="./k8s-deploy-$ENV-$TIMESTAMP.log"

# Logging function
log() {
    echo "[$(date +"%H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log ""
log "=== STARTING K8S DEPLOYMENT ($ENV) ==="

# Check if folder exists
if [ ! -d "$K8S_PATH" ]; then
    log "❌ Environment folder not found: $K8S_PATH"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log "❌ kubectl not found in PATH"
    exit 1
fi

# Find YAML files
YAMLS=$(find "$K8S_PATH" -name '*.yaml' -type f -size +0c)
if [ -z "$YAMLS" ]; then
    log "❌ No valid YAML files found in $K8S_PATH"
    exit 1
fi

log "Files to be applied:"
echo "$YAMLS" | xargs -n 1 basename | while read -r file; do
    log "- $file"
done

# Dry-run validation
log ""
log "Executing validation (dry-run)..."
VALIDATION_ERRORS=0

while IFS= read -r yaml; do
    if ! kubectl apply -f "$yaml" --dry-run=client -o name &>> "$LOG_FILE"; then
        log "VALIDATION ERROR: $(basename "$yaml")"
        ((VALIDATION_ERRORS++))
    fi
done <<< "$YAMLS"

if [ "$VALIDATION_ERRORS" -gt 0 ]; then
    log "❌ $VALIDATION_ERRORS file(s) failed validation. Fix before deploying."
    exit 1
fi

# User confirmation
read -p "Everything validated. Do you want to apply the configurations? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then
    log "Deployment cancelled by user."
    exit 0
fi

# Apply configurations
log ""
log "Starting configuration application..."
APPLY_ERRORS=0
APPLIED=0

while IFS= read -r yaml; do
    log "Applying $(basename "$yaml")..."
    if kubectl apply -f "$yaml" &>> "$LOG_FILE"; then
        ((APPLIED++))
    else
        log "APPLICATION ERROR: $(basename "$yaml")"
        ((APPLY_ERRORS++))
    fi
done <<< "$YAMLS"

# Summary
log ""
log "=== DEPLOYMENT SUMMARY ==="
log "Files applied: $APPLIED"
log "Errors found: $APPLY_ERRORS"

if [ "$APPLY_ERRORS" -eq 0 ]; then
    log "✅ DEPLOYMENT COMPLETED SUCCESSFULLY"

    # Show created resources (if app=fastapi is used)
    log ""
    log "Created resources:"
    kubectl get all -l app=fastapi --no-headers 2>/dev/null | tee -a "$LOG_FILE"

    # Optional port-forward suggestion
    SVC=$(kubectl get svc -l app=fastapi -o name 2>/dev/null | head -n 1)
    if [ -n "$SVC" ]; then
        log ""
        log "Run to access the application:"
        log "kubectl port-forward $SVC 8000:80"
    fi
else
    log "⚠️ DEPLOYMENT COMPLETED WITH ERRORS. Check the log: $LOG_FILE"
    exit 1
fi
