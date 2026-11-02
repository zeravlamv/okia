# Contrato de pantalla: cierre y aviso

## Administración

La persona administradora ve una lista de cierres. Puede filtrar por empresa y por ejercicio.

Cada fila muestra la empresa, el ejercicio, el mes, si está cerrado, quién lo cambió y cuándo. El mes se lee por su nombre (enero a diciembre) y se guarda del 1 al 12.

Puede crear un cierre, marcarlo cerrado o volver a abrirlo. No hay otra acción: guardar no actualiza proyectos ni muestra importes.

Una persona que no administra no entra en esta lista.

## Al terminar Actualizar

Si en esa empresa y ese ejercicio hay algún mes cerrado, la persona ve un aviso con los nombres de esos meses, de enero a diciembre y sin repetir. El aviso dice que esos meses no se han actualizado.

Si no hay ningún mes cerrado, no aparece ese aviso.

Si los doce meses están cerrados, el aviso dice que no había ningún mes abierto y que no se ha actualizado ningún proyecto.

El aviso sale al terminar el progreso y también cuando Actualizar solo vuelve a la página. No cambia las tarjetas, la jerarquía ni la ficha que se esté mirando: esas cifras son las guardadas.

Abrir un proyecto retenido muestra la ficha anterior, con su fecha de actualización anterior. Si nunca se guardó, sigue el aviso de que hay que actualizar, y actualizar no la creará mientras el mes siga cerrado.
