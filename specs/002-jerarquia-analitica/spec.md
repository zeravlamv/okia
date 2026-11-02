# Feature Specification: Jerarquía analítica

**Feature Branch**: `002-jerarquia-analitica`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "Analitica. La relación de niveles analíticos indica la forma en la que se ha de acumular y mostrar la información. El orden de los niveles es la forma de agrupar. El nivel 1 engloba el 2, el 3, el 4 y el 5. El nivel 2 engloba el 3, el 4 y el 5, y así sucesivamente. Cualquier nivel analítico muestra ventas, ingresos, compras, gastos y margen."

## Clarifications

### Session 2026-10-30

- Q: ¿Qué importe entra en compras y qué importe entra en gastos dentro de cada grupo analítico? → A: Compras: todas las líneas de compra del proyecto. Gastos: apuntes de horas, mano de obra o personal. Margen: ventas menos compras menos gastos. Si la misma hora está en una línea y en un apunte, las dos cuentan.
- Q: Cuando un pedido no puede cerrar el margen porque no tiene proyecto o lo comparte con otro pedido vigente, ¿sus ventas entran en la jerarquía? → A: Esos pedidos se muestran en un grupo aparte, fuera de los niveles, con sus ventas y sin margen.
- Q: Al abrir la consulta, ¿la jerarquía sustituye las cinco listas sueltas de canal, delegación, departamento, proyecto y sección? → A: La jerarquía sustituye las cinco listas. Los indicadores generales y la consulta de cada pedido se mantienen.
- Q: Al abrir la analítica, ¿se ve solo el primer nivel y hay que abrir cada grupo para ver el siguiente? → A: Se ve el primer nivel. Abrir un grupo muestra el nivel siguiente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar la información acumulada por niveles (Priority: P1)

Una persona autorizada, con una empresa y un ejercicio ya elegidos, consulta la analítica como una sola jerarquía. El primer nivel agrupa todo lo que cuelga de él. Cada nivel siguiente agrupa solo lo que tiene debajo. En cualquier grupo, sea el más alto o el más bajo, se ven cinco cifras: ventas, ingresos, compras, gastos y margen.

**Why this priority**: Sin esta lectura, los niveles analíticos son cinco listas sueltas y no dicen cómo se acumula el resultado de la empresa.

**Independent Test**: Con una empresa, un ejercicio y al menos dos pedidos que compartan los niveles altos y se separen en un nivel inferior, la persona abre la analítica y comprueba que el grupo superior suma a los inferiores y que cada grupo muestra las cinco cifras.

**Acceptance Scenarios**:

1. **Given** el orden canal, delegación, departamento, proyecto y sección, y dos pedidos de la misma empresa y del mismo ejercicio que comparten canal, delegación y departamento y tienen proyectos distintos, **When** la persona abre la analítica, **Then** el canal muestra unas ventas, unos ingresos, unas compras, unos gastos y un margen iguales a la suma de esos mismos conceptos en los proyectos que contiene.
2. **Given** ese mismo canal, **When** la persona abre la delegación y después el departamento, **Then** cada grupo intermedio repite la suma de los grupos que engloba y no añade importes que no estén en esos grupos.
3. **Given** un grupo de último nivel con un único pedido cerrado, **When** la persona lo consulta, **Then** ve las ventas, los ingresos, las compras, los gastos y el margen de ese pedido.
4. **Given** un pedido con precio de venta, compras del proyecto y gastos del proyecto, **When** se muestra su margen dentro de cualquier grupo, **Then** el margen es el precio de venta menos las compras y menos los gastos. Los ingresos se ven al lado y no entran en esa resta.
5. **Given** una línea de compra del proyecto y un apunte de horas, mano de obra o personal del mismo proyecto, **When** se muestran las cifras del grupo, **Then** la línea entra en compras, el apunte entra en gastos y el margen resta las dos cantidades.
6. **Given** dos empresas con los mismos códigos analíticos, **When** la persona consulta la empresa elegida, **Then** la jerarquía no incluye pedidos, compras, gastos ni ingresos de la otra empresa.
7. **Given** un grupo con código y descripción, **When** se muestra, **Then** se leen el código y la descripción. Si no hay descripción, se lee el código. Si no hay código, el grupo se llama «Sin dato».
8. **Given** un pedido del ejercicio sin proyecto y otro que comparte proyecto con un segundo pedido vigente, **When** la persona abre la analítica, **Then** los dos aparecen en un grupo aparte, fuera de los niveles, con su precio de venta y sin margen, y ese precio no se suma a ningún canal, delegación, departamento, proyecto ni sección.
9. **Given** la consulta que antes mostraba una lista por canal, otra por delegación, otra por departamento, otra por proyecto y otra por sección, **When** la persona abre la analítica, **Then** esas cinco listas ya no están, la jerarquía sí está y los indicadores generales siguen visibles.
10. **Given** cinco niveles con pedidos en el más bajo, **When** la persona abre la analítica, **Then** ve solo el primer nivel con sus cifras. **When** abre un grupo de ese nivel, **Then** aparece únicamente el nivel siguiente que ese grupo engloba y los importes no cambian.

