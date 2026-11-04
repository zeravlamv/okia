# Feature Specification: Aviso de discrepancias

**Feature Branch**: `006-aviso-discrepancias`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "Quiero que en el dashboard aparezca un aviso, modo campanita, indicando el número de proyectos que tienen discrepancia entre el pedido de venta y lo albaranado, pedido de compra y albaranado y ventas con ingresos. Si clico en la campanita me mostrará, en ventana emergente, los proyectos afectados y tendré acceso a la ficha de cada uno. Después, dentro de la ficha quiero que añadas un selector donde pueda seleccionar, Revisado, Pdte. Revisar. El revisado dará por buena la discrepancia y no volverá a salir dentro de los pendientes. Dentro de la ficha podré cambiar el estado siempre."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver cuántos proyectos no cuadran (Priority: P1)

La persona entra en el cuadro de mando, con la empresa y el ejercicio ya elegidos, y ve una campanita con el número de proyectos de ese ejercicio que tienen alguna discrepancia pendiente de revisar. Al pulsarla se abre una ventana con esos proyectos y, desde cada uno, pasa a su ficha.

**Why this priority**: Sin el aviso y la lista no hay forma de saber qué proyectos revisar. El estado de la ficha solo tiene sentido cuando esa lista existe.

**Independent Test**: Con tres proyectos del ejercicio, uno con el pedido de venta distinto de lo albaranado, otro con las tres parejas iguales y otro ya marcado como revisado aunque no cuadre, la campanita muestra 1. La ventana lista solo el primero y desde ahí se abre su ficha.

**Acceptance Scenarios**:

1. **Given** la empresa y el ejercicio elegidos, **When** la persona abre el cuadro de mando, **Then** ve una campanita con el número de proyectos de ese ejercicio que tienen al menos una discrepancia y siguen pendientes de revisar.
2. **Given** ningún proyecto en ese caso, **When** mira la campanita, **Then** el número es cero y la campanita sigue visible.
3. **Given** un número mayor que cero, **When** pulsa la campanita, **Then** se abre una ventana con un proyecto por fila, sin repetir el mismo proyecto aunque falle más de una pareja.
4. **Given** esa fila, **When** la lee, **Then** ve el código del proyecto, el nombre si existe, qué parejas no cuadran y los dos importes de cada pareja.
5. **Given** la fila de un proyecto, **When** la abre, **Then** llega a la ficha de ese proyecto. Cerrar la ventana no cambia el estado de revisión.
6. **Given** la empresa A, **When** consulta el mismo ejercicio de la empresa B, **Then** la campanita y la ventana no incluyen los proyectos de A.
7. **Given** otro ejercicio de la misma empresa, **When** cambia el ejercicio, **Then** el número y la lista son los de ese ejercicio.

---

### User Story 2 - Dar por buena una discrepancia (Priority: P2)

Dentro de la ficha, la persona elige si el proyecto está revisado o pendiente de revisar. Revisado da por buena la discrepancia: el proyecto deja de contarse en la campanita y no vuelve a la ventana. Puede cambiar el estado cuando quiera y el aviso vuelve a seguir la regla.

**Why this priority**: La lista sola obligaría a revisar siempre los mismos proyectos. El selector es lo que permite cerrar una discrepancia conocida sin borrarla de la ficha.

**Independent Test**: Con un proyecto cuyo pedido de venta no coincide con lo albaranado, la persona lo marca Revisado, vuelve al cuadro de mando y comprueba que ya no está en el número ni en la ventana. Lo vuelve a poner en Pdte. Revisar y reaparece.

**Acceptance Scenarios**:

