# Implementation Plan: Margen de pedidos por proyecto

**Branch**: `001-margen-pedidos-proyecto` | **Date**: 2026-10-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-margen-pedidos-proyecto/spec.md`

## Summary

OKIA consulta, sin modificarlos, los pedidos de venta y las imputaciones de OKOA. Para cada pedido no anulado muestra el precio de venta sin impuestos, el coste del pedido y el margen del pedido. Al lado, y sin mezclarlo, muestra los ingresos contables del proyecto. El coste suma las líneas de compra del proyecto y los apuntes cuya cuenta indique horas, mano de obra o personal, aunque esa hora ya esté en una compra.

La aplicación es un proyecto Django con pantallas HTML. Los usuarios, perfiles, empresas autorizadas y permisos por grupo de información se configuran en el administrador. La base propia de la aplicación usa PostgreSQL en el entorno de back y SQL Server en producción. La información comercial y contable se lee, solo lectura, de SQL Server.

## Technical Context

**Language/Version**: Python 3.12 y Django 5.2 LTS

**Primary Dependencies**: Django templates, el administrador de Django, `psycopg` para PostgreSQL, `mssql-django` para SQL Server, correo de Django para la recuperación de contraseña

**Storage**: Dos conexiones. `default` guarda usuarios, perfiles, empresas autorizadas, permisos y parámetros de conexión: PostgreSQL en back y SQL Server en producción. `erp` lee SQL Server y no escribe.

**Testing**: pytest y pytest-django. El cálculo del margen se prueba con filas de ejemplo. Los modelos propios se prueban sobre PostgreSQL. La lectura real de SQL Server se prueba solo cuando esa conexión está configurada.

**Target Platform**: Servidor web interno, navegador de escritorio

**Project Type**: Aplicación web Django, pantallas de servidor y administrador

**Performance Goals**: Con hasta 50 personas a la vez y hasta 5.000 pedidos del periodo, el panel y la ficha de un pedido se muestran en menos de 5 segundos

**Constraints**: Cada consulta del ERP filtra por empresa. No se guarda la contraseña en el navegador. El enlace de recuperación caduca a los 60 minutos y solo sirve una vez. La sesión recordada dura 30 días. Los importes se muestran con dos decimales. La moneda sale de la empresa o, si no existe, es el euro.

**Scale/Scope**: Varias empresas en el mismo origen, usuarios internos, cinco recorridos: acceso, margen del pedido, pendientes de cruce, panel e administración de permisos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. No aporta principios exigibles. La constitución vigente es `constitution.md` de la raíz, corregida por la sesión de aclaraciones del 2026-10-30 cuando ambas discrepan.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación ya aclarada | Pasa |
| Django, Python, HTML y JavaScript | Pasa |
| Usuarios, perfiles y acceso por grupo de información se configuran en el administrador | Pasa |
| La información comercial y contable se lee de SQL Server con parámetros definidos en el administrador | Pasa |
| La base propia usa PostgreSQL en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a las empresas asignadas a la persona | Pasa |
| La aplicación no crea ni modifica pedidos, compras, artículos ni apuntes | Pasa |
| Las reglas de negocio viven en `negocio.md` y el estado del trabajo en `memory.md` | Pasa |
| La frase original de margen bruto y margen neto de `constitution.md` no se implementa: manda la especificación aclarada | Pasa, con esa sustitución explícita |

### Revisión posterior al diseño

Las puertas siguen en pie. El modelo separa los datos propios de la lectura del ERP. Los contratos no abren escrituras sobre el origen. `research.md` cierra el mapeo de columnas sin inventar un esquema físico definitivo.

## Project Structure

### Documentation (this feature)

```text
specs/001-margen-pedidos-proyecto/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ui.md
│   └── margin-query.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
├── settings.py
├── urls.py
└── wsgi.py
apps/
├── accounts/
├── access/
├── erp/
└── margins/
templates/
static/
tests/
├── unit/
└── integration/
negocio.md
memory.md
```

**Structure Decision**: Un solo proyecto Django. El administrador y las pantallas HTML conviven en ese proyecto. `accounts` cubre el acceso y la recuperación de contraseña. `access` cubre empresas autorizadas y grupos de información. `erp` cubre la conexión de solo lectura y el mapeo por nombre de columna. `margins` cubre el cálculo, el panel y los pendientes de cruce.

## Complexity Tracking

No hay violaciones de la constitución que justificar. Las dos conexiones de base de datos cumplen, cada una, una regla distinta: la base propia cambia de motor según el entorno y el origen comercial permanece en SQL Server de solo lectura.