---

### User Story 2 - Cambiar el orden cambia la agrupación (Priority: P2)

Quien administra el orden de los niveles analíticos decide qué concepto engloba a los demás. Al cambiar las posiciones, la misma información se reagrupa. Los totales de la empresa no cambian.

**Why this priority**: El orden es la definición de la consulta. Si solo decorara la pantalla, la persona no podría elegir cómo acumular.

**Independent Test**: Con los mismos pedidos, se guarda un orden distinto y se comprueba que la anidación sigue el nuevo orden y que las cinco cifras de toda la empresa siguen igual.

**Acceptance Scenarios**:

1. **Given** un orden en el que el canal es el nivel 1 y la sección es el nivel 5, **When** quien administra pone la sección como nivel 1 y el canal como nivel 5, **Then** la sección pasa a englobar departamento, proyecto y canal, en el orden que haya quedado.
2. **Given** ese cambio de orden, **When** la persona vuelve a la analítica de la misma empresa y del mismo ejercicio, **Then** las ventas, los ingresos, las compras, los gastos y el margen de toda la empresa son los mismos que antes del cambio.
3. **Given** cinco niveles guardados, **When** se consulta la analítica, **Then** hay como máximo esos cinco escalones y cada uno engloba a los de posición mayor.

---

### User Story 3 - Respetar lo que el perfil puede ver (Priority: P3)

Una persona solo acumula los niveles y las cifras que su perfil permite. Un nivel no permitido no ocupa un escalón. Una cifra no permitida no aparece como cero.

**Why this priority**: La jerarquía no debe revelar un concepto o un importe que el perfil no tiene concedido.

**Independent Test**: Con un perfil que no puede ver un nivel intermedio y otro que no puede ver los gastos, se abre la misma empresa y se comprueba que ese nivel desaparece de la anidación y que los gastos no se muestran.

**Acceptance Scenarios**:

1. **Given** un perfil que puede ver canal, proyecto y las cinco cifras, pero no delegación, departamento ni sección, **When** abre la analítica, **Then** el canal engloba directamente los proyectos y no aparecen los tres niveles omitidos.
2. **Given** un perfil que no puede ver los gastos, **When** abre un grupo, **Then** ve las demás cifras permitidas y no ve un gasto con valor cero.
3. **Given** un perfil que no puede ver ningún nivel analítico, **When** abre la consulta, **Then** no aparece la jerarquía.

---

### Edge Cases

