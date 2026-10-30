# Feature Specification: Margen de pedidos por proyecto

**Feature Branch**: `001-margen-pedidos-proyecto`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "En base al constitution.md y un proceso de clarify de 50 preguntas empezamos a confeccionar el plan."

## Clarifications

### Session 2026-10-30

- Q: ¿Cómo deben mostrarse, por separado, el valor del pedido y los ingresos contables del proyecto? → A: Dos cifras independientes: el pedido con su coste y su margen, y los ingresos contables del proyecto al lado, sin sumarlos ni restarlos.
- Q: ¿El precio de venta del pedido debe tomarse sin impuestos o con los impuestos incluidos? → A: Sin impuestos. El precio de venta es la base del pedido.
- Q: ¿Qué pedidos de venta deben entrar en el margen y en los totales? → A: Todos los pedidos salvo los anulados.
- Q: Cuando se consulta un periodo, ¿el margen de un pedido debe incluir todo el coste y todos los ingresos de su proyecto, aunque esas imputaciones tengan otra fecha? → A: El periodo elige los pedidos. El margen de cada uno usa todo el coste y todos los ingresos de su proyecto, sea cual sea la fecha de la imputación.
- Q: ¿Qué registros deben sumar como coste del pedido cuando una hora también puede estar anotada en contabilidad? → A: Entran las líneas de compra y también los apuntes cuya cuenta indique horas, mano de obra o personal.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar el margen de un pedido (Priority: P1)

Una persona autorizada, con una empresa ya elegida, consulta cada pedido de venta y ve dos cifras independientes. Por un lado, el precio de venta, el coste del pedido y el margen del pedido. Por otro, los ingresos contables del proyecto, sin sumarlos ni restarlos al pedido. El pedido y sus costes se agrupan por el proyecto, y ese proyecto es el número de pedido. El coste del pedido reúne las líneas de compra del proyecto y los apuntes cuya cuenta indique horas, mano de obra o personal.

**Why this priority**: Es el motivo del producto. Sin esta lectura, la empresa no puede conocer el resultado de cada operación.

**Independent Test**: Con una empresa que tenga al menos un pedido de venta, compras o ingresos contables con el mismo proyecto, y un usuario autorizado a ver pedidos, compras e información contable, se puede abrir ese pedido y comprobar el precio, el coste, el margen y, al lado, los ingresos contables, sin usar el resto de pantallas.

**Acceptance Scenarios**:

1. **Given** un pedido de venta con precio de venta y con compras de material e imputaciones de horas del mismo proyecto y de la misma empresa, **When** la persona abre el margen de ese pedido, **Then** el margen del pedido es el precio de venta menos esas compras de material y esas horas.
2. **Given** el mismo pedido con ingresos contables imputados a su proyecto, **When** la persona lo consulta, **Then** esos ingresos aparecen al lado del pedido y no se suman ni se restan al precio, al coste ni al margen.
3. **Given** dos empresas con el mismo número de proyecto, **When** la persona consulta la empresa seleccionada, **Then** no entran en el cálculo costes, precio ni ingresos de la otra empresa.
4. **Given** un pedido con precio de venta distinto de cero, **When** se muestra el margen del pedido, **Then** se ven su importe y su porcentaje respecto al precio de venta. Los ingresos contables se ven como importe aparte.
5. **Given** un pedido con precio de venta cero y con coste, **When** se muestra el margen del pedido, **Then** se ve el importe del margen y el porcentaje se indica como no aplicable.
6. **Given** un pedido cuyo número es el proyecto y un único conjunto de costes de esa misma empresa con ese proyecto, **When** la persona abre el margen, **Then** esos costes se atribuyen a ese pedido.
7. **Given** una línea de compra del proyecto clasificada como horas, mano de obra o personal, y otra línea del mismo proyecto que no lo está, **When** se calcula el coste del pedido, **Then** la primera entra como imputación de horas y la segunda como material.
8. **Given** un apunte del proyecto en una cuenta de horas, mano de obra o personal, y otro apunte del proyecto en una cuenta que no es de ingreso ni de horas, **When** se calcula el coste, **Then** solo el primero se suma al coste. Ninguno de los dos se muestra como ingreso contable.
9. **Given** un pedido con base en la cabecera distinta de la suma de las bases de sus líneas, **When** se calcula el precio de venta, **Then** se usa la base de la cabecera, sin impuestos.
10. **Given** un pedido sin base en la cabecera, **When** se calcula el precio de venta, **Then** se usa la suma de las bases de sus líneas, sin impuestos.
11. **Given** un pedido con un importe con impuestos distinto de su base, **When** se calcula el precio de venta, **Then** el impuesto no entra en el precio ni en el margen.
12. **Given** una línea o un apunte sin importe, **When** se calcula el margen, **Then** esa pieza no se suma y el margen queda marcado como incompleto.
13. **Given** una empresa con moneda informada, **When** se muestran los importes, **Then** usan esa moneda y dos decimales. **Given** una empresa sin moneda, **When** se muestran los importes, **Then** usan el euro y dos decimales.
14. **Given** un pedido anulado y otro pendiente con costes de su proyecto, **When** se consulta el margen, **Then** solo entra el pendiente. El anulado no aporta precio, coste ni ingresos a un margen cerrado.

