# Contrato de consulta: margen del pedido

Consulta de solo lectura. No tiene escritura sobre el origen.

## Entrada

- Persona autenticada.
- `CodigoEmpresa` asignado a esa persona.
- Periodo. Si no se envía, el año natural en curso.
- Permiso de pedidos de venta. El coste exige además pedidos de compra. Los ingresos exigen movimientos contables. Sin el permiso correspondiente, esa parte no se calcula y no se devuelve como cero.

## Pedidos incluidos

Un pedido entra si pertenece a la empresa, no está anulado y su fecha cae en el periodo. Sin fecha, entra cuando el ejercicio coincide con el año del periodo.

## Precio

Base imponible de la cabecera, sin impuestos. Si no existe, suma de las bases de las líneas. Un importe con impuestos distinto de la base no sustituye a la base.

## Coste

Suma sin impuestos de:

- todas las líneas de compra de la misma empresa y del mismo proyecto, con cualquier fecha;
- los apuntes de la misma empresa y proyecto cuya cuenta indique horas, mano de obra o personal, con cualquier fecha.

Esas dos cantidades se suman aunque describan la misma hora. Los demás apuntes no entran.

## Margen

Precio menos coste. El porcentaje es el margen dividido por el precio cuando el precio no es cero. Si el precio es cero, el porcentaje no se informa.

## Ingresos contables

Abonos menos cargos de las cuentas de ingreso del mismo proyecto y empresa, con cualquier fecha. No se aplican al precio, al coste ni al margen. Un apunte de horas no se informa aquí.

## Asignación

El coste y los ingresos se vinculan al pedido solo si el proyecto coincide con un único pedido no anulado de la empresa. En otro caso el resultado es pendiente de revisión y no un margen cerrado.

## Incompleto

Si falta un importe necesario, esa pieza no se suma y el resultado queda marcado como incompleto.

## Aislamiento

Ninguna fila de otra empresa entra en el precio, el coste, el margen ni los ingresos, aunque el número de proyecto sea igual.

## Salida de un pedido cerrado

- Identidad del pedido: empresa, ejercicio, serie y número.
- Proyecto.
- Precio de venta.
- Coste.
- Margen en importe y porcentaje, o porcentaje no aplicable.
- Ingresos contables.
- Marca de incompleto, si corresponde.

## Salida de un pendiente

- Motivo: sin proyecto, sin pedido vigente o proyecto compartido.
- Pedidos e imputaciones afectados, sin atribuirles un margen cerrado.
