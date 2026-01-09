# Constitución Técnica — Framework Base (Django SSR + HTMX / “Backpack-lite”)

**Estado:** Normativa vigente del framework base (contrato técnico).

**Propósito:** Establecer reglas explícitas, auditables y estables para construir módulos sobre el framework base sin “magias” implícitas, preservando consistencia, mantenibilidad y calidad.

**Ámbito:** Aplicaciones Django 5.x con renderizado del lado del servidor (SSR) y uso de HTMX para interacciones incrementales. Incluye el patrón CRUD declarativo “Backpack-lite”, exportaciones server‑side, multiempresa v0 por scoping, y un Service Core desacoplado.

---

## 1) Principios innegociables

### 1.1 Reglas (Sí / No)

**Sí**
- **Django 5.x** como runtime y convenciones idiomáticas del framework.
- **SSR (Server-Side Rendering)** como modo primario de UI.
- **HTMX** para mejoras incrementales (modales, acciones, partials) sin convertir la UI en un cliente pesado.
- **CRUD declarativo**: los módulos declaran configuración y el framework provee el comportamiento estándar.
- **Exportaciones server-side** (CSV/XLSX/PDF) con permisos y scoping aplicados.
- **Multiempresa v0 por scoping** (no multi‑DB) basada en “empresa activa” y filtrado consistente.
- **Service Core desacoplado** como capa de orquestación de negocio: `Context` + `BaseService` + `ServiceResult` (nombres referenciales del contrato, no promesa de implementación).
- **Navegación declarativa por permisos**, sin lógica ad-hoc en templates.
- **Core congelado**: solo cambios aditivos y versionados del contrato.
- **Cierre por fases** con pruebas funcionales y depuración: lo temporal va a `/legacy`.

**No**
- No “cliente pesado” como fuente de verdad, no replicar lógica de negocio al frontend.
- No “magias”: no comportamiento crítico basado en side effects implícitos, reflexión oculta o convenciones sin documentación.
- No lógica de negocio en vistas, templates o middleware más allá de validación/enrutamiento/ensamblado.
- No bypass de permisos o scoping para “salvar el sprint”.
- No cambios destructivos del core en fases normales; no refactors masivos sin ADR.

### 1.2 Anti‑ejemplos (prohibidos)
- “Si el nombre del template coincide, el permiso se asume automáticamente” (implícito, no auditable).
- “El filtrado por empresa se aplica solo en UI” (scoping incompleto; fuga de datos).
- “La vista hace queries complejas, aplica reglas y devuelve HTML” (vistas gruesas; imposible de probar).
- “El export ignora permisos porque es ‘solo descarga’” (violación de seguridad).

---

## 2) Separación estricta: `accounts` (auth) vs `usuarios` (negocio)

**Objetivo:** Mantener la identidad/autenticación desacoplada del dominio de miembros/empresa.

**Sí**
- `accounts`: autenticación, sesiones, credenciales, login/logout, recuperación, integración con `django.contrib.auth`.
- `usuarios`: dominio de negocio “miembros” (membresías, roles por empresa, altas/bajas, estados), sin redefinir autenticación.
- El dominio de permisos por empresa se expresa en `usuarios`/dominio, pero se integra con el sistema de auth de Django.

**No**
- No mezclar modelos de negocio (membresías/roles) dentro de `accounts`.
- No introducir lógica de autenticación (passwords, login flows) dentro de `usuarios`.

---

## 3) Reglas de arquitectura: vistas delgadas, servicios orquestadores

### 3.1 Regla principal (Sí / No)

**Sí**
- Las **views** coordinan: obtener request/contexto, validar entrada, delegar a servicio, seleccionar template/partial, responder.
- Los **servicios** orquestan reglas de negocio y efectos (persistencia, permisos, scoping, validaciones complejas).
- Los **modelos** encapsulan invariantes simples (constraints, clean, helpers) sin convertirse en “God objects”.

**No**
- No lógica de negocio en templates (más allá de presentación).
- No queries “inteligentes” en templates ni “if” de permisos dispersos.
- No servicios que renderizan HTML (los servicios devuelven datos/resultados; la presentación vive en views/templates).

### 3.2 Service Core (contrato)

**Contrato mínimo (auditable):**
- `Context`: porta identidad, empresa activa, permisos/rol efectivo, metadatos de request.
- `ServiceResult`: estructura uniforme (éxito/fallo, payload, errores normalizados, warnings, metadata).
- `BaseService`: patrón de ejecución consistente (validación → autorización → operación → resultado).

**Nota:** Estos nombres son parte del contrato del framework; si existen implementaciones distintas, deben mapearse explícitamente a este contrato.

