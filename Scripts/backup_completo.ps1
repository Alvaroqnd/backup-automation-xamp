$fecha = Get-Date -Format "yyyyMMdd_HHmm"

$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$destino = Join-Path $backupDir "backup_completo_$fecha.zip"

$paths = @(
    (Join-Path $env:USERPROFILE "Documents"),
    (Join-Path $env:USERPROFILE "Desktop"),
    (Join-Path $env:USERPROFILE "Downloads")
)

Compress-Archive -Path $paths -DestinationPath $destino -Force
