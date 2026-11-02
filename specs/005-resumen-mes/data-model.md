# Modelo de datos: Resumen del mes

No se añade ninguna tabla. El resumen es una lectura de las fichas ya guardadas de la empresa elegida. El origen comercial no recibe datos ni se consulta al abrir el mes.

## De dónde sale cada cifra

| Cifra del resumen | Lectura |
|-------------------|---------|
| Proyectos del mes | Cada ficha con un pedido de venta guardado cuya fecha cae en el mes y en el ejercicio. Una ficha por proyecto, aunque tenga dos pedidos en el mismo mes. |
| Pedido de cliente | La base de pedido ya guardada en la ficha. |
| Albaranes de cliente | La suma de los hitos de albarán de venta de esa ficha. |
| Pedidos de compra | La suma de los pedidos de compra guardados en la ficha, cubiertos o comprometidos. |
| Albaranes de compra | La suma de los albaranes de compra guardados en la ficha. |
| Gastos | La suma de los gastos guardados en la ficha. |

Esas sumas incluyen documentos de cualquier fecha. El mes solo decide qué fichas entran.

Si la ficha no tiene los pedidos desglosados y solo tiene fecha de inicio, entra en el mes de esa fecha cuando el año coincide con el ejercicio.

## Qué se calcula al abrir y no se guarda

- El mes seleccionado y si está cerrado.
- Los cinco totales, el número de proyectos y el aviso de ficha incompleta.
- El margen y su porcentaje.
- El pendiente de albaranar de venta, sobre los totales del mes.
- El pendiente de albaranar de compra, por proyecto y luego sumado.
- Los otros meses del ejercicio en los que la misma ficha también entra.
- El dibujo de las tres gráficas.

## Reglas de validez

- La lectura filtra por la empresa elegida. Un proyecto con el mismo código en otra empresa no entra.
- Un pedido anulado no está guardado y no coloca la ficha en un mes.
- Una ficha sin fecha de pedido no entra en ningún mes.
- Un importe vacío no se suma y el mes queda incompleto. No se guarda un cero en su lugar.
- La misma ficha no se suma dos veces dentro del mismo mes.
- Si la ficha entra en dos meses del ejercicio, se suma entera en cada uno y la fila nombra los otros meses.
- El albarán de compra no se suma al gasto ni se resta en el margen.
- Consultar el mes no crea, no modifica y no borra fichas, cierres ni documentos.
- Un mes sin fichas no tiene totales. La pantalla dice que no hay proyectos calculados.

## Entidades que ya existen y no cambian

- **Ficha del proyecto**: una por empresa y proyecto. Aporta la base del pedido, la fecha de inicio y si está incompleta.
- **Pedido de venta guardado**: fecha y base que deciden el mes. Cuelga de la ficha.
- **Hito de albarán, compra y gasto**: cuelgan de la ficha y alimentan los otros cuatro totales.
- **Cierre de mes**: dice si el mes está cerrado. El resumen lo lee y no lo cambia.
