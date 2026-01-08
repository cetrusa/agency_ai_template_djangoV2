# PROJECT_BASE

Plantilla Django SSR (Templates) + HTMX para dashboards administrativos.

## Qué incluye (implementado)

- UI base con Bootstrap 5 + estilos/tokens del proyecto.
- CRUD Kit Enterprise V1 (listado + tabla partial con filtros/orden/paginación).
- Sistema de modales reusable (HTMX) para formularios y confirmaciones.
- Export engine server-side (CSV/XLSX/PDF).
- docker-compose con Redis y modo DB flexible:
	- PostgreSQL opcional via perfil `postgres`.
	- MySQL/MariaDB del host (ej. Laragon en `3306`) soportado via `.env` (`DJANGO_DB_HOST=host.docker.internal`).

## Qué NO incluye todavía (intencional)

- Automatización CRUD declarativa (tipo Backpack). Se diseña primero, se implementa después.
- Multi-tenant y RBAC empresarial.
- Background workers (Celery/RQ) y colas.

## Registro de Usuarios y Verificación

El sistema incluye un flujo de registro público con verificación por correo electrónico:

1.  **Registro**: Los usuarios pueden crear una cuenta desde `/accounts/register/`.
2.  **Verificación**: Se envía un correo con un enlace temporal (firmado) para activar la cuenta.
3.  **Aprobación**: Tras verificar el correo, el usuario queda en estado "Pendiente de Asignación" y no puede acceder al dashboard hasta que un administrador le asigne permisos o grupos.

**Configuración de Correo:**
Para que el envío de correos funcione, configura las variables SMTP en `.env` o `settings.py`:
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`.
- En desarrollo, los correos se imprimen en la consola si no hay SMTP configurado.

## Uso

### Docker + MySQL (Laragon, puerto 3306)

Pre-requisito: tener MySQL corriendo en Windows (Laragon) y una base creada (ej. `agency_db`).

En `PROJECT_BASE/.env` (ejemplo):

- `DJANGO_DB_ENGINE=django.db.backends.mysql`
- `DJANGO_DB_HOST=host.docker.internal`
- `DJANGO_DB_PORT=3306`

Levantar contenedores (sin Postgres):

- `docker compose up -d --build web redis`

Aplicar migraciones dentro del contenedor:

- `docker compose exec -T web python manage.py migrate`

Notas:

- En Windows + Docker Desktop, `host.docker.internal` resuelve al host automáticamente.
- Si Laragon tiene password en `root`, setea `DJANGO_DB_PASSWORD`.

### Docker + PostgreSQL (perfil opcional)

- `docker compose --profile postgres up -d --build web db redis`

Consulta:
- `PROMPTS/00_CONTEXT.md` para filosofía y reglas.
- `HOW_TO_USE.md` para levantar el entorno.
- `PLATFORM_DECISIONS.md` para decisiones explícitas.
