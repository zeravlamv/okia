# Feature Specification: Análisis profundo

**Feature Branch**: `003-analisis-profundo`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "El centro de la información es el proyecto. Ver la progresión temporal por meses, contemplando proyectos que abarcan más de un ejercicio. El inicio es la fecha del pedido. La fecha del albarán marca los hitos de progresión. Indicar la progresión porcentual de los albaranes respecto al pedido. Separar si el albarán está facturado o no. Las compras y los gastos asociados también se presentan de forma temporal. Detallar las compras por proveedor y los gastos por cuenta, con la descripción del plan contable. Con eso: gráficas, Gantt e indicadores."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver la progresión del proyecto (Priority: P1)

Una persona autorizada abre un proyecto de su empresa y ve su vida entera, aunque cruce varios ejercicios. El inicio es la fecha del pedido de venta. Cada albarán de venta es un hito en su fecha. La ficha dice cuánto se ha albaranado respecto al pedido, y separa lo facturado de lo que aún no lo está.

**Why this priority**: Sin esta lectura, el proyecto queda partido por ejercicio y no se ve si el pedido avanza, si ya está servido o si lo servido está facturado.

**Independent Test**: Con un pedido de 1.000 en 2024 y dos albaranes de venta en 2025 y 2026, uno facturado de 400 y otro sin facturar de 100, la persona abre el proyecto y comprueba el inicio, los tres ejercicios, el 50 % de progresión y las dos partes.

**Acceptance Scenarios**:

1. **Given** un proyecto cuyo pedido de venta es de marzo de 2024 y cuyos albaranes de venta caen en 2025 y 2026, **When** la persona lo abre, **Then** los documentos de los tres ejercicios aparecen en la misma ficha, con los meses desde el pedido hasta el final de su barra.
2. **Given** un pedido con base 1.000 y albaranes de venta que suman 500, **When** se muestra la progresión, **Then** el porcentaje es 50,00 %. El albaranado es 500 y el pendiente de albaranar es 500.
3. **Given** esos 500 repartidos en 400 facturados y 100 no facturados, **When** se muestra la ficha, **Then** las dos partes se leen por separado, cada una con su importe y con su porcentaje sobre el pedido, y su suma es el albaranado.
4. **Given** albaranes que suman más que el pedido, **When** se muestra la progresión, **Then** el porcentaje pasa de 100 y el pendiente de albaranar es cero.
5. **Given** un pedido con base cero y albaranes con importe, **When** se muestra la progresión, **Then** se ven los importes y el porcentaje dice «No aplicable».
6. **Given** un proyecto sin albaranes de venta, **When** se abre, **Then** la progresión es cero, no hay hitos y el pendiente de albaranar es la base del pedido.
7. **Given** la fecha del pedido y tres albaranes, **When** se mira la tabla de hitos, **Then** cada albarán muestra su fecha, su base, si está facturado o no, y el porcentaje acumulado sobre el pedido hasta ese hito. El orden es de la fecha más antigua a la más reciente.
8. **Given** un importe de 2447563.88 euros y un porcentaje de 50, **When** se muestran, **Then** se leen «2.447.563,88 EUR» y «50,00 %», alineados a la izquierda.

---

### User Story 2 - Ver el calendario y la Gantt (Priority: P2)

La persona ve el mismo proyecto dibujado en el tiempo. La Gantt marca el inicio y cada hito. Una gráfica acumula, mes a mes, lo albaranado y lo separa entre facturado y no facturado. Otra gráfica pone compras y gastos en esos mismos meses.

**Why this priority**: Los indicadores dicen el total. El calendario enseña cuándo avanzó el proyecto y cuándo entraron las compras y los gastos.

**Independent Test**: Con un pedido en enero, un albarán facturado en marzo y otro sin facturar en junio, más una compra y un gasto en marzo, la persona comprueba la barra, los dos hitos distintos y que marzo reúne albarán, compra y gasto.

**Acceptance Scenarios**:

