Set-Location $PSScriptRoot

$RutaRepositorio = $env:BACKUPS_DIR
if (-not $RutaRepositorio -or $RutaRepositorio.Trim() -eq "") {
    # fallback (modo proyecto)
    $RutaRepositorio = Join-Path $PSScriptRoot "..\backups"
}

# Carpeta de restauración (por defecto: Documentos\CORE_SYNC\restored)
$RutaDestino = $env:RESTORE_DIR
if (-not $RutaDestino -or $RutaDestino.Trim() -eq "") {
    $RutaDestino = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "CORE_SYNC\restored"
}

New-Item -ItemType Directory -Path $RutaDestino -Force | Out-Null

# --- BUSCAR LA COPIA MÁS RECIENTE ---
$UltimaCopia = Get-ChildItem -Path $RutaRepositorio -Filter "*.zip" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($UltimaCopia) {
    Write-Host "Restaurando desde: $($UltimaCopia.FullName)" -ForegroundColor Cyan
    try {
        Expand-Archive -Path $UltimaCopia.FullName -DestinationPath $RutaDestino -Force
        Write-Host "ÉXITO: Datos recuperados en $RutaDestino" -ForegroundColor Green
    }
    catch {
        Write-Error "ERROR: No se pudo descomprimir el archivo. $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Host "ADVERTENCIA: No hay copias disponibles para restaurar en $RutaRepositorio" -ForegroundColor Yellow
    exit 1
}
