# SYNTHEX — Diccionario técnico de módulos y funciones Python/SQLite

**Versión:** 1.2  
**Fecha:** 12 de noviembre de 2026  

Este documento describe las responsabilidades de los módulos y las funciones utilizadas por la interfaz. Los nombres se basan en las funciones observadas en el código y en los flujos implementados; cuando una operación se realiza mediante SQL interno y no mediante una función pública separada, se describe a nivel de responsabilidad.

## 1. Convenciones generales

- Los módulos funcionales usan `get_connection()` desde `database.py`.
- Las consultas devuelven estructuras compatibles con `sqlite3.Row`, normalmente convertidas a diccionarios.
- Los valores de entrada se deben pasar mediante parámetros SQL `?`, no concatenarse directamente en las consultas.
- En operaciones que modifican varias tablas se debe mantener una transacción: `commit()` si todo termina correctamente; `rollback()` si ocurre una excepción.
- Los módulos de negocio no deben duplicar fórmulas o reglas que pertenecen a otro módulo.

## 2. `database.py`

| Función | Responsabilidad |
|---|---|
| `get_connection()` | Abre la conexión a `synthex.db`, configura `row_factory = sqlite3.Row` y activa `PRAGMA foreign_keys = ON`. |
| `init_db()` | Crea tablas si no existen, revisa y agrega columnas necesarias mediante migraciones, e inserta los datos semilla cuando `products` está vacía. |

## 3. `products.py`

| Función | Responsabilidad |
|---|---|
| `create_product(...)` | Registra un producto o componente y su existencia inicial, de acuerdo con los parámetros recibidos. |
| `get_products()` | Consulta el catálogo para los módulos de productos, recetas, demandas, compras y producción. |

## 4. `recipes.py`

| Función | Responsabilidad |
|---|---|
| `create_recipe(product_id, recipe_name, components)` | Crea una versión de receta y sus líneas de componentes. |
| `get_recipes()` | Consulta recetas y sus datos de versión/estado. |
| `get_recipe_details(recipe_id)` | Devuelve los componentes de una receta. |
| `calculate_recipe_cost(recipe_id)` | Calcula costo estimado de materiales por unidad a partir de cantidad de componente por costo unitario. |

## 5. `demands.py`

| Función | Responsabilidad |
|---|---|
| `create_demand(code, description, items)` | Registra una demanda y sus productos/cantidades. |
| `get_demands()` | Consulta demandas y totales solicitados. |
| `get_demand_production_summary(demand_id)` | Resume cantidades solicitadas, programadas, producidas y pendientes, incluyendo saldo por programar. |
| `get_demand_orders(demand_id)` | Consulta órdenes vinculadas a una demanda. |

La consulta enriquecida de materiales se encuentra en `purchases.py` como `get_demand_material_requirements(demand_id)` para combinar necesidad, stock inicial reconstruido, recepciones asociadas, consumo y stock actual.

## 6. `purchases.py`

| Función | Responsabilidad |
|---|---|
| `create_purchase_request(code, items)` | Registra una solicitud de compra independiente con líneas de materiales. |
| `create_purchase_from_demand(demand_id, code)` | Genera una solicitud desde el faltante neto de una demanda, descontando abastecimiento existente y material ya asignado según las reglas del cálculo. |
| `get_purchase_requests()` | Consulta solicitudes de compra. |
| `get_demand_purchase_requests(demand_id)` | Consulta las solicitudes asociadas a una DEM, con código y estado, para presentarlas dentro del seguimiento de la demanda. |
| `get_demand_material_requirements(demand_id)` | Calcula requerimientos, stock inicial reconstruido, recepciones relacionadas, consumo por avances de esa demanda, stock físico actual y faltante. |
| `get_purchase_details(purchase_id)` | Consulta cantidades solicitadas, recibidas y costos por material. |
| `get_purchase_receipts(purchase_id)` | Consulta historial de recepciones de una solicitud. |
| `receive_purchase(receipt_code, purchase_id, items)` | Registra una recepción parcial o total, sus detalles y las entradas correspondientes de inventario. |

## 7. `production.py`

