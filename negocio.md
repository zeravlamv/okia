# Reglas de negocio OKIA

Estas reglas mandan sobre la frase de margen bruto y margen neto escrita al principio de `constitution.md`. Salen de la especificación aclarada el 2026-10-30. El 2026-10-31 se separan el control comercial y el control contable.

## Qué se consulta

OKIA lee pedidos, compras, apuntes y maestros. No los crea, no los modifica y no los anula.

Cada pedido de venta no anulado es una operación. Su proyecto es el número de pedido. Solo se cruzan filas de la misma empresa.

Entran los pedidos pendientes, servidos y facturados. Los anulados no entran. Si un proyecto solo pertenece a un pedido anulado, sus imputaciones quedan sin asignar.

## Precio, coste y margen

El precio de venta es la base del pedido, sin impuestos. Manda la base de la cabecera. Si no existe, se suman las bases de las líneas.

El coste del proyecto son los gastos de AnaMovimientos de ese proyecto. El grupo 60 entra: es el albarán de compra ya contabilizado. También entra el resto del grupo 6, o una cuenta cuyo nombre indique gasto, horas, mano de obra o personal. Una cuenta de ingreso no es coste. Una cuenta del grupo 7 es ingreso aunque su nombre mencione horas.

El importe y los niveles son los de la fila. Si el apunte no tiene filas vigentes, entra una vez con los niveles escritos en el propio apunte. La base del albarán de compra no se suma otra vez.

El margen del cuadro de mando es los ingresos menos los gastos. El porcentaje se calcula sobre los ingresos. Si los ingresos son cero, el porcentaje no aplica. El margen neto de la ficha es lo albaranado menos los gastos.

## Dos controles

Hay dos controles y no se mezclan.

El control comercial son los pedidos y los albaranes de venta y de compra. El importe es la base, sin impuestos. El departamento y la sección son los del documento. Sirven para la progresión, lo pendiente de albaranar, lo pendiente de facturar y lo comprometido. Un pedido de compra sin albarán es comprometido y no es coste.

El control contable es AnaMovimientos, unido a Movimientos por CabPosicion = MovPosicion. Una fila con borrado no entra. El asiento de cierre del ejercicio no entra. El coste de un proyecto son los gastos de esas filas. El albarán de compra contabilizado ya está en ese gasto y no se vuelve a contar. La analítica de costes agrupa solo esas filas, por el canal, la delegación, el departamento, el proyecto y la sección que la fila ya trae. No repite el pedido ni los albaranes.

## Ingresos contables

Los ingresos del proyecto son los abonos menos los cargos de sus cuentas de ingreso. Una cuenta del grupo 7 es ingreso aunque su nombre mencione horas: esas horas son venta. El apunte de horas que es coste es el que no pertenece a una cuenta de ingreso, y entra por AnaMovimientos.

## Cruce

El coste y los ingresos pertenecen a un pedido solo cuando su proyecto corresponde a un único pedido no anulado de la empresa. Si el pedido no tiene proyecto, si el proyecto no tiene pedido vigente o si lo comparten varios pedidos vigentes, el caso queda pendiente de revisión y no cierra un margen.

## Periodo

El periodo por defecto es el año natural en curso. Un pedido entra por su fecha. Si no tiene fecha, entra por el año de su ejercicio. El periodo no recorta el coste ni los ingresos del proyecto.

Un mes de un ejercicio se puede cerrar para una empresa. Sin esa marca, el mes está abierto. Actualizar solo sustituye los proyectos cuyos pedidos de venta de ese ejercicio caen en meses abiertos. El mes del proyecto es el de la fecha de su pedido de venta. Si algún pedido vigente cae en un mes cerrado, el proyecto entero queda fuera de esa actualización y conserva la ficha que ya tenía. Cerrar o reabrir no lee el origen.

## Indicadores del cuadro de mando

De la empresa y el ejercicio elegidos, el panel muestra seis valoraciones. El importe es la base, sin impuestos. Manda la base de la cabecera. Si no existe, se suman las bases de las líneas. Un documento anulado no entra.

- Pedidos de venta.
- Pedidos de compra. Valora el pedido al proveedor. No es el coste del pedido de venta.
- Albaranes de venta y albaranes de compra. Entran por la fecha del albarán y, si no tiene fecha, por su ejercicio. En el origen se identifican por ejercicio, serie y número de albarán.
- Ingresos: abono menos cargo de los movimientos de cuentas de ingreso. Cada movimiento entra una vez, tenga o no proyecto.
- Gastos: cargo menos abono de las cuentas de gasto, grupo 60 incluido. Un movimiento de ingreso no entra. Cada movimiento entra una vez.

El asiento cuyo comentario indica el cierre del ejercicio no es un ingreso ni un gasto. Anula esas cuentas y no entra en el panel ni en el árbol.

