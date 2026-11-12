# SYNTHEX — Diagrama del proceso operativo

**Versión:** 1.2  
**Fecha:** 12 de noviembre de 2026

## 1. Resumen del flujo vigente

El proceso conecta la preparación del catálogo y las recetas con la demanda, la programación por disponibilidad, el abastecimiento, la producción y la conciliación del inventario.

1. Registrar artículos: componentes y productos terminados.
2. Crear una receta versionada con cantidades de componentes por unidad.
3. Registrar la DEM con la cantidad total requerida.
4. Calcular los materiales requeridos y la cantidad máxima fabricable, considerando inventario utilizable, reservas y compromisos de órdenes en Borrador.
5. Crear una primera OP independiente por la cantidad que se puede fabricar ahora. El saldo continúa pendiente por programar.
6. Identificar el faltante neto y revisar OC ya asociadas. Mostrar documento y estado; evitar duplicar compras que ya cubren ese faltante.
7. Generar OC solo por la cantidad no cubierta y registrar recepción REC. La solicitud no cambia el inventario; la recepción sí.
8. Recalcular disponibilidad y crear otra OP por el saldo pendiente de la DEM.
9. Liberar cada OP cuando haya materiales para toda su cantidad planeada; al liberar se reservan componentes.
10. Registrar avances ADV. El consumo reduce componentes físicos, actualiza reservas y aumenta el producto terminado.
11. Repetir avances hasta completar cada OP y luego conciliar la DEM, las OC, las recepciones, los consumos y el stock actual.

## 2. Diagrama general

- `07_diagrama_proceso.mmd`: fuente Mermaid editable.
- `07_diagrama_proceso.dot`: fuente Graphviz alternativa.
- `07_diagrama_proceso.svg`: render vectorial.
- `07_diagrama_proceso.png`: render PNG para presentación.

## 3. Flujo E2E demostrado

El escenario **AL001 / DEM-008** y sus documentos OP-010, OC-007, OP-011, ADV-006 y ADV-007 se documentan paso a paso en `10_guia_prueba_e2e_demanda_produccion_parcial.md`. El archivo `10_flujo_e2e_demanda_produccion_parcial.mmd` y sus versiones PNG/SVG representan la secuencia concreta de prueba.

## 4. Reglas del proceso

- Una DEM puede vincularse con varias OP independientes; la suma programada no puede superar la cantidad solicitada.
- Cada OP conserva su cantidad planeada y la receta utilizada. No se transforma una OP completa en una OP parcialmente liberada.
- El máximo fabricable considera stock físico asignable, reservas activas y compromisos de órdenes en Borrador.
- La creación de una OC no incrementa existencias; solo una recepción REC confirmada produce una entrada de inventario.
- Una OC asociada a una DEM se muestra con su estado y cantidades solicitadas/recibidas; no debe generarse otra OC si el faltante ya está cubierto.
- La liberación reserva componentes, pero no los consume físicamente.
- El avance ADV registra consumo real, reduce componentes y aumenta producto terminado.
- Las órdenes Borrador pueden anularse y conservarse como historial; las órdenes anuladas no cuentan en la programación vigente.
- La IA explica los faltantes usando los datos calculados, pero no cambia inventario, cantidades, compras u órdenes.
- El stock inicial mostrado en la ficha de una DEM se reconstruye con movimientos; requiere trazabilidad completa para ser confiable.
