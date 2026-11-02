# Research: Resumen del mes

## Decision: El mes se lee de los pedidos ya guardados en la ficha

**Decision**: Un proyecto entra en un mes del ejercicio cuando la ficha guardada tiene un pedido de venta, no anulado, con fecha en ese mes y ese ejercicio. Si la ficha guarda varios pedidos, se usa la fecha de cada uno. Si la ficha es anterior y solo guarda una fecha de inicio, esa fecha coloca el proyecto en un solo mes. Un pedido anulado no se guarda, así que no coloca el proyecto. Sin fecha, el proyecto no entra en ningún mes.

**Rationale**: Abrir Resumen mes no puede leer el origen. La ficha ya guarda cada pedido de venta del ejercicio con su fecha y su base. Esa fecha es la misma que usa el cierre para decir «proyecto de ese mes».

**Alternatives considered**: Volver a leer los pedidos al abrir el mes. Se rechaza porque la especificación prohíbe leer el origen y pulsar Actualizar al consultar. Usar solo la fecha de inicio de la ficha se rechaza cuando hay varios pedidos: un pedido de marzo desaparecería si el primero fue en enero. Agrupar por la fecha del albarán o del gasto se rechaza porque la especificación fija el mes en el pedido de venta.

## Decision: Cada mes muestra la ficha entera, una sola vez

**Decision**: Los cinco importes de la fila son los de la ficha completa: la base de sus pedidos, la suma de sus albaranes de venta, la suma de sus pedidos de compra, la suma de sus albaranes de compra y la suma de sus gastos, con cualquier fecha. Si el proyecto tiene dos pedidos del ejercicio en el mismo mes, la fila sale una vez. Si esos pedidos caen en meses distintos, el proyecto sale en cada uno de esos meses con la misma ficha, y la fila nombra los otros meses. El total del mes suma esa ficha una vez por cada proyecto de la lista.

**Rationale**: La especificación pide agrupar los proyectos del mes y presentar la ficha ya calculada, no la parte de documentos fechada en el mes. Avisa el caso de dos meses para que, al recorrer el ejercicio, no se sumen sin querer.

**Alternatives considered**: Partir la ficha y sumar solo los documentos del mes. Se rechaza porque deja de ser la ficha agrupada y cambia el margen respecto a la ficha del proyecto. Dejar el proyecto solo en el mes del primer pedido se rechaza porque un pedido posterior del ejercicio no aparecería en su mes.

## Decision: No hay tabla nueva

**Decision**: El resumen, los indicadores y las gráficas se calculan al abrir. No se guardan. Un importe vacío no se convierte en cero: no entra en la suma y el mes queda incompleto. Un proyecto que nunca se ha calculado no se puede nombrar sin leer el origen. El mes sin fichas dice que no hay proyectos calculados y remite a Actualizar. No inventa un recuento de proyectos ausentes.

**Rationale**: Las fichas ya están guardadas por empresa y proyecto. Otra tabla repetiría importes y envejecería con el siguiente Actualizar. El origen es la única lista de proyectos aún no calculados, y esta pantalla no lo consulta.

**Alternatives considered**: Guardar un resumen por mes al actualizar. Se rechaza porque el cierre ya impide reescribir unos proyectos y no otros, y el resumen se puede rehacer al leer. Consultar el origen para contar los que faltan se rechaza porque abre la pantalla a una lectura larga y la especificación la deja fuera.

## Decision: El margen y los pendientes siguen las dos reglas de la especificación

**Decision**: El margen del mes es el total de albaranes de cliente menos el total de gastos. El porcentaje usa los albaranes de cliente. Si ese total es cero, no hay porcentaje. El pendiente de albaranar de venta es la diferencia de los totales del mes cuando el pedido es mayor, y cero cuando los albaranes cubren el pedido. El pendiente de compra se calcula en cada proyecto con la regla ya vigente del pedido no cubierto por su albarán, y después se suma. El albarán de compra no se resta en el margen.

**Rationale**: El margen queda alineado con la ficha del proyecto, no con el margen del cuadro de mando. El pendiente de venta está definido sobre los totales. El de compra ya existe por pedido y no se puede rehacer restando los dos totales, porque un albarán de más en un pedido no cubre otro.

**Alternatives considered**: Margen del cuadro de mando, ingresos menos gastos del mes contable. Se rechaza porque la especificación agrupa fichas de proyecto. Restar los totales de compra para el pendiente se rechaza porque mezcla pedidos que no se corresponden.

## Decision: Las gráficas repiten los indicadores y respetan el perfil

**Decision**: Hay tres gráficas y ninguna cifra nueva. La de totales dibuja solo los totales que el perfil puede ver. La composición pone el pedido de cliente en el centro y parte albaranes de cliente, gastos y margen positivo. El margen negativo se lee al lado y no es una parte. La de proyectos dibuja una fila por proyecto con su albaranado de cliente y su gasto. Un grupo no concedido quita la columna, el total, el indicador y la parte gráfica. No se dibuja un cero. El margen del mes solo aparece si se ven albaranes de cliente y gastos. Cada pendiente solo aparece si se ven las dos cifras de las que sale.

**Rationale**: La especificación exige que la gráfica coincida con el indicador y que un permiso ausente no se vea como cero. El dibujo de la ficha ya resuelve el centro, las partes y el margen negativo.

**Alternatives considered**: Una librería de gráficas nueva. Se rechaza porque la constitución ya cubre el dibujo con el HTML y el CSS actuales, y el mes no pide un tipo de gráfica distinto. Una cuarta gráfica de evolución diaria se rechaza porque la especificación fija tres y el resumen no es la evolución de un proyecto.

## Decision: El mes inicial y el mes cerrado no disparan una actualización

**Decision**: La ruta recibe el mes del 1 al 12. Si falta o no es válido, el mes es el de hoy cuando el ejercicio es el año en curso, y enero en cualquier otro ejercicio. Cambiar de mes no cambia la empresa ni el ejercicio. Si el mes está cerrado, la pantalla lo dice y muestra las fichas guardadas. No lo abre y no recalcula.

**Rationale**: La especificación fija el mes inicial y permite consultar un mes cerrado sin tocarlo. El cierre ya está guardado en la base propia. Leer esa marca no es leer el origen.

**Alternatives considered**: Recordar el último mes consultado. Se rechaza porque la especificación no lo pide y enero, o el mes de hoy, es un inicio estable. Ocultar los meses cerrados se rechaza porque la especificación permite consultarlos.
