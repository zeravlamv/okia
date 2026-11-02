Proyecto: OKIA

Empresa: OKOA

Objetivo: Realizar consultas a la base de datos para extraer información de pedidos de venta e imputaciones realizadas a traes del codigo de proyecto. Todos los pedidos tiene como proyecto el mismo numero de pedido. Todas las imputaciones (compras de material, imputacion de horas,y cualquier input contable que tenga el mismo numero de proyecto) representan el coste final. El pedido de venta tiene el precio de venta y a traves de analizar las imputaciones se obtien el coste, mediante la diferencia se obtiene el margen bruto de la operación y con las imputaciones contables se obtiene el margen neto.

Arquitectura: Herramienta django y lenguaje python / html / javascrip / otros complementeos necesarios de python para realizar graficas, informes, etc.

Acceso a la app: Acceso securizado mediante configuración de perifles y usuarios en django/admin
   
Acceso a la base de datos: Acceso securizado a MSSQL mediante parametros de configuración que se han de definir en django/admin.

Seguridad acceso a los datos: Control de accaso a tablas a definir en django/admin

Forma de trabajar: todas las fucniones se deben desarrollar bajo norma SDD (Spec Kit instalado). el sistema debe trabajar con memory.md y las reglas de negocio se han de almacenar en negocio.md. Para todo lo que sea necesario se ha de crear el ".md" correspondiente.

ESTRUCTURA DE LA BASE DE DATOS:
===============================

Empresas: la base de datos de MSSQL es multi empresa y la lista de empresas esta en la tabla Empresas. A nivel de usuario se han de asignar las empresas autorizadas.

Relaciones: Todas las tablas de la BBDD de MSSQL tiene como realción principal el campo CodigoEmpresa.

Relaciones entre tablas y campos claves principales:

	TABLAS DATOS MAESTROS:
	====================== 
	Empresas (CodigoEmpresa) > esta tabla contiene todas la empresas a gestionar.
	
	Clientes (CodigoEmpresa, CodigoCliente) > esta tabla contiene todos los clientes de la empresa a gestionar y sus datos principales.
	
	Proveedores (CodigoEmpresa,CodigoProveedor) > esta tabla contiene todos los proveedores de la empresa a gestionar y sus datos principales.
	
	Articulos (CodigoEmpresa, CodigoArticulo) > esta tabla contiene los datos asociados a articulos o servicios que presta la empresa.
	
	PlanCuentas (CodigoEmpresa, CodigoCuenta) > relación de las cuentas de la empresa. Se relaciona con clientes y proveedor por el campo CodigoCuenta.

	TABLAS ANALITICAS
	=================

	Proyectos (CodigoEmpresa, CodigoProyecto) > campo analitico que sirve para agrupar informacion de diferentes tablas.
	
	CanalesEmpresa (CodigoEmpresa, Canal) > campo analitico que sirve para agrupar informacion de diferentes tablas.
	
	Delegaciones (CodigoEmpresa, Delegacion) > campo analitico que sirve para agrupar informacion de diferentes tablas.
	
	Departamentos (CodigoEmpresa, Departamento) > campo analitico que sirve para agrupar informacion de diferentes tablas.
	
	Secciones (CodigoEmpresa, Seccion) > campo analitico que sirve para agrupar informacion de diferentes tablas.

	TABLAS DATOs TRANSACCIONALES:
	=============================
	CabeceraPedidoCliente (CodigoEmpresa, CodigoCliente, EjercicioPedido, SeriePedido, NumeroPedido) > esta tabla contiene la cabecera del pedido de venta de un cliente. Los datos son especificos para el pedido. Se han de mapear los campos y por el nombre deberas interpretar el contexto.
	 
	LineasPedidoCliente (CodigoEmpresa, EjercicioPedido, SeriePedido, NumeroPedido, CodigoArticulo) > esta tabla contiene el detalle de los articulos o servicios vendidos a un cliente. Los datos son especificos de cada linea. Se han de mapear los campos y por el nombre deberas interpretar el contexto.

	CabeceraAlbaranCliente (CodigoEmpresa, CodigoCliente, EjercicioAlbaran, SerieAlbaran, NumeroAlbaran) > esta tabla contiene la cabecera del albaran de venta a un cliente. Los datos son especificos del albaran. Se han de mapear los campos y por el nombre deberas interpretar el contexto.
	 
	LineasAlbaranCliente (CodigoEmpresa, EjercicioAlbaran, SerieAlbaran, NumeroAlbaran, CodigoArticulo) > esta tabla contiene el detalle de los articulos o servicios vendidos a un cliente. Los datos son especificos de cada linea. Se han de mapear los campos y por el nombre deberas interpretar el contexto.

	CabeceraAlbaranProveedor (CodigoEmpresa, CodigoProveedor, EjercicioPedido, SeriePedido, NumeroPedido) > esta tabla contiene la cabecera del albaran de compra a un Proveedor. Los datos son especificos del albaran. Se han de mapear los campos y por el nombre deberas interpretar el contexto.
	 
	LineasAlbaranProveedor (CodigoEmpresa, EjercicioPedido, SeriePedido, NumeroPedido, CodigoArticulo) > esta tabla contiene el detalle de los articulos o servicios comprados a un proveedor. Los datos son especificos de cada linea. Se han de mapear los campos y por el nombre deberas interpretar el contexto.

	CabeceraPedidoProveedor (CodigoEmpresa, CodigoProveedor, EjercicioPedido, SeriePedido, NumeroPedido) > esta tabla contiene la cabecera del pedido a un Proveedor. Los datos son especificos para el pedido. Se han de mapear los campos y por el nombre deberas interpretar el contexto.
	 
	LineasPedidoProveedor (CodigoEmpresa, EjercicioPedido, SeriePedido, NumeroPedido, CodigoArticulo) > esta tabla contiene el detalle de los articulos o servicios pedidos a un proveedor. Los datos son especificos de cada linea. Se han de mapear los campos y por el nombre deberas interpretar el contexto.

	Movimientos (CodigoEmpresa, Ejericicio, CodigoCuenta) > relación de movimientos contables. Se han de mapear los campos y por el nombre deberas interpretar el contexto.

	AnaMovimientos (MovPosicion) > relacion con la tabla Movimientos. Esta tabla contiene la relación de movimientos analiticos de los niveles establecidos.
  
Frontend acceso: Acceso mediante usuario/contraseña, recordar usuario contraseña, opcion de recuperación mediante correo electronico.

Frontend principal: Mostrar selector de empresas. Información usuario. Acceso a django/admin. Dashboard con los proincpales indicadores que peudas obtener al acceder a la tablas de pedidos de clientes, proveedores y tablas como la de proveedores, articulos, movimientos, canalesempresa, proyectos, departamentos, secciones y delegaciones.

Formato de los datos: Los importes se han mostrar con separacion de miles con un punto, decimales con coma y dos decimales. Siempre alineados al izquierda de la columna.