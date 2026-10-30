# Reglas de negocio OKIA

Estas reglas mandan sobre la frase de margen bruto y margen neto escrita al principio de `constitution.md`. Salen de la especificación aclarada el 2026-10-30.

## Qué se consulta

OKIA lee pedidos, compras, apuntes y maestros. No los crea, no los modifica y no los anula.

Cada pedido de venta no anulado es una operación. Su proyecto es el número de pedido. Solo se cruzan filas de la misma empresa.

Entran los pedidos pendientes, servidos y facturados. Los anulados no entran. Si un proyecto solo pertenece a un pedido anulado, sus imputaciones quedan sin asignar.

## Precio, coste y margen

El precio de venta es la base del pedido, sin impuestos. Manda la base de la cabecera. Si no existe, se suman las bases de las líneas.

El coste del pedido suma, sin impuestos y con cualquier fecha:

- todas las líneas de compra del proyecto;
- los apuntes cuya cuenta indique horas, mano de obra o personal.

Si la misma hora está en una línea y en un apunte, las dos cantidades entran. Una línea es hora cuando el artículo indica horas, mano de obra o personal. Si no lo indica, es material. El resto de apuntes no entra en el coste.

El margen del pedido es el precio menos el coste. Si el precio no es cero, también se muestra el porcentaje sobre ese precio. Si el precio es cero, el porcentaje no aplica.

## Ingresos contables

Los ingresos del proyecto son los abonos menos los cargos de sus cuentas de ingreso. Se muestran al lado del pedido. No se suman ni se restan al precio, al coste ni al margen. Un apunte de horas no se presenta como ingreso.

## Cruce

El coste y los ingresos pertenecen a un pedido solo cuando su proyecto corresponde a un único pedido no anulado de la empresa. Si el pedido no tiene proyecto, si el proyecto no tiene pedido vigente o si lo comparten varios pedidos vigentes, el caso queda pendiente de revisión y no cierra un margen.

## Periodo

El periodo por defecto es el año natural en curso. Un pedido entra por su fecha. Si no tiene fecha, entra por el año de su ejercicio. El periodo no recorta el coste ni los ingresos del proyecto.

El indicador de compras del panel cuenta las compras fechadas en el periodo. No es el coste de los pedidos.

## Acceso

Cada persona solo ve sus empresas. Cada perfil solo ve sus grupos de información. Un grupo no concedido no se muestra como cero. Recordar el acceso no guarda la contraseña. El enlace de recuperación dura 60 minutos y sirve una vez. La sesión mantenida dura 30 días.

## Importes

Se muestran con dos decimales, en la moneda de la empresa. Si la empresa no tiene moneda, se usa el euro. Una pieza sin importe no se suma y el resultado queda incompleto.
