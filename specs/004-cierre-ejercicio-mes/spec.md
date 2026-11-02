# Feature Specification: Cierre por ejercicio y mes

**Feature Branch**: `004-cierre-ejercicio-mes`

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Crear en django/admin un control de cierre por ejercicio/mes. Si se marca un mes como cerrado no se pueden actualizar proyecto de ese mes. El proceso actualizar solo lo hará de los meses o periodos abiertos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cerrar y reabrir un mes (Priority: P1)

Una persona administradora marca, para una empresa y un ejercicio, qué meses están cerrados. Un mes cerrado queda protegido. Un mes sin marca, o vuelto a abrir, queda abierto y se puede actualizar.

**Why this priority**: Sin este control no hay forma de impedir que una actualización pise un mes ya revisado.

**Independent Test**: La persona administradora cierra marzo de 2026 de su empresa, comprueba que queda cerrado, lo reabre y comprueba que vuelve a estar abierto. Otra empresa no cambia.

**Acceptance Scenarios**:

1. **Given** una empresa y el ejercicio 2026 sin ningún mes cerrado, **When** la persona administradora abre el control, **Then** los doce meses se leen como abiertos.
2. **Given** ese ejercicio, **When** marca marzo como cerrado, **Then** marzo queda cerrado para esa empresa y ese ejercicio, y el resto de meses sigue abierto.
3. **Given** marzo cerrado, **When** lo vuelve a abrir, **Then** marzo queda abierto y la siguiente actualización puede incluir sus proyectos.
4. **Given** marzo cerrado en la empresa A, **When** se consulta la empresa B, **Then** marzo de la empresa B sigue abierto.
5. **Given** el mismo mes cerrado dos veces, **When** se consulta el control, **Then** hay una sola marca de cierre para esa empresa, ese ejercicio y ese mes.
6. **Given** una persona que no administra, **When** intenta cerrar o abrir un mes, **Then** no puede hacerlo.
7. **Given** un mes cerrado, **When** otra persona administradora lo consulta, **Then** ve que está cerrado, quién lo cerró y cuándo.

---

### User Story 2 - Actualizar solo los meses abiertos (Priority: P1)

La persona pulsa Actualizar sobre un ejercicio. Los proyectos de los meses abiertos se calculan de nuevo. Los proyectos de los meses cerrados conservan la ficha que ya tenían y no se vuelven a leer.

**Why this priority**: El cierre solo sirve si Actualizar lo respeta. Es la protección que pide el control.

**Independent Test**: Con enero cerrado y febrero abierto, y con fichas ya guardadas de ambos meses, la persona pulsa Actualizar del ejercicio y comprueba que febrero cambia y enero permanece igual, incluida la fecha de su última actualización.

**Acceptance Scenarios**:

1. **Given** un ejercicio con todos los meses abiertos, **When** se pulsa Actualizar, **Then** se actualizan los proyectos de todos los meses, igual que antes de existir el cierre.
2. **Given** marzo cerrado y el resto abierto, y proyectos de marzo ya guardados, **When** se pulsa Actualizar de ese ejercicio, **Then** ningún proyecto cuyo pedido de venta cae en marzo cambia de importes ni de fecha de actualización.
3. **Given** el mismo caso, **When** termina Actualizar, **Then** los proyectos cuyo pedido de venta cae en un mes abierto quedan calculados con los datos de ese momento.
4. **Given** un proyecto con pedidos de venta no anulados en un mes cerrado y en un mes abierto del mismo ejercicio, **When** se pulsa Actualizar, **Then** ese proyecto no se actualiza, para no reescribir la parte del mes cerrado.
5. **Given** un mes cerrado que nunca se había actualizado, **When** se pulsa Actualizar, **Then** no se crean fichas de los proyectos de ese mes.
6. **Given** marzo cerrado y luego reabierto, **When** se pulsa Actualizar, **Then** los proyectos de marzo vuelven a calcularse.
7. **Given** los doce meses cerrados, **When** se pulsa Actualizar, **Then** no cambia ninguna ficha del ejercicio y la persona ve que no hay ningún mes abierto.
8. **Given** marzo cerrado en la empresa A, **When** se actualiza la empresa B, **Then** el cierre de A no afecta a B.

