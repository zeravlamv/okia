# Data Model: Margen de pedidos por proyecto

Los datos propios y el origen comercial no se guardan en la misma conexión. Las claves físicas citadas aquí son las de `constitution.md`. El resto de campos son lógicos y se resuelven por el nombre de columna, según `research.md`.

## Datos propios

### Usuario

Identidad de acceso. Tiene identificador, contraseña gestionada por la aplicación, correo opcional y estado activo.

- Sin correo no puede recuperar la contraseña por sí mismo.
- Una cuenta inactiva no entra.

### Perfil

Conjunto de grupos de información que una persona puede consultar. No autoriza a modificar el origen.

Grupos: empresas, clientes, proveedores, artículos, proyectos, canales, delegaciones, departamentos, secciones, pedidos de venta, pedidos de compra, movimientos contables y plan de cuentas.

### Empresa autorizada

Relación entre una persona y un `CodigoEmpresa` del origen.

- Una persona solo elige y consulta empresas de esta lista.
- Quien administra también queda limitado a sus empresas.
- Con una sola empresa, queda seleccionada al entrar.
- Sin empresas, no hay cifras económicas.

### Conexión al origen

Parámetros de lectura del SQL Server comercial: servidor, base, usuario y secreto. Se configuran en el administrador. El secreto no se muestra de nuevo en claro.

## Origen comercial, solo lectura

Todas las filas pertenecen a un `CodigoEmpresa`. Una consulta de otra empresa no puede mezclarse.

### Empresa

Clave: `CodigoEmpresa`. Campo lógico: moneda. Si no hay moneda, el euro.

### Cliente

Clave: `CodigoEmpresa`, `CodigoCliente`.

### Proveedor

Clave: `CodigoEmpresa`, `CodigoProveedor`.

### Artículo

Clave: `CodigoEmpresa`, `CodigoArticulo`. Campo lógico: denominación o naturaleza. Si indica horas, mano de obra o personal, la línea de compra es una hora. Si no, es material.

### Proyecto

Clave: `CodigoEmpresa`, `CodigoProyecto`. En un pedido de venta coincide con el número de pedido.

### Canal, delegación, departamento y sección

Claves documentadas: `CodigoEmpresa` más `Canal`, `Delegacion`, `Departamento` o `Seccion`.

### Pedido de venta

Cabecera: `CodigoEmpresa`, `CodigoCliente`, `EjercicioPedido`, `SeriePedido`, `NumeroPedido`.

Líneas: `CodigoEmpresa`, `EjercicioPedido`, `SeriePedido`, `NumeroPedido`, `CodigoArticulo`.

Campos lógicos de cabecera: base imponible, total con impuestos, fecha, estado, proyecto, canal, delegación, departamento y sección.

- Entran los pendientes, servidos y facturados.
- Un estado que signifique anulado no entra en consultas, márgenes ni totales.
- El precio de venta es la base de la cabecera. Si no existe, es la suma de las bases de las líneas.
- El impuesto no entra en el precio ni en el margen.
- Sin fecha, el año del periodo es `EjercicioPedido`.
- Sin proyecto, el pedido no recibe coste ni ingresos y queda pendiente de proyecto.

### Pedido de compra

Cabecera: `CodigoEmpresa`, `CodigoProveedor`, `EjercicioPedido`, `SeriePedido`, `NumeroPedido`.

Líneas: `CodigoEmpresa`, `EjercicioPedido`, `SeriePedido`, `NumeroPedido`, `CodigoArticulo`.

Campos lógicos: proyecto, base sin impuestos, fecha y denominación del artículo.

- Toda línea con proyecto entra en el coste de ese proyecto, sea material u hora.
- Una compra sin proyecto puede contarse en el total de compras del panel y no entra en ningún margen.

### Movimiento contable

Clave documentada: `CodigoEmpresa`, ejercicio, `CodigoCuenta`. La constitución escribe el ejercicio como `Ejericicio`; el mapeo debe aceptar el nombre real de esa columna.

Campos lógicos: proyecto, cargo, abono e importe.

- Si la cuenta indica horas, mano de obra o personal, el importe sin impuestos entra en el coste y no se muestra como ingreso.
- Si la cuenta es de ingreso y no indica horas, el ingreso del proyecto es abonos menos cargos.
- El resto de apuntes no entra en el coste ni en los ingresos del pedido.
- Un movimiento sin importe no se suma y marca el resultado como incompleto.

### Plan de cuentas

Clave: `CodigoEmpresa`, `CodigoCuenta`. Sirve para conocer la denominación, la naturaleza y la relación con clientes o proveedores por `CodigoCuenta`.

## Resultado calculado, no almacenado

### Margen de la operación

Existe solo como resultado de consulta para un pedido no anulado cuyo proyecto es único en la empresa.

- Precio de venta: base sin impuestos.
- Coste: líneas de compra del proyecto, sin impuestos, más apuntes de cuentas de horas, mano de obra o personal. Si la misma hora está en los dos sitios, entran las dos.
- Margen: precio de venta menos coste. Con precio distinto de cero se muestra también el porcentaje. Con precio cero, el porcentaje no aplica.
- Ingresos contables: cifra aparte. No se suma ni se resta al precio, al coste ni al margen.
- El periodo elige el pedido. No recorta el coste ni los ingresos por la fecha de la imputación.

### Proyecto pendiente de revisión

Si más de un pedido no anulado de la empresa comparte proyecto, el coste y los ingresos no se asignan a uno ni se duplican. El proyecto, sus pedidos y sus imputaciones se listan como pendientes.

### Importe incompleto

Falta la base o el importe de una pieza necesaria. Esa pieza no se suma. El margen visible no se presenta como cerrado.

## Transiciones que importan

| Situación | Efecto |
|-----------|--------|
| Pedido pendiente, servido o facturado | Entra en el margen y en los totales |
| Pedido anulado | No entra. Si no queda otro pedido vigente con su proyecto, las imputaciones quedan sin asignar |
| Pedido sin proyecto | Se lista como pendiente y no absorbe costes |
| Proyecto compartido por varios pedidos vigentes | Queda pendiente de revisión |
| Persona sin la empresa o sin el grupo de información | No recibe la cifra, ni siquiera como cero |
