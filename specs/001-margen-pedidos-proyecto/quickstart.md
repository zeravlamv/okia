# Quickstart: Margen de pedidos por proyecto

Guía para comprobar el comportamiento acordado. No sustituye a la implementación ni trae el código de pantallas, modelos o migraciones.

## Requisitos

- Python 3.12.
- PostgreSQL para la base propia del entorno de back.
- SQL Server solo cuando se quiera leer un origen real. Las pruebas de cálculo no lo necesitan.
- Un correo de consola en back. En producción, un servidor de correo.

Los parámetros del origen se crean en el administrador. No se guardan en el repositorio.

## Preparación

Desde la raíz del repositorio, cuando exista el proyecto Django:

1. Crear un entorno virtual e instalar las dependencias del proyecto.
2. Aplicar las migraciones de la base propia sobre PostgreSQL.
3. Crear una persona administradora.
4. Arrancar la aplicación y abrir el administrador.

Comandos previstos, todavía sin el código de la aplicación:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Las pruebas de cálculo y de permisos:

```powershell
pytest
```

La prueba de integración contra SQL Server solo se ejecuta si la conexión `erp` está configurada. Si no lo está, se omite y el resto de pruebas sigue siendo válido.

## Comprobaciones

Los resultados esperados están en [spec.md](./spec.md). La forma de las pantallas está en [contracts/ui.md](./contracts/ui.md). Las cifras están en [contracts/margin-query.md](./contracts/margin-query.md). Las reglas persistentes están en [negocio.md](../../negocio.md).

1. Entrar con contraseña correcta muestra la identidad. Una contraseña incorrecta no dice si el usuario existe.
2. Recordar usuario rellena el identificador y no la contraseña. El enlace de recuperación deja de servir al usarse o a los 60 minutos.
3. Una persona con dos empresas no ve cifras hasta elegir una. Al cambiar de empresa, las cifras anteriores desaparecen.
4. Un pedido con base y con total con impuestos usa la base. El margen es esa base menos las compras del proyecto y menos los apuntes de horas, mano de obra o personal.
5. Los ingresos contables aparecen al lado y no cambian el margen. Si la misma hora está en una compra y en un apunte, el coste incluye las dos.
6. Un pedido anulado no entra. Un proyecto compartido por dos pedidos vigentes queda pendiente y no duplica el coste.
7. Un pedido del año consultado incluye una compra de su proyecto fechada en otro año.
8. Una persona sin permiso de pedidos de venta no obtiene esa cifra ni como cero.
9. Con filas de ejemplo equivalentes a 5.000 pedidos, la consulta de un pedido y el panel responden en menos de 5 segundos en el entorno interno.

## Qué no comprueba esta guía

No crea pedidos, compras ni apuntes en el origen. No da por válidos nombres físicos de columnas hasta que el mapeo los encuentre en el esquema real.
