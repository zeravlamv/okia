# Quickstart: Aviso de discrepancias

Comprueba el aviso sin el origen real. Bastan fichas de ejemplo ya guardadas. La lectura está en [contracts/aviso.md](./contracts/aviso.md) y la pantalla en [contracts/ui.md](./contracts/ui.md).

## Preparar

Desde la raíz del repositorio, con el entorno de la aplicación:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_discrepancies.py tests/integration/test_discrepancy_notice.py -q
```

Esos archivos de prueba son el sitio de las comprobaciones de abajo. No hace falta pulsar Actualizar contra el origen real.

## Tres proyectos, una campanita

1. Guarda tres fichas de la empresa de prueba con pedido de venta en el ejercicio.
2. En la primera, la base del pedido es 100 y los albaranes de venta suman 40.
3. En la segunda, pedido, albaranes, compras e ingresos cuadran, aunque sean cero donde no hay documentos.
4. En la tercera, el pedido es 80 y los albaranes suman 10, y el estado es Revisado.
5. Abre el cuadro de mando de esa empresa y ese ejercicio.

Resultado esperado:

- La campanita muestra 1.
- La ventana lista solo el primer proyecto, con el pedido 100 y el albaranado 40.
- Abrir la fila lleva a su ficha.
- La página no ha leído el origen.

## Dar por buena y volver a abrir

1. En la ficha del primer proyecto, elige Revisado.
2. Vuelve al cuadro de mando.
3. Regresa a la ficha y elige Pdte. Revisar.
4. Vuelve otra vez al cuadro.

Resultado esperado:

- Después de Revisado, la campanita muestra 0 y la ventana dice que no hay pendientes.
- Los importes de la ficha no han cambiado.
- Después de Pdte. Revisar, la campanita vuelve a mostrar 1 y la ventana vuelve a listar ese proyecto.

## Una pareja que no se puede ver

1. Entra con un perfil que no ve los ingresos ni los movimientos.
2. Deja un proyecto cuyo albaranado de venta es 50 y cuyos ingresos son 0, y cuyas otras parejas cuadran.

Resultado esperado:

- Ese proyecto no entra en la campanita.
- La ventana no muestra la pareja de ingresos ni un cero en su lugar.