1. **Given** la ficha de un proyecto, **When** la persona mira el selector, **Then** puede elegir Revisado o Pdte. Revisar, y ve cuál de los dos está activo.
2. **Given** un proyecto que nunca se ha marcado, **When** abre la ficha, **Then** el selector está en Pdte. Revisar.
3. **Given** una discrepancia pendiente, **When** elige Revisado, **Then** el proyecto deja de sumar en la campanita y deja de aparecer en la ventana, aunque los importes sigan distintos.
4. **Given** un proyecto revisado cuyos importes siguen distintos, **When** vuelve a elegir Pdte. Revisar, **Then** vuelve a la campanita y a la ventana.
5. **Given** un proyecto revisado cuyos importes pasan a cuadrar, **When** lo deja en Revisado y después lo pone en Pdte. Revisar, **Then** no entra en la campanita, porque ya no hay discrepancia.
6. **Given** cualquier ficha, con o sin discrepancia, **When** la persona cambia el selector, **Then** el cambio queda guardado y puede volver a cambiarlo más adelante.
7. **Given** una persona que marca Revisado, **When** otra persona con acceso a la misma empresa abre el cuadro de mando, **Then** ese proyecto tampoco le aparece entre los pendientes.

---

### Edge Cases

- Un proyecto cuenta como uno aunque fallen las tres parejas. La ventana muestra las tres, cada una con sus dos importes.
- Pedido y albarán iguales a cero no son discrepancia. Tampoco lo son unas ventas albaranadas de cero frente a unos ingresos de cero.
- Cualquier diferencia distinta de cero es discrepancia, en los dos sentidos. Un albarán mayor que el pedido también cuenta. Un abono que deja el albaranado por debajo del pedido también cuenta.
- Una pareja a la que le falta un importe no se trata como diferencia numérica y no mete sola al proyecto en la campanita.
- Un pedido o un albarán anulado no entra en la comparación.
- Un proyecto del ejercicio que todavía no tiene ficha calculada no entra en el número ni en la ventana.
- Un proyecto sin pedido de compra y sin albarán de compra no falla esa pareja.
- Marcar Revisado no modifica pedidos, albaranes ni ingresos. La ficha sigue mostrando los importes que no cuadran.
- Cerrar la ventana, cambiar de empresa o cambiar de ejercicio no marca ningún proyecto como revisado.
- El estado revisado se mantiene aunque después cambien los importes. Solo vuelve a la lista si la persona lo pone otra vez en Pdte. Revisar y, en ese momento, sigue habiendo alguna pareja distinta.
- Una persona que no puede ver una de las cifras no ve esa pareja en la ventana. Si las parejas que sí puede ver cuadran, el proyecto no le cuenta. El estado de revisión es el mismo para quien sí ve el resto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El cuadro de mando muestra una campanita con el número de proyectos del ejercicio elegido, de la empresa elegida, que tienen al menos una discrepancia pendiente de revisar.
- **FR-002**: Si no hay ninguno, la campanita muestra cero y permanece visible.
- **FR-003**: Una discrepancia es una de estas tres parejas cuando sus dos importes existen y no son iguales: el pedido de venta frente a lo albaranado de venta; el pedido de compra frente a lo albaranado de compra; las ventas albaranadas frente a los ingresos del proyecto.
- **FR-004**: El número cuenta proyectos, no parejas. Un proyecto con varias parejas distintas cuenta una sola vez.
- **FR-005**: Pulsar la campanita abre una ventana con esos proyectos. Cada fila identifica el proyecto, dice qué parejas no cuadran y muestra los dos importes de cada una.
- **FR-006**: Desde cada fila se abre la ficha de ese proyecto. Cerrar la ventana no cambia el estado de revisión ni los importes.
- **FR-007**: La ficha de un proyecto ofrece un selector con dos estados: Revisado y Pdte. Revisar. Si nadie lo ha cambiado, el estado es Pdte. Revisar.
- **FR-008**: Revisado da por buena la discrepancia de ese proyecto. El proyecto deja de entrar en la campanita y en la ventana mientras siga en Revisado, aunque los importes sigan siendo distintos.
- **FR-009**: La persona puede cambiar el estado en cualquier momento, haya o no discrepancia. Al guardarlo, el cuadro de mando vuelve a aplicar la regla: solo entran los proyectos con alguna pareja distinta y en Pdte. Revisar.
- **FR-010**: El estado pertenece al proyecto de esa empresa. Quien tenga acceso ve el mismo estado y el mismo efecto en la campanita.
- **FR-011**: La campanita, la ventana y la ficha se limitan a la empresa y al ejercicio elegidos, y a las cifras que esa persona puede ver.
- **FR-012**: El aviso no crea, no modifica y no anula pedidos, albaranes ni ingresos.

