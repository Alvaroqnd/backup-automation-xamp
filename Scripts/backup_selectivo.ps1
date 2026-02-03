param(
    [Parameter(Mandatory=$true)]
    [string]$Tipo,

    # Recibimos todo en una sola cadena: "a|b|c"
    [Parameter(Mandatory=$true)]
    [string]$ItemsStr
)

$fecha = Get-Date -Format "yyyyMMdd_HHmm"

# Convertir a array
$Items = $ItemsStr -split "\|" | Where-Object { $_ -and $_.Trim() -ne "" }

switch ($Tipo) {
    "documentos" {
        $base = [Environment]::GetFolderPath("MyDocuments")
    }
    "escritorio" {
        $base = [Environment]::GetFolderPath("Desktop")
    }
    "descargas" {
        $downloadsGuid = "{374DE290-123F-4565-9164-39C4925E467B}"
        $base = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders").$downloadsGuid
        $base = [Environment]::ExpandEnvironmentVariables($base)
    }
    default { throw "Tipo no válido: $Tipo" }
}

$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$paths = @()
foreach ($i in $Items) {
    $p = Join-Path $base $i
    if (Test-Path $p) { $paths += $p }
}

if ($paths.Count -eq 0) {
    throw "No hay elementos válidos para copiar"
}

$destino = Join-Path $backupDir "backup_selectivo_$Tipo`_$fecha.zip"
Compress-Archive -Path $paths -DestinationPath $destino -Force