---

### User Story 2 - Entrar y elegir una empresa autorizada (Priority: P2)

Una persona entra con usuario y contraseña, puede recordar el usuario en ese dispositivo, puede recuperar la contraseña por correo y, al entrar, ve su identidad y elige una de las empresas que tiene asignadas. A partir de ahí solo ve información de esa empresa.

**Why this priority**: La información es multiempresa y económica. Sin un acceso acotado, el margen del pedido no se puede enseñar con seguridad.

**Independent Test**: Se puede probar solo con cuentas, empresas asignadas y el correo de recuperación, sin calcular todavía un margen.

**Acceptance Scenarios**:

1. **Given** una cuenta activa con contraseña correcta, **When** la persona entra, **Then** accede a la aplicación y ve su identidad.
2. **Given** una contraseña incorrecta, **When** la persona intenta entrar, **Then** no accede y recibe un aviso que no revela si el usuario existe.
3. **Given** que la persona marca recordar usuario, **When** vuelve a la pantalla de acceso en el mismo dispositivo, **Then** el usuario aparece relleno y la contraseña no queda guardada.
4. **Given** una cuenta con correo registrado, **When** solicita recuperar la contraseña, **Then** recibe un enlace de un solo uso válido durante 60 minutos.
5. **Given** un enlace caducado o ya usado, **When** la persona lo abre, **Then** no puede cambiar la contraseña y puede pedir un enlace nuevo.
6. **Given** una persona con varias empresas asignadas, **When** entra, **Then** debe elegir una antes de ver pedidos, costes o indicadores.
7. **Given** una persona con una sola empresa asignada, **When** entra, **Then** esa empresa queda seleccionada.
8. **Given** una empresa seleccionada, **When** la persona cambia a otra empresa autorizada, **Then** dejan de mostrarse las cifras de la empresa anterior.
9. **Given** que la persona eligió mantener la sesión, **When** vuelve al mismo dispositivo antes de 30 días, **Then** entra sin escribir la contraseña. **When** han pasado 30 días, **Then** debe identificarse de nuevo.
10. **Given** que la persona no eligió mantener la sesión, **When** cierra la sesión o esta caduca, **Then** debe identificarse de nuevo y no ve la información de la empresa anterior.

---

### User Story 3 - Revisar lo que no cuadra con un pedido (Priority: P3)

La persona revisa los pedidos que no tienen proyecto y las imputaciones cuyo proyecto no corresponde a un único pedido de venta. Así el margen no absorbe costes ajenos ni los hace desaparecer.

**Why this priority**: Un margen aparentemente correcto, pero mal cruzado, lleva a decisiones erróneas. Esta revisión protege la cifra principal.

**Independent Test**: Con pedidos sin proyecto, imputaciones huérfanas y un proyecto compartido por dos pedidos, se puede comprobar la lista de pendientes sin depender del panel de indicadores.

**Acceptance Scenarios**:

