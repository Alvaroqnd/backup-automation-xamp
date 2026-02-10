Set-Location $PSScriptRoot

$backupDir = $env:BACKUPS_DIR
if (-not $backupDir -or $backupDir.Trim() -eq "") {
    $backupDir = Join-Path $PSScriptRoot "..\backups"
}
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$fecha = Get-Date -Format "yyyyMMdd_HHmm"

# Ruta REAL de "Escritorio"
$origen = [Environment]::GetFolderPath("Desktop")

$destino = Join-Path $backupDir "backup_escritorio_$fecha.zip"
Compress-Archive -Path $origen -DestinationPath $destino -Force
