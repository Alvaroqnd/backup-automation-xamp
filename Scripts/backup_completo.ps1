Set-Location $PSScriptRoot

$backupDir = $env:BACKUPS_DIR
if (-not $backupDir -or $backupDir.Trim() -eq "") {
    $backupDir = Join-Path $PSScriptRoot "..\backups"
}
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$fecha = Get-Date -Format "yyyyMMdd_HHmm"

$destino = Join-Path $backupDir "backup_completo_$fecha.zip"

$paths = @(
    (Join-Path $env:USERPROFILE "Documents"),
    (Join-Path $env:USERPROFILE "Desktop"),
    (Join-Path $env:USERPROFILE "Downloads")
)

Compress-Archive -Path $paths -DestinationPath $destino -Force
