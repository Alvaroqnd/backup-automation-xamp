Set-Location $PSScriptRoot

$backupDir = $env:BACKUPS_DIR
if (-not $backupDir -or $backupDir.Trim() -eq "") {
    $backupDir = Join-Path $PSScriptRoot "..\backups"
}
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$fecha = Get-Date -Format "yyyyMMdd_HHmm"

# Ruta REAL de "Descargas" desde el registro (Known Folder)
$downloadsGuid = "{374DE290-123F-4565-9164-39C4925E467B}"
$origen = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders").$downloadsGuid
$origen = [Environment]::ExpandEnvironmentVariables($origen)

$destino = Join-Path $backupDir "backup_descargas_$fecha.zip"
Compress-Archive -Path $origen -DestinationPath $destino -Force
