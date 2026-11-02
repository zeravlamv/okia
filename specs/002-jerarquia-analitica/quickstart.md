# Quickstart: Jerarquía analítica

Comprueba el árbol con los pedidos de ejemplo, sin el origen comercial. Las reglas de cálculo están en [hierarchy.md](./contracts/hierarchy.md) y la pantalla en [ui.md](./contracts/ui.md).

## Preparación

Desde la raíz del proyecto, con el entorno ya creado:

```text
.venv\Scripts\python -m pytest tests\integration\test_dashboard.py
```

Esa orden sigue sirviendo para los indicadores generales. La jerarquía añade sus propias comprobaciones en la misma batería cuando esté construida.

## Qué debe cumplirse con la empresa 1 y el ejercicio 2026 de ejemplo

Los pedidos que cierran margen son el 1001, el 1003 y el 1004. Los pedidos 2001 y 2002 comparten proyecto y van al grupo aparte. El 1002 está anulado y no aparece. El 1005 es de 2025 por su fecha y no entra en 2026.

En el conjunto del árbol:

- Ventas: 1.010,00
- Compras: 340,00
- Gastos: 50,00
- Margen: 620,00
- Ingresos: 800,00

El 1001 aporta ventas 1.000,00, compras 300,00, gastos 50,00, margen 650,00 e ingresos 800,00. La línea de horas está en compras y el apunte de personal está en gastos. El margen de ese pedido sigue siendo 650,00 en la consulta de cada pedido.

El grupo aparte muestra el pedido 2001 con 100,00 y el 2002 con 80,00, sin margen. Esos 180,00 no están dentro de las ventas del árbol.

El indicador general de ventas del panel sigue en 1.190,00. Ese indicador sí incluye los pedidos del grupo aparte. No debe igualarse a las ventas del árbol.

Con el orden inicial, el primer nivel es el canal. «Tienda» contiene solo el 1001. «Sin dato» contiene el 1003 y el 1004. Abrir uno de esos canales muestra la delegación y no cambia las cifras del canal.

El 1004 tiene una línea sin importe. Su grupo y los que lo engloban quedan incompletos. El importe ausente no se suma como cero.

## Qué debe verse en el cuadro de mando

1. Entrar con la persona de ejemplo y abrir el cuadro de mando.
2. Comprobar que ya no hay una lista independiente por cada nivel.
3. Comprobar que se ve el primer nivel, no el árbol entero.
4. Abrir un grupo y comprobar que aparece el nivel siguiente con la misma suma.
5. Comprobar que el grupo aparte, cuando hay pedidos sin cierre, queda fuera de ese árbol.
6. Cambiar el ejercicio o la empresa y comprobar que las cifras anteriores desaparecen.

Los indicadores de pedidos, compras del ejercicio, clientes, proveedores y artículos siguen en su sitio. Las compras del panel no son las compras de la jerarquía.
