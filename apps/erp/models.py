from django.db import models


class Empresa(models.Model):
    codigo_empresa = models.CharField(
        max_length=15, primary_key=True, db_column="CodigoEmpresa"
    )

    class Meta:
        managed = False
        db_table = "Empresas"


class Cliente(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "codigo_cliente")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_cliente = models.CharField(max_length=20, db_column="CodigoCliente")

    class Meta:
        managed = False
        db_table = "Clientes"


class Proveedor(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "codigo_proveedor")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_proveedor = models.CharField(max_length=20, db_column="CodigoProveedor")

    class Meta:
        managed = False
        db_table = "Proveedores"


class Articulo(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "codigo_articulo")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_articulo = models.CharField(max_length=30, db_column="CodigoArticulo")

    class Meta:
        managed = False
        db_table = "Articulos"


class Proyecto(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "codigo_proyecto")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_proyecto = models.CharField(max_length=30, db_column="CodigoProyecto")

    class Meta:
        managed = False
        db_table = "Proyectos"


class CabeceraPedidoCliente(models.Model):
    pk = models.CompositePrimaryKey(
        "codigo_empresa", "ejercicio_pedido", "serie_pedido", "numero_pedido"
    )
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_cliente = models.CharField(max_length=20, db_column="CodigoCliente")
    ejercicio_pedido = models.IntegerField(db_column="EjercicioPedido")
    serie_pedido = models.CharField(max_length=10, db_column="SeriePedido")
    numero_pedido = models.CharField(max_length=20, db_column="NumeroPedido")

    class Meta:
        managed = False
        db_table = "CabeceraPedidoCliente"


class LineasPedidoCliente(models.Model):
    pk = models.CompositePrimaryKey(
        "codigo_empresa",
        "ejercicio_pedido",
        "serie_pedido",
        "numero_pedido",
        "codigo_articulo",
    )
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    ejercicio_pedido = models.IntegerField(db_column="EjercicioPedido")
    serie_pedido = models.CharField(max_length=10, db_column="SeriePedido")
    numero_pedido = models.CharField(max_length=20, db_column="NumeroPedido")
    codigo_articulo = models.CharField(max_length=30, db_column="CodigoArticulo")

    class Meta:
        managed = False
        db_table = "LineasPedidoCliente"


class CabeceraPedidoProveedor(models.Model):
    pk = models.CompositePrimaryKey(
        "codigo_empresa", "ejercicio_pedido", "serie_pedido", "numero_pedido"
    )
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_proveedor = models.CharField(max_length=20, db_column="CodigoProveedor")
    ejercicio_pedido = models.IntegerField(db_column="EjercicioPedido")
    serie_pedido = models.CharField(max_length=10, db_column="SeriePedido")
    numero_pedido = models.CharField(max_length=20, db_column="NumeroPedido")

    class Meta:
        managed = False
        db_table = "CabeceraPedidoProveedor"


class LineasPedidoProveedor(models.Model):
    pk = models.CompositePrimaryKey(
        "codigo_empresa",
        "ejercicio_pedido",
        "serie_pedido",
        "numero_pedido",
        "codigo_articulo",
    )
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    ejercicio_pedido = models.IntegerField(db_column="EjercicioPedido")
    serie_pedido = models.CharField(max_length=10, db_column="SeriePedido")
    numero_pedido = models.CharField(max_length=20, db_column="NumeroPedido")
    codigo_articulo = models.CharField(max_length=30, db_column="CodigoArticulo")

    class Meta:
        managed = False
        db_table = "LineasPedidoProveedor"


class Movimiento(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "ejercicio", "codigo_cuenta")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    ejercicio = models.IntegerField(db_column="Ejercicio")
    codigo_cuenta = models.CharField(max_length=20, db_column="CodigoCuenta")

    class Meta:
        managed = False
        db_table = "Movimientos"


class PlanCuentas(models.Model):
    pk = models.CompositePrimaryKey("codigo_empresa", "codigo_cuenta")
    codigo_empresa = models.CharField(max_length=15, db_column="CodigoEmpresa")
    codigo_cuenta = models.CharField(max_length=20, db_column="CodigoCuenta")

    class Meta:
        managed = False
        db_table = "PlanCuentas"
