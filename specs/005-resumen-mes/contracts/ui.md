# Contrato de pantalla: Resumen mes

## Menú

Quien ya consulta la empresa ve **Resumen mes** en el menú, junto al cuadro de mando y al margen de pedidos. Abrirlo no cambia la empresa ni el ejercicio.

## Mes

Se muestran los doce meses del ejercicio, con su nombre. Uno está seleccionado.

Si no se ha pedido un mes, o el pedido no es un mes del 1 al 12, queda seleccionado el mes de hoy cuando el ejercicio es el año en curso, y enero en cualquier otro ejercicio.

Elegir otro mes vuelve a pintar la misma pantalla con ese mes. No pide confirmación y no actualiza.

Si el mes está cerrado, se lee que está cerrado y que las cifras son las de la última ficha guardada.

## Ficha del mes

La cabecera muestra el mes, el ejercicio y los totales visibles.

Debajo, una fila por proyecto: el código del proyecto y los cinco importes de resumen que el perfil puede ver. La fila abre la ficha de ese proyecto.

No hay líneas, ni documentos, ni el desglose analítico del proyecto.

Si el proyecto también entra en otros meses del ejercicio, la fila nombra esos meses.

Si alguna ficha está incompleta, el mes lo dice. Un importe vacío no se muestra como cero.

Si no hay proyectos calculados, la pantalla lo dice y remite a Actualizar. No muestra totales a cero.

## Indicadores

Se leen el número de proyectos, los cinco totales, el margen, el porcentaje cuando existe, el pendiente de albaranar de venta y el pendiente de albaranar de compra.

El margen y su porcentaje solo aparecen si se pueden ver los albaranes de cliente y los gastos. El pendiente de venta solo si se pueden ver el pedido y los albaranes de cliente. El pendiente de compra solo si se pueden ver los pedidos y los albaranes de compra.

Un grupo no concedido quita su columna, su total y su indicador. No deja un cero en su sitio.

Los importes usan punto de miles, coma decimal, dos decimales y la moneda de la empresa. Si no tiene moneda, el euro. Quedan alineados a la izquierda.

## Gráficas

Las tres gráficas usan los mismos importes que la ficha y omiten lo que el perfil no puede ver.

1. **Totales.** Una barra por cada total visible, con su importe.
2. **Composición.** El centro es el pedido de cliente. Las partes son los albaranes de cliente, los gastos y el margen cuando es positivo. Si el margen es negativo, se lee junto a la gráfica y no ocupa una parte.
3. **Proyectos.** Una fila por proyecto, con su albaranado de cliente y su gasto, sin líneas de documentos.

Si una gráfica se queda sin cifras visibles, no se dibuja.
