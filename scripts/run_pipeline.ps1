# ==============================================================================
# ENTERPRISE LOGISTICS PIPELINE ORCHESTRATOR & MONITOR
# ==============================================================================
# Definición de rutas absolutas basadas en la ubicación del script
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootPath = Split-Path -Parent $ScriptPath
$DataVolume = "$RootPath\data"
$ContainerName = "logistics_pipeline_runtime"
$ImageName = "logistics-pipeline:latest"

# Configuración de políticas de resiliencia
$MaxRetries = 3
$RetryCount = 0
$PipelineSuccess = $false

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING LOGISTICS DATA PIPELINE ORCHESTRATION" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Ciclo adaptativo de reintentos ante fallos de infraestructura
while (-not $PipelineSuccess -and $RetryCount -lt $MaxRetries) {
    $RetryCount++
    Write-Host "[INFO] Execution Attempt $RetryCount of $MaxRetries..." -ForegroundColor Yellow

    # 1. Limpieza de contenedores huérfanos o bloqueados de ejecuciones previas
    $OldContainer = docker ps -a -q --filter "name=$ContainerName"
    if ($OldContainer) {
        Write-Host "[WARN] Cleaning up legacy container instances..." -ForegroundColor DarkYellow
        docker rm -f $ContainerName | Out-Null
    }

    # 2. Ejecución del contenedor Docker montando el volumen de datos local
    Write-Host "[INFO] Launching high-performance container engine..." -ForegroundColor Gray
    docker run --name $ContainerName -v "${DataVolume}:/app/data" $ImageName 2>&1 | Out-File -FilePath "$RootPath\data\pipeline_execution.log" -Append

    # 3. Validación del código de salida del contenedor (Exit Code)
    $ExitCode = (docker inspect $ContainerName --format='{{.State.ExitCode}}')

    if ($ExitCode -eq 0) {
        Write-Host "[SUCCESS] Pipeline execution finalized seamlessly." -ForegroundColor Green
        $PipelineSuccess = $true
    } else {
        Write-Host "[ERROR] Pipeline runtime failed with Exit Code: $ExitCode" -ForegroundColor Red
        if ($RetryCount -lt $MaxRetries) {
            $WaitTime = 5 * $RetryCount
            Write-Host "[RECOVERY] Micro-network anomaly suspected. Backing off for $WaitTime seconds before retry..." -ForegroundColor DarkCyan
            Start-Sleep -Seconds $WaitTime
        }
    }

    # Limpieza final del contenedor para liberar recursos del servidor
    docker rm -f $ContainerName | Out-Null
}

# 4. Estado de salida de la tarea de automatización
Write-Host "======================================================================" -ForegroundColor Cyan
if ($PipelineSuccess) {
    Write-Host "🏁 ORCHESTRATION COMPLETE: Analytical targets are live in data/ folder." -ForegroundColor Green
    Exit 0
} else {
    Write-Host "🚨 ORCHESTRATION CRITICAL: Max pipeline retries exhausted. Check execution logs." -ForegroundColor Red
    Exit 1
}