---

### User Story 3 - Saber qué quedó fuera (Priority: P2)

Quien pulsa Actualizar ve, al terminar, qué meses se han actualizado y qué meses se han dejado fuera por estar cerrados. No tiene que adivinar si la cifra es nueva o es la que ya estaba guardada.

**Why this priority**: El proceso puede terminar bien y, aun así, dejar meses sin tocar. Si no se dice, la persona cree que todo el ejercicio está al día.

**Independent Test**: Con marzo cerrado, la persona pulsa Actualizar y lee un aviso con marzo como mes no actualizado y con el resto como meses actualizados.

**Acceptance Scenarios**:

1. **Given** uno o varios meses cerrados, **When** Actualizar termina, **Then** se nombran los meses cerrados que no se han tocado y se indica que el resto del ejercicio sí se ha actualizado.
2. **Given** todos los meses abiertos, **When** Actualizar termina, **Then** no aparece un aviso de meses cerrados.
3. **Given** el aviso de meses cerrados, **When** la persona abre un proyecto de uno de esos meses, **Then** la ficha sigue mostrando la actualización anterior, no la que acaba de terminar.

---

### Edge Cases

- Un mes que no tiene marca de cierre está abierto. No hace falta abrir los doce meses uno a uno para poder actualizar.
- El mes de un proyecto es el mes de la fecha de su pedido de venta no anulado. Un albarán, una compra o un gasto de otro mes no cambian el mes del proyecto.
- Un proyecto sin fecha de pedido no pertenece a ningún mes cerrado y sigue pudiendo actualizarse.
- Un pedido anulado no coloca el proyecto en el mes de ese pedido.
- Si el proyecto tiene algún pedido de venta vigente del ejercicio en un mes cerrado, el proyecto entero queda fuera de esa actualización.
- Cerrar un mes no borra las fichas ya guardadas ni cambia sus importes. Tampoco crea, modifica ni anula pedidos, albaranes ni apuntes.
- Cerrar un mes no cierra el mismo mes de otra empresa ni de otro ejercicio.
- No se puede guardar un cierre sin empresa, sin ejercicio o con un mes que no exista.
- Reabrir un mes no recalcula por sí solo. Los proyectos de ese mes se calculan en la siguiente actualización.
- La primera actualización de un ejercicio, con algún mes ya cerrado, deja ese mes sin fichas nuevas y actualiza solo los meses abiertos.
- El cuadro de mando y el margen de pedidos de la misma actualización tampoco sustituyen las cifras que salen de los proyectos de un mes cerrado. Esas cifras siguen siendo las de la última actualización en la que ese mes estaba abierto.
- Una persona autorizada a pulsar Actualizar, pero que no administra, no puede cambiar el cierre y sí ve el aviso de los meses que se han dejado fuera.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Una persona administradora puede cerrar y reabrir cada mes de un ejercicio para una empresa. El control está en la administración, donde ya se configuran usuarios, perfiles y empresas.
- **FR-002**: Cada cierre identifica una empresa, un ejercicio y un mes del 1 al 12. Para esa combinación solo existe una marca. Un mes sin marca está abierto.
- **FR-003**: El cierre guarda si el mes está cerrado, qué persona lo cambió y cuándo. Una persona que no administra no puede cerrar ni reabrir.
- **FR-004**: El mes de un proyecto, dentro del ejercicio que se actualiza, es el mes de la fecha de cada pedido de venta no anulado de ese proyecto en ese ejercicio. Sin fecha de pedido, el proyecto no queda retenido por ningún cierre.
- **FR-005**: Actualizar un ejercicio solo calcula los proyectos cuyos pedidos de venta de ese ejercicio caen todos en meses abiertos. Si alguno cae en un mes cerrado, el proyecto no se actualiza.
- **FR-006**: Un proyecto no actualizado conserva sus importes y la fecha de su última actualización. Si nunca se había guardado, sigue sin ficha.
- **FR-007**: Los proyectos de los meses abiertos se calculan con las mismas reglas ya vigentes y quedan con la fecha de esta actualización.
- **FR-008**: Si los doce meses están cerrados, Actualizar no cambia fichas ni cifras del ejercicio y lo indica.
- **FR-009**: Al terminar, si hubo meses cerrados, se nombran esos meses. Si no hubo ninguno, no se muestra ese aviso.
- **FR-010**: El cierre de una empresa no afecta a otra. El cierre de un ejercicio no afecta a otro.
- **FR-011**: Cerrar o reabrir no lee el origen y no recalcula. Solo la siguiente actualización aplica el cierre.
- **FR-012**: El cierre no crea, no modifica y no anula documentos ni apuntes. No cambia el cálculo de un proyecto que sí se actualiza.

