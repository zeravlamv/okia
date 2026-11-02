# Implementation Plan: Análisis profundo

**Branch**: `003-analisis-profundo` | **Date**: 2026-10-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-analisis-profundo/spec.md`

## Summary

La ficha de un proyecto muestra su vida entera, desde la fecha del pedido de venta, aunque los albaranes, las compras y los gastos caigan en otros ejercicios. El albaranado se compara con la base del pedido. Lo facturado y lo no facturado van separados. Una Gantt marca el inicio y los hitos. Las compras se ven por proveedor y los gastos por cuenta, con la descripción del plan contable.

Actualizar, el botón que ya existe, guarda esa vida en la base de la aplicación. Abrir la ficha lee lo guardado. El cuadro de mando y la jerarquía no se sustituyen. El proyecto de la jerarquía enlaza con la ficha.

## Technical Context

**Language/Version**: Python 3.13 y Django 5.2 LTS

**Primary Dependencies**: Plantillas de Django y `pyodbc` para leer el origen comercial. Las gráficas y la Gantt se dibujan en la página, sin una librería nueva.

**Storage**: La base propia es SQLite en el entorno de back y SQL Server en producción. Además del resumen por ejercicio, guarda la vida de cada proyecto. El origen comercial se lee con `pyodbc` y no se escribe. No se usa PostgreSQL.

**Testing**: pytest y pytest-django, con los datos de ejemplo. La ficha de un pedido de 1.000 con albaranes en otros ejercicios se comprueba sin conectar al origen real.

**Target Platform**: Servidor web interno y navegador de escritorio

**Project Type**: Aplicación web Django, con una pantalla nueva junto al cuadro de mando

**Performance Goals**: Abrir la ficha de un proyecto no lee el origen y aparece en menos de 2 segundos. Actualizar lee cada familia de documentos de la empresa una vez, no una vez por proyecto.

**Constraints**: Solo entra la empresa elegida. Lo no concedido no se muestra como cero. Los importes usan punto de miles, coma decimal, dos decimales y alineación a la izquierda. Un proyecto puede cruzar varios ejercicios. La aplicación no crea, no modifica y no anula datos del origen. El cierre de ejercicio no entra en los gastos.

**Scale/Scope**: Una pantalla por proyecto, cuatro gráficas, una Gantt y tres tablas. El cuadro de mando conserva sus indicadores y su árbol. No se añade el ranking de clientes ni la ficha de canal, delegación o departamento.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. La constitución vigente es `constitution.md` de la raíz, corregida por `negocio.md` y por la especificación de esta ficha.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación del proyecto y su progresión | Pasa |
| Django, Python, HTML y JavaScript | Pasa |
| El origen comercial se lee de SQL Server y no se modifica | Pasa |
| La base propia no vuelve a PostgreSQL: SQLite en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a la empresa elegida y a los grupos concedidos | Pasa |
| Las reglas nuevas de la ficha se escriben en `negocio.md` al implementarla | Pasa |
| Los importes se muestran con punto de miles, coma decimal y dos decimales, alineados a la izquierda | Pasa |

El margen del cuadro de mando no cambia. Esta ficha no lo recalcula: mide la progresión del albarán sobre el pedido.

### Revisión posterior al diseño

Las puertas siguen en pie. La vida del proyecto se guarda en la base propia porque el resumen actual es de un ejercicio y de cuatro niveles, y no puede cruzar ejercicios. El origen solo se lee al pulsar Actualizar. La Gantt y las gráficas salen de esas filas guardadas. No hay una librería nueva ni una aplicación nueva.

## Project Structure

### Documentation (this feature)

```text
specs/003-analisis-profundo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ui.md
│   └── project-life.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
apps/
├── access/                 # permisos ya existentes
├── erp/                    # lectura de pedidos, albaranes, compras, apuntes y nombres
└── margins/                # vida del proyecto, ficha, Actualizar
templates/margins/project.html
templates/includes/filters.html
static/                     # sin librería de gráficas
tests/
├── unit/
└── integration/
negocio.md
```

**Structure Decision**: Se amplía el proyecto Django actual. `erp` lee la vida del proyecto en el origen. `margins` la guarda y la presenta. El enlace sale del proyecto visible en la jerarquía. No se crea una aplicación nueva.

## Complexity Tracking

No hay violaciones de la constitución que justificar. Hace falta guardar la vida del proyecto porque el resumen del ejercicio no abarca otros años. Calcularla al abrir la página se rechaza: la especificación pide no volver a leer el origen al entrar en la ficha.
