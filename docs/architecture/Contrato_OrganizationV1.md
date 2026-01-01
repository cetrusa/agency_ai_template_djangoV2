Perfecto. Procedemos **formalmente**.

A partir de aquí hablo **como Arquitecto de Plataforma**, con criterio **conservador, explícito y orientado a cerrar el MVP del framework**, no a adelantarnos a multi-tenant avanzado.

---

# 📜 FASE 2.5 — PASO 2

## Contrato **Organization v1** (Framework ERP SSR)

Este contrato define **qué es** y **qué no es** una Organization en la **v1 del framework**, tomando como referencia **DataZenith real**, pero **sin arrastrar complejidad innecesaria**.

---

## 1️⃣ Rol de Organization en el Framework

### Definición formal

> **Organization** es la **entidad de negocio activa** sobre la cual se habilitan módulos, permisos y navegación dentro del sistema.

### Importante

* **NO** es infraestructura
* **NO** es configuración del servidor
* **NO** es multi-DB activa en v1
* **SÍ** es el **eje de contexto del usuario autenticado**

---

## 2️⃣ Separación de planos (clave arquitectónica)

Inspirado directamente en tu `powerbi_adm` + `conf_empresas`.

### 🔹 Control Plane (ya existe)

* `organization_admin` (congelada)
* Configura **la instancia**
* Vive fuera del flujo diario del usuario

### 🔹 Business Plane (nuevo)

* `apps/orgs`
* Representa **empresas de negocio**
* Interactúa con usuarios, permisos y módulos

👉 **Organization v1 vive en el Business Plane.**

---

## 3️⃣ Alcance explícito de Organization v1

### ✅ INCLUYE (v1)

1. **Identidad**

   * id
   * nombre
   * slug / código corto

2. **Estado**

   * activa / inactiva

3. **Auditoría mínima**

   * created_at
   * updated_at

4. **Relación con usuarios**

   * Many-to-Many (User ↔ Organization)
   * Con rol simple (member / admin)

5. **Empresa activa**

   * Concepto explícito (una por sesión)
   * Selección manual (no automática)

---

### ❌ EXCLUYE (v1)

Todo lo siguiente queda **LATENTE**, inspirado en DataZenith pero **NO implementado ahora**:

* ❌ credenciales de DB
* ❌ host / puerto
* ❌ múltiples conexiones activas
* ❌ SQLAlchemy engines
* ❌ integración Power BI
* ❌ stored procedures
* ❌ middleware de resolución automática
* ❌ switching por subdominio

Esto **no se descarta**, solo se **postpone conscientemente**.

---

## 4️⃣ Contrato funcional (qué garantiza el framework)

### Garantías v1

* Un usuario **DEBE**:

  * estar autenticado
  * tener al menos una Organization
  * tener una Organization activa para operar

* El sistema **DEBE**:

  * bloquear acceso funcional si no hay Organization activa
  * permitir cambiar Organization manualmente
  * reflejar la Organization activa en navegación

---

## 5️⃣ Relación con `accounts` y `users_admin`

### Claridad absoluta

| App                  | Responsabilidad                         |
| -------------------- | --------------------------------------- |
| `accounts`           | Autenticación (login / logout / sesión) |
| `users_admin`        | Gestión de usuarios                     |
| `orgs`               | Asociación usuario ↔ empresa            |
| `organization_admin` | Configuración global (congelada)        |

👉 **Ninguna app pisa a la otra.**

---

## 6️⃣ Contrato de datos (conceptual, no código aún)

### Organization (v1)

```text
Organization
- id
- name
- slug
- is_active
- created_at
- updated_at
```

### Membership (User ↔ Organization)

```text
Membership
- user
- organization
- role (admin | member)
- is_active
```

---

## 7️⃣ UX mínima esperada (sin diseño aún)

* Si el usuario:

  * no tiene Organization → mensaje claro
  * tiene una sola → se auto-selecciona
  * tiene varias → selector explícito

Esto **NO requiere middleware** en v1.

---

## 8️⃣ Estado del contrato

✅ **Organization v1 DEFINIDA**
✅ Compatible con DataZenith
✅ Conservadora
✅ No rompe core
✅ Habilita Fase 3 cuando toque

---

## ➡️ Siguiente paso (uno solo)

Ahora sí podemos avanzar de forma segura a:

### **FASE 2.5 — PASO 3: Diseño de la App `apps/orgs` (sin código aún)**

En ese paso veremos:

* responsabilidades exactas de la app
* qué vistas existen
* qué NO debe hacer
* cómo interactúa con navegación y sesión

Cuando confirmes, avanzamos **sin tocar código todavía**.

Responde solo con:

> **“Avancemos a Fase 2.5 — Paso 3”**

Excelente trabajo manteniendo el rumbo. Aquí es donde muchos proyectos se descarrilan; tú lo estás evitando.
