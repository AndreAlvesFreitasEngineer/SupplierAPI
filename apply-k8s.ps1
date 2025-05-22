<#
.SYNOPSIS
  Complete Kubernetes deployment script with validations and error handling
.DESCRIPTION
  Applies all YAML files from a specific environment, with prior checks
  and detailed error handling.
.PARAMETER env
  Environment to be deployed (default: 'prod')
.EXAMPLE
  .\apply-k8s.ps1 -env prod
#>

param(
    [string]$env = "prod"
)

# 1. Initial configuration
$ErrorActionPreference = "Stop"
$k8sPath = "$PSScriptRoot\k8s\$env"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logFile = "$PSScriptRoot\k8s-deploy-$env-$timestamp.log"

# 2. Logging function
function Write-Log {
    param([string]$message)
    Add-Content -Path $logFile -Value "[$(Get-Date -Format 'HH:mm:ss')] $message"
    Write-Host $message
}

# 3. Initial checks
try {
    Write-Log "`n=== STARTING K8S DEPLOYMENT ($env) ==="

    # Check if folder exists
    if (-not (Test-Path $k8sPath)) {
        throw "Environment folder not found: $k8sPath"
    }

    # Check if kubectl is available
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        throw "kubectl not found in PATH"
    }

    # 4. YAML files validation
    $yamls = Get-ChildItem -Path "$k8sPath\*.yaml" -File | Where-Object { $_.Length -gt 0 }

    if (-not $yamls) {
        throw "No valid YAML files found in $k8sPath"
    }

    Write-Log "Files to be applied:"
    $yamls | ForEach-Object { Write-Log ("- " + $_.Name) }

    # 5. Dry-run (preliminary validation)
    Write-Log "`nExecuting validation (dry-run)..."
    $validationErrors = 0

    foreach ($yaml in $yamls) {
        try {
            $output = kubectl apply -f $yaml.FullName --dry-run=client -o name 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Log "VALIDATION ERROR: $($yaml.Name) - $output"
                $validationErrors++
            }
        }
        catch {
            $validationErrors++
            Write-Log "VALIDATION ERROR: $($yaml.Name) - $($_.Exception.Message)"
        }
    }

    if ($validationErrors -gt 0) {
        throw "$validationErrors file(s) with validation error(s). Fix before deploying."
    }

    # 6. Confirmation
    $confirmation = Read-Host "`nEverything validated. Do you want to apply the configurations? (y/n)"
    if ($confirmation -ne 'y') {
        Write-Log "Deployment cancelled by user"
        exit 0
    }

    # 7. Actual application
    Write-Log "`nStarting configuration application..."
    $applyErrors = 0

    foreach ($yaml in $yamls) {
        try {
            Write-Log "Applying $($yaml.Name)..."
            $output = kubectl apply -f $yaml.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw $output
            }
            Write-Log $output
        }
        catch {
            $applyErrors++
            Write-Log "APPLICATION ERROR: $($yaml.Name) - $($_.Exception.Message)"
        }
    }

    # 8. Final summary
    Write-Log "`n=== DEPLOYMENT SUMMARY ==="
    Write-Log "Files applied: $($yamls.Count - $applyErrors)"
    Write-Log "Errors found: $applyErrors"

    if ($applyErrors -eq 0) {
        Write-Log "`n✅ DEPLOYMENT COMPLETED SUCCESSFULLY"

        # Show created resources
        Write-Log "`nCreated resources:"
        kubectl get all -l app=fastapi --no-headers | ForEach-Object { Write-Log $_ }

        # Automatic port-forward (optional)
        $svc = kubectl get svc -l app=fastapi -o name 2>$null
        if ($svc) {
            Write-Log "`nRun to access the application:"
            Write-Log "kubectl port-forward $svc 8000:80"
        }
    }
    else {
        Write-Log "`n⚠️ DEPLOYMENT COMPLETED WITH ERRORS. Check the log: $logFile"
        exit 1
    }
}
catch {
    Write-Log "`n❌ CRITICAL ERROR: $($_.Exception.Message)"
    Write-Log "Details in log: $logFile"
    exit 1
}