# Research: Jerarquía analítica

## Decision: El árbol se calcula una vez en el servidor

**Decision**: Con los pedidos, las compras y los apuntes ya leídos para la empresa y el ejercicio, se construye el árbol completo en memoria. El navegador recibe ese árbol y solo muestra u oculta niveles. Abrir un grupo no hace otra consulta.

**Rationale**: La especificación exige el primer nivel en menos de 5 segundos para 1.500 pedidos y que abrir un grupo no cambie los importes. El cuadro de mando ya carga esas filas. Un segundo recorrido por nivel repetiría la lectura. Varios grupos pueden permanecer abiertos a la vez: ocultar uno no borra a los demás.

**Alternatives considered**: Pedir cada nivel al servidor al abrirlo. Se rechaza porque repetiría la lectura y podría mostrar una suma distinta si los datos cambiaran entre aperturas. Desplegar el árbol entero desde el principio se rechaza porque el último nivel puede reunir más de mil proyectos.

## Decision: Compras y gastos salen del coste actual, partidos

**Decision**: Las compras de un pedido cerrado son la suma de las bases de todas sus líneas de compra, con cualquier fecha. Los gastos son los apuntes de horas, mano de obra o personal de ese proyecto. Su suma es el coste que ya usa el margen del pedido. El margen del grupo es ventas menos compras menos gastos. Los ingresos se calculan como ahora y no entran en la resta.

**Rationale**: La aclaración del 2026-10-30 fija esa separación y mantiene la regla de contar la hora dos veces si está en una línea y en un apunte. La línea queda en compras y el apunte en gastos.

**Alternatives considered**: Tratar las líneas de horas como gasto y no como compra. Se rechaza porque la aclaración mete todas las líneas de compra en compras. Usar las compras fechadas en el ejercicio como cifra de la jerarquía se rechaza porque ese indicador del panel es otro concepto y no sigue el proyecto del pedido.

## Decision: Solo los pedidos que cierran margen entran en el árbol

**Decision**: Entra en el árbol el pedido no anulado del ejercicio cuyo proyecto corresponde a un único pedido no anulado de la empresa. El pedido sin proyecto y el que comparte proyecto van al grupo aparte, con su precio de venta y sin compras, gastos, ingresos ni margen. El pedido anulado no va a ningún sitio. Esas ventas del grupo aparte no se suman a ningún nivel.

**Rationale**: Así cada cifra de un grupo es la suma de la misma cifra en los grupos que engloba, y el margen del grupo coincide con ventas menos compras menos gastos. El indicador general de ventas del panel sigue contando todos los pedidos no anulados del ejercicio, incluidos los del grupo aparte.

**Alternatives considered**: Meter las ventas de los pedidos sin cierre dentro del canal y dejar el margen solo con los cerrados. Se rechaza porque el nivel superior dejaría de ser la suma exacta de los inferiores.

## Decision: El camino de un pedido omite los niveles no concedidos

**Decision**: El orden guardado define la anidación. Si el perfil no puede ver un nivel, ese escalón no existe y el nivel visible anterior engloba directamente el siguiente visible. Si no puede ver una cifra, esa cifra no viaja al navegador. Los demás grupos se identifican con código y descripción; sin descripción, con el código; sin código, con «Sin dato». Dos códigos distintos siguen siendo dos grupos aunque la descripción coincida.

**Rationale**: Es la regla de permisos ya vigente: lo no concedido no aparece como cero. El orden ya está en el árbol analítico del administrador y no hace falta otra tabla.

**Alternatives considered**: Mostrar el nivel oculto vacío. Se rechaza porque revelaría el concepto. Guardar un árbol distinto por persona. Se rechaza porque el orden es de la instalación y el permiso solo recorta la vista.

## Decision: Un importe ausente no se convierte en cero

**Decision**: Si a un pedido cerrado le falta un importe, se suman los importes conocidos y el grupo, más todos los que lo engloban, queda marcado como incompleto.

**Rationale**: `negocio.md` impide sustituir una pieza sin importe por cero y obliga a marcar el resultado.

**Alternatives considered**: Excluir el pedido incompleto del árbol y pasarlo al grupo aparte. Se rechaza porque sí tiene proyecto único y su precio conocido forma parte del margen, aunque el resultado esté incompleto.
