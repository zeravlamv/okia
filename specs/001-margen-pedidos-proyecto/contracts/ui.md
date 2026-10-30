# Contrato de pantallas: Margen de pedidos por proyecto

Las pantallas muestran solo datos de la empresa seleccionada y de los grupos de información permitidos. Ninguna pantalla crea, modifica ni anula datos del origen.

## Acceso

Entrada: identificador y contraseña.

- Si son correctos y la cuenta está activa, la persona ve su identidad.
- Si no son correctos, el aviso no revela si el identificador existe.
- Recordar usuario rellena el identificador en ese dispositivo y no guarda la contraseña.
- Mantener la sesión, si se elige, dura 30 días. Si no se elige, hay que identificarse de nuevo al cerrar la sesión o al caducar.
- Recuperar la contraseña envía un enlace de un solo uso, válido 60 minutos, solo si hay correo. Un enlace usado o caducado no cambia la contraseña. Pedir la recuperación de una cuenta inexistente o sin correo no revela si existe.

## Empresa

- Con varias empresas autorizadas, no se muestran pedidos, costes ni indicadores hasta elegir una.
- Con una sola, queda seleccionada.
- Sin ninguna, se indica que hay que solicitar una empresa a quien administra.
- Al cambiar de empresa desaparecen las cifras de la anterior.

## Margen del pedido

Para cada pedido no anulado del periodo, con proyecto único:

- Precio de venta sin impuestos, coste del pedido, margen en importe y, si el precio no es cero, porcentaje.
- Ingresos contables del proyecto, como importe aparte.
- La misma hora en una línea de compra y en un apunte de personal cuenta dos veces en el coste.
- Un pedido anulado no aparece en esta lista ni aporta cifras.
- Un pedido sin proyecto, una imputación sin pedido y un proyecto compartido no cierran un margen: pasan a la revisión.

## Revisión de cruces

Lista pedidos sin proyecto, imputaciones cuyo proyecto no corresponde a un único pedido vigente y proyectos compartidos. Esas filas no modifican un margen cerrado ni se presentan como ingreso de un pedido.

## Panel

Para la empresa y el periodo, por defecto el año natural en curso:

- Número e importe sin impuestos de los pedidos de venta del periodo.
- Número e importe sin impuestos de las compras fechadas en el periodo.
- Suma del margen de esos pedidos, con el coste completo de cada proyecto.
- Suma de los ingresos contables completos de esos proyectos.
- Número de clientes, proveedores y artículos de la empresa.
- Precio de venta sin impuestos agrupado por canal, delegación, departamento, sección y proyecto.

Un grupo no permitido no ocupa un hueco con valor cero. Cambiar el periodo cambia los pedidos incluidos, no recorta las imputaciones de un pedido ya incluido.

## Administración

Quien administra, dentro de sus empresas, mantiene usuarios, perfiles, empresas autorizadas, grupos de información y parámetros de conexión al origen. Consultar el plan de cuentas muestra solo las cuentas de la empresa seleccionada.