- Un ejercicio sin pedidos que cierren margen no muestra grupos analíticos con cifras inventadas. Si hay pedidos sin proyecto o con proyecto compartido, el grupo aparte sigue mostrando sus ventas.
- Un pedido anulado no entra en la jerarquía ni en el grupo aparte. Si un proyecto solo pertenece a un pedido anulado, sus imputaciones siguen sin asignar y no crean un grupo.
- Un pedido no anulado del ejercicio que no tiene proyecto, o cuyo proyecto lo comparte otro pedido vigente, no entra en ningún nivel analítico. Aparece en un único grupo aparte, con su precio de venta y sin compras, gastos, ingresos ni margen. Esas ventas no se suman a la jerarquía.
- Una pieza sin importe no se suma. El grupo y todos los grupos que lo engloban quedan marcados como incompletos.
- Un pedido con precio de venta cero muestra el importe del margen. No se calcula un porcentaje dentro de esta jerarquía.
- Dos códigos distintos con la misma descripción siguen siendo dos grupos. Sus importes no se mezclan.
- Un código sin descripción se muestra solo con el código. Varios pedidos sin código en el mismo nivel forman un único grupo «Sin dato».
- El periodo elige los pedidos por su fecha y, si no tienen fecha, por el año de su ejercicio. Las compras, los gastos y los ingresos del proyecto entran enteros, aunque tengan otra fecha.
- La moneda y los dos decimales son los de la empresa. Si la empresa no tiene moneda, los importes se leen en euros.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La analítica de la empresa y del ejercicio elegidos se muestra como una jerarquía y sustituye las cinco listas sueltas de cada nivel. Los indicadores generales, el filtro de empresa y ejercicio, y la consulta de cada pedido se mantienen.
- **FR-002**: El orden guardado de los niveles analíticos es el orden de agrupación. El nivel de la posición 1 engloba a los de las posiciones 2, 3, 4 y 5. El de la posición 2 engloba a los de las posiciones 3, 4 y 5. La misma regla sigue hasta el último nivel, que ya no engloba a ningún otro.
- **FR-003**: Cada grupo, en cualquier posición, muestra las ventas, los ingresos, las compras, los gastos y el margen que le corresponden, salvo la cifra que el perfil no pueda ver.
- **FR-004**: Las ventas de un grupo son la base sin impuestos de los pedidos de venta no anulados del ejercicio que cierran margen y caen en ese grupo. Manda la base de la cabecera. Si no existe, se suman las bases de las líneas.
- **FR-005**: Las compras de un grupo son las bases sin impuestos de todas las líneas de compra de los proyectos de esos pedidos, con cualquier fecha. Entran tanto el material como las líneas cuyo artículo indique horas, mano de obra o personal.
- **FR-006**: Los gastos de un grupo son los apuntes de esos proyectos, con cualquier fecha, cuya cuenta indique horas, mano de obra o personal. Un apunte de horas no se presenta como ingreso ni como compra.
- **FR-007**: Si la misma hora está en una línea de compra y en un apunte, la línea entra en compras, el apunte entra en gastos y el margen resta las dos cantidades.
- **FR-008**: Los ingresos de un grupo son los abonos menos los cargos de las cuentas de ingreso de esos proyectos. Se muestran junto al grupo y no se suman ni se restan a las ventas, a las compras, a los gastos ni al margen.
- **FR-009**: El margen de un grupo es sus ventas menos sus compras y menos sus gastos.
- **FR-010**: Cada cifra de un grupo analítico es la suma de esa misma cifra en los grupos que engloba directamente. El grupo aparte no es un grupo englobado y sus ventas no entran en esa suma.
- **FR-011**: Cambiar el orden de los niveles cambia qué grupo engloba a cuál. No cambia las cinco cifras del conjunto de la empresa para el mismo ejercicio.
- **FR-012**: Solo entran pedidos, compras, gastos e ingresos de la empresa elegida.
- **FR-013**: Un pedido entra en el ejercicio por su fecha. Si no tiene fecha, entra por el año de su ejercicio.
- **FR-014**: El coste y los ingresos se atribuyen a un pedido solo cuando su proyecto corresponde a un único pedido no anulado de la empresa. Si el pedido del ejercicio no tiene proyecto o lo comparte con otro pedido vigente, se muestra en un grupo aparte, fuera de los niveles, con su precio de venta y sin compras, sin gastos, sin ingresos y sin margen.
- **FR-015**: Un importe ausente no se sustituye por cero. El grupo queda incompleto, y también quedan incompletos los grupos que lo engloban.
- **FR-016**: Cada grupo se identifica con su código y su descripción. Sin descripción se identifica con el código. Sin código se identifica como «Sin dato».
- **FR-017**: Un nivel no concedido al perfil no aparece. El nivel visible anterior engloba directamente el siguiente nivel visible.
- **FR-018**: Una cifra no concedida al perfil no aparece y no se sustituye por cero.
- **FR-019**: Al abrir la consulta se ve solo el primer nivel visible, con sus cinco cifras permitidas. El resto del árbol no aparece desplegado. Abrir un grupo muestra únicamente el nivel siguiente que ese grupo engloba, sin modificar los importes.
- **FR-020**: La jerarquía no crea, no modifica y no anula pedidos, compras ni apuntes.

