$fecha = Get-Date -Format "yyyyMMdd_HHmm"

# Ruta REAL de "Documentos" (incluye OneDrive si está redirigido)
$origen = [Environment]::GetFolderPath("MyDocuments")

$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$destino = Join-Path $backupDir "backup_documentos_$fecha.zip"
Compress-Archive -Path $origen -DestinationPath $destino -Force
