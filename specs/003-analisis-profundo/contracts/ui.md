# Contrato de pantalla: ficha del proyecto

La ficha es una pantalla propia. No sustituye el cuadro de mando, la jerarquía ni el margen de cada pedido. Se abre desde el proyecto visible en la jerarquía de la empresa elegida.

## Al abrir

- Si esa empresa no tiene guardada la vida de ese proyecto, se indica que hay que pulsar Actualizar. No aparecen cifras ni gráficas.
- Si existe, se muestran la fecha de inicio, los ejercicios que tocan los documentos fechados y los indicadores concedidos: base del pedido, albaranado, progresión, facturado, no facturado, sin dato de facturación, pendiente de albaranar, compras y gastos.
- Los importes usan punto de miles, coma decimal y dos decimales, alineados a la izquierda. El porcentaje usa coma decimal y dos decimales. La moneda es la de la empresa, o el euro si no tiene.
- Una cifra no concedida no ocupa un hueco ni un cero.
- La marca de incompleto aparece cuando falta algún importe.

## Gantt

- Un carril del proyecto, desde el inicio hasta el final de la barra definido en el contrato de cálculo.
- Un hito por albarán de venta con fecha. Facturado, no facturado y sin dato se distinguen.
- Un hito por albarán de compra con fecha, con el proveedor.
- El pedido de compra comprometido, si tiene fecha, se marca como comprometido y no como compra.
- Los documentos sin fecha no se colocan en la barra. Se listan debajo como «Sin fecha».

## Gráficas

Solo se dibuja una gráfica cuando hay datos concedidos para ella.

- Progresión mensual acumulada: albaranado, separado en facturado, no facturado y sin dato, con la base del pedido como referencia y el porcentaje de cada mes.
- Compras y gastos de cada mes, en el importe de ese mes.
- Compras por proveedor, de mayor a menor.
- Gastos por cuenta, de mayor a menor, con código y descripción.

El importe de una gráfica es el de la tabla correspondiente.

## Tablas

- Hitos, de la fecha más antigua a la más reciente: fecha, importe, facturación y porcentaje acumulado sobre el pedido.
- Compras por proveedor y por mes.
- Gastos por cuenta y por mes.
- Comprometidos, aparte de las compras, con proveedor, fecha e importe.

## Actualizar y filtros

- El botón Actualizar sigue junto a Aplicar y guarda la vida de los proyectos de la empresa y el ejercicio elegidos.
- Cambiar de empresa sin actualizar no muestra la vida de la empresa anterior.
- Abrir la ficha, cambiar de gráfica o recorrer una tabla no vuelve a leer el origen.
- La fecha de la última actualización de esa vida se muestra junto a Actualizar, en texto pequeño, cuando la vida existe.

## Texto visible

- Proveedor o cuenta con código y descripción: `código — descripción`.
- Sin descripción, o descripción igual al código: el código.
- Porcentaje que no aplica: «No aplicable».
- Facturación desconocida: «Sin dato de facturación».
- Pedido de compra aún no albaranado: «Comprometido».
