# Quickstart: Resumen del mes

Comprueba el resumen sin el origen real. Bastan fichas de ejemplo ya guardadas. La lectura está en [contracts/resumen.md](./contracts/resumen.md) y la pantalla en [contracts/ui.md](./contracts/ui.md).

## Preparar

Desde la raíz del repositorio, con el entorno de la aplicación:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_month_summary.py tests/integration/test_month_page.py -q
```

Esos archivos de prueba son el sitio de las comprobaciones de abajo. No hace falta pulsar Actualizar contra el origen real.

## Un mes, dos proyectos

1. Guarda dos fichas de la empresa de prueba con pedido de venta en marzo del ejercicio, y otra con pedido en abril.
2. Anota de cada ficha de marzo el pedido de cliente, los albaranes de cliente, los pedidos de compra, los albaranes de compra y los gastos.
3. Abre Resumen mes, con esa empresa y ese ejercicio, en marzo.

Resultado esperado:

- El menú muestra Resumen mes.
- Marzo está seleccionado y abril no aporta filas.
- Hay dos filas, cada una con el código del proyecto y los cinco importes de su ficha.
- Cada total es la suma de las dos filas.
- El margen es los albaranes de cliente menos los gastos.
- Abrir una fila lleva a la ficha de ese proyecto.
- La página no ha leído el origen.

## Proyecto en dos meses

1. Guarda una ficha con un pedido en enero y otro en marzo del mismo ejercicio.
2. Abre enero y después marzo.

Resultado esperado:

- La ficha sale en los dos meses, con los mismos cinco importes.
- Cada fila nombra el otro mes.
- Dentro de enero la ficha se suma una sola vez.

## Permiso, mes vacío y mes cerrado

1. Entra con un perfil sin gastos y abre el mes.
2. Comprueba que no aparecen el gasto, el margen ni su gráfica, y que el resto de importes sigue.
3. Abre un mes sin fichas y comprueba que dice que no hay proyectos calculados, sin totales a cero.
4. Cierra ese mes en la administración y vuelve a abrirlo en Resumen mes.

Resultado esperado: se lee que el mes está cerrado, las cifras no cambian y el cierre sigue igual.