| Función | Responsabilidad |
|---|---|
| `create_production_order(code, product_id, quantity, demand_id=None)` | Crea orden en Borrador, conserva la receta seleccionada y costo estimado; valida que no se exceda la cantidad aún no programada de la demanda cuando aplica. |
| `get_max_producible_quantity(product_id, pending_quantity)` | Calcula el máximo adicional fabricable limitado por el saldo pendiente y por materiales disponibles; descuenta reservas activas y compromisos de órdenes en Borrador. |
| `release_production_order(order_id)` | Valida disponibilidad de componentes para la cantidad planeada completa de esa OP, crea reservas y cambia el estado a En producción. Si falta cualquier componente, rechaza la liberación de esa OP. |
| `register_production_advance(code, order_id, quantity, notes="")` | Registra avance, valida reservas, registra consumos reales, descuenta componentes, aumenta inventario terminado y actualiza el estado de la orden. |
| `cancel_production_order(order_id)` | Anula una orden en Borrador y conserva el documento. |
| `get_production_orders()` | Consulta órdenes, productos, demanda, cantidades y estado. |
| `get_production_advances(order_id)` | Consulta avances de una orden y su costo de materiales calculado desde los consumos. |
| `get_advance_consumptions(advance_id)` | Consulta los materiales consumidos por un avance. |

## 8. `inventory.py`

| Función | Responsabilidad |
|---|---|
| `get_inventory()` | Consulta stock físico y reservas activas; calcula disponibilidad y valor de inventario. |
| `get_inventory_movements(product_id=None, start_date=None, end_date=None)` | Consulta movimientos, opcionalmente por producto y rango de fechas. Los límites de fecha se interpretan en `America/Bogota` y se convierten a UTC para la consulta. |
| `get_inventory_summary()` | Calcula referencias, unidades físicas, reservadas, disponibles, valor y referencias sin disponibilidad. |

## 9. `reports.py`

| Función | Responsabilidad |
|---|---|
| `get_production_summary()` | Resume total de órdenes, borrador, en producción, completadas, anuladas, unidades programadas vigentes, unidades producidas históricas y pendientes vigentes. |
| `get_purchase_summary()` | Resume solicitudes registradas, pendientes y recibidas. |
| `get_material_consumption()` | Agrupa cantidades y costos de consumo real por material. |
| `get_production_costs()` | Consulta costo estimado y consumo real agrupado por orden. |

## 10. `ai_assistant.py`

| Función | Responsabilidad |
|---|---|
| `analyze_material_shortages(context)` | Envía contexto calculado por SYNTHEX al servicio de IA para redactar una explicación de faltantes. La IA no decide ni ejecuta modificaciones de inventario o producción. |

## 11. `date_utils.py`

| Función | Responsabilidad |
|---|---|
| `format_colombia_datetime(value)` | Convierte/representa una marca de tiempo en la zona `America/Bogota` y la presenta en formato legible. Los valores ausentes se muestran como `No disponible`. |

## 12. Generación de consecutivos

La interfaz utiliza un generador de documentos para asignar consecutivos a:

- `DEM`: demanda.
- `OC`: solicitud de compra.
- `REC`: recepción.
- `OP`: orden de producción.
- `ADV`: avance de producción.

La generación automática de estos códigos está incorporada en los flujos del MVP.

## 13. Operaciones SQL y tablas relacionadas

| Operación | Tablas que normalmente intervienen |
|---|---|
| Alta de producto y stock inicial | `products`, `stock_balances` |
| Crear receta | `recipes`, `recipe_details` |
| Registrar demanda | `demands`, `demand_details` |
| Crear solicitud de compra | `purchase_requests`, `purchase_details` |
| Consultar compras asociadas a demanda | `purchase_requests`, `purchase_details`, `purchase_receipts`, `purchase_receipt_details` |
| Recibir compra | `purchase_receipts`, `purchase_receipt_details`, `stock_balances`, `inventory_movements` |
| Crear orden | `production_orders` |
| Liberar orden | `production_orders`, `reservations` |
| Registrar avance | `production_advances`, `production_consumptions`, `reservations`, `stock_balances`, `inventory_movements`, `products`, `production_orders` |

## 14. Límites conocidos

- La base no almacena `user_id` en movimientos ni en documentos.
- No hay auditoría de antes/después de cambios.
- Las fechas de liberación, finalización y anulación existen para eventos registrados después de incorporar esos campos; los datos históricos anteriores pueden quedar nulos.
- El costo real de fabricación reportado cubre consumos de materiales, no costos de conversión completos.
- El stock inicial que se muestra en la ficha de materiales de una DEM se reconstruye con `inventory_movements`; para garantizar la exactitud deben estar registrados todos los movimientos posteriores a la creación de la demanda. Una instantánea de stock al crear DEM sería una mejora futura.
