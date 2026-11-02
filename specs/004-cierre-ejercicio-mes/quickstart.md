# Quickstart: Cierre por ejercicio y mes

Comprueba el cierre sin el origen real. Los datos de ejemplo y la actualización de prueba bastan. Los contratos están en [contracts/cierre.md](./contracts/cierre.md) y [contracts/ui.md](./contracts/ui.md).

## Preparar

Desde la raíz del repositorio, con el entorno de la aplicación:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_period_close.py tests/integration/test_closed_month.py -q
```

Esos archivos de prueba son el sitio de las comprobaciones de abajo. No hace falta pulsar Actualizar contra el origen real.

## Cerrar y reabrir

1. Entra en la administración con una persona administradora.
2. Crea el cierre de marzo del ejercicio de prueba para la empresa de prueba y márcalo cerrado.
3. Comprueba que marzo sale cerrado, con esa persona y con una hora.
4. Ábrelo otra vez y comprueba que queda abierto y que no se ha creado una segunda fila.
5. Entra con una persona que no administra y comprueba que no puede abrir el cierre.

## Actualizar con un mes cerrado

1. Guarda antes las fichas del ejercicio, con todos los meses abiertos.
2. Anota la fecha de actualización y los importes de un proyecto cuyo pedido cae en marzo, y los de otro cuyo pedido cae en un mes abierto.
3. Cierra marzo.
4. Cambia en los datos de ejemplo el importe del pedido de marzo y el del mes abierto.
5. Pulsa Actualizar de ese ejercicio.

Resultado esperado:

- El proyecto de marzo conserva importes y fecha de actualización.
- El proyecto del mes abierto muestra el importe nuevo y la fecha de esta actualización.
- El aviso nombra marzo y no nombra los meses abiertos.
- El resumen sigue incluyendo la aportación que el proyecto de marzo tenía antes del cambio. No incluye el importe nuevo.
- Otra empresa del mismo marzo no queda cerrada.

## Proyecto en dos meses

1. Con marzo cerrado y febrero abierto, toma un proyecto que tenga un pedido vigente en cada uno.
2. Pulsa Actualizar.

Resultado esperado: el proyecto no cambia. No se actualiza la parte de febrero.

## Doce meses cerrados

1. Cierra los doce meses del ejercicio.
2. Pulsa Actualizar.

Resultado esperado: ninguna ficha cambia y el aviso dice que no había ningún mes abierto.

## Mes cerrado sin ficha previa

1. Elige un proyecto de marzo que todavía no tenga ficha.
2. Cierra marzo y pulsa Actualizar.

Resultado esperado: sigue sin ficha. Al abrir marzo y actualizar, la ficha aparece.