1. **Given** un pedido de venta sin proyecto, **When** la persona consulta los márgenes, **Then** ese pedido no recibe costes y aparece como pendiente de proyecto.
2. **Given** una compra, una hora o un ingreso con proyecto que no coincide con ningún pedido de venta de la empresa, **When** la persona consulta los pendientes, **Then** esa imputación aparece como no asignada y no modifica ningún margen ni se muestra como ingreso de un pedido.
3. **Given** dos pedidos de venta de la misma empresa con el mismo proyecto, **When** la persona consulta ese proyecto, **Then** el coste y los ingresos contables no se asignan a uno solo ni se duplican en ambos, y el proyecto queda pendiente de revisión junto con sus pedidos e imputaciones.

---

### User Story 4 - Ver el panel de indicadores (Priority: P4)

Tras elegir empresa, la persona ve un resumen del periodo: pedidos de venta, pedidos de compra, márgenes, clientes, proveedores, artículos, movimientos contables y el reparto del precio de venta por canal, delegación, departamento, sección y proyecto.

**Why this priority**: El margen por pedido responde a la operación concreta. El panel da contexto, pero no sustituye esa consulta.

**Independent Test**: Con datos de un periodo conocido y un usuario con permiso para ver esos grupos de información, se pueden contrastar los totales del panel sin abrir el detalle de un pedido.

**Acceptance Scenarios**:

1. **Given** una empresa seleccionada y el periodo por defecto, **When** la persona abre el panel, **Then** ve el número y el importe sin impuestos de pedidos de venta, el número y el importe sin impuestos de pedidos de compra, el margen del pedido total, el total de ingresos contables, y el número de clientes, proveedores y artículos.
2. **Given** ventas con canal, delegación, departamento, sección o proyecto, **When** la persona consulta el reparto, **Then** ve el precio de venta agrupado por cada una de esas dimensiones.
3. **Given** un perfil que no puede ver un grupo de información, **When** abre el panel, **Then** ese grupo no aparece y no se muestra como cero.
4. **Given** que la persona cambia el periodo, **When** el panel se actualiza, **Then** solo aparecen los pedidos de ese periodo y de la empresa seleccionada. El margen y los ingresos de cada uno incluyen todo su proyecto, aunque una imputación tenga otra fecha.
5. **Given** un pedido no anulado con fecha dentro del periodo, **When** se calcula el panel, **Then** el pedido entra en ese periodo. **Given** un pedido no anulado sin fecha cuyo ejercicio corresponde al año del periodo, **When** se calcula el panel, **Then** también entra. **Given** un pedido con fecha fuera del periodo, o un pedido anulado, **When** se calcula el panel, **Then** queda fuera.
6. **Given** un pedido del periodo y una compra de su proyecto fechada en otro año, **When** se calcula su margen, **Then** esa compra entra en el coste.

---

### User Story 5 - Administrar usuarios, perfiles y empresas (Priority: P5)

Una persona administradora crea y mantiene usuarios, perfiles, las empresas que cada usuario puede consultar y los grupos de información que cada perfil puede ver.

**Why this priority**: Hace posible el acceso seguro en el día a día. El primer administrador puede prepararse antes de abrir la consulta al resto de la empresa.

**Independent Test**: Se puede dar de alta un usuario, asignarle una empresa y un perfil, y comprobar que solo entra a lo permitido, sin necesidad de revisar el cálculo del margen.

**Acceptance Scenarios**:

1. **Given** una persona administradora, **When** asigna empresas a un usuario, **Then** ese usuario solo puede elegir y consultar esas empresas.
2. **Given** un perfil sin permiso sobre pedidos de venta, **When** un usuario con ese perfil intenta ver márgenes o el indicador de ventas, **Then** no ve esas cifras y recibe un aviso de acceso no permitido.
3. **Given** un perfil con permiso de consulta sobre un grupo, **When** el usuario entra en una empresa autorizada, **Then** puede consultar ese grupo y no puede modificar pedidos, compras, artículos ni apuntes.
4. **Given** un usuario sin ninguna empresa asignada, **When** entra, **Then** no ve datos económicos y se le indica que solicite una empresa a una persona administradora.
5. **Given** un perfil con permiso para consultar el plan de cuentas, **When** la persona lo abre en la empresa seleccionada, **Then** ve solo las cuentas de esa empresa.

---

### Edge Cases

