# Research: Margen de pedidos por proyecto

## Aplicación Django de pantallas de servidor

- **Decision**: Django 5.2 LTS con plantillas HTML, el administrador integrado y JavaScript solo para completar la interacción de las pantallas.
- **Rationale**: La constitución fija Django, Python, HTML y JavaScript, y exige configurar usuarios, perfiles y permisos en el administrador.
- **Alternatives considered**: Una API separada con una aplicación de cliente queda fuera: duplicaría el acceso y el administrador ya cubre la configuración.

## Dos bases de datos

- **Decision**: La conexión `default` guarda los datos propios. Usa PostgreSQL en el entorno de back y SQL Server en producción. La conexión `erp` lee SQL Server y rechaza cualquier escritura.
- **Rationale**: El entorno de back debe usar PostgreSQL y producción SQL Server. La constitución, a la vez, obliga a leer el origen comercial desde SQL Server con parámetros guardados en el administrador.
- **Alternatives considered**: Copiar el origen comercial a PostgreSQL rompería la lectura directa exigida. Usar SQL Server también para la base propia en back contradice el entorno de desarrollo.

## Lectura del origen sin darlo por gestionado

- **Decision**: Los modelos del ERP se declaran como no gestionados. Django no crea ni migra esas tablas. Un módulo de mapeo resuelve los campos lógicos por el nombre de columna en el esquema real, antes de calcular márgenes.
- **Rationale**: La constitución entrega las claves de las tablas y pide interpretar el resto por el nombre. Las columnas de base imponible, fecha, estado, proyecto, cargo y abono no están inventariadas todavía.
- **Alternatives considered**: Fijar ya nombres físicos de un fabricante concreto se rechaza: un nombre distinto en el origen invalidaría el cálculo sin que la especificación hubiera cambiado.

## Reglas de mapeo que el cálculo debe poder comprobar

- **Decision**: El precio de venta es la columna de base imponible, no la de total con impuestos. Si la cabecera no tiene base, se suman las bases de las líneas. El estado anulado se reconoce por el valor o el nombre que signifique anulado. La fecha del pedido se reconoce por su nombre; si no existe, el año es el ejercicio. La moneda se lee de la empresa si hay una columna de moneda. Una cuenta es de ingreso cuando su código empieza por 7 o su naturaleza dice ingreso, salvo que su denominación indique horas, mano de obra o personal: en ese caso entra en el coste y no en los ingresos. Una línea de compra siempre entra en el coste.
- **Rationale**: Así se cumplen las cinco aclaraciones sin esperar a tener el catálogo físico, y el primer arranque contra el origen puede fallar de forma explícita si falta una columna lógica.
- **Alternatives considered**: Tratar todo el grupo 6 como coste se rechazó en la aclaración. Excluir el apunte cuando ya existe la línea de compra también se rechazó: las dos cantidades se suman.

## Consulta agregada en el origen

- **Decision**: El margen y el panel se calculan en el origen, filtrando por empresa y por los proyectos de los pedidos del periodo. No se traen todos los movimientos a la aplicación para sumarlos después.
- **Rationale**: El objetivo es responder en menos de 5 segundos con 5.000 pedidos y 50 personas concurrentes. El origen ya agrupa por empresa y proyecto.
- **Alternatives considered**: Calcular en memoria solo es aceptable en las pruebas unitarias, con filas de ejemplo, no contra el origen real.

## Panel y ficha no usan el mismo recorte de fechas

- **Decision**: El periodo elige pedidos de venta no anulados por su fecha, o por el ejercicio si no hay fecha. El margen y los ingresos de cada pedido incluyen todo el proyecto. El número y el importe de compras del panel cuentan las compras de la empresa fechadas en el periodo, también sin impuestos. Los recuentos de clientes, proveedores y artículos son los maestros vigentes de la empresa, no un recorte por fecha.
- **Rationale**: La aclaración obliga a no partir el margen por la fecha de la imputación. El indicador de compras del panel es otro dato de contexto y no es el coste del pedido.
- **Alternatives considered**: Usar el indicador de compras como si fuera el coste del periodo mezclaría dos preguntas distintas y contradiría la ficha del pedido.

## Acceso, recuerdo de usuario y correo

- **Decision**: Identidad y contraseña con el mecanismo de usuarios de Django. Recordar usuario guarda solo el identificador en una cookie. Mantener la sesión, si la persona lo pide, dura 30 días; si no lo pide, la sesión termina al cerrar el navegador o al caducar. La recuperación usa el flujo de correo de Django, con enlace de un solo uso durante 60 minutos. En back el correo se escribe en consola. En producción se envía por el servidor de correo configurado.
- **Rationale**: Cubre el acceso pedido sin almacenar la contraseña y sin añadir un proveedor de identidad.
- **Alternatives considered**: Guardar la contraseña en el navegador queda prohibido por la especificación.

## Permisos antes de calcular

- **Decision**: Cada grupo de información de la especificación es un permiso comprobable. La consulta no se ejecuta si el perfil no tiene el grupo necesario. Si falta el grupo, el indicador no aparece y no se sustituye por cero. La empresa seleccionada tiene que estar asignada a la persona.
- **Rationale**: Un permiso solo visual dejaría ver cifras por una consulta directa.
- **Alternatives considered**: Ocultar bloques en la plantilla y calcular igual no cumple el criterio de que una persona sin permiso no obtenga el dato.

## Gráficos

- **Decision**: La primera versión muestra las cifras y el reparto por canal, delegación, departamento, sección y proyecto en tablas. Un gráfico solo puede representar ese mismo reparto, sin indicadores nuevos.
- **Rationale**: La especificación fija los indicadores. La constitución admite gráficos como complemento, no como otro alcance.
- **Alternatives considered**: Un cuadro de mando con indicadores adicionales queda fuera hasta que se pida.

## Pruebas

- **Decision**: pytest comprueba el cálculo con filas de ejemplo y los permisos sobre PostgreSQL. La conexión real a SQL Server queda en una prueba de integración que se omite si no hay parámetros de origen.
- **Rationale**: El margen tiene que poder validarse sin el origen de producción. La lectura real no debe fingirse con otro motor.
- **Alternatives considered**: Exigir SQL Server en cada ejecución de pruebas impediría comprobar el cálculo en el entorno de back.
