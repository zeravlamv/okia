# Tasks: Análisis profundo

**Input**: Design documents from `/specs/003-analisis-profundo/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación del ejemplo queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2, US3)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `apps/margins/`, `apps/erp/`, `templates/margins/project.html`, `static/js/breakdown.js`, `tests/unit/test_project_progression.py`, `tests/integration/test_project_life.py`, `negocio.md`. No se crea una aplicación nueva ni se añade una librería de gráficas.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar que la ficha entra en el proyecto ya existente.

- [X] T001 Dejar `requirements.txt` y `config/settings.py` como están para esta funcionalidad: sin PostgreSQL, sin librería de gráficas, con SQLite en back y con la lectura del origen por `pyodbc`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Guardar la vida completa del proyecto al pulsar Actualizar. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Crear en `apps/margins/models.py` la vida del proyecto, el hito de albarán, la compra y el gasto. Reglas literales: «Una fila por empresa y código de proyecto.», «No hay dos vidas para la misma empresa y el mismo proyecto.», inicio «Fecha más antigua de sus pedidos de venta no anulados.», base «Suma de las bases de esos pedidos.», incompleta «Verdadero si falta alguna base que debía entrar.», facturación «Facturado, no facturado o sin dato.», importe del hito «Negativa si es un abono. Vacía si falta», clase de compra «Albarán de compra, o pedido de compra comprometido.» y «Un importe vacío no se convierte en cero.»
- [X] T003 Crear la migración `apps/margins/migrations/0002_project_life.py` para las tablas de T002, con la unicidad de empresa y proyecto y el borrado en cascada de hitos, compras y gastos
- [X] T004 [P] Leer en `apps/erp/documents.py` y `apps/erp/ledger.py` los documentos del proyecto con cualquier fecha: albarán de venta con marca de facturación y de abono, albarán de compra con proveedor y enlace al pedido, pedido de compra, y apuntes de gasto con código y descripción `Cuenta`. Regla literal: «La clave del albarán de compra es ejercicio, serie y número de albarán.»
- [X] T005 [P] Añadir en `apps/erp/sample.py` el proyecto de ejemplo de quickstart.md: pedido de 1.000 en marzo de 2024, albarán facturado de 400 en 2025, albarán no facturado de 100 en 2026, un albarán de compra, un pedido de compra sin albarán, un gasto con descripción y un apunte de cierre de ejercicio
- [X] T006 Sustituir en `apps/margins/project_life.py`, llamado desde `refresh_snapshot` de `apps/margins/snapshot.py`, la vida de los proyectos del ejercicio actualizado. Regla literal: «Sustituir una vida borra sus hitos, compras y gastos anteriores y escribe los nuevos juntos.» Una lectura por familia y los apuntes por bloques de proyectos

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ver la progresión del proyecto (Priority: P1) 🎯 MVP

**Goal**: Abrir un proyecto y ver su inicio, el albaranado, la progresión, lo facturado, lo no facturado y el pendiente, aunque los albaranes caigan en otros ejercicios.

**Independent Test**: Con el pedido de 1.000 de marzo de 2024 y los albaranes de 400 y 100, la ficha muestra los tres ejercicios, el albaranado 500,00 EUR, la progresión 50,00 %, el facturado 400,00 EUR, el no facturado 100,00 EUR y el pendiente 500,00 EUR.

### Implementation for User Story 1

- [X] T007 [US1] Calcular al abrir en `apps/margins/project_life.py` el albaranado, la progresión, las tres partes de facturación y el pendiente, sin guardarlos. Reglas literales: «Albaranado = suma de los importes de los hitos, incluidos abonos y sin dato de facturación.», «Progresión = albaranado partido por la base del pedido. Si la base es cero o falta, el porcentaje es «No aplicable». Puede pasar de 100.», «La suma de esas tres partes es el albaranado.» y «Pendiente de albaranar = base del pedido menos albaranado cuando el pedido es mayor. Si el albaranado es igual o mayor, el pendiente es cero.»
- [X] T008 [US1] Servir la ficha en `apps/margins/views.py` y `apps/margins/urls.py` con la ruta del proyecto de la empresa elegida. Si no hay vida guardada, indicar que hay que pulsar Actualizar y no mostrar cifras. Un proyecto de otra empresa no se abre
- [X] T009 [US1] Mostrar en `templates/margins/project.html` los indicadores y la tabla de hitos, de la fecha más antigua a la más reciente, con el formato de `apps/margins/format.py`: punto de miles, coma decimal, dos decimales y alineación a la izquierda
- [X] T010 [P] [US1] Enlazar cada proyecto visible de la jerarquía con su ficha desde `static/js/breakdown.js`, sin sustituir el cuadro de mando ni el árbol

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Ver el calendario y la Gantt (Priority: P2)

**Goal**: Dibujar la barra del proyecto, los hitos y las gráficas mensuales de progresión, compras y gastos.

**Independent Test**: Con un pedido de enero, un albarán facturado en marzo, otro sin facturar en junio, y una compra y un gasto en marzo, la barra sigue hasta el día de la visita, los dos hitos se distinguen y marzo reúne albarán, compra y gasto.

### Implementation for User Story 2

- [X] T011 [US2] Generar al abrir en `apps/margins/project_life.py` los meses y el final de la barra. Reglas literales: «Los meses vacíos. Se generan al abrir, desde el mes del inicio hasta el mes en que termina la barra.», «El día «hoy». Se toma al abrir la ficha.», «Si el albaranado cubre o supera la base del pedido y hay algún hito con fecha, la barra termina en la fecha del último hito.», «Si el pedido sigue descubierto, no hay hitos, o la base falta, la barra termina el día en que se abre la ficha.» y «Si la fecha de inicio es posterior a ese día y el pedido sigue descubierto, la barra es solo la fecha de inicio.»
- [X] T012 [US2] Dibujar en `templates/margins/project.html` la Gantt y las gráficas de progresión acumulada y de compras y gastos de cada mes, sin librería nueva. Los documentos sin fecha se listan como «Sin fecha» y no se colocan en la barra

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Detallar compras y gastos (Priority: P3)

**Goal**: Ver las compras por proveedor y los gastos por cuenta, con la descripción del plan contable, y apartar el comprometido y el cierre.

**Independent Test**: Dos proveedores suman la cifra de compras. Dos cuentas suman la cifra de gastos y muestran código y descripción. El pedido de compra sin albarán no aumenta las compras. El cierre de ejercicio no aparece.

### Implementation for User Story 3

- [X] T013 [US3] Agrupar en `apps/margins/project_life.py` las compras por proveedor y los gastos por cuenta. Reglas literales: «Compras = suma de las bases de los albaranes de compra del proyecto.», «Un pedido de compra es comprometido solo cuando ningún albarán de compra guardado apunta a su ejercicio, serie y número.», «El comprometido no se suma a las compras ni a la barra mensual de compras.» y «La cuenta de ingreso no entra. El cierre de ejercicio no entra.»
- [X] T014 [US3] Añadir en `templates/margins/project.html` las tablas y las gráficas de proveedores y de cuentas, ordenadas de mayor a menor. El texto con código y descripción es `código — descripción`. Sin descripción, o si es igual al código, queda el código. El comprometido se rotula «Comprometido»
- [X] T015 [US3] Ocultar en `apps/margins/views.py` la parte no concedida, sin sustituirla por cero, en indicadores, Gantt, gráficas y tablas. Sin permiso de proveedores se muestra el código y no el nombre

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Dejar la regla escrita y comprobar el ejemplo.

- [X] T016 [P] Anotar en `negocio.md` que la ficha del proyecto empieza en la fecha del pedido, sigue por los meses de su vida, mide el albaranado sobre el pedido, separa lo facturado y no suma el comprometido ni el cierre de ejercicio
- [X] T017 [P] Fijar en `tests/unit/test_project_progression.py` la progresión 50,00 %, el paso por encima de 100, el porcentaje «No aplicable» con base cero, el abono en negativo y la exclusión del cierre
- [X] T018 Comprobar `specs/003-analisis-profundo/quickstart.md` y fijar en `tests/integration/test_project_life.py` el recorrido de la empresa 1: sin cifras antes de Actualizar, y después la ficha con 500,00 EUR, 50,00 %, 400,00 EUR, 100,00 EUR y el comprometido fuera de las compras

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Dibuja sobre la ficha de US1 y debe poder comprobarse sola
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Añade el detalle a la misma ficha y debe poder comprobarse sola

### Within Each User Story

- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- `apps/margins/project_life.py` lo tocan T006, T007, T011 y T013: esas cuatro tareas no se hacen a la vez
- `templates/margins/project.html` lo tocan T009, T012 y T014: esas tres tareas no se hacen a la vez
- `apps/margins/views.py` lo tocan T008 y T015: esas dos tareas no se hacen a la vez

---

## Parallel Example: User Story 1

```text
Task: "T009 [US1] Mostrar indicadores e hitos en templates/margins/project.html"
Task: "T010 [US1] Enlazar el proyecto de la jerarquía en static/js/breakdown.js"
```

T009 y T010 pueden avanzar a la vez después de T008 porque usan archivos distintos. T004 y T005 también pueden avanzar a la vez.

## Parallel Example: User Story 2

```text
Task: "T011 [US2] Generar los meses y el final de la barra en apps/margins/project_life.py"
Task: "T012 [US2] Dibujar la Gantt y las gráficas mensuales en templates/margins/project.html"
```

T012 espera a T011. US2 no se paraleliza con T007 ni con T013, ni T012 con T009.

## Parallel Example: User Story 3

```text
Task: "T013 [US3] Agrupar compras y gastos en apps/margins/project_life.py"
Task: "T014 [US3] Añadir tablas y gráficas en templates/margins/project.html"
Task: "T015 [US3] Ocultar lo no concedido en apps/margins/views.py"
```

T014 espera a T013. T015 puede avanzar con T014 si T008 ya terminó. T013 no se hace a la vez que T011.

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
