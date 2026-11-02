# Implementation Plan: Cierre por ejercicio y mes

**Branch**: `004-cierre-ejercicio-mes` | **Date**: 2026-10-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-cierre-ejercicio-mes/spec.md`

## Summary

Una persona administradora cierra o reabre un mes de un ejercicio para una empresa. Actualizar sigue leyendo el origen una vez por familia, pero no sustituye la ficha de un proyecto que tenga algún pedido de venta no anulado de ese ejercicio en un mes cerrado. El cuadro de mando y el margen de pedidos conservan la aportación ya guardada de esos proyectos y recalculan el resto. Al terminar, se nombran los meses que no se han tocado.

## Technical Context

**Language/Version**: Python 3.13 y Django 5.2 LTS

**Primary Dependencies**: Django admin para el cierre. La actualización ya usa las lecturas de `apps.erp` y el guardado de `apps.margins`. No se añade una librería nueva.

**Storage**: La base propia es SQLite en el entorno de back y SQL Server en producción. El cierre y la aportación por proyecto se guardan ahí. El origen comercial se lee con `pyodbc` y no se escribe. No se usa PostgreSQL.

**Testing**: pytest y pytest-django, con los datos de ejemplo. Se cierra un mes, se actualiza y se comprueba que la ficha retenida no cambia, sin conectar al origen real.

**Target Platform**: Servidor web interno, navegador de escritorio y la administración de Django

**Project Type**: Aplicación web Django. El control nuevo está en la administración. La pantalla de Actualizar solo añade el aviso de meses cerrados.

**Performance Goals**: Abrir la ficha no lee el origen. Actualizar sigue leyendo cada familia una vez por empresa, también cuando hay meses cerrados. Cerrar o reabrir un mes no lee el origen.

**Constraints**: Solo entra la empresa elegida. Un mes sin marca está abierto. La persona que no administra no cambia el cierre. Los importes no cambian de formato. La aplicación no crea, no modifica y no anula datos del origen. Un proyecto retenido conserva importes y fecha de actualización.

**Scale/Scope**: Doce meses por empresa y ejercicio. Una marca por combinación. La actualización de un ejercicio con meses abiertos y cerrados. El aviso nombra los meses cerrados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. La constitución vigente es `constitution.md` de la raíz, corregida por `negocio.md` y por la especificación de este cierre.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación del cierre | Pasa |
| Django, Python, HTML y JavaScript. El control vive en la administración, como usuarios y empresas | Pasa |
| El origen comercial se lee de SQL Server y no se modifica | Pasa |
| La base propia no vuelve a PostgreSQL: SQLite en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a la empresa elegida | Pasa |
| La regla del cierre se escribe en `negocio.md` al implementarla | Pasa |
| Los importes se muestran con punto de miles, coma decimal y dos decimales, alineados a la izquierda | Pasa |

El cierre no cambia el cálculo de un proyecto que sí se actualiza. Solo decide cuáles se sustituyen.

### Revisión posterior al diseño

Las puertas siguen en pie. El cierre es una fila de la base propia. Actualizar sigue siendo la única lectura del origen. Un mes cerrado no se rellena con esa lectura. No hay una librería nueva ni una aplicación nueva.

## Project Structure

### Documentation (this feature)

```text
specs/004-cierre-ejercicio-mes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cierre.md
│   └── ui.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
apps/
├── access/                 # la administración ya registra usuarios, perfiles y empresas
├── erp/                    # lectura del origen; no cambia la forma de leer
└── margins/
    ├── admin.py            # alta del cierre en la administración
    ├── models.py           # cierre de mes y aportación guardada del proyecto
    ├── snapshot.py         # Actualizar separa proyectos retenidos y abiertos
    ├── project_life.py     # no borra ni reescribe la ficha retenida
    └── views.py            # el aviso de meses cerrados al terminar
negocio.md                  # la regla del cierre, al implementar
tests/
├── unit/
└── integration/
```

**Structure Decision**: Se queda en la aplicación `margins`, que ya guarda el resumen y las fichas. La administración de Django descubre `apps/margins/admin.py`. No se crea otra aplicación.

## Complexity Tracking

No aplica. El diseño no abre una puerta de la constitución.
