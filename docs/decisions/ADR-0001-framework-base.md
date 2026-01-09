# ADR-0001: Framework Base Django SSR+HTMX (“Backpack-lite”)

**Estado:** Aprobado (v0)

**Fecha:** 2026-01-08

---

## Contexto

Se requiere un framework base para proyectos internos que:
- use Django 5.x con SSR (renderizado server-side),
- utilice HTMX para interacciones incrementales sin adoptar un enfoque de UI cliente pesada,
- ofrezca un patrón CRUD declarativo estilo “Backpack-lite”,
- permita exportaciones server-side (CSV/XLSX/PDF) con permisos y scoping,
- implemente multiempresa v0 mediante scoping (no multi‑DB),
- mantenga un Service Core desacoplado (Context + ServiceResult + BaseService),
- tenga navegación declarativa por permisos,
- congele el core (solo cambios aditivos) y cierre cada fase con pruebas funcionales y depuración/legacy.

El objetivo es maximizar consistencia y auditabilidad, minimizando magia implícita y divergencias por proyecto.

---

## Decisión

Adoptar como base del framework:
- **Django 5.x + SSR** como modelo de UI principal.
- **HTMX** para mejoras incrementales (partials, modales, acciones) manteniendo la fuente de verdad en servidor.
- **CRUD declarativo tipo Backpack-lite** mediante configuración versionable, rutas estándar y permisos declarativos.
- **Exportaciones server-side** (CSV/XLSX/PDF) que respeten permisos, filtros y scoping.
- **Multiempresa v0 por scoping** basado en empresa activa y filtrado consistente, descartando multi‑DB en v0.
- **Service Core desacoplado** como patrón obligatorio de orquestación de negocio.
- **Navegación declarativa por permisos** como única fuente de la estructura del menú.
- **Core congelado**: solo cambios aditivos; cualquier cambio de comportamiento requiere ADR.
- **Cierre por fases** con pruebas funcionales, evidencia y movimiento de lo temporal a `/legacy`.

---

## Alternativas consideradas

1) **Multiempresa por múltiples DB desde el inicio**
- Pros: aislamiento fuerte por tenant.
- Contras: complejidad operativa (routers, migraciones, bootstrap, observabilidad), mayor costo de adopción inicial.

2) **UI cliente pesada con API**
- Pros: desacoplo frontend/backend.
- Contras: duplicación de lógica, mayor superficie y complejidad, menor alineación con objetivo SSR/HTMX.

3) **CRUD ad-hoc por módulo (sin contrato)**
- Pros: velocidad local de un equipo.
- Contras: divergencia, difícil auditoría, deuda técnica acumulada.

---

## Consecuencias

**Positivas**
- Consistencia transversal: permisos, scoping, exports y navegación se aplican de forma uniforme.
- Auditabilidad: reglas explícitas, revisables en PR.
- Menor costo de onboarding: contrato + ejemplo canónico.

**Costes / Trade-offs**
- Requiere disciplina: vistas delgadas y servicios como unidad de negocio.
- Cambios al core son más lentos (necesitan compatibilidad y, cuando aplique, ADR).

**Riesgos y mitigaciones**
- Riesgo: “magia por conveniencia”. Mitigación: secciones Sí/No y checklist PR obligatoria.
- Riesgo: scoping incompleto. Mitigación: casos funcionales negativos obligatorios.

---

## Notas de cumplimiento

- Este ADR no describe un roadmap; define reglas vigentes del framework base.
- No se adopta multi‑DB en v0.

