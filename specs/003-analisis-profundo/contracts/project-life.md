# Contrato de cálculo: vida del proyecto

Las cifras de la ficha salen de la vida guardada. Este contrato fija cómo se obtienen al actualizar y cómo se presentan al abrir. No cambia los indicadores del cuadro de mando ni las cifras de la jerarquía.

## Qué proyectos entran

Al actualizar un ejercicio entran los pedidos de venta no anulados de esa empresa que pertenecen a ese ejercicio por su fecha y, si no tienen fecha, por el año del ejercicio. Su proyecto es el código de proyecto. Si varios pedidos comparten código, la vida usa la fecha más antigua y la suma de las bases.

Un pedido anulado no crea vida. Un documento de otra empresa no entra.

## Albaranes de venta

- Se toman todos los albaranes de venta del proyecto, con cualquier fecha.
- La base es la de la cabecera. Si no existe, la suma de las bases de las líneas.
- Facturado y no facturado salen de la marca de facturación de la cabecera. Sin marca reconocible, queda «sin dato de facturación».
- Un abono guarda la base en negativo y conserva su marca de facturación.
- Un albarán anulado no entra.

## Progresión

- Albaranado = suma de los importes de los hitos, incluidos abonos y sin dato de facturación.
- Progresión = albaranado partido por la base del pedido. Si la base es cero o falta, el porcentaje es «No aplicable». Puede pasar de 100. Puede ser negativo si los abonos superan al resto.
- Facturado, no facturado y sin dato tienen cada uno su porcentaje sobre la misma base.
- La suma de esas tres partes es el albaranado.
- Pendiente de albaranar = base del pedido menos albaranado cuando el pedido es mayor. Si el albaranado es igual o mayor, el pendiente es cero.

## Compras

- Compras = suma de las bases de los albaranes de compra del proyecto.
- Cada albarán cae en el mes de su fecha. Sin fecha, se lista aparte y sí entra en el total.
- Un pedido de compra es comprometido solo cuando ningún albarán de compra guardado apunta a su ejercicio, serie y número.
- El comprometido no se suma a las compras ni a la barra mensual de compras.
- No se guarda un resto parcial del pedido de compra.

## Gastos

- Gastos = suma de los apuntes de gasto del proyecto.
- Cada apunte cae en el mes de su fecha. Sin fecha, se lista aparte y sí entra en el total.
- La cuenta de ingreso no entra. El cierre de ejercicio no entra.
- El detalle agrupa por código de cuenta. La descripción es la guardada del plan contable.

## Meses y barra

- El primer mes es el mes de la fecha de inicio.
- Si el albaranado cubre o supera la base del pedido y hay algún hito con fecha, la barra termina en la fecha del último hito.
- Si el pedido sigue descubierto, no hay hitos, o la base falta, la barra termina el día en que se abre la ficha.
- Si la fecha de inicio es posterior a ese día y el pedido sigue descubierto, la barra es solo la fecha de inicio.
- Todos los meses intermedios se muestran. Un mes sin movimiento conserva el albaranado acumulado y muestra compras y gastos vacíos.
- La gráfica de progresión acumula. La de compras y gastos muestra el mes, no el acumulado.

## Permisos

Si el perfil no puede ver una familia, esa parte no se calcula para él al abrir: no aparece y no se sustituye por cero. Lo guardado puede contenerla. Las familias son pedidos de venta, albaranes de venta, pedidos de compra, albaranes de compra y movimientos. El nombre del proveedor exige además poder ver proveedores. Sin ese permiso se ve el código.
