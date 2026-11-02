# Contrato de cálculo: cierre del mes

Actualizar sigue siendo la única lectura del origen. Este contrato dice qué proyectos sustituye cuando hay meses cerrados. La ficha de un proyecto que sí entra se calcula con las reglas ya vigentes.

## Quién puede cerrar

- Solo una persona administradora, en la administración, donde ya se configuran usuarios, perfiles y empresas.
- Una persona que no administra no crea, no cierra y no reabre.
- Cerrar o reabrir no lee el origen, no borra fichas y no cambia el resumen.

## Qué mes está cerrado

- La marca es empresa + ejercicio + mes, con el mes del 1 al 12.
- Sin marca, el mes está abierto.
- La marca de una empresa no se aplica a otra. La de un ejercicio no se aplica a otro.
- No se guarda un mes fuera del 1 al 12 ni una marca repetida.

## Qué proyecto se retiene

Para la empresa y el ejercicio que se están actualizando:

1. Se toman los pedidos de venta no anulados de ese ejercicio que tienen proyecto.
2. El mes de cada pedido es el mes de su fecha.
3. Si el proyecto tiene al menos uno de esos pedidos en un mes cerrado, queda retenido entero.
4. Si todos esos pedidos caen en meses abiertos, se actualiza entero.
5. Si no tiene fecha de pedido, no queda retenido por este control.
6. Un pedido anulado no coloca al proyecto en ese mes.

Los albaranes, las compras y los gastos no deciden el mes. Si el proyecto está abierto, entran en su ficha aunque su fecha caiga en un mes cerrado para otros proyectos.

## Qué se escribe

- Proyecto abierto: se sustituye su ficha y se sustituye su aportación al ejercicio.
- Proyecto retenido con ficha: no se borra, no se reescribe y no cambia su fecha de actualización.
- Proyecto retenido sin ficha: no se crea.
- Proyecto retenido con aportación guardada: el resumen nuevo suma esa aportación y conserva sus márgenes de pedido. No se calculan otra vez.
- Proyecto retenido sin aportación guardada: el resumen nuevo no lo incluye. No se rellena con la lectura que acaba de hacerse.
- Los documentos de un proyecto retenido no entran en el cálculo de las tarjetas, del árbol ni de los márgenes de los proyectos abiertos.
- Si los doce meses están cerrados, no se sustituye ninguna ficha del ejercicio. El aviso lo dice.

## Qué no cambia

- La lectura sigue siendo una vez por familia y por empresa. El descarte es posterior.
- Misma empresa, documentos anulados fuera, importe ausente como dato incompleto.
- El cálculo de margen, progresión, compras y gastos de un proyecto abierto no cambia.
- Cerrar no crea, no modifica y no anula pedidos, albaranes ni apuntes.
