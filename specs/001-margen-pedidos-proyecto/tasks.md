# Tasks: Margen de pedidos por proyecto

**Input**: Design documents from `/specs/001-margen-pedidos-proyecto/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: La especificación no pide desarrollo guiado por pruebas. No hay tareas de pruebas previas a la implementación. La comprobación manual queda en la fase final, según quickstart.md.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede hacerse en paralelo (otro archivo, sin depender de una tarea incompleta)
- **[Story]**: Historia a la que pertenece (US1, US2, US3, US4, US5)
- Cada tarea incluye la ruta del archivo

## Path Conventions

Rutas del plan: `manage.py`, `config/`, `apps/accounts/`, `apps/access/`, `apps/erp/`, `apps/margins/`, `templates/`, `static/`, `tests/unit/`, `tests/integration/`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Crear el proyecto Django y fijar las dependencias del plan.

- [X] T001 Crear el esqueleto Django del plan en `manage.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `apps/accounts/`, `apps/access/`, `apps/erp/`, `apps/margins/`, `templates/`, `static/`, `tests/unit/` y `tests/integration/`
- [X] T002 [P] Declarar Django 5.2 LTS, psycopg, mssql-django, pytest y pytest-django en `requirements.txt`
- [X] T003 [P] Configurar pytest-django para la base propia PostgreSQL en `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Conexiones, modelos compartidos y la barrera de empresa y permiso. Ninguna historia empieza antes de terminar esta fase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Configurar en `config/settings.py` la conexión `default` con PostgreSQL en el entorno de back y SQL Server en producción, y la conexión `erp` de solo lectura contra SQL Server
- [X] T005 [P] Dejar el enrutado raíz preparado en `config/urls.py` para incluir `apps/accounts/`, `apps/access/`, `apps/erp/` y `apps/margins/`
- [X] T006 [P] Resolver por nombre de columna los campos lógicos y fallar de forma explícita si falta alguno en `apps/erp/mapping.py`
- [X] T007 [P] Declarar modelos no gestionados del origen, con las claves de `data-model.md`, en `apps/erp/models.py`
- [X] T008 [P] Rechazar escrituras sobre la conexión `erp` en `apps/erp/router.py`
- [X] T009 [P] Crear perfil, empresa autorizada y conexión al origen en `apps/access/models.py`, con estas reglas literales: «Una persona solo elige y consulta empresas de esta lista.», «Quien administra también queda limitado a sus empresas.», «Con una sola empresa, queda seleccionada al entrar.», «Sin empresas, no hay cifras económicas.» y «El secreto no se muestra de nuevo en claro.»
- [X] T010 Crear las migraciones de la base propia en `apps/access/migrations/`
- [X] T011 Exigir empresa asignada y grupo de información antes de calcular, y permitir fijar la empresa en sesión para la comprobación de US1, en `apps/access/services.py`
- [X] T012 [P] Crear la plantilla común con hueco para la identidad de la persona en `templates/base.html`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Consultar el margen de un pedido (Priority: P1) 🎯 MVP

**Goal**: Mostrar, para cada pedido no anulado, el precio sin impuestos, el coste, el margen y, al lado, los ingresos contables del proyecto.

**Independent Test**: Con una empresa ya elegida, un usuario autorizado a ver pedidos, compras y movimientos, y al menos un pedido con compras o ingresos de su proyecto, se abre ese pedido y se comprueban el precio, el coste, el margen y los ingresos sin usar el resto de pantallas.

### Implementation for User Story 1

- [X] T013 [P] [US1] Leer cabecera y líneas de venta desde `CabeceraPedidoCliente` y `LineasPedidoCliente` en `apps/erp/sales.py`, excluyendo el estado que signifique anulado y tomando la base sin impuestos
- [X] T014 [P] [US1] Leer las líneas de compra del proyecto desde `LineasPedidoProveedor` en `apps/erp/purchases.py`, siempre por su importe sin impuestos y con cualquier fecha
- [X] T015 [P] [US1] Separar en `apps/erp/ledger.py` los apuntes de `Movimientos` cuya cuenta indique horas, mano de obra o personal de los ingresos de las cuentas de ingreso
- [X] T016 [US1] Calcular el margen en `apps/margins/services.py` con estas reglas literales: «El precio de venta es la base de la cabecera. Si no existe, es la suma de las bases de las líneas.», «El impuesto no entra en el precio ni en el margen.», «Si la misma hora está en los dos sitios, entran las dos.», «No se suma ni se resta al precio, al coste ni al margen.», «El periodo elige el pedido. No recorta el coste ni los ingresos por la fecha de la imputación.», «Si más de un pedido no anulado de la empresa comparte proyecto, el coste y los ingresos no se asignan a uno ni se duplican.» y «Una pieza sin importe no se suma y el resultado queda incompleto.»
- [X] T017 [US1] Mostrar precio, coste, margen, porcentaje solo si el precio no es cero, e ingresos aparte en `apps/margins/views.py` y `templates/margins/order.html`
- [X] T018 [US1] Publicar la pantalla del margen en `apps/margins/urls.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Entrar y elegir una empresa autorizada (Priority: P2)

**Goal**: Entrar con usuario y contraseña, recordar solo el usuario, recuperar la contraseña por correo y trabajar en una empresa autorizada.

**Independent Test**: Se comprueba con cuentas, empresas asignadas y el correo de recuperación, sin calcular un margen.

### Implementation for User Story 2