1. **Given** un pedido del 10 de enero y un último albarán de venta del 2 de junio que no cubre el pedido, **When** se muestra la Gantt, **Then** la barra del proyecto empieza el 10 de enero y llega hasta hoy. **Given** un último albarán que ya cubre o supera el pedido, **Then** la barra termina en la fecha de ese último albarán.
2. **Given** dos albaranes de venta, uno facturado y otro no, **When** se muestra la Gantt, **Then** cada uno es un hito en su fecha y se distinguen entre sí.
3. **Given** un albarán de compra de un proveedor en una fecha, **When** se muestra la Gantt, **Then** hay un hito de compra en esa fecha con el proveedor. Un pedido de compra del proyecto que no tiene albarán de compra aparece como comprometido y su base no se suma a las compras.
4. **Given** meses desde el pedido hasta el final de la barra, **When** se muestra la gráfica de progresión, **Then** cada mes acumula lo albaranado hasta entonces, separa lo facturado de lo no facturado, marca la base del pedido como referencia y muestra el porcentaje acumulado. Un mes sin albaranes conserva el acumulado anterior.
5. **Given** compras y gastos del proyecto en distintos meses, **When** se muestra su gráfica, **Then** cada mes tiene el importe de compras y el de gastos de ese mes, no el acumulado. Un mes sin ninguno se ve vacío.
6. **Given** la ficha ya abierta, **When** la persona pasa de los indicadores a la Gantt o a una gráfica, **Then** los importes no cambian y no se vuelve a leer el origen.
7. **Given** el cuadro de mando y la jerarquía de la misma empresa, **When** la persona abre la ficha del proyecto, **Then** las dos consultas siguen disponibles.

---

### User Story 3 - Detallar compras y gastos (Priority: P3)

La persona revisa quién cobra las compras del proyecto y qué cuentas recogen los gastos. Las compras se agrupan por proveedor. Los gastos se agrupan por cuenta, con su código y la descripción del plan contable. Las dos lecturas también se pueden ver por mes.

**Why this priority**: La gráfica mensual dice cuánto salió. El detalle dice a quién y en qué cuenta, que es lo que permite revisar el proyecto.

**Independent Test**: Con dos proveedores y dos cuentas de gasto en el mismo proyecto, la persona abre cada tabla y comprueba que los totales coinciden con las compras y los gastos de la ficha.

**Acceptance Scenarios**:

1. **Given** albaranes de compra de dos proveedores, **When** la persona abre las compras por proveedor, **Then** cada proveedor muestra su código, su nombre y la suma de sus bases, y la suma de los proveedores es la cifra de compras del proyecto.
2. **Given** esos albaranes en meses distintos, **When** abre las compras por proveedor y por mes, **Then** cada importe está en el mes de la fecha del albarán de compra.
3. **Given** gastos del proyecto en dos cuentas, **When** abre los gastos por cuenta, **Then** cada cuenta muestra su código, la descripción del plan contable y su importe. La suma de las cuentas es la cifra de gastos del proyecto.
4. **Given** una cuenta sin descripción, o cuya descripción es igual al código, **When** se muestra, **Then** se lee solo el código. **Given** una cuenta con descripción distinta, **Then** se leen el código y la descripción.
5. **Given** un apunte cuyo comentario indica el cierre del ejercicio, **When** se ven los gastos, **Then** ese apunte no está y no reduce los gastos del proyecto.
6. **Given** una cuenta de ingreso aunque su nombre mencione horas, **When** se ven los gastos, **Then** esa cuenta no entra en los gastos. Un apunte de horas, mano de obra o personal que no es ingreso sí entra.
7. **Given** las tablas de proveedores y de cuentas, **When** se muestran sus gráficas, **Then** cada proveedor y cada cuenta tienen el mismo importe que en la tabla.

---

### Edge Cases

