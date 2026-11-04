# Research: Aviso de discrepancias

## Decision: El aviso lee las fichas ya guardadas

**Decision**: Un proyecto entra en el ejercicio cuando su ficha tiene un pedido de venta guardado con fecha en ese ejercicio. Si la ficha todavía no guarda los pedidos uno a uno, entra por la fecha de inicio cuando el año coincide. Los importes que se comparan son los de la ficha completa, con cualquier fecha. Abrir el cuadro de mando no lee el origen y no pulsa Actualizar. Un proyecto sin ficha no entra en el número.

**Rationale**: La especificación limita el aviso a la empresa y al ejercicio, y prohíbe modificar pedidos, albaranes e ingresos. La ficha ya guarda la base del pedido, los albaranes, las compras y los ingresos. El resumen del mes ya usa esa misma fecha para colocar el proyecto.

**Alternatives considered**: Volver a leer el origen al abrir el cuadro. Se rechaza porque alarga la página y la especificación no lo pide. Comparar solo los documentos fechados dentro del ejercicio se rechaza porque la ficha es la vida completa y el aviso tiene que coincidir con ella. Usar el resumen del cuadro, que es por niveles analíticos, se rechaza porque el aviso es por proyecto.

## Decision: Las tres parejas salen de la ficha y un importe vacío no es un cero

**Decision**: La primera pareja es la base del pedido de venta frente a la suma de los albaranes de venta. La segunda es la suma de los pedidos de compra, cubiertos o todavía comprometidos, frente a la suma de los albaranes de compra. La tercera es esa misma suma de albaranes de venta frente a la suma de los ingresos del proyecto. Si no hay filas, el lado suma cero. Si la base del pedido está vacía, o alguna fila que entra en el lado tiene el importe vacío, esa pareja se omite y no mete sola al proyecto en el aviso. Dos importes cuadran cuando son iguales al céntimo, también si los dos son cero. Una diferencia en cualquier sentido es discrepancia.

**Rationale**: La especificación nombra esas tres parejas y dice que la venta frente al ingreso es lo albaranado, no el pedido. El pedido de compra comprometido ya forma parte del total de pedidos de compra de la ficha. Inventar un cero cuando falta un importe marcaría proyectos incompletos como si no cuadraran.

**Alternatives considered**: Comparar el pedido de venta con los ingresos. Se rechaza porque la especificación reserva esa pareja al albaranado y el pedido ya tiene la suya. Restar solo el pendiente de albaranar, que es cero cuando el albarán supera el pedido, se rechaza porque una diferencia al alza también es discrepancia. Dejar fuera el pedido de compra comprometido se rechaza porque entonces un pedido sin albarán no avisaría.

## Decision: El estado es de la ficha y Actualizar lo conserva

**Decision**: La ficha guarda dos estados, Pdte. Revisar y Revisado. Si nadie lo ha cambiado, es Pdte. Revisar. El proyecto entra en la campanita solo cuando tiene alguna pareja visible distinta y el estado es Pdte. Revisar. Revisado no se reabre solo aunque cambien los importes. Actualizar borra la ficha y crea otra: antes de borrarla se recuerda el estado de cada proyecto y la ficha nueva lo recupera. Un recálculo que no borra la ficha tampoco toca el estado.

**Rationale**: La especificación dice que Revisado da por buena la discrepancia hasta que la persona lo cambie, y que todas las personas con acceso ven el mismo efecto. Si el estado viviera solo en la pantalla, se perdería. Si se guardara sin copiarlo, el siguiente Actualizar lo devolvería a Pdte. Revisar.

**Alternatives considered**: Una tabla aparte solo para el estado. Se rechaza porque el estado es uno por proyecto y por empresa, que es justo la ficha, y habría que mantenerla al borrar. Reabrir Revisado cuando los importes cambian se rechaza porque la especificación dice que no vuelve solo. Guardar el estado por persona se rechaza porque la especificación lo comparte.

## Decision: Cada persona ve solo las parejas de sus grupos

**Decision**: La pareja del pedido y el albarán de venta se usa si se pueden ver los dos. La de compra, si se pueden ver el pedido y el albarán de compra. La del albaranado y los ingresos, si se pueden ver los albaranes de venta y los movimientos. Una pareja no concedida no se lista y no cuenta como cero. Si las parejas visibles cuadran, el proyecto no entra en su campanita. El estado guardado es el mismo para todo el mundo.

**Rationale**: La constitución y la especificación impiden mostrar un cero en el lugar de un grupo no concedido. El estado no es una cifra del origen: quien abre la ficha puede cambiarlo.

**Alternatives considered**: Exigir un permiso nuevo para el aviso o para el selector. Se rechaza porque la especificación no lo pide y quien ya abre la ficha puede marcarla. Ocultar la campanita entera si falta un solo grupo se rechaza porque las otras parejas seguirían siendo útiles.

## Decision: La campanita y la ventana están solo en el cuadro de mando

**Decision**: La campanita se ve también cuando el cuadro todavía no tiene resumen, porque el aviso no depende de ese resumen. Con cero proyectos sigue visible y la ventana dice que no hay pendientes. Cada fila muestra el código, el cliente si la ficha lo tiene, las parejas que no cuadran y los dos importes. Abrir la fila va a la ficha. El selector está en la ficha, no en la ventana. Guardar el estado no lee el origen. Un valor que no sea uno de los dos estados no se guarda.

**Rationale**: La especificación coloca el aviso en el cuadro y el cambio de estado en la ficha. El cliente ya está en la ficha; el nombre del proyecto no, y leer el maestro al abrir repetiría una consulta al origen. Cero visible confirma que el aviso se ha calculado.

**Alternatives considered**: Poner la campanita también en Resumen mes. Se rechaza porque la especificación nombra el cuadro de mando. Leer la tabla de proyectos para el nombre se rechaza porque abre el origen en una consulta. Marcar Revisado desde la ventana se rechaza porque la especificación deja ese cambio en la ficha.
