# Tasks: Cierre por ejercicio y mes

**Input**: Design documents from `/specs/004-cierre-ejercicio-mes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación del ejemplo queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2, US3)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `apps/margins/models.py`, `apps/margins/admin.py`, `apps/margins/snapshot.py`, `apps/margins/project_life.py`, `apps/margins/views.py`, `templates/includes/filters.html`, `negocio.md`, `tests/unit/test_period_close.py`, `tests/integration/test_closed_month.py`. No se crea otra aplicación ni se añade una librería.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar que el cierre entra en el proyecto ya existente.

- [X] T001 Dejar `requirements.txt` y `config/settings.py` como están para esta funcionalidad: sin PostgreSQL, sin librería nueva, con SQLite en back, SQL Server en producción y la lectura del origen por `pyodbc`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Guardar el cierre de un mes. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Crear en `apps/margins/models.py` el cierre de mes. Reglas literales: «Si no existe fila, el mes está abierto.», «Mes natural, del 1 al 12», «Un valor fuera de ese rango no se guarda», «Cerrado. Sí o no. Al reabrir queda en no y la fila se conserva», «Cambiado por. Obligatoria al guardar desde la administración» y «Una sola fila por empresa, ejercicio y mes.»
- [X] T003 Crear la migración `apps/margins/migrations/0006_period_close.py` para la tabla de T002, con la unicidad de empresa, ejercicio y mes

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Cerrar y reabrir un mes (Priority: P1) 🎯 MVP

**Goal**: Una persona administradora cierra o reabre un mes de una empresa y un ejercicio, y ve quién lo cambió y cuándo.

**Independent Test**: Cierra marzo de 2026 de una empresa, comprueba que queda cerrado con persona y hora, lo reabre sin crear otra fila, y comprueba que marzo de otra empresa sigue abierto. Una persona que no administra no entra.

### Implementation for User Story 1

- [X] T004 [US1] Registrar el cierre en `apps/margins/admin.py`, visible solo para quien administra. La lista se filtra por empresa y por ejercicio y muestra el mes por su nombre, de enero a diciembre, si está cerrado, quién lo cambió y cuándo. Guardar escribe la persona y el momento. No lee el origen ni recalcula

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Actualizar solo los meses abiertos (Priority: P1)

**Goal**: Actualizar no sustituye la ficha de un proyecto retenido y el resumen repone la aportación que ese proyecto tenía cuando estaba abierto.

**Independent Test**: Con fichas ya guardadas, marzo cerrado y febrero abierto, al actualizar el proyecto de marzo conserva importes y fecha, y el de febrero queda con la fecha nueva. Un proyecto con pedidos en los dos meses no cambia.

### Implementation for User Story 2

- [X] T005 [P] [US2] Crear en `apps/margins/models.py` la aportación del proyecto al ejercicio. Reglas literales: «Una sola fila por empresa, proyecto y ejercicio.», «Se sustituye solo cuando el proyecto se actualiza.», «Si el proyecto está retenido, la fila no se toca.» y «Si nunca se escribió, no se inventa con la lectura del mes cerrado.»
- [X] T006 [US2] Crear la migración `apps/margins/migrations/0007_project_exercise_share.py` para la tabla de T005, con la unicidad de empresa, proyecto y ejercicio
- [X] T007 [P] [US2] Apartar en `apps/margins/project_life.py` los proyectos retenidos y no borrarlos ni reescribirlos dentro de `refresh_project_lives`. Reglas literales: «Si el proyecto tiene al menos uno de esos pedidos en un mes cerrado, queda retenido entero.», «Un pedido anulado no coloca al proyecto en ese mes.» y «Si no tiene fecha de pedido, no queda retenido por este control.»
- [X] T008 [US2] En `apps/margins/snapshot.py`, calcular el resumen sin los documentos de los proyectos retenidos, guardar la aportación de cada proyecto abierto y sumar las aportaciones ya guardadas de los retenidos, copiando también sus márgenes de pedido. Regla literal: «Proyecto retenido sin aportación guardada: el resumen nuevo no lo incluye.»

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Saber qué quedó fuera (Priority: P2)

**Goal**: Al terminar Actualizar, la persona ve los meses cerrados que no se han tocado.

**Independent Test**: Con marzo cerrado, al terminar se nombra marzo. Con todos los meses abiertos no hay aviso. Con los doce cerrados se dice que no había ningún mes abierto.

### Implementation for User Story 3

- [X] T009 [US3] Hacer que `refresh_snapshot` en `apps/margins/snapshot.py` devuelva los meses cerrados de esa empresa y ese ejercicio, del 1 al 12 y sin repetir
- [X] T010 [US3] En `apps/margins/views.py`, llevar esos meses al resultado de la actualización con progreso y a la actualización que solo redirige. Si están los doce, el texto dice que no había ningún mes abierto y que no se ha actualizado ningún proyecto
- [X] T011 [US3] Mostrar ese aviso en `templates/includes/filters.html` al terminar el progreso, y no mostrarlo cuando no hay meses cerrados

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Dejar la regla escrita y comprobar el ejemplo sin tocar los totales de ejemplo ya fijados.

- [X] T012 [P] Anotar en `negocio.md` que un mes cerrado no se actualiza, que el mes del proyecto es el de su pedido de venta y que un proyecto con algún pedido en un mes cerrado queda entero fuera de esa actualización
- [X] T013 [P] Fijar en `tests/unit/test_period_close.py` la retención del proyecto de marzo, la conservación de su fecha, la actualización del mes abierto y que un proyecto con pedidos en un mes cerrado y en uno abierto no cambia. Construir esos pedidos en la prueba, sin cambiar los totales de ejemplo de 2024, 2025 ni 2026
- [X] T014 Comprobar `specs/004-cierre-ejercicio-mes/quickstart.md` y fijar en `tests/integration/test_closed_month.py` el recorrido: la persona que no administra no cierra, marzo cerrado se nombra al actualizar, y con los doce meses cerrados no cambia ninguna ficha

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Usa el cierre de la fase 2 y debe poder comprobarse creando la marca sin pasar por la pantalla
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Lee los meses cerrados. El aviso completo se comprueba cuando Actualizar ya respeta el cierre

### Within Each User Story

- Models before services
- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- `apps/margins/models.py` lo tocan T002 y T005: T005 espera a que T002 haya dejado el cierre
- `apps/margins/snapshot.py` lo tocan T008 y T009: esas dos tareas no se hacen a la vez
- `apps/margins/project_life.py` solo lo toca T007

---

## Parallel Example: User Story 1

```text
Task: "T004 [US1] Registrar el cierre en apps/margins/admin.py"
```

US1 tiene una sola tarea de pantalla. Puede avanzar en cuanto existan T002 y T003.

## Parallel Example: User Story 2

```text
Task: "T005 [US2] Crear la aportación del proyecto en apps/margins/models.py"
Task: "T007 [US2] No reescribir la ficha retenida en apps/margins/project_life.py"
```

T005 y T007 pueden avanzar a la vez después de T003 porque usan archivos distintos. T006 espera a T005. T008 espera a T006 y a T007.

## Parallel Example: User Story 3

```text
Task: "T010 [US3] Llevar los meses cerrados al resultado en apps/margins/views.py"
Task: "T011 [US3] Mostrar el aviso en templates/includes/filters.html"
```

T011 espera a T010. T009 espera a T008 porque las dos escriben `apps/margins/snapshot.py`.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

La pantalla ya permite cerrar un mes. El proceso Actualizar todavía no lo obedece: eso es la historia 2. La petición queda cumplida al terminar la historia 2.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
