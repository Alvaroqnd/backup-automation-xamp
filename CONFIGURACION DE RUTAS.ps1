# --- CONFIGURACIÓN DE RUTAS ---
# Definimos las rutas como variables para que el script sea fácil de mantener [cite: 112, 113, 114]
$RutaOrigen = "C:\Users\Alvar\Downloads\Origen"
$RutaRepositorio = "C:\Users\Alvar\Downloads\Origen\backups"

# --- GENERACIÓN DEL NOMBRE DEL ARCHIVO ---
# Creamos el formato backup_YYYYMMDD.zip como pide tu esquema [cite: 18, 41]
$Fecha = Get-Date -Format "yyyyMMdd"
$NombreZip = "backup_$Fecha.zip"
$RutaDestinoFinal = Join-Path -Path $RutaRepositorio -ChildPath $NombreZip

# --- PROCESO DE COMPRESIÓN ---
# Usamos el comando nativo de PowerShell para comprimir [cite: 40, 65, 95]
Write-Host "Iniciando la copia de seguridad de: $RutaOrigen" -ForegroundColor Cyan

try {
    # Comprime la carpeta de origen en el destino especificado
    Compress-Archive -Path $RutaOrigen -DestinationPath $RutaDestinoFinal -Force
    Write-Host "Copia finalizada con éxito en: $RutaDestinoFinal" -ForegroundColor Green
}
catch {
    Write-Host "Error al realizar la copia: $($_.Exception.Message)" -ForegroundColor Red
}