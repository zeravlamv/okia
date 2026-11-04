# Tasks: Aviso de discrepancias

**Input**: Design documents from `/specs/006-aviso-discrepancias/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación del ejemplo queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `apps/margins/models.py`, `apps/margins/migrations/`, `apps/margins/project_life.py`, `apps/margins/month_refresh.py`, `apps/margins/discrepancies.py`, `apps/margins/views.py`, `templates/margins/dashboard.html`, `templates/margins/project.html`, `negocio.md`, `tests/unit/test_discrepancies.py`, `tests/integration/test_discrepancy_notice.py`. No se crea otra aplicación, ni otra tabla, ni una librería nueva. El origen comercial no se lee al abrir el aviso ni al guardar el estado.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar que el aviso entra en el proyecto ya existente.

- [X] T001 Dejar `requirements.txt` y `config/settings.py` como están para esta funcionalidad: sin PostgreSQL, sin librería nueva, con SQLite en back, SQL Server en producción y sin lectura del origen al abrir el cuadro o al guardar el estado

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Guardar el estado en la ficha y saber qué proyectos del ejercicio no cuadran. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Añadir el estado de revisión a la ficha en `apps/margins/models.py` y una migración en `apps/margins/migrations/`. Reglas literales: «Cada ficha guarda un estado» con los dos valores exactos `Pdte. Revisar` y `Revisado`, «Si la ficha es anterior a este campo, el estado es Pdte. Revisar.» y «El estado es uno por empresa y proyecto, el mismo para todas las personas. No depende del ejercicio.» El valor inicial es `Pdte. Revisar`. El campo cabe en SQLite y en SQL Server
- [X] T003 [P] Conservar el estado al rehacer la ficha en `apps/margins/project_life.py` y no tocarlo en `apps/margins/month_refresh.py` cuando el recálculo no borra la ficha. Reglas literales: «Actualizar borra las fichas del ejercicio que vuelve a calcular y crea otras. El estado se copia a la ficha nueva del mismo proyecto. Si el proyecto deja de tener ficha, el estado desaparece con ella. Cuando vuelva a calcularse, empieza en Pdte. Revisar.» y «Cambiar los importes no lo cambia. Solo lo cambia la persona desde la ficha.»
- [X] T004 [P] Crear `apps/margins/discrepancies.py` para listar, al leer, los proyectos pendientes de una empresa, un ejercicio y unos grupos. Reglas literales: «Entra cada ficha con un pedido de venta guardado cuya fecha cae en el ejercicio.», «Si la ficha no tiene los pedidos desglosados y solo tiene fecha de inicio, entra cuando el año de esa fecha coincide con el ejercicio.», «Una ficha sin fecha de pedido no entra en ningún ejercicio.», «Si no hay filas en un lado, ese lado es cero.», «Si la base del pedido está vacía, o alguna fila sumada tiene el importe vacío, esa pareja se omite.», «Dos importes iguales al céntimo cuadran, también cero con cero. Cualquier otra diferencia, al alza o a la baja, es discrepancia.», «El proyecto cuenta una vez aunque fallen varias parejas.» y «Consultar el aviso no crea, no modifica y no borra fichas ni documentos.» Las tres parejas son la base del pedido de venta frente a la suma de albaranes de venta, la suma de pedidos de compra cubiertos o comprometidos frente a la suma de albaranes de compra, y esa suma de albaranes de venta frente a la suma de ingresos. No importa `apps.erp`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ver cuántos proyectos no cuadran (Priority: P1) 🎯 MVP

**Goal**: El cuadro de mando muestra la campanita con el número de proyectos pendientes y, al pulsarla, la ventana con cada proyecto, sus parejas y el acceso a la ficha.

**Independent Test**: Con tres fichas del ejercicio, una con pedido 100 y albaranado 40, otra que cuadra y otra en Revisado que no cuadra, la campanita muestra 1. La ventana lista solo la primera y desde ahí se abre su ficha.

### Implementation for User Story 1

- [X] T005 [US1] Pasar el aviso a la pantalla en `apps/margins/views.py`, con la empresa, el ejercicio y los grupos ya elegidos. La campanita se calcula también cuando el cuadro todavía no tiene resumen. Reglas literales de `specs/006-aviso-discrepancias/contracts/aviso.md`: la pareja de venta solo si se ven pedidos de venta y albaranes de venta; la de compra solo si se ven pedidos de compra y albaranes de compra; la de ingresos solo si se ven albaranes de venta y movimientos contables. «Una pareja de un grupo no concedido no se calcula para esa persona y no aparece como cero.» La lista va ordenada por el código del proyecto, sin repetirlo, y cada elemento trae el código, el cliente si la ficha lo tiene y las parejas que no cuadran con sus dos importes. No lee el origen
- [X] T006 [P] [US1] Pintar en `templates/margins/dashboard.html` la campanita junto al título, con el número, visible también cuando es cero y cuando no hay resumen. Pulsarla abre una ventana en la misma página. Si el número es cero, la ventana dice que no hay proyectos pendientes de revisar. Si hay proyectos, una fila por proyecto con el código, el cliente cuando existe y cada pareja con sus dos importes. La fila abre la ficha ya existente. Cerrar la ventana no cambia el estado. Los importes usan punto de miles, coma decimal, dos decimales, la moneda de la empresa y quedan alineados a la izquierda. Reutilizar el diálogo que ya tiene el cuadro; no añadir una librería

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Dar por buena una discrepancia (Priority: P2)

**Goal**: La ficha deja elegir Revisado o Pdte. Revisar. Revisado saca el proyecto de la campanita hasta que la persona lo cambie.

**Independent Test**: Un proyecto con pedido 100 y albaranado 40 deja de contarse al marcarlo Revisado y vuelve a contarse al ponerlo en Pdte. Revisar. Los importes de la ficha no cambian.

### Implementation for User Story 2

- [X] T007 [US2] Guardar el estado en la ficha ya publicada por `apps/margins/views.py`, solo para un proyecto de la empresa elegida que ya tiene ficha. Acepta únicamente `Pdte. Revisar` o `Revisado`. Cualquier otro valor no se guarda. Reglas literales: «Guardar no cambia importes, no lee el origen y no marca otros proyectos.» y «Revisado saca el proyecto de la lista aunque alguna pareja siga distinta.» Si la ficha no existe, no hay nada que guardar
- [X] T008 [P] [US2] Mostrar en `templates/margins/project.html` el selector con `Pdte. Revisar` y `Revisado`, indicando cuál está activo, solo cuando la ficha existe. Confirmarlo guarda el estado y la ficha sigue mostrando los mismos importes. El selector se puede usar aunque las parejas cuadren

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Dejar la regla escrita y comprobar el ejemplo sin leer el origen real.

- [X] T009 [P] Anotar en `negocio.md` que el aviso compara, en la ficha del ejercicio, el pedido de venta con lo albaranado, el pedido de compra con lo albaranado y lo albaranado de venta con los ingresos, y que Revisado saca el proyecto de la campanita hasta que la persona vuelva a elegir Pdte. Revisar
- [X] T010 [P] Fijar en `tests/unit/test_discrepancies.py` el pedido 100 frente al albaranado 40, el cero contra cero que cuadra, el albarán mayor que el pedido, el pedido de compra comprometido sin albarán, el albaranado 50 frente a ingresos 0, la pareja omitida cuando falta un importe, el proyecto en Revisado que no entra y el que vuelve al elegirlo Pdte. Revisar
- [X] T011 [P] Comprobar `specs/006-aviso-discrepancias/quickstart.md` y fijar en `tests/integration/test_discrepancy_notice.py` el recorrido: la campanita muestra 1, la ventana no lista el proyecto que cuadra ni el revisado, la fila abre la ficha, Revisado deja el número en 0 sin cambiar importes, Pdte. Revisar lo devuelve, y un perfil sin movimientos no ve la pareja de ingresos ni un cero en su lugar

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - El selector cambia el mismo estado que la campanita ya filtra. Se puede comprobar el guardado en la ficha sin redibujar la ventana

### Within Each User Story

- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- `apps/margins/views.py` lo tocan T005 y T007: van en ese orden, no a la vez
- `apps/margins/project_life.py` lo toca T003 y `apps/margins/discrepancies.py` lo toca T004: pueden ir a la vez después de T002
- `templates/margins/dashboard.html` lo toca solo T006 y `templates/margins/project.html` lo toca solo T008

---

## Parallel Example: User Story 1

```text
Task: "T005 [US1] Pasar el aviso a la pantalla en apps/margins/views.py"
Task: "T006 [P] [US1] Pintar la campanita y la ventana en templates/margins/dashboard.html"
```

T005 y T006 pueden avanzar a la vez después de T004 porque usan archivos distintos. T006 lee el contrato de `specs/006-aviso-discrepancias/contracts/ui.md`.

## Parallel Example: User Story 2

```text
Task: "T007 [US2] Guardar el estado en apps/margins/views.py"
Task: "T008 [P] [US2] Mostrar el selector en templates/margins/project.html"
```

T008 puede avanzar a la vez que T007. T007 espera a T005 porque escribe el mismo `apps/margins/views.py`.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

Al terminar la historia 1 ya se ve la campanita y la ventana. Dar por buena una discrepancia es la historia 2. Hasta entonces todas las fichas siguen en Pdte. Revisar.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently

Quien reparta el trabajo respeta el orden de `apps/margins/views.py`.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
