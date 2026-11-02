# Validación: ficha del proyecto

Comprueba la vida de un proyecto de ejemplo, sin el origen comercial real. Los importes y los porcentajes esperados están en [project-life.md](contracts/project-life.md). La pantalla está en [ui.md](contracts/ui.md).

## Preparación

Desde la raíz del repositorio, con el entorno de la aplicación:

```text
.venv\Scripts\python.exe -m pytest tests/unit tests/integration -q
```

Los datos de ejemplo deben incluir un proyecto de la empresa 1 con:

- un pedido de venta no anulado de 1.000 con fecha en marzo de 2024;
- un albarán de venta facturado de 400 en 2025;
- un albarán de venta no facturado de 100 en 2026;
- un albarán de compra de un proveedor en marzo de 2025;
- un pedido de compra sin albarán;
- un apunte de gasto de una cuenta con descripción, y un apunte de cierre de ejercicio que no debe entrar.

Hace falta una persona de prueba con permiso para ver pedidos, albaranes, compras y movimientos de la empresa 1.

## Recorrido

1. Entrar y elegir la empresa 1.
2. Abrir el cuadro de mando del ejercicio 2024 antes de actualizar. La ficha del proyecto no debe mostrar 1.000 ni 400.
3. Pulsar Actualizar para la empresa 1 y el ejercicio 2024.
4. Abrir el proyecto desde la jerarquía.
5. Comprobar la ficha:
   - inicio en marzo de 2024;
   - aparecen 2024, 2025 y 2026;
   - albaranado 500,00 EUR y progresión 50,00 %;
   - facturado 400,00 EUR y no facturado 100,00 EUR;
   - pendiente de albaranar 500,00 EUR;
   - la suma de las dos partes es el albaranado.
6. Comprobar la Gantt: la barra no termina en 2025; sigue hasta el día de la visita porque el pedido no está cubierto. Hay un hito facturado y otro que no lo está.
7. Comprobar que el pedido de compra sin albarán figura como comprometido y no aumenta las compras.
8. Comprobar que el gasto de la cuenta entra, con código y descripción, y que el cierre de ejercicio no está.
9. Recargar la ficha. Las cifras siguen igual y no se dispara otra actualización.
10. Entrar con un perfil sin permiso de albaranes de venta. No se ve la progresión ni un cero en su lugar.

## Resultado

El recorrido pasa cuando los diez puntos se cumplen y la suite termina sin fallos. El origen real no hace falta para este recorrido.
