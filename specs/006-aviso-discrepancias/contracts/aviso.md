# Contrato del aviso: Discrepancias pendientes

## Entrada

La empresa elegida, el ejercicio elegido y los grupos que la persona puede ver.

No recibe códigos de proyecto sueltos. No lee el origen.

## Qué proyectos se miran

Los de [data-model.md](../data-model.md): fichas de esa empresa con pedido de venta en el ejercicio.

## Parejas visibles

| Pareja | Hace falta ver |
|--------|----------------|
| Pedido de venta y albaranado de venta | Pedidos de venta y albaranes de venta |
| Pedido de compra y albaranado de compra | Pedidos de compra y albaranes de compra |
| Albaranado de venta e ingresos | Albaranes de venta y movimientos contables |

Si falta uno de los dos grupos, la pareja no existe para esa persona.

## Pendiente

Un proyecto está pendiente cuando el estado es Pdte. Revisar y al menos una pareja visible tiene los dos importes y no son iguales.

El resultado es una lista, ordenada por el código del proyecto, sin repetir proyectos. Cada elemento trae:

- el código del proyecto
- el cliente, si la ficha lo tiene
- el estado
- las parejas que no cuadran, cada una con su nombre y sus dos importes

El número del aviso es la longitud de esa lista.

## Fuera de la lista

- Parejas iguales, también cero con cero.
- Parejas omitidas por un importe vacío.
- Proyectos en Revisado.
- Proyectos de otra empresa o de otro ejercicio.
- Proyectos sin ficha.

## Guardar el estado

La ficha acepta solo Pdte. Revisar o Revisado, para un proyecto de la empresa elegida que ya tiene ficha.

Cualquier otro valor no se guarda.

Guardar no cambia importes, no lee el origen y no marca otros proyectos.

Después de guardarlo, la misma regla del pendiente vuelve a decidir si el proyecto entra en la lista.
