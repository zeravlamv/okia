# Data Model: Jerarquía analítica

No se añade ninguna tabla. El orden de los niveles ya está guardado. El árbol y el grupo aparte se calculan al consultar y no se persisten.

## Nivel analítico

Ya existe. Cada uno de los cinco conceptos tiene una posición única.

- Código del concepto: canal, delegación, departamento, proyecto o sección.
- Posición: de 1 a 5. La posición 1 engloba a las demás.
- El perfil puede ocultar el concepto. Entonces no ocupa escalón.

## Pedido clasificado

Cada pedido no anulado del ejercicio queda en un solo sitio.

- Cierra margen cuando su proyecto corresponde a un único pedido no anulado de la empresa. Entra en el árbol.
- No cierra margen cuando no tiene proyecto o lo comparte con otro pedido vigente. Entra en el grupo aparte.
- Anulado: no entra en ningún sitio.
- Incompleto: cierra margen, pero le falta algún importe. Sigue en el árbol y marca incompletos a sus grupos.

Atributos usados para colocarlo en el árbol, en el orden de las posiciones visibles: canal, delegación, departamento, proyecto y sección. Cada valor tiene código y, si el maestro de la empresa lo tiene, descripción.

## Cifras de un pedido cerrado

- Ventas: base sin impuestos. Manda la cabecera. Si no existe, la suma de las bases de las líneas.
- Compras: bases de todas las líneas de compra del proyecto, con cualquier fecha.
- Gastos: apuntes del proyecto cuya cuenta indique horas, mano de obra o personal.
- Ingresos: abonos menos cargos de las cuentas de ingreso del proyecto.
- Margen: ventas menos compras menos gastos.

Compras más gastos es el coste ya definido para el pedido. Los ingresos no entran en el margen.

## Grupo analítico

Un valor de un nivel dentro de su grupo padre.

- Identidad: código del concepto, código del valor y texto visible. El texto es «código — descripción», solo el código si no hay descripción, o «Sin dato» si no hay código.
- Hijos: grupos del siguiente nivel visible. El último nivel no tiene hijos.
- Cifras: suma de la misma cifra en los hijos, o la del pedido si es el último nivel con un solo pedido cerrado. Una cifra no concedida no existe en el grupo.
- Incompleto: verdadero si él o alguno de sus hijos está incompleto.
- No incluye los pedidos del grupo aparte.

La cifra de un grupo es exactamente la suma de esa cifra en los grupos que engloba directamente.

## Grupo aparte

Un solo conjunto, fuera del árbol.

- Contiene los pedidos del ejercicio que no cierran margen.
- De cada uno muestra la identidad del pedido y el precio de venta.
- No muestra compras, gastos, ingresos ni margen.
- Sus ventas no se suman a ningún grupo analítico.

## Relaciones

- Una empresa y un ejercicio producen un árbol y, si hace falta, un grupo aparte.
- El pedido cerrado pertenece a un camino de grupos, uno por cada nivel visible.
- El pedido del grupo aparte no pertenece a ningún camino.
- Cambiar el orden de los niveles cambia los caminos. No cambia la suma de cada cifra en el conjunto de los pedidos cerrados.
