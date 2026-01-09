# Arquitectura Base — Django SSR + HTMX (Framework Base)

**Objetivo:** Describir la arquitectura de referencia del framework base: capas, responsabilidades, flujos y decisiones operativas para construir módulos consistentes sin acoplamientos.

**Alcance:** Aplicaciones en Django 5.x con SSR + HTMX, CRUD declarativo tipo Backpack-lite, Service Core desacoplado, navegación declarativa por permisos y multiempresa v0 por scoping.

---

## 1) Vista general de capas

### 1.1 Capas (Sí / No)

**Sí**
- **Presentación (SSR/HTMX):** templates, partials, modales, componentes de UI reutilizables.
- **Aplicación (Views/URLs):** routing, composición de respuestas, validación superficial, delegación.
- **Servicios (Service Core):** orquestación de casos de uso, autorización, scoping, validaciones de negocio, llamadas a infraestructura.
- **Dominio (Models + reglas):** entidades e invariantes básicas.
- **Infraestructura:** repositorios/queries, integraciones, exportadores, utilidades.

**No**
- No “mezclar capas” por conveniencia (p.ej. reglas de negocio en templates o views).

---

## 2) Separación de apps: system vs business

**System apps:** piezas transversales (auth, empresa/scoping, usuarios/miembros, navegación, CRUD base, utilidades).

**Business apps:** módulos de negocio (clientes, productos, etc.) que consumen el contrato del framework.

### 2.1 `accounts` vs `usuarios` (regla estricta)

**Sí**
- `accounts`: identidad/autenticación/sesión.
- `usuarios`: miembros, roles por empresa, estados, gestión operativa.

**No**
- No duplicar auth en `usuarios`.
- No poner modelos de membresía/rol dentro de `accounts`.

---

## 3) Flujo de una request SSR/HTMX

### 3.1 Flujo base (auditable)

1. Resolución de URL determina la view.
2. View crea/obtiene `Context` (usuario autenticado, empresa activa, rol/permisos efectivos).
3. View valida input mínimo (forms/serialización) y delega al servicio.
4. Servicio ejecuta: autorización → scoping → operación → `ServiceResult`.
5. View traduce `ServiceResult` a response SSR o partial HTMX.

### 3.2 Reglas (Sí / No)

**Sí**
- El contexto de empresa/permisos es explícito en cada operación de negocio.
- HTMX se usa para partial updates (tabla, fila, modal content, alerts) sin duplicar lógica.

**No**
- No endpoints “especiales” sin permisos porque son HTMX.

---

## 4) Service Core (desacoplado)

### 4.1 Contrato mínimo

**Context**
- Identidad (user), empresa activa, permisos efectivos, metadata de request.

**ServiceResult**
- Estructura uniforme: `ok/failed`, `data`, `errors`, `warnings`, `meta`.

**BaseService**
- Ejecución consistente: `validate()` → `authorize()` → `execute()` → `result`.

### 4.2 Reglas (Sí / No)

**Sí**
- Los servicios son la unidad primaria para pruebas de negocio.
- Las views permanecen delgadas y repetibles.

**No**
- No servicios que rendericen HTML o dependan de templates.

---

## 5) Multiempresa v0 (scoping)

### 5.1 Conceptos

- **Empresa activa:** selección explícita que define alcance.
- **Scoping:** filtros y reglas obligatorias por empresa activa.

### 5.2 Dónde aplica (Sí / No)

**Sí**
- Listados, detalle, creación/edición/borrado, exportaciones, acciones HTMX.

**No**
- No “scoping solo en UI”.

---

## 6) CRUD declarativo tipo Backpack-lite

### 6.1 Objetivo

Estandarizar la construcción de módulos CRUD mediante configuración declarativa para evitar duplicación y divergencias.

### 6.2 Contrato de un CRUD

**Sí**
- Declaración de: modelo/consulta base, campos visibles/editables, filtros, permisos, acciones, templates/partials.
- Rutas estándar predecibles.

**No**
- No CRUD ad-hoc con rutas arbitrarias fuera del contrato.

---

## 7) Exportaciones server-side

### 7.1 Formatos

- CSV
- XLSX
- PDF

### 7.2 Reglas (Sí / No)

**Sí**
- Export respeta permiso + scoping + filtros aplicados.
- Export es trazable (mínimo: actor, alcance, timestamp).

**No**
- No exportaciones que salten autorizaciones.

---

## 8) Navegación declarativa por permisos

### 8.1 Contrato

**Sí**
- Declaración central de items de menú: etiqueta, url, permiso requerido, condición (empresa activa).

**No**
- No menú “armado a mano” en múltiples templates con reglas divergentes.

---

## 9) Core congelado (operación)

### 9.1 Política de cambios

**Sí**
- Cambios al core: aditivos, con documentación normativa y evidencia de prueba.
- Cambios de comportamiento: requieren ADR.

**No**
- No refactors masivos sin decisión registrada.

---

## 10) Cierre de fase (operación)

**Sí**
- Pruebas funcionales ejecutadas con evidencia.
- Limpieza de documentación y artefactos temporales.
- Movimiento de temporal a `/legacy`.

**No**
- No dejar “pendientes” o documentación duplicada sin criterio.

