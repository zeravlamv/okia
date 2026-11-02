# Modelo de datos: Análisis profundo

La vida del proyecto se guarda en la base propia de la aplicación. El origen comercial no recibe tablas nuevas. El resumen del cuadro de mando, por empresa y ejercicio, sigue igual.

## Vida del proyecto

Una fila por empresa y código de proyecto.

| Dato | Sentido |
|------|---------|
| Empresa | La empresa elegida. No se mezcla con otra. |
| Proyecto | Código del proyecto. |
| Inicio | Fecha más antigua de sus pedidos de venta no anulados. |
| Base del pedido | Suma de las bases de esos pedidos. |
| Incompleta | Verdadero si falta alguna base que debía entrar. |
| Actualizada | Momento en que Actualizar sustituyó esta vida. |

Si varios pedidos vigentes comparten el proyecto, siguen siendo una sola vida.

## Hito de albarán de venta

Cuelga de una vida.

| Dato | Sentido |
|------|---------|
| Identidad | Ejercicio, serie y número del albarán. |
| Fecha | Fecha del albarán. Vacía si no tiene. |
| Importe | Base sin impuestos. Negativa si es un abono. Vacía si falta y la vida queda incompleta. |
| Facturación | Facturado, no facturado o sin dato. |

Un albarán anulado no se guarda.

## Compra del proyecto

Cuelga de una vida.

| Dato | Sentido |
|------|---------|
| Clase | Albarán de compra, o pedido de compra comprometido. |
| Identidad | Ejercicio, serie y número del documento. |
| Proveedor | Código y nombre guardado en la actualización. |
| Fecha | Fecha del albarán o del pedido. Vacía si no tiene. |
| Importe | Base sin impuestos. Vacía si falta. |
| Pedido enlazado | En un albarán, ejercicio, serie y número del pedido de compra cuando la cabecera los trae. Sirve para no guardar ese pedido como comprometido. |

## Gasto del proyecto

Cuelga de una vida.

| Dato | Sentido |
|------|---------|
| Cuenta | Código y descripción del plan contable guardados en la actualización. |
| Fecha | Fecha del apunte. Vacía si no tiene. |
| Importe | Cargo menos abono de la parte atribuida al proyecto. |

No se guardan el cierre de ejercicio ni las cuentas de ingreso.

## Qué no se guarda

- Los meses vacíos. Se generan al abrir, desde el mes del inicio hasta el mes en que termina la barra.
- El día «hoy». Se toma al abrir la ficha.
- El porcentaje y el pendiente. Se calculan al abrir a partir de la base y de los hitos.
- Canal, delegación, departamento y sección.

## Reglas de validez

- No hay dos vidas para la misma empresa y el mismo proyecto.
- Sustituir una vida borra sus hitos, compras y gastos anteriores y escribe los nuevos juntos.
- Una vida de otra empresa no se lee aunque el código coincida.
- Un importe vacío no se convierte en cero.
