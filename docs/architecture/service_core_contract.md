Sí, me parece **exactamente el movimiento correcto** 👍
Antes de escribir una sola línea de código, **consolidar el contrato en un `.md`** es lo que diferencia un framework serio de un proyecto que se improvisa.

A continuación te entrego el  **documento canónico del contrato** , incorporando  **todas las decisiones tuyas + las recomendaciones de Gemini** , listo para guardarse como, por ejemplo:

```
docs/architecture/service_core_contract.md
```

---

# 📘 Service Core Contract

## Framework Empresarial SSR – Django + HTMX

**Versión:** v0.1
**Estado:** APROBADO
**Fase:** FASE 2 — Paso 1 y Paso 2 (Diseño)
**Fecha:** 2026-01-02

---

## 1. Propósito del Service Core

El **Service Core** define el contrato estándar para toda la lógica de negocio del framework ERP.

Su objetivo es:

* Eliminar scripts espagueti
* Desacoplar la lógica de negocio de:
  * HTTP
  * Templates
  * Formularios
  * ORM de Django (cuando aplique)
* Permitir que el sistema escale sin convertirse en un monolito frágil
* Soportar SSR + HTMX, procesos largos y futura ejecución async

Este módulo  **NO implementa lógica de negocio concreta** .
Define  **infraestructura, contratos y reglas** .

---

## 2. Principios no negociables

* ❌ No SPA
* ❌ No React / Vue
* ❌ No DRF para UI
* ✅ Django SSR + HTMX
* ✅ Framework-first, no app-first
* ✅ Contratos explícitos
* ✅ Observabilidad desde el diseño

---

## 3. Ubicación y alcance del módulo

### 📁 Nombre aprobado

**`apps/service_core`** (singular)

**Justificación:**

* Mantiene coherencia semántica con `apps/core`
* Denota  **infraestructura base** , no servicios de negocio
* Evita confusión con servicios específicos (ej. `InvoiceService`)

---

## 4. Arquitectura de capas

### 🧱 Decisión: **Una sola capa**

**Justificación (Pragmatismo Radical):**

* Separar Application / Domain (DDD puro) hoy introduce:
  * boilerplate innecesario
  * fricción cognitiva
  * lentitud en Fase 3 y 4
* Comenzamos con una capa sólida y clara
* Si un módulo futuro lo requiere, se refactoriza  **ese módulo** , no todo el framework

---

## 5. Contrato de aislamiento (Dependencias prohibidas)

### 🚫 Prohibiciones estrictas

El módulo `apps/service_core` y cualquier servicio que herede de él tiene **PROHIBIDO** importar:

* `django.http`
* `django.shortcuts`
* `django.views`
* `django.forms`
* `django.template`

👉 **Regla de oro:**
Un servicio  **nunca conoce HTTP ni UI** .

---

### ⚠️ Aclaración sobre modelos Django

* Se **permite** importar `django.db.models`:
  * solo en servicios de negocio concretos
  * nunca en la base abstracta si se puede evitar
* **No se deben retornar modelos crudos** hacia la vista
* La salida debe viajar como:
  * `dict`
  * `dataclass`
    vía `ServiceResult`

---

## 6. Interfaz estándar de un Servicio

### 🔹 Firma conceptual

```text
Service.execute(input: Dataclass, *, actor, context) -> ServiceResult
```

### Componentes:

* **input**
  * Dataclass nativo de Python
  * Define explícitamente los datos requeridos
  * No es `dict`
  * No es `request`
* **actor**
  * Usuario, sistema o identidad ejecutora
  * Puede ser `None` en procesos automáticos
* **context**
  * Dataclass o dict con información de runtime:
    * organización actual
    * request_id
    * locale
    * flags de ejecución

---

## 7. Entidad estándar de retorno: ServiceResult

### 📦 Estructura obligatoria

```text
ServiceResult
- ok: bool
- data: dict
- errors: list[ServiceError]
- warnings: list[ServiceWarning]
- meta: dict
```

### Decisiones clave:

* `data` es **SIEMPRE un dict**
* Nunca se retorna:
  * int
  * list
  * tuple
  * Model
* Esto garantiza:
  * estabilidad
  * extensibilidad
  * compatibilidad SSR / JSON

---

### 🔸 ServiceError / ServiceWarning

Campos estándar:

* `code: str`
  Ej: `VALIDATION_ERROR`, `NOT_FOUND`
* `message: str`
  Texto humano, usable en UI
* `field: str | None`
  Para errores de validación
* `details: dict | None`
  Debug interno (no UI)

---

## 8. Ciclo de vida de ejecución

1. Validación de `input`
2. Ejecución de la operación principal
3. Post-procesos (si aplica)
4. Retorno de `ServiceResult`

Errores esperables:

* se agregan a `errors`
* `ok = False`

Errores inesperados:

* se capturan en capa superior (runner)
* se convierten a error estándar
* se loguean

---

## 9. Soporte para procesos largos

Desde el contrato (sin implementación aún):

* `meta["duration_ms"]`
* `meta["progress"]` (opcional)
* `warnings` acumulables

Esto habilita:

* feedback HTMX
* futura integración con RQ / workers
* monitoreo básico

---

## 10. Estructura física aprobada

```text
apps/
  service_core/
    __init__.py
    base/
      __init__.py
      service.py          # Clase abstracta BaseService
      result.py           # Dataclasses: ServiceResult, ServiceError, ServiceWarning
      exceptions.py       # Excepciones base del service layer
    infra/
      __init__.py
      logging.py          # Adaptador de logs estructurados
      context.py          # Dataclass Context (actor, request_id, org)
    db/
      __init__.py
      connector.py        # Placeholder SQLAlchemy (fuera del ORM Django)
```

---

## 11. Estado del diseño

* ✅ FASE 2 — PASO 1: Contrato lógico → **CERRADO**
* ✅ FASE 2 — PASO 2: Estructura física → **CERRADO**
* ⏭️ FASE 2 — PASO 3: Primer esqueleto de código (mínimo)

---

## 12. Regla final

> **Todo servicio que no cumpla este contrato
> no forma parte del framework.**
