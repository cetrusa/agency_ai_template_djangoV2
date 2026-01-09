# Definición de Hecho (DoD) — Framework Base

**Propósito:** Establecer criterios objetivos para declarar “terminado” un incremento del framework base sin contaminar el contrato ni acumular deuda documental.

**Regla:** Ningún trabajo se considera “hecho” sin cumplir **documentación + pruebas funcionales + depuración + legacy + commit**.

---

## 1) DoD por tipo de cambio

### 1.1 Cambio en contrato / arquitectura

**Hecho = Sí**
- Documentación normativa actualizada (constitución/arquitectura/ADR según aplique).
- Sección “Sí/No” revisada y consistente.
- No hay “promesas” (texto que compromete implementación futura), solo reglas/contratos vigentes.
- Evidencia de prueba funcional relacionada al cambio.
- Se movió a `/legacy` todo artefacto temporal (notas de trabajo, borradores, evidencias detalladas que ya no aplican).
- Limpieza: sin duplicidad de docs y sin referencias rotas.
- Commit con mensaje trazable (convención del equipo).

**Hecho = No**
- Falta ADR cuando el cambio altera reglas del core.
- El cambio introduce ambigüedad (“se verá más adelante”, “por ahora no importa”).

### 1.2 Módulo CRUD nuevo (business o system)

**Hecho = Sí**
- Sigue el contrato CRUD declarativo.
- Permisos definidos y validados (caso negativo incluido).
- Scoping multiempresa verificado (caso “empresa A no ve B”).
- Exportaciones aplican permisos/scoping/filtros.
- Pruebas funcionales ejecutadas con evidencia.
- Cierre: limpieza y movimiento a `/legacy` de lo temporal.
- Commit trazable.

**Hecho = No**
- CRUD ad-hoc fuera del contrato.
- Vistas con lógica de negocio.

---

## 2) Evidencias mínimas requeridas (pruebas funcionales)

**Sí**
- Matriz de casos (happy path + permisos + scoping + export).
- Evidencia: capturas, logs o checklist firmado (según política del equipo).

**No**
- No cerrar fase con “probado en mi máquina” sin evidencia.

---

## 3) Política de legacy (cierre obligatorio)

**Qué va a `/legacy`**
- Notas temporales de investigación.
- Evidencias detalladas por fase que ya no son necesarias para operar el framework.
- Experimentos y documentación revertida.

**Qué NO va a `/legacy`**
- Contrato vigente y arquitectura vigente.
- ADRs (las decisiones se mantienen accesibles).

---

## 4) Checklist de cierre (para cada fase)

- Docs vigentes actualizados (si aplica).
- Pruebas funcionales ejecutadas + evidencia.
- Sin “promesas” de implementación en docs.
- Limpieza (referencias rotas / duplicados / artefactos temporales).
- Movimiento de temporal a `/legacy`.
- Commit trazable.

