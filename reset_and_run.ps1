# Script de utilidad para reiniciar el entorno de desarrollo localmente
# Uso: .\reset_and_run.ps1

Write-Host "🔄 Iniciando reinicio de entorno local..." -ForegroundColor Cyan

# 1. Limpiar entorno anterior
if (Test-Path ".env") {
    Remove-Item ".env" -Force
    Write-Host "✓ Archivo .env eliminado" -ForegroundColor Green
}
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "✓ Base de datos SQLite eliminada" -ForegroundColor Green
}

# 2. Crear configuración fresca para SQLite
$envContent = @"
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=django-insecure-dev-key-$(Get-Random)
DJANGO_DB_ENGINE=django.db.backends.sqlite3
DJANGO_DB_NAME=db.sqlite3
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
"@
$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host "✓ Nuevo .env creado para SQLite" -ForegroundColor Green

# 3. Ejecutar migraciones
Write-Host "📦 Ejecutando migraciones..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migraciones completadas" -ForegroundColor Green
} else {
    Write-Host "❌ Error en migraciones" -ForegroundColor Red
    exit 1
}

# 4. Iniciar servidor
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
Write-Host "   Accede a: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "   (Se abrirá el asistente de configuración automáticamente)" -ForegroundColor Yellow
python manage.py runserver
