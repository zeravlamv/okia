# Data Model: Cierre por ejercicio y mes

Las reglas de qué proyecto se retiene están en [research.md](./research.md). Los importes siguen el formato ya vigente.

## Cierre de mes

Marca de una empresa, un ejercicio y un mes. Si no existe fila, el mes está abierto.

| Campo | Sentido | Regla |
|-------|---------|--------|
| Empresa | Empresa a la que aplica | Obligatoria. No afecta a otra empresa |
| Ejercicio | Año del cierre | Obligatorio. No afecta a otro ejercicio |
| Mes | Mes natural, del 1 al 12 | Obligatorio. Un valor fuera de ese rango no se guarda |
| Cerrado | Si el mes está cerrado | Sí o no. Al reabrir queda en no y la fila se conserva |
| Cambiado por | Persona administradora que hizo el último cambio | Obligatoria al guardar desde la administración |
| Cambiado el | Momento del último cambio | Se escribe al guardar |

Una sola fila por empresa, ejercicio y mes. Cerrar no lee el origen y no modifica fichas ni resúmenes.

## Aportación del proyecto al ejercicio

Lo que un proyecto sumó al resumen la última vez que se actualizó estando abierto. Sirve para reponerlo cuando pasa a estar retenido.

| Campo | Sentido | Regla |
|-------|---------|--------|
| Empresa | Empresa del proyecto | Obligatoria |
| Proyecto | Código de proyecto | Obligatorio |
| Ejercicio | Ejercicio de aquella actualización | Obligatorio |
| Seis pares de tarjetas | Número e importe de pedidos de venta, pedidos de compra, albaranes de venta, albaranes de compra, ingresos y gastos atribuibles a este proyecto en el ejercicio | Cero si ese concepto no le corresponde |
| Camino analítico | Los cuatro primeros niveles donde cayó su importe | Pueden ir vacíos |
| Importes del camino | Venta, ingreso, compra, gasto y margen colocados en ese camino | Los de aquella actualización |
| Incompleto | Si faltó algún importe | Se conserva al reponer |

Una sola fila por empresa, proyecto y ejercicio. Se sustituye solo cuando el proyecto se actualiza. Si el proyecto está retenido, la fila no se toca. Si nunca se escribió, no se inventa con la lectura del mes cerrado.

Los márgenes de pedido que ya guarda el resumen siguen identificados por el proyecto. Los de un proyecto retenido se copian al resumen nuevo. Los de un proyecto abierto se calculan de nuevo.

## Ficha de proyecto

No gana campos. La retención se decide al actualizar:

- Proyecto abierto: se borra su ficha y se vuelve a guardar, como ahora. Su fecha de actualización es la de esta pasada.
- Proyecto retenido: no se borra y no se vuelve a guardar. Importes y fecha quedan igual.
- Proyecto retenido sin ficha previa: sigue sin ficha.

## Resumen del ejercicio

Sigue habiendo un resumen por empresa y ejercicio. Sus tarjetas, su árbol y sus pedidos fuera de la jerarquía son la suma de lo recién calculado para los proyectos abiertos más las aportaciones guardadas de los proyectos retenidos. Los documentos de un proyecto retenido no entran en el cálculo nuevo.

## Relaciones

- Un cierre pertenece a una empresa y a un ejercicio. No pertenece a un proyecto.
- Una aportación pertenece a un proyecto dentro de un ejercicio. El camino analítico es el de aquella actualización, no una fila viva del árbol.
- La ficha del proyecto sigue siendo una por empresa y código, con documentos de cualquier fecha.

## Transiciones

1. Mes abierto, sin fila o con cerrado en no. Actualizar incluye los proyectos que solo tienen pedidos en meses abiertos.
2. La persona administradora marca cerrado. No hay lectura ni recálculo.
3. La siguiente actualización retiene esos proyectos y repone su aportación si existe.
4. La persona administradora vuelve a abrir el mes. La ficha no cambia todavía.
5. La siguiente actualización trata otra vez esos proyectos como abiertos, sustituye su ficha y sustituye su aportación.