### Key Entities

- **Cierre de mes**: la marca de que un mes de un ejercicio, en una empresa, está cerrado. Si no existe, el mes está abierto. Guarda la persona y el momento del último cambio.
- **Mes del proyecto**: el mes de la fecha de un pedido de venta no anulado del proyecto dentro del ejercicio que se actualiza.
- **Actualización del ejercicio**: el proceso ya existente que vuelve a calcular la empresa y el ejercicio elegidos, limitado a partir de ahora a los meses abiertos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona administradora cierra o reabre un mes de una empresa y un ejercicio en una sola acción, y al volver a consultarlo ve el estado que acaba de dejar.
- **SC-002**: Tras Actualizar un ejercicio con meses cerrados, el 100 % de los proyectos retenidos por esos meses conserva los mismos importes y la misma fecha de actualización que antes de pulsar.
- **SC-003**: Tras esa misma actualización, el 100 % de los proyectos cuyo pedido cae solo en meses abiertos muestra la fecha de la actualización que acaba de terminar.
- **SC-004**: Con los doce meses cerrados, Actualizar deja cero proyectos modificados y la persona ve que no había meses abiertos.
- **SC-005**: Una persona que no administra no puede cambiar ningún cierre. Quien sí pulsa Actualizar ve el nombre de cada mes cerrado que no se ha tocado.

## Assumptions

- El periodo que se cierra es un mes de un ejercicio de una empresa. No hay un cierre distinto para un trimestre ni para el ejercicio entero: el ejercicio queda cerrado cuando sus doce meses lo están.
- El mes que protege a un proyecto es el de su pedido de venta, no el de un albarán, una compra o un gasto posterior. Así, «proyecto de ese mes» tiene una sola fecha de referencia.
- Si el proyecto tiene varios pedidos vigentes en el ejercicio y alguno cae en un mes cerrado, no se actualiza ninguno de sus datos. La actualización sustituye la ficha entera, y tocarla reescribiría también el mes cerrado.
- Un mes abierto se actualiza con la ficha completa, aunque el proyecto tenga albaranes o gastos en un mes que está cerrado para otros proyectos. Esos documentos pertenecen al proyecto del mes de su pedido.
- Las cifras del cuadro de mando y del margen de pedidos que proceden de proyectos no actualizados se mantienen como estaban. No se sustituyen por una lectura nueva del mes cerrado.
- El cierre lo gestiona quien ya administra usuarios y empresas. Quien solo consulta o pulsa Actualizar no cambia el cierre.
- Mientras nadie cierre un mes, Actualizar sigue cubriendo el ejercicio entero.
- Las reglas ya vigentes siguen mandando en lo que este control no cambia: misma empresa, documentos anulados fuera, y lectura del origen solo al actualizar.