- La sesión caduca: se pide entrar de nuevo y no se muestra información de la empresa que estaba abierta.
- Una persona pide recuperar la contraseña de un usuario inexistente o sin correo: la respuesta no revela si la cuenta existe.
- Un pedido tiene precio de venta y ningún coste: el margen del pedido coincide con el precio de venta y el porcentaje es del cien por cien.
- Un coste es mayor que el precio de venta: el margen del pedido se muestra negativo, tanto en importe como en porcentaje.
- Una compra sin proyecto cuenta en los totales de compras del panel, si el perfil puede verlas, y no entra en el margen de ningún pedido.
- Un ingreso contable sin proyecto no se atribuye a ningún pedido. No modifica el margen del pedido ni se presenta como ingreso de un pedido.
- El mismo número de pedido existe en otra serie o en otro ejercicio, pero el proyecto es distinto: cada pedido conserva su propio margen.
- El mismo proyecto está imputado en otra empresa: no se mezcla.
- Una compra o un ingreso del proyecto tiene fecha distinta de la del pedido: entra en el margen y en los ingresos de ese pedido si el pedido está en el periodo consultado.
- La misma hora está en una línea de compra y en un apunte de una cuenta de horas: las dos entran en el coste del pedido.
- Falta el importe de una línea o de un apunte: esa pieza no se suma, el pedido o la imputación queda señalado como importe incompleto y el margen visible no se presenta como cerrado.
- Una persona administradora solo administra y consulta las empresas que ella misma tiene asignadas.
- Un pedido anulado no entra en listas, márgenes ni totales. Si su proyecto no tiene otro pedido vigente, sus imputaciones quedan sin asignar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema debe permitir entrar con usuario y contraseña a las personas que tengan una cuenta activa.
- **FR-002**: El sistema debe rechazar un acceso incorrecto sin indicar si el usuario existe o si solo la contraseña es errónea.
- **FR-003**: La persona debe poder elegir recordar el usuario en el dispositivo. El sistema no debe guardar la contraseña.
- **FR-004**: La persona debe poder mantener la sesión iniciada en ese dispositivo durante 30 días, y debe poder entrar sin usar esa opción.
- **FR-005**: La persona debe poder solicitar la recuperación de la contraseña. Si la cuenta tiene correo, el sistema envía un enlace de un solo uso, válido 60 minutos.
- **FR-006**: El sistema debe permitir a una persona administradora crear y mantener usuarios, perfiles, la asignación de empresas por usuario y los grupos de información que cada perfil puede consultar.
- **FR-007**: Los grupos de información gobernados por el perfil son: empresas, clientes, proveedores, artículos, proyectos, canales, delegaciones, departamentos, secciones, pedidos de venta, pedidos de compra, movimientos contables y plan de cuentas.
- **FR-008**: Si un perfil no tiene concedido un grupo, el sistema no debe mostrar sus datos, ni en listados, ni en totales, ni en márgenes que dependan de ese grupo.
- **FR-009**: Toda persona, incluida quien administra, solo puede ver y administrar las empresas que tenga asignadas.
- **FR-010**: Antes de mostrar información económica, la persona debe tener una empresa seleccionada entre las suyas. Si solo tiene una, queda seleccionada al entrar.
- **FR-011**: Al cambiar de empresa, el sistema debe mostrar únicamente información de la empresa nueva.
- **FR-012**: El sistema debe tratar cada pedido de venta no anulado como una operación cuyo proyecto es el número de pedido, dentro de su empresa. Entran los pendientes, los servidos y los facturados. Los anulados no entran en la consulta, el margen ni los totales.
- **FR-013**: El precio de venta de un pedido es su base, sin impuestos. Si la cabecera tiene base, se usa esa. Si no la tiene, es la suma de las bases de sus líneas.
- **FR-014**: El coste del pedido es la suma, sin impuestos, de las líneas de compra del proyecto y de los apuntes del proyecto cuya cuenta indique horas, mano de obra o personal. El resto de apuntes no se suma a ese coste.
- **FR-015**: Una línea de compra es material cuando su artículo no indica horas, mano de obra o personal, y es una imputación de horas cuando sí lo indica. Un apunte es imputación de horas cuando su cuenta indica horas, mano de obra o personal. Ese apunte entra en el coste y no se muestra como ingreso contable.
- **FR-016**: El margen del pedido es el precio de venta menos el coste del pedido. Si el precio de venta no es cero, el sistema también muestra el porcentaje sobre ese precio.
- **FR-017**: Los ingresos contables de un proyecto son los abonos menos los cargos de las cuentas de ingreso de la misma empresa imputadas a ese proyecto. Se muestran al lado del pedido.
- **FR-018**: El sistema no debe sumar ni restar los ingresos contables al precio de venta, al coste del pedido ni al margen del pedido. Los apuntes que no son de ingreso no forman parte de esa cifra.
- **FR-019**: Un coste o un ingreso contable solo pertenece a un pedido cuando la empresa coincide y el proyecto corresponde a un único pedido de venta no anulado de esa empresa.
- **FR-020**: El sistema debe separar, sin incluirlos en un margen cerrado ni como ingreso de un pedido, los pedidos sin proyecto, las imputaciones cuyo proyecto no corresponde a ningún pedido y los proyectos compartidos por más de un pedido de venta.
- **FR-021**: El sistema debe mostrar un panel de la empresa seleccionada para el periodo elegido con: número e importe sin impuestos de pedidos de venta, número e importe sin impuestos de pedidos de compra, margen del pedido total, total de ingresos contables, número de clientes, proveedores y artículos, y precio de venta sin impuestos agrupado por canal, delegación, departamento, sección y proyecto.
- **FR-022**: El periodo por defecto es el año natural en curso. La persona debe poder cambiarlo. Un pedido no anulado entra en el periodo por su fecha; si no tiene fecha, por el año de su ejercicio. El margen y los ingresos contables de ese pedido incluyen todo el coste y todos los ingresos de su proyecto, aunque la imputación tenga otra fecha.
- **FR-023**: Las compras sin proyecto pueden aparecer en los totales de compras del panel, según el permiso del perfil. No entran en el margen de un pedido. Los ingresos sin proyecto no se muestran como ingreso de ningún pedido.
- **FR-024**: La consulta no debe permitir crear, modificar ni anular pedidos, compras, artículos, clientes, proveedores ni apuntes contables.
- **FR-025**: Si falta un importe necesario para cerrar un margen, el sistema debe excluir esa pieza del cálculo y marcar el resultado como incompleto.
- **FR-026**: Los importes se muestran con dos decimales, en la moneda de la empresa. Si la empresa no tiene moneda informada, se usa el euro.

