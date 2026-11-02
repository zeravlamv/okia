# Contrato de lectura: resumen del mes

Abrir Resumen mes no lee el origen y no sustituye fichas. Parte de la empresa y del ejercicio ya elegidos, y de un mes del 1 al 12.

## Quién entra

Entran las fichas de esa empresa con al menos un pedido de venta guardado fechado en ese mes y ese ejercicio. La ficha entra una vez.

Una ficha antigua, sin pedidos desglosados, entra si su fecha de inicio cae en ese mes y ese ejercicio.

No entra una ficha de otra empresa, un pedido anulado, ni una ficha sin fecha.

## Importes de cada fila

| Importe | Regla |
|---------|--------|
| Pedido de cliente | Base de pedido de la ficha. |
| Albaranes de cliente | Suma de los hitos de venta. |
| Pedidos de compra | Suma de los pedidos de compra guardados. |
| Albaranes de compra | Suma de los albaranes de compra guardados. |
| Gastos | Suma de los gastos guardados. |

Un importe vacío no entra en la suma. La fila y el mes quedan incompletos.

Si la ficha tiene pedidos del mismo ejercicio en otros meses, la fila lo dice con el nombre de esos meses. Los importes siguen siendo los de la ficha entera.

## Totales e indicadores

Cada total es la suma del importe homónimo de las filas. Una ficha no se suma dos veces en el mismo mes.

| Indicador | Regla |
|-----------|--------|
| Proyectos | Número de filas. |
| Margen | Albaranes de cliente menos gastos. |
| Porcentaje | Margen sobre albaranes de cliente. Si los albaranes son cero, no hay porcentaje. |
| Pendiente de albaranar de venta | Pedido de cliente menos albaranes de cliente cuando el pedido es mayor. Si no, cero. |
| Pendiente de albaranar de compra | En cada ficha, lo que de cada pedido de compra aún no cubre su albarán. Luego se suma. |

El margen negativo se conserva. El albarán de compra no se resta en el margen.

## Qué no hace esta lectura

- No abre ni cierra el mes.
- No pulsa Actualizar.
- No reparte una ficha entre meses.
- No inventa el número de proyectos que todavía no tienen ficha.
- No devuelve líneas ni documentos.
