$fecha = Get-Date -Format "yyyyMMdd_HHmm"

# Ruta REAL de "Escritorio"
$origen = [Environment]::GetFolderPath("Desktop")

$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$destino = Join-Path $backupDir "backup_escritorio_$fecha.zip"
Compress-Archive -Path $origen -DestinationPath $destino -Force