### Key Entities *(include if feature involves data)*

- **Empresa**: Organización consultable. Todas las demás informaciones pertenecen a una empresa. Una persona solo accede a las empresas asignadas.
- **Usuario y perfil**: Identidad de acceso y conjunto de grupos de información que puede consultar. El perfil no autoriza a cambiar la información comercial o contable.
- **Cliente**: Cliente de una empresa, identificado por la empresa y su código de cliente.
- **Proveedor**: Proveedor de una empresa, identificado por la empresa y su código de proveedor.
- **Artículo**: Bien o servicio que la empresa vende o compra, identificado por la empresa y su código. Su naturaleza distingue material y mano de obra cuando esa naturaleza existe.
- **Proyecto**: Código analítico que agrupa la información de una operación. En un pedido de venta coincide con el número de pedido.
- **Canal, delegación, departamento y sección**: Dimensiones analíticas de la empresa para agrupar ventas e indicadores.
- **Pedido de venta**: Acuerdo de venta con un cliente, identificado por empresa, ejercicio, serie y número. Tiene cabecera, líneas, cliente, precio de venta y proyecto.
- **Pedido de compra**: Compra a un proveedor, identificada por empresa, ejercicio, serie y número. Sus líneas aportan material o servicios imputables a un proyecto.
- **Movimiento contable**: Cargo o abono de una cuenta de la empresa, imputable a un proyecto. Se relaciona con el plan de cuentas y, a través de la cuenta, con clientes y proveedores cuando corresponde.
- **Plan de cuentas**: Cuentas de la empresa. Sirve para interpretar la naturaleza del movimiento y su relación con clientes y proveedores.
- **Margen de la operación**: Resultado de un pedido de venta. Incluye precio de venta, coste del pedido y margen del pedido. Los ingresos contables del proyecto se consultan al lado y no forman parte de ese resultado. Si no se puede cerrar, lleva la marca de pendiente o incompleto.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona autorizada identifica el precio de venta, el coste del pedido, el margen del pedido y los ingresos contables del proyecto en menos de un minuto desde que la empresa está seleccionada.
- **SC-002**: En una muestra de pedidos con su documentación de apoyo, el cien por cien de los márgenes cerrados coincide con las reglas de esta especificación, sin diferencias sin explicar.
- **SC-003**: El cien por cien de las cifras visibles pertenecen a la empresa seleccionada y a grupos de información permitidos al perfil.
- **SC-004**: Una persona sin permiso no consigue ver un grupo restringido ni cambiando de empresa, ni reabriendo la consulta, ni usando un acceso directo.
- **SC-005**: Al menos el 90 % de las personas autorizadas consigue, en el primer intento y sin ayuda, entrar, situarse en su empresa y leer el margen de un pedido.
- **SC-006**: Con hasta 50 personas consultando a la vez y hasta 5.000 pedidos de venta en el periodo elegido, el panel y la consulta de un pedido se muestran en menos de 5 segundos en condiciones normales de trabajo interno.
- **SC-007**: El enlace de recuperación llega utilizable y deja de servir después de usarse o de pasar 60 minutos.
- **SC-008**: Ningún coste de un proyecto ambiguo, huérfano o de otra empresa aparece dentro de un margen cerrado.

