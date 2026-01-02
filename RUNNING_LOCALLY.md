# Ejecutar el Proyecto Localmente (Sin Docker)

## 🚀 Inicio Rápido (Recomendado)

Hemos creado un script que automatiza todo el proceso de limpieza y configuración inicial:

```powershell
cd PROJECT_BASE
.\reset_and_run.ps1
```

Este script:
1. Elimina configuraciones antiguas (`.env`, `db.sqlite3`).
2. Genera una configuración nueva para SQLite.
3. Ejecuta las migraciones.
4. Inicia el servidor en `http://127.0.0.1:8000/`.

Al entrar, verás el **Setup Wizard** para configurar la empresa y crear tu usuario administrador.

---

## 🛠️ Configuración Manual

Si prefieres hacerlo paso a paso:

### 1. Activar el entorno virtual

```powershell
# Desde la raíz del proyecto
cd D:\Desarrollo\AI_DJANGO_DASHBOARD_AGENCY_V1
.venv\Scripts\Activate.ps1
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajústalo según tu entorno:

```powershell
cd PROJECT_BASE
copy .env.example .env
```

Edita `.env` con tus credenciales de base de datos.

**Opciones:**

#### Opción A: MySQL (Laragon)
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DB_ENGINE=django.db.backends.mysql
DJANGO_DB_NAME=agency_dashboard
DJANGO_DB_USER=root
DJANGO_DB_PASSWORD=        # Contraseña de tu MySQL local
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=3306
```

#### Opción B: SQLite (más simple para desarrollo)
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DB_ENGINE=django.db.backends.sqlite3
DJANGO_DB_NAME=db.sqlite3
```

### 3. Cargar las variables de entorno

**PowerShell:**
```powershell
# Cargar .env en PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}
```

O usa `python-dotenv` (recomendado):
```powershell
pip install python-dotenv
```

### 4. Aplicar migraciones

```powershell
python manage.py migrate
```

### 5. Crear superusuario

```powershell
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo

```powershell
python manage.py runserver
```

Accede a: http://127.0.0.1:8000/accounts/login/

## Troubleshooting

### Error de conexión a base de datos

**Síntoma:** `Access denied for user 'root'@'host.docker.internal'`

**Solución:** No cargaste las variables de entorno. Ejecuta el paso 3 de nuevo o asegúrate de que `.env` existe y tiene valores correctos.

### Tabla no existe

**Síntoma:** `no such table` o `Table doesn't exist`

**Solución:** Ejecuta `python manage.py migrate`

### No puedo hacer login

**Síntoma:** "Usuario o contraseña incorrecta"

**Solución:** 
1. Verifica que creaste un usuario: `python manage.py createsuperuser`
2. Verifica la base de datos esté funcionando
3. Intenta crear un nuevo usuario

### Puerto 8000 ya en uso

**Síntoma:** `Error: That port is already in use`

**Solución:** 
- Detén otros servidores Django ejecutándose
- O usa otro puerto: `python manage.py runserver 8001`

## Diferencias con Docker

Cuando ejecutas con `docker-compose up`:
- Las variables de entorno están en `docker-compose.yml`
- La base de datos se crea automáticamente
- No necesitas activar venv ni instalar dependencias

Cuando ejecutas localmente:
- Debes gestionar la base de datos manualmente
- Debes activar el venv
- Debes configurar el archivo `.env`
