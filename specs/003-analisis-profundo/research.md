# Research: Análisis profundo

## Decision: La vida del proyecto se guarda al actualizar

**Decision**: Actualizar, para la empresa y el ejercicio elegidos, sigue guardando el resumen del cuadro de mando. Además sustituye la vida de cada proyecto cuyo pedido de venta no anulado entra en ese ejercicio. Esa vida incluye los albaranes, las compras y los gastos del proyecto con cualquier fecha. Abrir la ficha lee lo guardado. Si no hay vida guardada, se indica y no se calcula.

**Rationale**: La especificación exige ver varios ejercicios en la misma ficha y no volver a leer el origen al abrirla. El resumen actual está partido por ejercicio y por los cuatro primeros niveles. No conserva hitos, facturación, proveedor ni cuenta.

**Alternatives considered**: Leer el origen cada vez que se abre el proyecto. Se rechaza porque la ficha cambiaría sola y la actualización dejaría de ser el único momento de lectura. Guardar solo los documentos del ejercicio elegido se rechaza porque un pedido de 2024 con albaranes de 2025 y 2026 quedaría cortado.

## Decision: Una lectura por familia, no una por proyecto

**Decision**: En cada actualización se leen una vez los pedidos de venta, los albaranes de venta, los pedidos de compra, los albaranes de compra y los apuntes de los proyectos de ese ejercicio. Los apuntes se piden por bloques de proyectos, no con una consulta por proyecto. En memoria se reparten a cada vida.

**Rationale**: Un ejercicio puede tener más de mil proyectos. Repetir la consulta por cada uno alargaría la actualización sin cambiar el resultado.

**Alternatives considered**: Una consulta por proyecto y por tabla. Se rechaza por el número de idas al origen. Cargar todos los apuntes de la empresa y de todos los ejercicios se rechaza porque metería cuentas que no pertenecen a estos proyectos.

## Decision: El albarán de venta se clasifica con su marca de facturación

**Decision**: En la cabecera del albarán de venta, la marca de facturado decide la parte. El valor usado por el origen para «sí» es el de marcado (en esta instalación, −1). Cero es no facturado. Si la marca no está o no se reconoce, el albarán entra en el albaranado como «sin dato de facturación» y no se suma a ninguna de las dos partes. La marca de abono, con el mismo criterio de marcado, guarda la base en negativo.

**Rationale**: La especificación separa facturado y no facturado y pide que un abono reste. El origen ya trae esas dos marcas en la cabecera del albarán de cliente. La base que se usa es la de la cabecera y, si falta, la suma de las líneas.

**Alternatives considered**: Tratar cualquier valor distinto de cero como facturado. Se rechaza porque un valor desconocido se colaría en facturado. Dejar el abono como un albarán positivo se rechaza porque inflaría la progresión.

## Decision: La compra acumulada es el albarán de compra

**Decision**: La cifra de compras y la gráfica mensual suman la base de los albaranes de compra del proyecto, en el mes de su fecha. El pedido de compra solo se guarda como comprometido cuando ningún albarán de compra de la misma empresa apunta a su ejercicio, serie y número. El comprometido no entra en las compras. No se calcula el resto de un pedido ya albaranado en parte. La clave del albarán de compra es ejercicio, serie y número de albarán. El enlace al pedido, cuando existe, es otro dato de esa cabecera.

**Rationale**: La especificación prohíbe sumar dos veces el pedido y el albarán. En este origen la cabecera del albarán de proveedor se identifica por el albarán y puede guardar el pedido del que sale. Usar la clave de pedido como si fuera la del albarán mezclaría documentos.

**Alternatives considered**: Sumar las líneas de compra de cualquier fecha, como hace hoy la jerarquía. Se rechaza porque esta ficha habla de albaranes y de su fecha. Restar lo ya albaranado del pedido de compra se rechaza porque la especificación lo deja fuera.

## Decision: El gasto sigue la regla vigente y se parte por cuenta

**Decision**: Entra el apunte del proyecto que ya cuenta como gasto: grupo 6, o nombre de gasto, horas, mano de obra o personal, y que no sea una cuenta de ingreso. El grupo 7 es ingreso aunque el nombre mencione horas. El cierre de ejercicio no entra. El importe es cargo menos abono. La fecha es la del apunte. La cuenta muestra su código y la descripción del plan contable (`Cuenta`). Si hay reparto analítico, se usa la parte del proyecto, como en la jerarquía.

**Rationale**: La especificación pide el gasto por mes y por cuenta sin cambiar qué apunte es un gasto. La descripción ya se lee del plan contable.

**Alternatives considered**: Mostrar todas las cuentas del proyecto, incluidos impuestos y tesorería. Se rechaza porque la ficha llama gastos a los gastos, y el resto no debe cambiar esa cifra. Limitar los gastos a las cuentas de horas, como hace el árbol, se rechaza porque aquí el detalle pedido es por cuenta de gasto.

## Decision: La Gantt y las gráficas se dibujan en la página

**Decision**: La vista prepara los meses, los acumulados y la posición de cada hito. La plantilla dibuja la Gantt con barras e hitos y las cuatro gráficas con figuras en la propia página. No se añade una librería de gráficas. El día final de la barra, cuando el pedido sigue descubierto, es el día en que se abre la ficha. Los importes no dependen de ese día.

**Rationale**: La constitución admite HTML y JavaScript para gráficas. Dibujarlas en el servidor permite comprobar los textos y los importes en las pruebas. Una librería nueva no aporta una cifra distinta.

**Alternatives considered**: Incorporar una librería de gráficos o de Gantt. Se rechaza porque obliga a servir y mantener otro paquete para unas series que ya están calculadas. Calcular «hoy» durante Actualizar se rechaza porque la barra debe llegar al día de la visita y los importes deben seguir siendo los guardados.

## Decision: El nombre del proveedor sale de su ficha maestra

**Decision**: El nombre se lee de la ficha del proveedor de la misma empresa. El primer candidato es `RazonSocial` y el siguiente `Nombre`. Si no hay nombre, o si el perfil no puede ver proveedores, se muestra el código. La descripción de la cuenta vacía, o igual al código, también deja solo el código.

**Rationale**: El maestro de proveedores no tiene hoy la descripción mapeada en la aplicación. Los candidatos evitan fijar una columna que la ficha pueda no traer. El código basta para no ocultar la compra.

**Alternatives considered**: Exigir una sola columna de nombre. Se rechaza porque un cambio de nombre de columna dejaría la ficha sin compras. Ocultar el proveedor entero cuando falta el nombre se rechaza porque la especificación identifica por código.
