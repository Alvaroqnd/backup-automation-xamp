# --- CONFIGURACIÓN DE RUTAS ---
$RutaOrigen = "C:\Users\Alvar\Downloads\Origen"
$RutaRepositorio = "C:\Users\Alvar\Downloads\Origen\backups"

# --- BUSCAR LA COPIA MÁS RECIENTE ---
# Filtramos por archivos .zip y seleccionamos el último creado [cite: 50]
$UltimaCopia = Get-ChildItem -Path $RutaRepositorio -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($UltimaCopia) {
    Write-Host "Restaurando desde: $($UltimaCopia.Name)" -ForegroundColor Cyan
    try {
        # Descomprimimos en la ubicación original [cite: 52, 69]
        Expand-Archive -Path $UltimaCopia.FullName -DestinationPath $RutaOrigen -Force
        Write-Host "ÉXITO: Datos recuperados en $RutaOrigen" -ForegroundColor Green
    }
    catch {
        Write-Error "ERROR: No se pudo descomprimir el archivo."
    }
} else {
    Write-Host "ADVERTENCIA: No hay copias disponibles para restaurar." -ForegroundColor Yellow
}