---

## 4) Multiempresa v0 por scoping (NO multi‑DB)

**Definición:** Multiempresa v0 significa que la empresa activa determina el conjunto de datos visibles/modificables; el aislamiento se logra por filtros y reglas consistentes en toda operación.

**Sí**
- “Empresa activa” explícita (session/contexto) y verificable.
- Scoping aplicado en: listados, detalle, mutaciones, exports y endpoints HTMX.
- Pruebas funcionales que validan no‑fuga entre empresas.

**No**
- No múltiples conexiones/routers por empresa en v0.
- No permitir acciones sin empresa activa cuando el módulo requiera scoping.

---

## 5) CRUD declarativo tipo Backpack-lite

**Definición:** Un módulo define una configuración declarativa (campos, filtros, permisos, acciones, templates/partials) y el framework ejecuta el comportamiento estándar con consistencia.

**Sí**
- Configuración explícita y versionable (p.ej., `CrudConfig` o equivalente).
- Rutas estándar, permisos declarativos, acciones y modales HTMX consistentes.
- Un ejemplo canónico (“contrato vivo”) que siempre compila y sirve como referencia.

**No**
- No duplicar CRUD ad-hoc por cada módulo.
- No reglas ocultas “por convención” sin contrato escrito.

---

## 6) Exportaciones server-side (CSV/XLSX/PDF)

**Sí**
- Exportaciones se ejecutan en servidor y respetan: permisos, scoping de empresa, y filtros aplicados.
- Registro/auditoría mínima: quién exportó, qué exportó, cuándo, con qué alcance.

**No**
- No exportar datasets completos si el usuario no tiene permiso de alcance.
- No “exportar desde UI” como simple serialización sin control.

---

## 7) Navegación declarativa por permisos

**Sí**
- El menú se deriva de una declaración central (items + permiso requerido + condiciones de empresa activa).
- Los templates consumen esa declaración, no duplican lógica.

**No**
- No condiciones dispersas en múltiples templates.
- No links a rutas no protegidas por permisos equivalentes.

---

## 8) Qué significa “core congelado” y cómo se versiona el contrato

### 8.1 Core congelado

**Core** = el conjunto mínimo de piezas transversales que habilitan módulos sin acoplarse entre sí (layout base, navegación declarativa, infraestructura de CRUD declarativo, Service Core, scoping y utilidades comunes).

**Congelado** significa:
- No se cambian comportamientos existentes de forma incompatible sin ADR.
- Los cambios permitidos son **aditivos**: nuevas capacidades o extensiones que no rompen módulos existentes.

### 8.2 Versionado del contrato

**Contrato** = documentos normativos + ejemplo canónico.

**Reglas:**
- Cada cambio al contrato debe:
  - actualizar documentación normativa,
  - incluir prueba funcional/regresión mínima,
  - y registrar decisión (ADR si afecta reglas/arquitectura).
- El contrato se versiona con una etiqueta semántica interna (p.ej., `v0`, `v0.1`, `v0.2`) reflejada en los docs.

---

## 9) Cierre por fases: pruebas funcionales + legacy + limpieza

**Sí**
- Toda fase termina con: ejecución de pruebas funcionales, evidencia, y limpieza.
- Todo lo temporal (notas, experimentos, evidencias detalladas que ya no aplican) se mueve a `/legacy`.

**No**
- No se acumulan documentos temporales en `/docs` como “basura histórica”.

---

## 10) Checklist de revisión de PR (obligatoria)

| Área | Pregunta de control | Sí/No | Evidencia esperada |
|---|---|---|---|
| SSR/HTMX | ¿La UI sigue SSR y usa HTMX solo para incremental? |  | Capturas + rutas/partials afectadas |
| Permisos | ¿Cada endpoint/acción tiene permiso explícito equivalente al menú? |  | Lista de permisos + prueba negativa |
| Multiempresa | ¿El scoping por empresa se aplica en list/detalle/mutación/export? |  | Caso “empresa A no ve B” |
| Servicios | ¿La lógica de negocio está en servicios y las views son delgadas? |  | Revisión de diff + pruebas |
| CRUD declarativo | ¿Se usó config declarativa (sin CRUD ad‑hoc)? |  | Config + rutas estándar |
| Exportaciones | ¿CSV/XLSX/PDF son server-side y respetan filtros/permisos? |  | Archivo export + prueba de alcance |
| Navegación | ¿El menú se deriva de declaración por permisos? |  | Item declarado + screenshot |
| Legacy/Limpieza | ¿Se movió lo temporal a `/legacy` y se eliminaron restos? |  | Rutas en legacy + checklist cierre |

