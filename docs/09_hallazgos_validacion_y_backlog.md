# SYNTHEX — Hallazgos de validación y backlog

**Versión:** 1.1  
**Fecha:** 12 de noviembre de 2026  
**Propósito:** registrar los hallazgos corregidos, su evidencia y las mejoras que permanecen pendientes.

## 1. Estado de hallazgos

| ID | Área | Hallazgo | Estado |
|---|---|---|---|
| H-01 | Demandas / Producción | La cantidad de cada OP debe limitarse a lo que permite el saldo de demanda y la disponibilidad real de materiales. | Corregido y validado E2E con DEM-008: OP-010 por 7 y OP-011 por 3 |
| H-02 | Compras / Demanda | La DEM debe mostrar OC asociadas y evitar sugerir compras duplicadas cuando los faltantes están cubiertos. | Corregido y validado con OC-007: 5 unidades MP007, recibida |
| H-03 | Catálogo / Fechas | Algunos productos históricos muestran `nan` en Fecha de creación. | Pendiente de corrección/regresión |
| H-04 | Reportes / Diseño | Cuadrícula ejecutiva, tarjetas y paneles sombreados. | Validado visualmente |
| H-05 | Trazabilidad histórica | El stock inicial se reconstruye a partir de movimientos posteriores a la DEM; requiere registro completo de movimientos. | Limitación documentada; evaluar instantánea de stock al crear DEM en Fase 2 |

## 2. Comportamiento validado para H-01 y H-02

- La DEM mantiene su cantidad total solicitada.
- `get_max_producible_quantity()` limita la cantidad de una nueva OP a la cantidad fabricable con el stock asignable y al saldo no programado.
- Una demanda puede asociarse a varias OP independientes; las órdenes anuladas se conservan, pero no cuentan como programación vigente.
- La compra desde demanda calcula el faltante neto sin volver a solicitar componentes ya cubiertos por materiales disponibles, reservas de otras órdenes y compras pendientes.
- `get_demand_purchase_requests()` permite mostrar las OC asociadas con código y estado.
- `get_demand_material_requirements()` calcula requerimiento, stock inicial reconstruido, compras recibidas, consumo por los avances de la DEM, stock actual y faltante.
- Después de recibir OC, se recalcula el máximo fabricable y puede crearse la OP del saldo.
- No se agregó un campo `released_quantity`; no se modifica la cantidad planeada de una OP ya creada.

## 3. Evidencia: DEM-008 / AL001

La prueba se ejecutó el 12 de noviembre de 2026 con AL001 — Reto y una receta de 2 unidades por componente (MP005, MP003 y MP007) por cada producto terminado.

Stock inicial: MP005 30, MP003 40, MP007 15. DEM-008 solicitó 10 unidades; requerimiento total: 20 por cada material. MP007 limitó el máximo fabricable inicial a 7. El faltante neto para producir las 3 unidades restantes fue 5 unidades de MP007.

| Documento | Cantidad / acción | Resultado |
|---|---|---|
| OP-009 | Orden antigua por 10 | Anulada y conservada como historial |
| OP-010 | Primera OP por 7 | Liberada y completada |
| OC-007 | Compra MP007 por 5 | Recibida completamente; 5 solicitadas, 5 recibidas, 0 pendientes |
| OP-011 | Segunda OP por 3 | Liberada y completada |
| ADV-006 | Avance de OP-010 por 7 | Consumo de 14 unidades por componente; COP 119.000 |
| ADV-007 | Avance de OP-011 por 3 | Consumo de 6 unidades por componente; COP 51.000 |

Resultado DEM-008: 10 solicitadas, 10 programadas, 10 fabricadas, 0 pendientes por fabricar y 0 pendientes por programar. Estado Completada.

### Conciliación de materiales

| Material | Requerido | Stock inicial | Compra recibida | Consumido | Stock actual | Faltante |
|---|---:|---:|---:|---:|---:|---:|
| MP003 — Cable eléctrico | 20 | 40 | 0 | 20 | 20 | 0 |
| MP005 — Bombillo LED | 20 | 30 | 0 | 20 | 10 | 0 |
| MP007 — Prueba | 20 | 15 | 5 | 20 | 0 | 0 |

Costo real total de materiales: **COP 170.000**. No incluye mano de obra ni costos indirectos.

## 4. Limitación del stock inicial reconstruido

La ficha de materiales calcula el stock inicial restando del stock físico actual los movimientos netos registrados después de la creación de la DEM. Las recepciones de compras asociadas se muestran por separado y el consumo se obtiene de los avances de las OP vinculadas a la DEM.

El cálculo presupone que todas las variaciones de inventario se registran en `inventory_movements` con marcas de tiempo válidas. Un ajuste directo a `stock_balances` sin movimiento, una marca temporal incorrecta o eventos no registrados puede afectar el stock inicial reconstruido. Se recomienda evaluar una instantánea explícita de existencias al registrar una DEM.

## 5. Pendientes y backlog

1. **H-03 — Fechas históricas:** normalizar valores nulos o no válidos a `No disponible`, sin inventar fechas.
2. **H-05 — Instantánea de stock:** evaluar persistir el stock inicial por componente al crear una DEM para que la conciliación histórica no dependa exclusivamente de reconstruir movimientos.
3. **Regresión de cierre:** repetir exportación Excel, filtros de fechas, restauración del demo y revisión del enlace público tras los cambios funcionales.
4. **Fase 2:** auditoría, usuarios/roles, trazabilidad de responsable y robustecimiento de proveedores/abastecimiento.

## 6. Criterio de salida

H-01 y H-02 están cerrados con evidencia visual del flujo E2E AL001 / DEM-008. El MVP puede demostrar creación de artículos, receta, demanda, programación parcial con OP independientes, abastecimiento, recepción, fabricación y conciliación del inventario. Las limitaciones H-03/H-05 y las regresiones enumeradas deben comunicarse y priorizarse antes de una evolución productiva.
