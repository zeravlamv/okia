# Research: Cierre por ejercicio y mes

## Decision: El mes del proyecto es el del pedido de venta

**Decision**: Dentro del ejercicio que se actualiza, cada pedido de venta no anulado coloca al proyecto en el mes de su fecha. Si alguno de esos pedidos cae en un mes cerrado, el proyecto entero queda retenido. Un pedido anulado no cuenta. Un proyecto sin fecha de pedido no queda retenido. Un albarán, una compra o un gasto de otro mes no cambian el mes del proyecto.

**Rationale**: La especificación habla de «proyecto de ese mes» y la ficha ya toma como inicio la fecha del pedido. La actualización sustituye la ficha entera: si se reescribiera un proyecto con un pedido en un mes cerrado, también cambiaría esa parte.

**Alternatives considered**: Retener solo los documentos fechados en el mes cerrado y recalcular el resto del proyecto. Se rechaza porque la ficha no se guarda por trozos y la especificación deja fuera el proyecto entero. Usar el mes del albarán como mes del proyecto se rechaza porque un mismo proyecto tendría varios meses de referencia.

## Decision: Cerrar no lee el origen y un mes sin fila está abierto

**Decision**: El cierre es una fila por empresa, ejercicio y mes. Guarda si está cerrado, qué persona lo cambió y cuándo. Si no hay fila, el mes está abierto. Crear, cerrar o reabrir esa fila no llama al origen. La siguiente actualización es la que obedece la marca.

**Rationale**: La especificación separa el control del proceso de actualizar. Doce filas por adelantado no aportan: el estado abierto es la ausencia de cierre.

**Alternatives considered**: Crear siempre los doce meses en estado abierto. Se rechaza porque obliga a mantener filas que no dicen nada distinto de «no hay cierre». Cerrar el ejercicio con una sola marca se rechaza porque la especificación cierra mes a mes; el ejercicio queda cerrado cuando lo están sus doce meses.

## Decision: La ficha retenida no se borra

**Decision**: Actualizar sigue eligiendo los proyectos con pedido de venta no anulado en el ejercicio. Antes de borrar, aparta los retenidos. Borra y vuelve a guardar solo los proyectos abiertos. La ficha retenida, sus documentos y su fecha de actualización quedan como estaban. Si el mes cerrado nunca tuvo ficha, no se crea.

**Rationale**: Hoy la actualización borra todas las fichas de los proyectos del ejercicio y las crea de nuevo. Hay que excluir las retenidas de ese borrado. Conservar la fila conserva los importes y `updated_at`.

**Alternatives considered**: Borrar y volver a insertar la misma ficha. Se rechaza porque cambiaría la fecha de actualización. Marcar la ficha como cerrada dentro del proyecto se rechaza porque el cierre es del mes, no una bandera distinta en cada ficha.

## Decision: El resumen guarda la aportación del proyecto y la repone si queda retenido

**Decision**: Cada vez que un proyecto se actualiza, se guarda la aportación de ese proyecto al ejercicio: importes de las seis tarjetas que le corresponden, el camino analítico donde cae y los márgenes de sus pedidos. En la siguiente actualización los proyectos abiertos se calculan de nuevo, sin los documentos de los proyectos retenidos. Después se suman las aportaciones guardadas de los retenidos. Esas aportaciones no se sustituyen. Las filas de margen de pedido de un proyecto retenido se copian al resumen nuevo.

**Rationale**: El resumen actual es un total del ejercicio, sin mes y sin proyecto. Si se recalcula entero, un mes cerrado cambiaría. Si solo se guardara el mes, un proyecto con un pedido en enero cerrado y otro en febrero abierto perdería febrero, porque esa parte está mezclada con proyectos que sí se actualizan. La aportación por proyecto se puede apartar y reponer.

**Alternatives considered**: Guardar doce totales mensuales y sustituir solo los meses abiertos. Se rechaza porque no separa, dentro de un mes abierto, el pedido de un proyecto que también tiene un mes cerrado. Dejar el cuadro de mando como está y cerrar solo las fichas se rechaza porque la especificación también protege las cifras del resumen que salen de esos proyectos.

## Decision: Sin aportación previa, el mes cerrado no se rellena con la lectura nueva

**Decision**: Si un proyecto está retenido y todavía no tiene aportación guardada, no se crea a partir de la lectura que se acaba de hacer. Su ficha antigua, si existe, sigue igual. En el resumen nuevo no entra hasta que el mes se abra, se actualice y se vuelva a cerrar. La primera actualización con todos los meses abiertos deja escrita la aportación de cada proyecto. A partir de ahí el cierre sí puede reponerla.

**Rationale**: La lectura nueva no es «la última actualización en la que el mes estaba abierto». Usarla para sembrar un mes ya cerrado violaría el cierre. El resumen anterior no está partido por proyecto y no se puede descomponer con fidelidad.

**Alternatives considered**: Sembrar la aportación con la lectura aunque el mes esté cerrado. Se rechaza porque actualizaría el resumen del mes cerrado. Conservar el resumen anterior entero y solo refrescar fichas abiertas se rechaza porque las tarjetas de los meses abiertos quedarían viejas.

## Decision: Se sigue leyendo una vez por familia

**Decision**: Pedidos, albaranes y apuntes se leen igual que ahora, una vez por empresa. El descarte de los proyectos retenidos se hace en memoria, después de la lectura.

**Rationale**: El número de proyectos no cambia. Repetir la consulta por mes o por proyecto alargaría la actualización sin cambiar el resultado. Cerrar un mes no reduce la lectura: evita sustituir lo ya guardado.

**Alternatives considered**: No leer los documentos de los meses cerrados. Se rechaza porque el origen no se consulta por el mes del pedido de otro documento, y porque un proyecto abierto puede tener albaranes en un mes cerrado que sí deben entrar en su ficha.

## Decision: El aviso nombra los meses cerrados al terminar

**Decision**: Actualizar devuelve los meses cerrados de esa empresa y ese ejercicio, del 1 al 12, con su nombre en español. Si la lista está vacía, no hay aviso. Si están los doce, el aviso dice que no había ningún mes abierto y no se sustituye ninguna ficha. El aviso aparece tanto en la actualización con progreso como en la que solo redirige.

**Rationale**: La especificación pide que la persona no confunda una cifra vieja con una recién calculada. El progreso ya termina con un resultado; el aviso viaja en ese resultado y en un mensaje de la página de destino.

**Alternatives considered**: Un paso nuevo en la barra de progreso por cada mes. Se rechaza porque el trabajo no está partido en doce lecturas. Ocultar el aviso si la actualización terminó bien se rechaza porque es justo el caso en el que hace falta.