### Key Entities

- **Nivel analítico**: uno de los cinco conceptos de agrupación, con una posición de orden. La posición decide a qué otros niveles engloba.
- **Grupo**: un valor concreto de un nivel, con código y descripción, que contiene los grupos del nivel siguiente y acumula sus cifras.
- **Cifra del grupo**: ventas, ingresos, compras, gastos o margen del conjunto de pedidos cerrados que caen en el grupo.
- **Grupo aparte**: conjunto de pedidos del ejercicio que no pueden cerrar un margen. Está fuera de los niveles analíticos, muestra el precio de venta de cada uno y no muestra margen ni imputaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con un ejercicio de hasta 1.500 pedidos, la persona ve el primer nivel y sus cifras en menos de 5 segundos desde que abre la consulta.
- **SC-002**: En una jerarquía de al menos tres niveles y dos grupos en el nivel más bajo, cada cifra de un grupo superior coincide, céntimo a céntimo, con la suma de esa cifra en los grupos que engloba.
- **SC-003**: Después de invertir el orden de los niveles, las cinco cifras de toda la empresa permanecen iguales y el primer grupo visible pasa a ser el que ocupó la posición 1.
- **SC-004**: Una persona puede leer, en el primer vistazo de cada grupo, el código, la descripción y las cinco cifras permitidas, sin abrir otra consulta para completarlas.
- **SC-005**: En una prueba con un nivel oculto y una cifra oculta, ni ese nivel ni un cero de esa cifra aparecen en la jerarquía.

## Assumptions

- Quedó confirmado que las compras son todas las líneas de compra del proyecto y los gastos son solo los apuntes de horas, mano de obra o personal. El margen resta las dos. Los ingresos contables van al lado y no entran en esa resta.
- Las compras de la jerarquía son el coste de compra de los proyectos agrupados. No son el indicador de compras fechadas dentro del ejercicio que ya muestra el panel.
- El margen de esta consulta es un importe. El porcentaje sigue perteneciendo a la consulta de cada pedido y no se añade como sexta cifra de la jerarquía.
- Quedó confirmado que los pedidos que no cierran margen forman un grupo aparte, fuera de los niveles, con sus ventas y sin margen. Sus compras, gastos e ingresos no se muestran porque no pueden atribuirse a un solo pedido.
- El orden inicial sigue siendo canal, delegación, departamento, proyecto y sección, hasta que quien administra lo cambie.
- Quedó confirmado que la jerarquía sustituye las cinco listas sueltas. Los indicadores generales, el filtro de empresa y ejercicio, y la consulta de cada pedido se mantienen.
- Quedó confirmado que al abrir se ve solo el primer nivel. Abrir un grupo muestra el nivel siguiente y no despliega de una vez todos los niveles inferiores.
- El grupo aparte muestra las ventas de esos pedidos. No resuelve la revisión pendiente ni permite corregir los datos de origen.
