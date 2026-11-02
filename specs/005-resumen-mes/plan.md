# Implementation Plan: Resumen del mes

**Branch**: `005-resumen-mes` | **Date**: 2026-10-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-resumen-mes/spec.md`

## Summary

El menú gana Resumen mes. Con la empresa y el ejercicio ya elegidos, la persona elige uno de los doce meses y ve la ficha agrupada de los proyectos cuyo pedido de venta cae en ese mes. Cada fila es el resumen de la ficha ya guardada: pedido de cliente, albaranes de cliente, pedidos de compra, albaranes de compra y gastos. Los totales, el margen, los pendientes y tres gráficas salen de esa misma suma. Abrir la página no lee el origen y no pulsa Actualizar.

## Technical Context

**Language/Version**: Python 3.13 y Django 5.2 LTS

**Primary Dependencies**: Django, las plantillas y el CSS que ya dibujan la ficha y las barras. No se añade una librería de gráficas.

**Storage**: La base propia es SQLite en el entorno de back y SQL Server en producción. El resumen se calcula al abrir, a partir de las fichas ya guardadas. No hay tabla nueva. El origen comercial no se lee ni se escribe. No se usa PostgreSQL.

**Testing**: pytest y pytest-django, con fichas de ejemplo. Se comprueba el mes, los totales, el aviso de un proyecto en dos meses y la omisión de un grupo no concedido, sin conectar al origen real.

**Target Platform**: Servidor web interno y navegador de escritorio

**Project Type**: Aplicación web Django. Una pantalla nueva y una entrada de menú. El cálculo vive junto a la ficha del proyecto.

**Performance Goals**: Abrir un mes no lee el origen. Un mes de unos doscientos proyectos se arma con las filas ya guardadas de esa empresa, en una sola consulta de pantalla.

**Constraints**: Solo entra la empresa elegida. El mes del proyecto es la fecha del pedido de venta. El gasto no vuelve a sumar el albarán de compra. Un grupo no concedido no se muestra como cero. Los importes siguen el formato ya vigente. Un mes cerrado se consulta y no se abre. La página no crea, no modifica y no anula documentos.

**Scale/Scope**: Doce meses del ejercicio elegido. Cinco totales, los indicadores de la especificación y tres gráficas. Una fila de resumen por proyecto, con enlace a su ficha.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. La constitución vigente es `constitution.md` de la raíz, corregida por `negocio.md` y por la especificación de este resumen.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación del resumen del mes | Pasa |
| Django, Python, HTML y JavaScript. Las gráficas reutilizan el dibujo que ya tiene la ficha | Pasa |
| El origen comercial se lee de SQL Server y no se modifica. Esta pantalla no lo lee | Pasa |
| La base propia no vuelve a PostgreSQL: SQLite en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a la empresa elegida | Pasa |
| La regla del resumen se escribe en `negocio.md` al implementarla | Pasa |
| Los importes se muestran con punto de miles, coma decimal y dos decimales, alineados a la izquierda | Pasa |
| Un grupo de información no concedido no se sustituye por cero | Pasa |

El resumen no cambia el cálculo de la ficha ni el cierre del mes. Solo agrupa lo ya guardado.

### Revisión posterior al diseño

Las puertas siguen en pie. No hay tabla nueva, ni migración, ni lectura del origen al abrir. El mes se reconoce por la fecha del pedido ya guardada en la ficha. Las tres gráficas usan los mismos importes que los indicadores. No hay una librería nueva ni una aplicación nueva.

## Project Structure

### Documentation (this feature)

```text
specs/005-resumen-mes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── resumen.md
│   └── ui.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
apps/
├── access/                 # los grupos de información ya deciden qué cifra se ve
├── erp/                    # no se llama al abrir Resumen mes
└── margins/
    ├── month_summary.py   # agrupa las fichas del mes
    ├── project_life.py    # la ficha de un proyecto no cambia de reglas
    ├── views.py           # la pantalla del mes
    └── urls.py            # la ruta del resumen
templates/
├── base.html              # la opción Resumen mes en el menú
└── margins/
    └── month.html         # la ficha agrupada, los indicadores y las gráficas
negocio.md                 # la regla del resumen, al implementar
tests/
├── unit/
└── integration/
```

**Structure Decision**: El agrupado es una lectura nueva dentro de `apps.margins`, porque las fichas ya viven ahí. No se crea otra aplicación ni otra tabla. La ficha de un proyecto sigue en su pantalla.

## Complexity Tracking

No aplica. El diseño no abre una puerta de la constitución.
