# Tasks: Jerarquía analítica

**Input**: Design documents from `/specs/002-jerarquia-analitica/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación del ejemplo queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2, US3)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `apps/margins/`, `apps/erp/`, `apps/access/`, `templates/margins/dashboard.html`, `static/js/breakdown.js`, `tests/integration/test_dashboard.py`, `negocio.md`. No se crea una aplicación nueva.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar que la jerarquía entra en el proyecto ya existente.

- [X] T001 Dejar `requirements.txt` y `config/settings.py` como están para esta funcionalidad: sin PostgreSQL, con SQLite en back y con la lectura del origen por `pyodbc`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Partir el coste ya calculado en compras y gastos. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Separar en `apps/margins/services.py` las compras y los gastos de un proyecto, con estas reglas literales: «Las compras de un pedido cerrado son la suma de las bases de todas sus líneas de compra, con cualquier fecha.», «Los gastos son los apuntes de horas, mano de obra o personal de ese proyecto.», «Su suma es el coste que ya usa el margen del pedido.» y «Una pieza sin importe no se suma y el resultado queda incompleto.»
- [X] T003 [P] Clasificar cada pedido no anulado del ejercicio en `apps/margins/hierarchy.py`: el de proyecto único cierra margen; el que no tiene proyecto o lo comparte va al grupo aparte con su precio de venta y sin compras, gastos, ingresos ni margen; el anulado no entra. Regla literal: «Sus ventas no se suman a ningún grupo analítico.»

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Consultar la información acumulada por niveles (Priority: P1) 🎯 MVP

**Goal**: Mostrar un árbol cuyo primer nivel engloba a los siguientes, con ventas, ingresos, compras, gastos y margen, y un grupo aparte fuera del árbol.

**Independent Test**: Con la empresa 1 y el ejercicio 2026 de ejemplo, el canal «Tienda» suma solo el pedido 1001, «Sin dato» suma el 1003 y el 1004, y los pedidos 2001 y 2002 aparecen fuera del árbol con 100,00 y 80,00 y sin margen.

### Implementation for User Story 1

- [X] T004 [US1] Anidar en `apps/margins/hierarchy.py` los pedidos que cierran margen según el orden guardado. Cada cifra del padre es la suma de esa cifra en los hijos. El texto visible es «código — descripción», solo el código si no hay descripción, o «Sin dato» si no hay código. Dos códigos distintos no se fusionan. Un importe ausente marca incompleto el grupo y todos los que lo engloban.
- [X] T005 [US1] Sustituir las cinco listas de `apps/margins/dashboard.py` y `apps/margins/views.py` por el árbol y el grupo aparte, y mantener los indicadores generales del panel, incluido el de compras fechadas en el ejercicio
- [X] T006 [P] [US1] Mostrar solo el primer nivel y, al abrir un grupo, solo el nivel siguiente, sin otra consulta y sin cambiar importes, en `templates/margins/dashboard.html` y `static/js/breakdown.js`. Varios grupos pueden quedar abiertos a la vez. El grupo aparte se dibuja fuera del árbol.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Cambiar el orden cambia la agrupación (Priority: P2)

**Goal**: La posición guardada de cada nivel decide quién engloba a quién. Las cinco cifras del conjunto de pedidos cerrados no cambian.

**Independent Test**: Con los mismos pedidos de ejemplo, poner la sección en la posición 1 y el canal en la posición 5. El primer nivel pasa a ser la sección y las ventas 1.010,00, las compras 340,00, los gastos 50,00, el margen 620,00 y los ingresos 800,00 siguen iguales.

### Implementation for User Story 2

- [X] T007 [US2] Reconstruir en `apps/margins/hierarchy.py` los padres y los hijos a partir de la posición de `apps/access/models.py`, de modo que invertir el orden cambie la anidación y no la suma de cada cifra en el conjunto de pedidos cerrados

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Respetar lo que el perfil puede ver (Priority: P3)

**Goal**: Un nivel no concedido no ocupa escalón. Una cifra no concedida no aparece como cero.

**Independent Test**: Con un perfil que ve canal y proyecto, pero no delegación, departamento ni sección, el canal engloba directamente los proyectos. Con un perfil que no ve los gastos, esa cifra no aparece. Sin ningún nivel concedido, no aparece la jerarquía.

### Implementation for User Story 3

- [X] T008 [US3] Omitir en `apps/margins/hierarchy.py` el nivel cuyo grupo de información no esté concedido, de forma que el nivel visible anterior englobe directamente el siguiente visible. Si no queda ningún nivel, no hay árbol.
- [X] T009 [US3] No enviar en `apps/margins/views.py` ni dibujar en `templates/margins/dashboard.html` una cifra no concedida, ni un cero en su lugar. Sin permiso de pedidos de venta, el grupo aparte no muestra el precio.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Dejar la regla escrita y comprobar el ejemplo.

- [X] T010 [P] Anotar en `negocio.md` que la jerarquía parte el coste en compras y gastos, que el margen es ventas menos compras menos gastos, y que las ventas del grupo aparte no entran en el árbol
- [X] T011 Comprobar `specs/002-jerarquia-analitica/quickstart.md` y fijar en `tests/integration/test_dashboard.py` el ejemplo de la empresa 1 y el ejercicio 2026: árbol con ventas 1010, compras 340, gastos 50, margen 620 e ingresos 800; grupo aparte con 100 y 80; indicador general de ventas en 1190

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Cambia la anidación de US1 en `apps/margins/hierarchy.py` y debe poder comprobarse sola
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Recorta el mismo árbol y debe poder comprobarse sola

### Within Each User Story

- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- `apps/margins/hierarchy.py` lo tocan T004, T007 y T008: esas tres tareas no se hacen a la vez
- `templates/margins/dashboard.html` lo tocan T006 y T009: esas dos tareas no se hacen a la vez

---

## Parallel Example: User Story 1

```text
Task: "T005 [US1] Sustituir las cinco listas en apps/margins/dashboard.py y apps/margins/views.py"
Task: "T006 [US1] Mostrar solo el primer nivel en templates/margins/dashboard.html y static/js/breakdown.js"
```

T005 y T006 pueden avanzar a la vez después de T004 porque usan archivos distintos. T002 y T003 también pueden avanzar a la vez.

## Parallel Example: User Story 2

```text
Task: "T007 [US2] Reconstruir padres e hijos en apps/margins/hierarchy.py"
```

US2 no tiene una segunda tarea en otro archivo. No se paraleliza con T004 ni con T008.

## Parallel Example: User Story 3

```text
Task: "T008 [US3] Omitir el nivel no concedido en apps/margins/hierarchy.py"
Task: "T009 [US3] No dibujar la cifra no concedida en apps/margins/views.py y templates/margins/dashboard.html"
```

T008 y T009 pueden avanzar a la vez si T004 ya terminó y T009 no coincide con T006.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

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
