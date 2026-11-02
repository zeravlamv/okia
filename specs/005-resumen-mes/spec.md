# Feature Specification: Resumen del mes

**Feature Branch**: `005-resumen-mes`

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Nueva opción de menú. Resumen mes. Agrupar proyecto del mes y presentar ficha con los datos agrupados, pero solo resumen. Total pedido cliente / total albaranes cliente / Total pedidos compra / Total albaranes compra / total gastos. KPI varios / Graficas varias."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver el resumen de los proyectos de un mes (Priority: P1)

La persona abre Resumen mes en el menú, con la empresa y el ejercicio ya elegidos. Elige un mes y ve una ficha de ese mes: los proyectos cuyo pedido de venta cae en ese mes, cada uno solo con su resumen, y los totales del conjunto.

**Why this priority**: Es la consulta que se pide. Sin el agrupado por mes no hay ficha que resumir.

**Independent Test**: Con fichas ya calculadas de marzo y de abril, la persona abre Resumen mes, elige marzo y comprueba que solo entran los proyectos de marzo y que cada total es la suma de esos proyectos. Abril no se mezcla.

**Acceptance Scenarios**:

1. **Given** una persona con acceso a la empresa y al ejercicio, **When** abre el menú, **Then** ve la opción Resumen mes, distinta del cuadro de mando, del margen de pedidos y de la ficha de un solo proyecto.
2. **Given** el ejercicio elegido, **When** entra en Resumen mes, **Then** ve los doce meses de ese ejercicio y uno de ellos está seleccionado.
3. **Given** marzo seleccionado, **When** lee la ficha, **Then** aparecen solo los proyectos cuyo pedido de venta no anulado tiene fecha en marzo de ese ejercicio.
4. **Given** esos proyectos, **When** lee cada fila, **Then** ve el código del proyecto y cinco importes de resumen: pedido de cliente, albaranes de cliente, pedidos de compra, albaranes de compra y gastos. No ve las líneas ni el detalle de cada documento.
5. **Given** las filas del mes, **When** lee la cabecera, **Then** cada total es la suma de la misma cifra en esas filas.
6. **Given** un proyecto de marzo con albaranes o gastos de otro mes, **When** se resume marzo, **Then** ese proyecto entra entero en marzo, con la vida ya guardada en su ficha, y no se parte entre meses.
7. **Given** la fila de un proyecto, **When** la persona la abre, **Then** llega a la ficha de ese proyecto. El resumen del mes no sustituye a esa ficha.
8. **Given** la empresa A, **When** se consulta el mismo mes de la empresa B, **Then** no aparecen los proyectos de A.

---

### User Story 2 - Leer los indicadores del mes (Priority: P2)

Además de los cinco totales, la ficha del mes muestra cuántos proyectos agrupa, el margen del conjunto y lo que sigue pendiente de albaranar. La persona ve el mes de un vistazo, sin sumar las filas a mano.

**Why this priority**: Los cinco totales ya responden a la petición. Los indicadores dicen si el mes va servido y con qué margen, que es para qué se agrupa.

**Independent Test**: Con dos proyectos de marzo, pedidos de cliente 100 y 40, albaranes de cliente 80 y 40, y gastos 10 y 5, la persona lee 2 proyectos, margen 105 y pendiente de albaranar de venta 20.

**Acceptance Scenarios**:

1. **Given** un mes con proyectos resumidos, **When** se leen los indicadores, **Then** el número de proyectos coincide con las filas del mes.
2. **Given** esos proyectos, **When** se lee el margen, **Then** es el total de albaranes de cliente menos el total de gastos, y el porcentaje se calcula sobre los albaranes de cliente.
3. **Given** albaranes de cliente a cero, **When** se lee el porcentaje de margen, **Then** no se muestra un porcentaje.
4. **Given** el pedido de cliente mayor que los albaranes de cliente, **When** se lee el pendiente de albaranar de venta, **Then** es la diferencia. Si los albaranes cubren el pedido, el pendiente es cero.
5. **Given** pedidos de compra y albaranes de compra, **When** se lee el pendiente de albaranar de compra, **Then** es lo que del pedido de compra aún no está cubierto por su albarán, con la misma regla que ya usa la ficha del proyecto, sumada al mes.
6. **Given** un margen negativo, **When** se lee el indicador, **Then** se muestra el importe negativo. No se presenta como si faltara un dato.

---

### User Story 3 - Ver el mes en gráficas (Priority: P3)

La misma ficha dibuja el mes: los totales que la persona puede ver, la composición del pedido frente al gasto y al margen, y el peso de cada proyecto. Las gráficas usan las mismas cifras que el resumen, no otras.

