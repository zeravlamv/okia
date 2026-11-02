# Contrato de pantalla: Jerarquía analítica

La jerarquía vive en el cuadro de mando de la empresa y el ejercicio elegidos. Sustituye las cinco listas de canal, delegación, departamento, proyecto y sección. No sustituye los indicadores generales ni la consulta de cada pedido.

## Al abrir

- Se ve el primer nivel concedido.
- Cada grupo de ese nivel muestra su código y su descripción, las cifras concedidas y, si corresponde, la marca de incompleto.
- No se ven los niveles inferiores hasta abrir un grupo.
- Si no hay ningún nivel concedido, no aparece la jerarquía.
- Si no hay pedidos que cierren margen, no aparecen grupos analíticos con cifras inventadas.

## Al abrir un grupo

- Aparece solo el nivel siguiente que ese grupo engloba.
- Los importes del grupo abierto no cambian.
- Se pueden dejar abiertos varios grupos a la vez.
- El último nivel no ofrece otro nivel dentro.

## Grupo aparte

- Aparece fuera del árbol.
- Lista cada pedido que no cierra margen con su identidad y su precio de venta.
- No muestra compras, gastos, ingresos ni margen.
- Esas ventas no se suman a los grupos del árbol.
- Si no hay pedidos en esa situación, el grupo aparte no aparece.

## Permisos y filtros

- Cambiar de empresa o de ejercicio reconstruye el árbol y el grupo aparte. No queda ninguna cifra de la selección anterior.
- Un nivel no concedido no ocupa una fila.
- Una cifra no concedida no ocupa una columna ni un cero.
- Quien no puede ver las ventas no ve el precio del grupo aparte.

## Texto visible

- Con código y descripción: `01 — TECH`.
- Sin descripción: el código.
- Sin código: «Sin dato».
- Importes con dos decimales, en la moneda de la empresa o en euros.
