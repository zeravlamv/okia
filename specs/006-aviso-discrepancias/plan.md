# Implementation Plan: Aviso de discrepancias

**Branch**: `006-aviso-discrepancias` | **Date**: 2026-11-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-aviso-discrepancias/spec.md`

## Summary

El cuadro de mando muestra una campanita con los proyectos del ejercicio cuya ficha ya guardada no cuadra y siguen en Pdte. Revisar. La ventana lista cada proyecto, dice qué pareja falla y abre su ficha. En la ficha, un selector guarda Revisado o Pdte. Revisar. Revisado saca el proyecto del aviso aunque los importes sigan distintos. Abrir el cuadro no lee el origen. Actualizar no borra el estado.

## Technical Context

**Language/Version**: Python 3.13 y Django 5.2 LTS

**Primary Dependencies**: Django, la plantilla del cuadro de mando y el diálogo que ya usa esa página. No se añade una librería.

**Storage**: La base propia es SQLite en el entorno de back y SQL Server en producción. El estado de revisión es un campo nuevo en la ficha del proyecto. Las tres parejas se leen de lo ya guardado. El origen comercial no se lee ni se escribe al abrir el aviso ni al cambiar el estado. No se usa PostgreSQL.

**Testing**: pytest y pytest-django, con fichas de ejemplo. Se comprueba el número, las tres parejas, el permiso que oculta una pareja, Revisado y la vuelta a Pdte. Revisar, sin conectar al origen real.

**Target Platform**: Servidor web interno y navegador de escritorio

**Project Type**: Aplicación web Django. La campanita vive en el cuadro de mando. El selector vive en la ficha del proyecto.

**Performance Goals**: Abrir el cuadro no lee el origen. El aviso de un ejercicio de unos doscientos proyectos se arma con las fichas ya guardadas de esa empresa.

**Constraints**: Solo entra la empresa elegida y el ejercicio elegido. Una pareja con un importe vacío no cuenta como diferencia. Un grupo no concedido no se muestra como cero. Los importes siguen el formato ya vigente. Revisado pertenece al proyecto y lo ven todas las personas con acceso. Actualizar no lo pone otra vez en Pdte. Revisar. El aviso no crea, no modifica y no anula documentos.

**Scale/Scope**: Una campanita, una ventana y un selector de dos estados. Tres parejas por proyecto. Un proyecto cuenta una sola vez.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` sigue siendo la plantilla sin ratificar. La constitución vigente es `constitution.md` de la raíz, corregida por `negocio.md` y por la especificación de este aviso.

| Puerta | Resultado |
|--------|-----------|
| El trabajo sigue la especificación del aviso de discrepancias | Pasa |
| Django, Python, HTML y JavaScript. La ventana reutiliza el diálogo del cuadro | Pasa |
| El origen comercial se lee de SQL Server y no se modifica. Esta pantalla no lo lee | Pasa |
| La base propia no vuelve a PostgreSQL: SQLite en back y SQL Server en producción | Pasa |
| Toda lectura queda limitada a la empresa elegida | Pasa |
| La regla del aviso se escribe en `negocio.md` al implementarla | Pasa |
| Los importes se muestran con punto de miles, coma decimal y dos decimales, alineados a la izquierda | Pasa |
| Un grupo de información no concedido no se sustituye por cero | Pasa |

El aviso no cambia el cálculo de la ficha ni el del cuadro. Solo compara lo ya guardado y recuerda si se dio por bueno.

### Revisión posterior al diseño

Las puertas siguen en pie. Hay un campo nuevo en la ficha, no una tabla nueva ni una aplicación nueva. El campo cabe en SQLite y en SQL Server. Abrir el cuadro y guardar el estado no leen el origen. Actualizar sigue rehaciendo la ficha, pero copia el estado antes de borrarla y lo deja en la ficha nueva. No hay una librería nueva.

## Project Structure

### Documentation (this feature)

```text
specs/006-aviso-discrepancias/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── aviso.md
│   └── ui.md
└── tasks.md
```

`tasks.md` no forma parte de este plan.

### Source Code (repository root)

```text
manage.py
config/
apps/
├── access/                 # los grupos ya deciden qué pareja se ve
├── erp/                    # no se llama al abrir el aviso ni al guardar el estado
└── margins/
    ├── models.py           # el estado en la ficha del proyecto
    ├── project_life.py     # guardar el estado al rehacer la ficha
    ├── discrepancies.py    # las tres parejas y la lista del aviso
    ├── views.py            # la campanita y el selector
    └── urls.py             # la ficha ya existe; el estado se guarda en ella
templates/
└── margins/
    ├── dashboard.html      # la campanita y la ventana
    └── project.html        # el selector
negocio.md                  # la regla del aviso, al implementar
tests/
├── unit/
└── integration/
```

**Structure Decision**: La comparación y el estado viven en `apps.margins`, porque la ficha ya vive ahí. No se crea otra aplicación. La campanita solo se pinta en el cuadro de mando.

## Complexity Tracking

No aplica. El campo nuevo no abre una puerta de la constitución: sin él, Actualizar perdería el Revisado al borrar y crear otra vez la ficha.