**Why this priority**: El resumen numérico ya se puede usar. Las gráficas lo hacen legible cuando el mes tiene muchos proyectos.

**Independent Test**: Con el mes del escenario anterior, la gráfica de composición muestra el pedido del mes en el centro y el margen igual al indicador, 105. La gráfica por proyecto tiene exactamente esas dos filas.

**Acceptance Scenarios**:

1. **Given** los totales visibles del mes, **When** se mira la gráfica de totales, **Then** cada barra corresponde a uno de esos totales y al mismo importe.
2. **Given** permiso para ver albaranes de cliente y gastos, **When** se mira la composición, **Then** el centro es el total de pedidos de cliente, y se distinguen los albaranes de cliente, los gastos y el margen cuando el margen es positivo.
3. **Given** un margen negativo, **When** se mira la composición, **Then** el margen se lee junto a la gráfica y no ocupa una porción.
4. **Given** los proyectos del mes, **When** se mira la gráfica por proyecto, **Then** hay una fila por proyecto, con su albaranado de cliente y su gasto, y no se dibujan las líneas de los documentos.
5. **Given** un total que el perfil no puede ver, **When** se miran las gráficas, **Then** esa cifra no aparece ni como barra ni como porción ni como cero.

---

### Edge Cases

- Un mes sin proyectos muestra que no hay proyectos ese mes. No inventa totales.
- Un proyecto del mes que aún no tiene ficha calculada se cuenta aparte, como pendiente de calcular, y no entra en las sumas como cero. La ficha del mes indica cuántos quedan así.
- Un pedido anulado no mete el proyecto en el mes de ese pedido.
- Un proyecto sin fecha de pedido no entra en ningún mes.
- Si el mismo proyecto tiene más de un pedido de venta vigente en el ejercicio y caen en meses distintos, el proyecto se resume en cada uno de esos meses con la ficha entera, y la página lo señala para que no se sumen dos veces sin querer al recorrer el ejercicio.
- El albarán de compra se muestra en su total y no se vuelve a sumar al gasto. El gasto es el que ya tiene la ficha del proyecto, incluido el albarán de compra que ya se contabilizó como gasto.
- Una nota de abono resta en el total que le corresponde.
- Una pieza sin importe no se suma y el resumen del mes queda incompleto.
- Un mes cerrado se puede consultar. Muestra la última ficha guardada. Abrir Resumen mes no recalcula y no abre el mes.
- Cambiar de mes no cambia de empresa ni de ejercicio. Cambiar de empresa o de ejercicio vuelve a agrupar con esa selección.
- Un grupo de información no concedido no se muestra como cero: desaparecen su columna, su total, su indicador y su gráfica.
- El margen del mes solo se muestra si se pueden ver los albaranes de cliente y los gastos. El pendiente de albaranar de venta solo si se pueden ver pedidos y albaranes de cliente. El de compra solo si se pueden ver pedidos y albaranes de compra.
- Los importes usan punto de miles, coma decimal y dos decimales, en la moneda de la empresa. Si no tiene moneda, se usa el euro.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El menú ofrece Resumen mes a quien ya consulta la empresa. No sustituye al cuadro de mando, al margen de pedidos ni a la ficha de un proyecto.
- **FR-002**: Resumen mes usa la empresa y el ejercicio ya elegidos. La persona puede elegir cualquiera de los doce meses de ese ejercicio sin lanzar una actualización.
- **FR-003**: Al entrar, si el ejercicio es el año en curso, el mes seleccionado es el mes de hoy. Si el ejercicio es otro, el mes seleccionado es enero. La persona puede cambiarlo.
- **FR-004**: Un proyecto pertenece a un mes cuando la fecha de un pedido de venta no anulado cae en ese mes y en el ejercicio elegido. Sin fecha de pedido, no pertenece a ningún mes.
- **FR-005**: La ficha del mes lista esos proyectos y, por cada uno, solo el resumen: pedido de cliente, albaranes de cliente, pedidos de compra, albaranes de compra y gastos. Esos importes son los de la ficha ya calculada del proyecto, con cualquier fecha de albarán o de gasto.
- **FR-006**: Cada total del mes es la suma del mismo importe en los proyectos listados. El total de gastos no incluye otra vez la base de los albaranes de compra.
- **FR-007**: La fila de un proyecto abre la ficha de ese proyecto. Resumen mes no muestra líneas ni documentos.
- **FR-008**: Los indicadores del mes son el número de proyectos, los cinco totales, el margen, su porcentaje sobre los albaranes de cliente, el pendiente de albaranar de venta y el pendiente de albaranar de compra.
- **FR-009**: El margen del mes es el total de albaranes de cliente menos el total de gastos. Si los albaranes de cliente son cero, el porcentaje no se muestra. Un margen negativo se muestra como importe negativo.
- **FR-010**: El pendiente de albaranar de venta es el pedido de cliente menos los albaranes de cliente cuando el pedido es mayor, y cero cuando los albaranes lo cubren. El pendiente de compra aplica, proyecto a proyecto, la regla ya vigente de pedido no cubierto por su albarán, y luego se suma.
- **FR-011**: Hay tres gráficas, y solo con cifras que el perfil puede ver: los totales del mes; la composición con el pedido de cliente en el centro y, como partes, albaranes de cliente, gastos y margen positivo; y una fila por proyecto con su albaranado de cliente y su gasto. El margen negativo se lee junto a la composición y no es una parte. Cada gráfica coincide con el indicador del mismo nombre.
- **FR-012**: Un grupo de información no concedido omite su cifra en la fila, en el total, en el indicador y en las gráficas. No la sustituye por cero.
- **FR-013**: Abrir o cambiar de mes no lee el origen y no pulsa Actualizar. Si un proyecto del mes no tiene ficha, se nombra como pendiente de calcular y no entra en las sumas.
- **FR-014**: Consultar un mes cerrado no lo abre ni cambia su ficha. Muestra lo último guardado.
- **FR-015**: Las cifras de una empresa no se mezclan con las de otra, ni las de un ejercicio con las de otro.
- **FR-016**: Un documento anulado no entra. Una pieza sin importe no se suma y el mes queda marcado como incompleto.