- Un proyecto de otra empresa, aunque repita el código, no entra en la ficha.
- Un pedido anulado no abre ficha. Un albarán anulado no es hito, no suma al albaranado y no entra en facturado ni en no facturado.
- Un albarán de abono resta su base del albaranado y aparece como hito con importe negativo. Si está facturado, la resta cae en la parte facturada.
- Un albarán de venta del que no se sabe si está facturado entra en el albaranado, se señala como «sin dato de facturación» y no se suma ni a facturado ni a no facturado.
- Una base ausente no se sustituye por cero. La ficha queda incompleta.
- La valoración usa la base sin impuestos. Manda la base de la cabecera. Si no existe, se suman las bases de las líneas. Si la cabecera y las líneas difieren, el indicador usa la cabecera y las líneas no se fuerzan a cuadrar.
- Varios albaranes en el mismo mes suman en ese mes y la Gantt conserva un hito por fecha.
- Un albarán o un apunte sin fecha no se coloca en un mes. Se lista aparte, marcado como sin fecha, y sí entra en el total del proyecto.
- El mes del pedido sin movimientos posteriores se muestra vacío y el acumulado no salta al mes siguiente.
- Un pedido de compra que ya tiene albarán de compra no se repite como comprometido. El comprometido no entra en la cifra de compras ni en la gráfica mensual de compras.
- Una cuenta, un proveedor o un importe no concedido al perfil no aparece y no se sustituye por cero.
- Sin actualización de la empresa no hay ficha, ni Gantt ni gráficas. Abrir el proyecto o cambiar de gráfica no vuelve a leer el origen.
- La consulta no crea, no modifica y no anula pedidos, albaranes ni apuntes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La persona analiza un proyecto de la empresa elegida y ve su vida completa, desde la fecha del pedido de venta, aunque los albaranes, las compras o los gastos caigan en otros ejercicios.
- **FR-002**: El inicio del proyecto es la fecha del pedido de venta. La base del pedido es la referencia de la progresión.
- **FR-003**: Cada albarán de venta del proyecto es un hito en su fecha. El albaranado es la suma de sus bases. La progresión es el albaranado partido por la base del pedido. Si el pedido es cero, el porcentaje es «No aplicable». Si el albaranado supera el pedido, el porcentaje pasa de 100.
- **FR-004**: Lo facturado y lo no facturado se muestran por separado, con importe y con porcentaje sobre el pedido. Su suma, más los albaranes sin dato de facturación, es el albaranado. El pendiente de albaranar es la base del pedido menos el albaranado cuando el pedido es mayor. Si el albaranado es igual o mayor, el pendiente es cero.
- **FR-005**: La ficha muestra los meses desde el mes del pedido hasta el mes en que termina la barra. Un mes sin movimiento se ve y no se omite.
- **FR-006**: La Gantt dibuja una barra desde la fecha del pedido hasta el último albarán de venta que cubre o supera el pedido. Si el pedido no está cubierto, o todavía no hay albaranes, la barra llega hasta hoy. Cada albarán de venta es un hito distinguido según esté facturado, no lo esté o no haya dato.
- **FR-007**: Las compras del proyecto son las bases de sus albaranes de compra, colocadas en el mes de su fecha y detalladas por proveedor. Un pedido de compra sin albarán de compra se muestra como comprometido y no se suma a las compras.
- **FR-008**: Los gastos del proyecto se colocan en el mes de la fecha del apunte y se detallan por cuenta, con el código y la descripción del plan contable. El cierre del ejercicio no entra. Una cuenta de ingreso no entra aunque su nombre mencione horas.
- **FR-009**: Hay cuatro lecturas gráficas cuando existen sus datos: progresión mensual acumulada, con pedido de referencia y separación entre facturado y no facturado; compras y gastos de cada mes; compras por proveedor; gastos por cuenta. Los importes de las gráficas son los de la ficha.
- **FR-010**: Hay tres tablas: hitos del albarán de venta con fecha, importe, situación de facturación y porcentaje acumulado; compras por proveedor y por mes; gastos por cuenta y por mes.
- **FR-011**: Las cifras son las de la última actualización de la empresa. Abrir el proyecto, la Gantt o una tabla no vuelve a calcular. Sin actualización no se muestran cifras ni gráficas.
- **FR-012**: Solo entra información de la empresa elegida. Una cifra o una lista no concedida al perfil no aparece y no se sustituye por cero. Un documento anulado no entra.
- **FR-013**: Los importes se muestran con punto de miles, coma decimal y dos decimales, alineados a la izquierda, en la moneda de la empresa. Si la empresa no tiene moneda, se usa el euro. El porcentaje usa coma decimal y dos decimales.
- **FR-014**: El código y la descripción de la cuenta, y el código y el nombre del proveedor, se leen juntos. Sin descripción, o si es igual al código, queda solo el código.
- **FR-015**: El análisis no crea, no modifica y no anula pedidos, albaranes ni apuntes. No sustituye el cuadro de mando ni la jerarquía.