## Assumptions

- El alcance de esta especificación es la primera versión descrita en la constitución del proyecto: consultar pedidos de venta e imputaciones por proyecto para obtener el coste del pedido, el margen del pedido y, por separado, los ingresos contables, con acceso seguro, panel de indicadores y administración de permisos.
- Queda fuera de esta versión crear o modificar pedidos, facturas, asientos, maestros o cualquier dato del sistema donde la empresa ya registra su actividad. Esta aplicación consulta; no sustituye a ese sistema.
- El proyecto de cada pedido de venta es el número de pedido, tal como indica la constitución. El pedido sigue identificándose por empresa, ejercicio, serie y número. El cruce con los costes se hace por empresa y proyecto. Solo cuentan los pedidos no anulados.
- El margen del pedido usa las líneas de compra del proyecto y los apuntes de cuentas de horas, mano de obra o personal. Los ingresos contables se leen solo de las cuentas de ingreso del proyecto y no modifican ese margen.
- Una cuenta o un artículo indican horas, mano de obra o personal cuando su denominación o su naturaleza lo dice. No hay otra lista aparte.
- El precio de venta y el coste del pedido se toman sin impuestos. La base de cabecera prevalece sobre la suma de las bases de las líneas. La suma se usa solo si no hay base de cabecera.
- En los ingresos contables, los abonos aumentan el importe y los cargos lo reducen.
- La moneda por defecto es el euro cuando la empresa no informa otra.
- Recordar el acceso significa recordar el usuario y, si la persona lo pide, mantener la sesión 30 días. No significa almacenar la contraseña.
- La recuperación por correo solo está disponible si el usuario tiene un correo registrado. Si no lo tiene, la contraseña la restablece una persona administradora.
- Existe al menos una persona administradora inicial con empresas asignadas para poder dar acceso al resto.
- El periodo por defecto es el año natural en curso. El periodo selecciona pedidos, no recorta el coste ni los ingresos de su proyecto.
- El panel muestra solo los indicadores enumerados en esta especificación. Otros indicadores quedan fuera hasta que se pidan de forma explícita.
- La constitución también fija una forma de trabajo por especificación previa, una memoria de proyecto y un documento de reglas de negocio. Eso gobierna cómo se construye el producto y no forma parte de lo que la persona usuaria consulta.
- Las decisiones de tecnología, de almacenamiento propio de la aplicación y de conexión con la información ya existente se dejan para el plan. No cambian las reglas de negocio de esta especificación.
- Si dos pedidos no anulados de la misma empresa comparten proyecto, el coste y los ingresos no se asignan a uno solo ni se duplican: el proyecto queda pendiente de revisión.