- [X] T019 [P] [US2] Guardar solo el identificador, nunca la contraseña, al recordar el usuario en `apps/accounts/remember.py`
- [X] T020 [P] [US2] Mantener la sesión 30 días solo si la persona lo pide, y cerrarla al terminar el navegador o al caducar si no lo pide, en `apps/accounts/sessions.py`
- [X] T021 [US2] Entrar con cuenta activa y rechazar una contraseña incorrecta sin revelar si el identificador existe, aplicando «Una cuenta inactiva no entra.», en `apps/accounts/views.py` y `templates/accounts/login.html`
- [X] T022 [US2] Enviar un enlace de un solo uso durante 60 minutos y aplicar «Sin correo no puede recuperar la contraseña por sí mismo.» sin revelar si la cuenta existe, en `apps/accounts/recovery.py` y `templates/accounts/recovery.html`
- [X] T023 [US2] Elegir empresa en `apps/access/views.py` y `templates/access/company.html`: con varias, no hay cifras hasta elegir; con una, queda seleccionada; sin ninguna, se pide solicitarla a quien administra; al cambiar, desaparecen las cifras anteriores
- [X] T024 [US2] Publicar acceso, recuperación y selector en `apps/accounts/urls.py` y `apps/access/urls.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Revisar lo que no cuadra con un pedido (Priority: P3)

**Goal**: Separar pedidos sin proyecto, imputaciones sin pedido vigente y proyectos compartidos, sin cerrar un margen falso.

**Independent Test**: Con un pedido sin proyecto, una imputación huérfana y un proyecto compartido por dos pedidos vigentes, la lista de pendientes se comprueba sin abrir el panel.

### Implementation for User Story 3

- [ ] T025 [US3] Clasificar los pendientes en `apps/margins/pending.py` con los motivos «sin proyecto», «sin pedido vigente» y «proyecto compartido», sin atribuir un margen cerrado
- [ ] T026 [US3] Listar pedidos e imputaciones afectados en `apps/margins/pending_views.py` y `templates/margins/pending.html`
- [ ] T027 [US3] Publicar la revisión en `apps/margins/urls.py`

**Checkpoint**: User Story 3 can be verified without the dashboard

---

## Phase 6: User Story 4 - Ver el panel de indicadores (Priority: P4)

**Goal**: Resumir la empresa y el periodo con los indicadores acordados, sin recortar el margen de cada pedido.

**Independent Test**: Con un periodo conocido y permiso para ver esos grupos, los totales del panel se contrastan sin abrir la ficha de un pedido.

### Implementation for User Story 4

- [X] T028 [P] [US4] Agregar en `apps/margins/dashboard.py` el número y el importe sin impuestos de los pedidos del periodo, el número y el importe sin impuestos de las compras fechadas en el periodo, la suma de los márgenes con el coste completo de cada proyecto, la suma de los ingresos completos, los recuentos vigentes de clientes, proveedores y artículos, y el precio de venta sin impuestos por canal, delegación, departamento, sección y proyecto
- [X] T029 [P] [US4] Dibujar solo ese reparto, sin indicadores nuevos, en `static/js/breakdown.js`
- [X] T030 [US4] Mostrar el panel y omitir, sin poner cero, cada grupo no permitido en `apps/margins/dashboard_views.py` y `templates/margins/dashboard.html`
- [X] T031 [US4] Publicar el panel en `apps/margins/urls.py`

**Checkpoint**: The dashboard matches the period rules without changing the order margin

---

## Phase 7: User Story 5 - Administrar usuarios, perfiles y empresas (Priority: P5)

**Goal**: Mantener usuarios, perfiles, empresas autorizadas, grupos de información y la conexión al origen dentro de las empresas de quien administra.

**Independent Test**: Se da de alta un usuario, se le asigna una empresa y un perfil, y se comprueba que solo entra a lo permitido sin revisar el cálculo del margen.

### Implementation for User Story 5

- [X] T032 [P] [US5] Registrar en el administrador perfil, empresas autorizadas, grupos de información y conexión al origen, sin volver a mostrar el secreto en claro y limitando a quien administra a sus empresas, en `apps/access/admin.py`
- [ ] T033 [P] [US5] Consultar solo las cuentas de la empresa seleccionada en `apps/erp/views.py` y `templates/erp/chart.html`
- [X] T034 [US5] Enlazar el administrador y la identidad de la persona desde `templates/base.html`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar la seguridad de lectura, el tiempo de respuesta y la comprobación de la guía.

- [ ] T035 [P] Citar `negocio.md` como regla de cálculo desde `apps/margins/services.py`
- [ ] T036 Mantener las sumas del margen y del panel en el origen, para 5.000 pedidos y 50 personas en menos de 5 segundos, en `apps/margins/services.py` y `apps/margins/dashboard.py`
- [ ] T037 Recorrer las comprobaciones de `specs/001-margen-pedidos-proyecto/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses the same assignment rules as US1 and should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Reuses the margin result of US1 and should be independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Configures the models of Phase 2 and should be independently testable

### Within Each User Story

- Models before services
- Services before screens
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models and selectors within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- `apps/margins/urls.py` lo tocan US1, US3 y US4: esas tres tareas de publicación no se hacen a la vez

---

## Parallel Example: User Story 1

```text
Task: "T013 [US1] Leer cabecera y líneas de venta en apps/erp/sales.py"
Task: "T014 [US1] Leer líneas de compra en apps/erp/purchases.py"
Task: "T015 [US1] Separar apuntes de horas e ingresos en apps/erp/ledger.py"
```

## Parallel Example: User Story 2

```text
Task: "T019 [US2] Recordar solo el identificador en apps/accounts/remember.py"
Task: "T020 [US2] Sesión de 30 días en apps/accounts/sessions.py"
```

## Parallel Example: User Story 4

```text
Task: "T028 [US4] Agregar indicadores en apps/margins/dashboard.py"
Task: "T029 [US4] Reparto visual en static/js/breakdown.js"
```

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
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

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