### Key Entities

- **Mes del resumen**: uno de los doce meses del ejercicio elegido, dentro de la empresa elegida. Agrupa proyectos; no es un cierre ni una actualización.
- **Proyecto del mes**: un proyecto con al menos un pedido de venta no anulado fechado en ese mes y en ese ejercicio. Su resumen es el de su ficha ya calculada.
- **Resumen del proyecto**: los cinco importes de la fila, sin documentos ni líneas.
- **Indicadores del mes**: el recuento, los cinco totales, el margen y los pendientes de albaranar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quien ya tiene las fichas calculadas abre Resumen mes y lee los cinco totales del mes elegido sin lanzar una actualización y en una sola pantalla.
- **SC-002**: En el 100 % de los meses de prueba, cada total coincide con la suma de las fichas de los proyectos de ese mes, y ningún proyecto de otro mes entra en la suma.
- **SC-003**: El margen mostrado y el margen de la gráfica de composición son el mismo importe, y coinciden con albaranes de cliente menos gastos.
- **SC-004**: Un perfil al que le falta un grupo no ve esa cifra en la fila, en el total ni en las gráficas, y el resto de cifras del mes sigue visible.
- **SC-005**: Con un mes de al menos diez proyectos, la persona distingue en la gráfica por proyecto cuál aporta albaranado y cuál aporta gasto, sin abrir las líneas.

## Assumptions

- El mes de un proyecto es el de la fecha de su pedido de venta, que es la regla ya vigente. No se agrupa por la fecha del albarán ni por la del gasto.
- «Solo resumen» significa los cinco importes por proyecto y los totales del mes. El detalle de documentos sigue viviendo en la ficha del proyecto, a la que se llega desde la fila.
- El gasto del resumen es el gasto de la ficha del proyecto. Ahí ya está el albarán de compra contabilizado. Por eso el total de albaranes de compra se enseña aparte y no se resta otra vez en el margen.
- El margen del mes sigue a la ficha del proyecto: albaranes de cliente menos gastos. No es el margen del cuadro de mando, que compara ingresos y gastos de todo el ejercicio.
- Los pendientes usan las reglas ya vigentes de la ficha y se suman. No se inventa un pendiente nuevo.
- Resumen mes lee fichas ya guardadas. Quien necesite cifras nuevas pulsa Actualizar en el ejercicio, como hasta ahora, y el cierre de mes sigue impidiendo recalcular un mes cerrado.
- Si el proyecto cae en dos meses del ejercicio porque tiene dos pedidos vigentes, se enseña en ambos con la ficha completa y se avisa. No se reparte la ficha entre los dos meses.
- Al entrar, el mes inicial es el de hoy cuando el ejercicio es el año en curso, y enero en cualquier otro ejercicio. No se recuerda el último mes consultado.
- Las tres gráficas son las de totales, composición y proyectos. No se añade una cuarta hasta que se pida.
- El formato de importes y la ocultación de un grupo no concedido siguen las reglas ya vigentes.
