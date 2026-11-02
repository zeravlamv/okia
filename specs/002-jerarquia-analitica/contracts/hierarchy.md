# Contrato de cálculo: Jerarquía analítica

La consulta recibe la empresa, el ejercicio, los pedidos, las compras, los apuntes, las descripciones de los códigos, el orden de los niveles y los grupos de información concedidos. No escribe en el origen.

## Quién entra

- El periodo elige los pedidos por su fecha. Si no tienen fecha, por el año de su ejercicio.
- Solo entra la empresa elegida.
- El pedido anulado no produce fila.
- El pedido con proyecto único entre los no anulados de la empresa cierra margen.
- El pedido sin proyecto, o cuyo proyecto comparten varios pedidos vigentes, va al grupo aparte.

## Cifras de un pedido que cierra margen

- Ventas: base de la cabecera sin impuestos. Si no existe, suma de las bases de las líneas. Un importe ausente no se cuenta como cero y el pedido queda incompleto.
- Compras: suma de las bases de todas las líneas de compra de ese proyecto, con cualquier fecha. Incluye material y líneas de horas.
- Gastos: apuntes de ese proyecto cuya cuenta indique horas, mano de obra o personal. No son ingresos ni compras.
- Si la misma hora está en una línea y en un apunte, la línea suma en compras y el apunte suma en gastos.
- Ingresos: abonos menos cargos de las cuentas de ingreso. No se suman ni se restan a las otras cifras.
- Margen: ventas menos compras menos gastos.

Compras más gastos coinciden con el coste que ya muestra la consulta de ese pedido.

## Árbol

- Los niveles concedidos se ordenan por la posición guardada.
- Cada pedido cerrado recorre ese orden. Un código vacío es el grupo «Sin dato» de su padre. Dos códigos distintos no se fusionan.
- Cada cifra del padre es la suma de esa cifra en sus hijos directos.
- El margen del padre también cumple ventas menos compras menos gastos.
- Si un pedido está incompleto, su grupo y todos los que lo engloban quedan incompletos.
- Una cifra no concedida no aparece. No se envía como cero.
- El grupo aparte no es hijo de ningún nivel. Sus ventas no entran en las sumas del árbol.

## Lo que no cambia

- El indicador de ventas del panel sigue contando todos los pedidos no anulados del ejercicio.
- El indicador de compras del panel sigue contando las compras con fecha en el ejercicio. No es la cifra de compras de la jerarquía.
- La consulta de cada pedido conserva su precio, su coste, su margen, su porcentaje y sus ingresos.
