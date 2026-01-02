
# CONTEXTO GENERAL DEL PROYECTO

## Framework Empresarial SSR en Django (Agency AI Template)

### 1. Naturaleza del proyecto

Este proyecto  **NO es una aplicación final** ,  **NO es una SPA** , y  **NO es un prototipo rápido** .

Es un **framework base empresarial** construido sobre  **Django 5.x + Server-Side Rendering (SSR) + HTMX** , cuyo objetivo es servir como **plataforma reutilizable** para desarrollar aplicaciones de tipo ERP, BI y sistemas administrativos (empresas, contabilidad, importaciones, reportes, etc.).

El framework está pensado para:

* formularios complejos
* procesos largos (ETL, cargues, validaciones)
* dashboards
* exportaciones
* operaciones empresariales reales

No para experiencias SPA, mobile-first ni frontend pesado.

---

### 2. Principios arquitectónicos (NO negociables)

* Django 5.x
* Server-Side Rendering (SSR)
* HTMX para interactividad puntual
* CRUD declarativo (motor propio ya existente)
* Navegación declarativa por permisos
* NO React
* NO Vue
* NO SPA
* NO DRF para UI (solo podría usarse JSONResponse puntual)
* Arquitectura modular por apps
* Core congelado y protegido

---

### 3. Estado del core (CRÍTICO)

Existe un  **CORE v1.0.0 CONGELADO** , que **NO se modifica** bajo ninguna circunstancia:

* `apps/core/*`
* Motor CRUD declarativo
* CRUD Kit (templates y lógica)
* exporting.py
* Registro de CRUDs vía `AppConfig.ready()`

El core **ya funciona** y  **ya fue auditado** .
Cualquier sugerencia que implique tocar el core debe  **detenerse y reportarse** , no ejecutarse.

---

### 4. Infraestructura

* Docker:
  * `web` + `db` siempre
  * `redis` + `worker` opcionales (infraestructura latente)
* El proyecto **DEBE funcionar sin Redis**
* RQ solo se activa bajo perfil específico
* Sin Node.js en el stack

---

### 5. Estado actual del proyecto

* Auditoría PRE-DOCKER completada
* Bloqueadores críticos corregidos
* Fase 1A (Estabilización Visual) **cerrada sin cambios**
* Bootstrap 5.3 y HTMX ya cargados globalmente
* Framework estable, sin errores 500
* **Actualmente ejecutando FASE 1B**

---

### 6. Fase actual: FASE 1B – Layout Limpio y Controlado

**Objetivo de Fase 1B**
Mejorar la claridad visual del layout (sidebar, navbar, contenido) usando  **solo clases Bootstrap 5** , sin cambiar estructura ni comportamiento.

 **Reglas de Fase 1B** :

* NO reescribir `base.html`
* NO mover jerarquía HTML
* NO renombrar bloques `{% block %}`
* NO tocar CRUD Kit
* NO tocar autenticación
* NO introducir JS nuevo
* NO eliminar CSS existente
* Solo ajustes visuales progresivos

---

### 7. Roadmap de alto nivel

1. Fase 1A – Estabilización visual (cerrada)
2. Fase 1B – Layout limpio y controlado (en curso)
3. Fase 2 – Service Core (patrón de servicios, SQLAlchemy externo)
4. Fase 3 – App piloto de importación (validar framework)
5. Fase 4 – Componentes UI reutilizables
6. Fase 5 – Módulos ERP reales
7. Fase 6 – BI y reportes

---

### 8. Cómo debe ayudar Gemini en este proyecto

Gemini debe actuar como:

* Ingeniero senior
* Conservador
* Crítico
* Paso a paso
* Framework-first, no app-first

Gemini  **NO debe** :

* inventar features
* proponer SPA
* refactorizar core
* reescribir templates base
* asumir código inexistente
* adelantarse de fase

Gemini  **SÍ debe** :

* respetar fases
* detectar riesgos
* sugerir mejoras mínimas
* validar antes de ejecutar
* esperar confirmación

---

### 9. Regla final de trabajo

> **Auditoría → cambios mínimos → validación → siguiente fase**

Cualquier sugerencia que rompa esta secuencia debe ser descartada.