### Key Entities

- **Discrepancia de proyecto**: una pareja de importes del proyecto que no coinciden. Las tres parejas posibles son pedido de venta y albaranado de venta, pedido de compra y albaranado de compra, y ventas albaranadas e ingresos.
- **Estado de revisión**: Revisado o Pdte. Revisar, asociado al proyecto dentro de la empresa. Decide si una discrepancia sigue apareciendo entre los pendientes. No sustituye a los importes de la ficha.
- **Aviso del cuadro de mando**: la campanita del ejercicio elegido y la ventana con los proyectos que aún están pendientes de revisar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el cuadro de mando, la persona ve el número de proyectos pendientes de revisar sin abrir ninguna ficha.
- **SC-002**: Ese número coincide siempre con las filas de la ventana, y cada proyecto aparece una sola vez.
- **SC-003**: Desde la ventana, la persona llega a la ficha del proyecto en un solo paso.
- **SC-004**: Después de marcar Revisado, ese proyecto desaparece del número y de la ventana la próxima vez que se abre el cuadro de mando, aunque los importes no hayan cambiado.
- **SC-005**: Después de volver a Pdte. Revisar, el proyecto reaparece en el número y en la ventana si alguna de las tres parejas sigue siendo distinta.
- **SC-006**: Un proyecto cuyas tres parejas son iguales no aparece en la campanita ni en la ventana, sea cual sea el estado elegido antes.
- **SC-007**: Dos personas con acceso a la misma empresa y al mismo ejercicio ven el mismo número después de que una de ellas marca un proyecto como Revisado.

## Assumptions

- El cuadro de mando sigue siendo el de la empresa y el ejercicio elegidos. La campanita no mezcla empresas ni ejercicios.
- Entran los proyectos cuyo pedido de venta vigente pertenece a ese ejercicio. Los importes que se comparan son los de la ficha del proyecto, con su vida completa, no solo los documentos fechados dentro del ejercicio.
- La venta que se compara con los ingresos es lo albaranado de venta, no la base del pedido. El pedido ya tiene su propia pareja frente al albarán. Así, un pedido servido y no contabilizado se señala, y un pedido todavía no servido no se señala solo porque el ingreso aún no exista.
- El pedido de venta, lo albaranado de venta, el pedido de compra, lo albaranado de compra y los ingresos son las mismas cifras que ya muestra la ficha, con las mismas exclusiones de anulados y de abonos.
- Dos importes cuadran cuando son iguales, céntimo a céntimo. Cero frente a cero cuadra.
- Si a una pareja le falta un importe, esa pareja se omite. No se inventa un cero para forzar una discrepancia.
- Un proyecto sin ficha calculada queda fuera del aviso hasta que la ficha exista.
- Revisado no caduca solo. Un cambio posterior de los importes no vuelve a abrir el proyecto. Para que vuelva a la lista, la persona tiene que elegir Pdte. Revisar y, además, tiene que seguir habiendo alguna pareja distinta.
- El selector de la ficha está disponible también cuando el proyecto cuadra. En ese caso el estado se guarda, pero el proyecto no entra en el aviso.
- No se añade un permiso nuevo. Quien puede abrir la ficha puede cambiar el estado. Quien no puede ver una cifra no la usa para decidir si el proyecto le cuenta.
- La ventana informa de las parejas y lleva a la ficha. No es el sitio donde se marca Revisado.