El margen del panel es sus ingresos menos sus gastos, y el del árbol es los ingresos menos los gastos de cada grupo. En el árbol, la venta usa el proyecto del pedido de venta. El gasto es la fila de AnaMovimientos y entra en los niveles de esa fila. La línea del pedido o del albarán de compra no suma un segundo coste. Los ingresos son los apuntes de ingreso del ejercicio. Si el apunte tiene filas, cada fila suma su importe. Si no tiene filas, usa los niveles del propio apunte. Si trae canal, delegación y departamento y el proyecto viene vacío, toma el proyecto del único pedido de venta o de compra con esos tres códigos. Si hay varios o ninguno, queda sin proyecto. No se reparte. Un apunte sin ninguno de esos niveles se queda en el panel. El panel no muestra el número de clientes, proveedores ni artículos.

El cuadro de mando y la página de margen leen un resumen guardado por empresa y ejercicio. No se vuelve a calcular al abrir o recargar la página. El botón Actualizar, junto a Aplicar, lee el origen y sustituye ese resumen. El resumen analítico guarda los cuatro primeros niveles del orden configurado. La sección, que es el quinto, no entra.

## Desglose analítico del movimiento

AnaMovimientos se une a Movimientos por CabPosicion = MovPosicion. Cada fila vigente ya trae su canal, su delegación, su departamento, su proyecto, su sección y su importe. El árbol suma ese importe en esos niveles y no vuelve a repartir el apunte de cabecera. Una fila borrada no entra. Los indicadores de ingresos y gastos del panel cuentan el movimiento completo, una vez.

## Acceso

Cada persona solo ve sus empresas. Cada perfil solo ve sus grupos de información. Un grupo no concedido no se muestra como cero. Recordar el acceso no guarda la contraseña. El enlace de recuperación dura 60 minutos y sirve una vez. La sesión mantenida dura 30 días.

## Jerarquía analítica

El orden de los niveles agrupa de arriba abajo. Cada grupo muestra la venta del pedido, el gasto, los ingresos y el margen. La venta sigue el pedido de venta. El gasto sigue la fila de AnaMovimientos. El margen de cada grupo es sus ingresos menos sus gastos. El porcentaje va al lado del importe y se alinea a la izquierda de su columna.

Un pedido que no cierra margen se muestra fuera de la jerarquía, con su precio de venta y sin margen. Esas ventas no se suman a los niveles.

## Ficha del proyecto

La ficha de un proyecto empieza en la fecha del pedido de venta y sigue por los meses de su vida, aunque los albaranes o los apuntes caigan en otros ejercicios. Si hay pedido, la cabecera muestra esa fecha y el cliente del pedido. La progresión es lo albaranado respecto a la base del pedido. Lo facturado y lo no facturado se ven por separado. La desviación es lo albaranado menos el pedido. El margen neto es lo albaranado menos los gastos. Un pedido de compra sin albarán queda como comprometido y no se suma al coste. Un albarán de compra contabilizado tampoco se suma: ya está en el gasto. La analítica de costes solo lee AnaMovimientos. Cada fila suma su importe en su departamento y su sección. Si no hay fila, usa el apunte una vez. El pedido y los albaranes no entran en esa tabla. El desglose se guarda al pulsar Actualizar. El cierre de ejercicio no entra en el coste. Abrir la ficha no vuelve a leer el origen: hace falta Actualizar.

## Resumen del mes

Resumen mes separa el comercial de la analítica. El pedido de venta y el de compra son los fechados en el mes. El albarán de venta y el de compra son los creados en el mes, aunque el pedido sea de otro: un albarán de marzo de un pedido de febrero entra en marzo. El margen de las tarjetas es esos albaranes de venta menos los gastos. La analítica toma los proyectos cuyo pedido cae en el mes y, de ellos, los apuntes del grupo 6 y del grupo 7, aunque el asiento sea de otro mes. El grupo 6 son los gastos, incluido el 60. El grupo 7 son los ingresos. El margen analítico es ingresos menos gastos. El listado plegado sigue siendo la ficha completa de cada proyecto del mes. Abrir el resumen no lee el origen. Los ingresos del grupo 7 se guardan al pulsar Actualizar.

## Aviso de discrepancias

El cuadro de mando avisa, con una campanita, de los proyectos del ejercicio cuya ficha no cuadra y siguen en Pdte. Revisar. Compara el pedido de venta con lo albaranado y el pedido de compra con lo albaranado. No compara los ingresos. Un proyecto cuenta una vez. Revisado lo saca de la campanita hasta que la persona vuelva a elegir Pdte. Revisar. El botón de al lado abre esos proyectos revisados que siguen sin cuadrar. Abrir el aviso no lee el origen. Actualizar conserva el estado.

## Importes

Se muestran con punto de miles, coma decimal y dos decimales, en la moneda de la empresa. Si la empresa no tiene moneda, se usa el euro. Ejemplo: 2.447.563,88 EUR. Una pieza sin importe no se suma y el resultado queda incompleto.
