# Modelo de datos: Aviso de discrepancias

El aviso es una lectura de las fichas ya guardadas de la empresa elegida. El origen comercial no recibe datos ni se consulta al abrir la campanita ni al cambiar el estado.

Se añade un estado a la ficha del proyecto. No hay tabla nueva.

## Estado de revisión

Cada ficha guarda un estado:

| Estado guardado | Lo que ve la persona |
|-----------------|----------------------|
| Pdte. Revisar | Pdte. Revisar |
| Revisado | Revisado |

Si la ficha es anterior a este campo, el estado es Pdte. Revisar.

El estado es uno por empresa y proyecto, el mismo para todas las personas. No depende del ejercicio. Cambiar los importes no lo cambia. Solo lo cambia la persona desde la ficha.

Actualizar borra las fichas del ejercicio que vuelve a calcular y crea otras. El estado se copia a la ficha nueva del mismo proyecto. Si el proyecto deja de tener ficha, el estado desaparece con ella. Cuando vuelva a calcularse, empieza en Pdte. Revisar.

## De dónde sale cada pareja

| Pareja | Lado izquierdo | Lado derecho |
|--------|----------------|--------------|
| Pedido de venta y albaranado | Base del pedido ya guardada en la ficha | Suma de los albaranes de venta de esa ficha |
| Pedido de compra y albaranado | Suma de los pedidos de compra guardados, cubiertos o comprometidos | Suma de los albaranes de compra de esa ficha |
| Ventas e ingresos | La misma suma de albaranes de venta | Suma de los ingresos del proyecto |

Esas sumas incluyen documentos de cualquier fecha. El ejercicio solo decide qué fichas entran.

## Qué proyecto entra en el ejercicio

Entra cada ficha con un pedido de venta guardado cuya fecha cae en el ejercicio. Una ficha por proyecto, aunque tenga dos pedidos en el mismo ejercicio.

Si la ficha no tiene los pedidos desglosados y solo tiene fecha de inicio, entra cuando el año de esa fecha coincide con el ejercicio.

Una ficha sin fecha de pedido no entra en ningún ejercicio.

## Qué se calcula al abrir y no se guarda

- Las tres parejas de cada ficha del ejercicio.
- Si una pareja se omite porque le falta un importe.
- Qué parejas puede ver la persona.
- La lista de proyectos con alguna pareja visible distinta y estado Pdte. Revisar.
- El número de esa lista, que es lo que muestra la campanita.

## Reglas de validez

- La lectura filtra por la empresa elegida. Un proyecto con el mismo código en otra empresa no entra.
- Un pedido o un albarán anulado no está guardado y no entra en la suma.
- Si no hay filas en un lado, ese lado es cero.
- Si la base del pedido está vacía, o alguna fila sumada tiene el importe vacío, esa pareja se omite. No se guarda un cero en su lugar y no se cuenta como discrepancia.
- Dos importes iguales al céntimo cuadran, también cero con cero. Cualquier otra diferencia, al alza o a la baja, es discrepancia.
- El proyecto cuenta una vez aunque fallen varias parejas.
- Una pareja de un grupo no concedido no se calcula para esa persona y no aparece como cero.
- Revisado saca el proyecto de la lista aunque alguna pareja siga distinta.
- Pdte. Revisar no mete el proyecto en la lista si las parejas visibles cuadran.
- Consultar el aviso no crea, no modifica y no borra fichas ni documentos. Guardar el estado solo cambia ese campo.

## Entidades que ya existen y no cambian de significado

- **Ficha del proyecto**: una por empresa y proyecto. Aporta la base del pedido, la fecha de inicio, el cliente y, a partir de ahora, el estado de revisión.
- **Albarán de venta guardado**: suma el albaranado.
- **Compra del proyecto**: el pedido cubierto, el comprometido y el albarán de compra.
- **Ingreso del proyecto**: suma los ingresos ya imputados a la ficha.
