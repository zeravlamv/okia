# Tasks: Resumen del mes

**Input**: Design documents from `/specs/005-resumen-mes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación del ejemplo queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2, US3)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `apps/margins/month_summary.py`, `apps/margins/views.py`, `apps/margins/urls.py`, `templates/base.html`, `templates/margins/month.html`, `static/css/okia.css`, `negocio.md`, `tests/unit/test_month_summary.py`, `tests/integration/test_month_page.py`. No se crea otra aplicación, ni otra tabla, ni una librería de gráficas.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar que el resumen entra en el proyecto ya existente.

- [X] T001 Dejar `requirements.txt` y `config/settings.py` como están para esta funcionalidad: sin PostgreSQL, sin librería nueva, con SQLite en back, SQL Server en producción y sin lectura del origen al abrir Resumen mes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Saber qué fichas entran en el mes y con qué cinco importes. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Crear `apps/margins/month_summary.py` para agrupar, al leer, las fichas ya guardadas de una empresa, un ejercicio y un mes. Reglas literales: «La lectura filtra por la empresa elegida. Un proyecto con el mismo código en otra empresa no entra.», «Un pedido anulado no está guardado y no coloca la ficha en un mes.», «Una ficha sin fecha de pedido no entra en ningún mes.», «Si la ficha es anterior y solo guarda una fecha de inicio, esa fecha coloca el proyecto en un solo mes.», «La misma ficha no se suma dos veces dentro del mismo mes.», «Si la ficha entra en dos meses del ejercicio, se suma entera en cada uno y la fila nombra los otros meses.», «Un importe vacío no se suma y el mes queda incompleto. No se guarda un cero en su lugar.» y «Consultar el mes no crea, no modifica y no borra fichas, cierres ni documentos.» Cada fila lleva el código del proyecto, el pedido de cliente, los albaranes de cliente, los pedidos de compra, los albaranes de compra y los gastos de la ficha completa, con cualquier fecha de albarán o de gasto. No importa `apps.erp` ni llama a Actualizar

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ver el resumen de los proyectos de un mes (Priority: P1) 🎯 MVP

**Goal**: El menú abre Resumen mes y muestra los proyectos del mes elegido, cada uno con su resumen, y los cinco totales.

**Independent Test**: Con fichas ya calculadas de marzo y de abril, abrir marzo muestra solo los proyectos de marzo y cada total es la suma de esas fichas. Abril no se mezcla. Una fila abre la ficha del proyecto.

### Implementation for User Story 1

- [X] T003 [US1] Publicar la pantalla en `apps/margins/urls.py` y `apps/margins/views.py`, con la empresa y el ejercicio ya elegidos. El mes llega como `mes`, del 1 al 12. Si falta o no es válido, el mes es el de hoy cuando el ejercicio es el año en curso, y enero en cualquier otro ejercicio. Si el mes está cerrado, la pantalla lo dice y muestra las fichas guardadas. No abre el mes y no lee el origen
- [X] T004 [P] [US1] Añadir **Resumen mes** al menú en `templates/base.html`, junto al cuadro de mando y al margen de pedidos
- [X] T005 [US1] Pintar en `templates/margins/month.html` el mes, el ejercicio, los totales y una fila por proyecto con su código y los cinco importes. La fila abre la ficha ya existente de ese proyecto. Si el proyecto entra en otros meses del ejercicio, la fila los nombra. Un mes sin fichas dice que no hay proyectos calculados y remite a Actualizar, sin totales a cero. Un grupo no concedido quita su columna y su total, y no deja un cero. Los importes usan punto de miles, coma decimal, dos decimales, la moneda de la empresa y quedan alineados a la izquierda

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Leer los indicadores del mes (Priority: P2)

**Goal**: La misma ficha muestra cuántos proyectos agrupa, el margen del conjunto y lo que sigue pendiente de albaranar.

**Independent Test**: Con dos proyectos de marzo, pedidos de cliente 100 y 40, albaranes de cliente 80 y 40, y gastos 10 y 5, se leen 2 proyectos, margen 105 y pendiente de albaranar de venta 20.

### Implementation for User Story 2

- [X] T006 [US2] Añadir en `apps/margins/month_summary.py` los indicadores del mes. Reglas literales: «El margen del mes es el total de albaranes de cliente menos el total de gastos.», «El porcentaje usa los albaranes de cliente. Si ese total es cero, no hay porcentaje.», «El pendiente de albaranar de venta es la diferencia de los totales del mes cuando el pedido es mayor, y cero cuando los albaranes cubren el pedido.», «El pendiente de compra se calcula en cada proyecto con la regla ya vigente del pedido no cubierto por su albarán, y después se suma.» y «El albarán de compra no se resta en el margen.» Un margen negativo se conserva
- [X] T007 [US2] Mostrar en `templates/margins/month.html` el número de proyectos, el margen, el porcentaje cuando existe y los dos pendientes. El margen y su porcentaje solo aparecen si se ven los albaranes de cliente y los gastos. El pendiente de venta solo si se ven el pedido y los albaranes de cliente. El pendiente de compra solo si se ven los pedidos y los albaranes de compra

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Ver el mes en gráficas (Priority: P3)

**Goal**: Tres gráficas repiten los indicadores visibles: totales, composición del pedido y una fila por proyecto.

**Independent Test**: Con el mes de la historia 2, la composición tiene el pedido del mes en el centro y el margen igual al indicador. La gráfica por proyecto tiene exactamente esas dos filas. Un total oculto por el perfil no se dibuja ni como cero.

### Implementation for User Story 3

- [X] T008 [US3] Dibujar en `templates/margins/month.html`, con los datos de `apps/margins/month_summary.py`, las tres gráficas: una barra por cada total visible; la composición con el pedido de cliente en el centro y, como partes, albaranes de cliente, gastos y margen positivo; y una fila por proyecto con su albaranado de cliente y su gasto. El margen negativo se lee junto a la composición y no es una parte. Si una gráfica se queda sin cifras visibles, no se dibuja. No se muestran líneas ni documentos
- [X] T009 [P] [US3] Reutilizar en `static/css/okia.css` el dibujo de barras y de composición que ya tiene la ficha, añadir solo las reglas que el resumen necesite y subir la versión de la hoja en `templates/base.html`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Dejar la regla escrita y comprobar el ejemplo sin leer el origen real.

- [X] T010 [P] Anotar en `negocio.md` que Resumen mes agrupa las fichas cuyo pedido de venta cae en el mes, que cada fila es la ficha entera, que el margen es albaranes de cliente menos gastos y que el albarán de compra no se vuelve a restar
- [X] T011 [P] Fijar en `tests/unit/test_month_summary.py` el mes de marzo frente a abril, la ficha entera en dos meses con el aviso, el margen 105, el pendiente de venta 20, el pendiente de compra por pedido y que un importe vacío deja el mes incompleto sin convertirse en cero
- [X] T012 Comprobar `specs/005-resumen-mes/quickstart.md` y fijar en `tests/integration/test_month_page.py` el recorrido: el menú muestra Resumen mes, marzo no mezcla abril, un perfil sin gastos no ve el gasto ni el margen, un mes sin fichas no muestra totales a cero y un mes cerrado se consulta sin abrirse

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Añade indicadores a la lectura de T002 y a la pantalla de T005. Se puede comprobar el cálculo sin las gráficas
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Dibuja las cifras que ya devuelven T002 y T006. No crea importes nuevos

### Within Each User Story

- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- `apps/margins/month_summary.py` lo tocan T002, T006 y T008: van en ese orden, no a la vez
- `templates/margins/month.html` lo tocan T005, T007 y T008: van en ese orden, no a la vez
- `templates/base.html` lo tocan T004 y T009: T009 espera a que el enlace del menú ya esté

---

## Parallel Example: User Story 1

```text
Task: "T003 [US1] Publicar la pantalla en apps/margins/urls.py y apps/margins/views.py"
Task: "T004 [P] [US1] Añadir Resumen mes al menú en templates/base.html"
```

T003 y T004 pueden avanzar a la vez después de T002 porque usan archivos distintos. T005 espera a T003.

## Parallel Example: User Story 2

```text
Task: "T006 [US2] Añadir los indicadores en apps/margins/month_summary.py"
```

T006 espera a T002. T007 espera a T005 y a T006 porque escribe la misma plantilla y lee los indicadores nuevos.

## Parallel Example: User Story 3

```text
Task: "T008 [US3] Dibujar las tres gráficas en templates/margins/month.html"
Task: "T009 [P] [US3] Ajustar el dibujo en static/css/okia.css"
```

T009 puede avanzar a la vez que T008. T008 espera a T006 y a T007.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

Al terminar la historia 1 ya se puede leer el mes agrupado. Los indicadores son la historia 2 y las gráficas la historia 3.

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

Quien reparta el trabajo respeta el orden de `month_summary.py` y de `templates/margins/month.html`.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
