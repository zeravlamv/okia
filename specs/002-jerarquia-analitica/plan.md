# Implementation Plan: Jerarquía analítica

**Branch**: `002-jerarquia-analitica` | **Date**: 2026-10-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-jerarquia-analitica/spec.md`

## Summary

La analítica del cuadro de mando deja de ser cinco listas sueltas. El orden guardado de los niveles analíticos construye un árbol: el nivel 1 engloba al 2, al 3, al 4 y al 5, y cada nivel siguiente engloba a los que tiene debajo. Al abrir solo se ve el primer nivel. Abrir un grupo muestra el nivel siguiente, sin recalcular.

Cada grupo muestra ventas, ingresos, compras, gastos y margen. Las compras son todas las líneas de compra del proyecto. Los gastos son los apuntes de horas, mano de obra o personal. El margen es ventas menos compras menos gastos. Los ingresos van al lado y no entran en esa resta. Los pedidos que no cierran margen forman un grupo aparte, fuera del árbol, con su precio de venta y sin margen.

Los indicadores generales, el filtro de empresa y ejercicio, y la consulta de cada pedido no cambian.

## Technical Context

**Language/Version**: Python 3.13 y Django 5.2 LTS

**Primary Dependencies**: Plantillas de Django, el administrador de Django y `pyodbc` para leer el origen comercial

**Storage**: La base propia de la aplicación es SQLite en el entorno de back y SQL Server en producción. Guarda personas, perfiles, empresas autorizadas y el orden de los niveles. El origen comercial se lee con `pyodbc` y no se escribe. No se usa PostgreSQL.

**Testing**: pytest y pytest-django. El árbol y el grupo aparte se prueban con los pedidos de ejemplo. La lectura real del origen solo se comprueba cuando esa conexión está configurada.

**Target Platform**: Servidor web interno y navegador de escritorio

**Project Type**: Aplicación web Django, pantallas de servidor y administrador

**Performance Goals**: Con un ejercicio de hasta 1.500 pedidos, el primer nivel y sus cifras aparecen en menos de 5 segundos. Abrir un grupo no vuelve a leer el origen.

**Constraints**: Solo entra la empresa elegida. Un nivel o una cifra no concedidos no se muestran como cero. Los importes usan dos decimales y la moneda de la empresa, o el euro si no tiene. La aplicación no crea, no modifica y no anula datos del origen. El indicador de compras fechadas en el ejercicio sigue siendo distinto de las compras de la jerarquía.

**Scale/Scope**: Una pantalla ya existente, el cuadro de mando. Sustituye el reparto por listas. No añade una pantalla de revisión pendiente ni cambia el margen de cada pedido.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. No aporta principios exigibles. La constitución vigente es `constitution.md` de la raíz, corregida por `negocio.md` y por las aclaraciones del 2026-10-30.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación ya aclarada | Pasa |
| Django, Python, HTML y JavaScript | Pasa |
| El orden de los niveles se configura en el administrador | Pasa |
| La información comercial y contable se lee de SQL Server y no se modifica | Pasa |
| La base propia no vuelve a PostgreSQL: SQLite en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a la empresa elegida y a los grupos concedidos | Pasa |
| Las reglas de negocio viven en `negocio.md` | Pasa |
| El margen de la jerarquía es ventas menos compras menos gastos. Los ingresos no se mezclan | Pasa |

### Revisión posterior al diseño

Las puertas siguen en pie. No hay una tabla nueva: el orden ya guardado decide la anidación. El contrato de cálculo separa compras y gastos sin cambiar la suma que hoy es el coste del pedido. El grupo aparte no entra en esa suma. Abrir un nivel es una acción del navegador sobre un árbol ya calculado.

## Project Structure

### Documentation (this feature)

```text
specs/002-jerarquia-analitica/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ui.md
│   └── hierarchy.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
apps/
├── access/          # orden de los niveles y permisos ya existentes
├── erp/             # lectura de pedidos, compras, apuntes y descripciones
└── margins/         # árbol, cifras y cuadro de mando
templates/margins/dashboard.html
static/js/breakdown.js
tests/
├── unit/
└── integration/
negocio.md
```

**Structure Decision**: Se amplía el proyecto Django actual. `margins` construye el árbol a partir del orden de `access` y de las filas que ya lee `erp`. No se crea una aplicación nueva ni una pantalla nueva.

## Complexity Tracking

No hay violaciones de la constitución que justificar. La jerarquía reutiliza el cálculo del pedido y el orden analítico ya guardado.