### Key Entities

- **Proyecto**: la operación que se analiza, con la fecha y la base de su pedido de venta, y con todos los meses de su vida.
- **Hito de albarán**: un albarán de venta del proyecto, con fecha, base y situación de facturación.
- **Progresión**: el albaranado acumulado respecto a la base del pedido.
- **Compra del proyecto**: un albarán de compra, con proveedor, fecha y base. El pedido de compra sin albarán es un comprometido y no es una compra acumulada.
- **Gasto del proyecto**: un apunte que entra como gasto, con fecha, cuenta, descripción del plan contable e importe.
- **Mes de la vida**: un mes del calendario entre el inicio y el fin de la barra, tenga o no movimiento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona abre un proyecto y ve, en una sola ficha, la fecha de inicio, la base del pedido, lo albaranado, la progresión, lo facturado, lo no facturado y el pendiente de albaranar, aunque los documentos pertenezcan a más de un ejercicio.
- **SC-002**: En cada proyecto con base de pedido distinta de cero, el porcentaje de progresión es el albaranado partido por esa base. Si el albaranado es mayor, el porcentaje mostrado es mayor que 100. Si la base es cero, el porcentaje dice «No aplicable».
- **SC-003**: En cada proyecto, la suma de lo facturado, lo no facturado y lo sin dato de facturación es igual al albaranado.
- **SC-004**: La barra de la Gantt empieza en la fecha del pedido. Termina en el último albarán de venta cuando ese albarán ya cubre el pedido, y termina hoy cuando el pedido sigue descubierto.
- **SC-005**: La suma de las compras por proveedor es la cifra de compras, y la suma de los gastos por cuenta es la cifra de gastos. Un comprometido sin albarán no aumenta las compras.
- **SC-006**: Una persona sin permiso para albaranes, compras o gastos no ve esa parte en la ficha, en la Gantt ni en las gráficas, tampoco con valor cero.

## Assumptions

- El proyecto que se abre es el de un pedido de venta no anulado de la empresa. Si varios pedidos vigentes comparten el proyecto, el inicio es la fecha más antigua y la base es la suma de sus bases.
- Los albaranes, las compras y los gastos se atribuyen al proyecto por su código, dentro de la misma empresa. Un documento sin proyecto no entra en la ficha.
- La compra acumulada sale del albarán de compra. El pedido de compra solo aparece como comprometido cuando todavía no tiene albarán. No se calcula el resto de un pedido de compra ya albaranado en parte.
- El gasto del proyecto sigue la regla ya vigente: entra lo que es gasto y no entra el ingreso ni el cierre del ejercicio. La novedad de esta ficha es mostrarlo por mes y por cuenta, con la descripción del plan contable.
- «Hoy» es el día en que la persona abre la ficha.
- Canal, delegación, departamento, sección, el ranking de clientes y el ranking de proveedores no son el centro de esta consulta. El proveedor aparece dentro de las compras del proyecto.
- El cuadro de mando y la jerarquía siguen como están. Esta ficha no recorta sus cifras al ejercicio elegido en el filtro.
- Las reglas ya vigentes siguen mandando para lo que esta ficha no cambia: misma empresa, documentos anulados fuera, importe ausente como dato incompleto, y lectura del origen solo al actualizar.
