# SYNTHEX — Modelo de Datos y Relaciones

**Versión:** 1.0  
**Estado:** Diseño inicial para el MVP  
**Base de datos:** SQLite  
**Motor de desarrollo:** Python

---

## 1. Objetivo

Definir la estructura de almacenamiento de información de SYNTHEX, identificando las entidades principales, sus atributos y las relaciones necesarias para gestionar el proceso de fabricación.

El modelo debe permitir trabajar con diferentes productos y recetas sin depender de información fija o exclusiva de la lámpara de demostración.

## 2. Principios de diseño

- Cada producto tendrá un identificador único.
- Un producto podrá ser un componente o un producto terminado.
- Un producto terminado podrá tener varias versiones de receta.
- Una demanda podrá generar varias órdenes de producción.
- Una orden conservará la versión de receta utilizada.
- Los inventarios físicos y las reservas se gestionarán por separado.
- Los movimientos históricos conservarán su trazabilidad.
- Las compras incrementarán el inventario únicamente al recibir los materiales.
- Los registros relacionados con una operación crítica deberán actualizarse de forma consistente.

## 3. Entidades principales

### 3.1. Productos (`products`)

Almacena el catálogo de productos y componentes.

Atributos principales:

- `id`: identificador único.
- `code`: código del producto.
- `name`: nombre.
- `product_type`: componente o terminado.
- `unit`: unidad de medida.
- `unit_cost`: costo unitario de referencia.
- `status`: activo o inactivo.
- `created_at`: fecha de creación.

### 3.2. Recetas (`recipes`)

Almacena las versiones de las recetas de fabricación.

Atributos:

- `id`: identificador.
- `product_id`: producto terminado asociado.
- `version`: número de versión.
- `status`: estado de la receta.
- `created_at`: fecha de creación.

### 3.3. Detalle de recetas (`recipe_details`)

Define los componentes y las cantidades necesarias para fabricar un producto.

Atributos:

- `id`: identificador.
- `recipe_id`: receta asociada.
- `component_id`: producto componente.
- `quantity`: cantidad necesaria por unidad terminada.

### 3.4. Demandas (`demands`)

Registra las solicitudes de fabricación.

Atributos:

- `id`: identificador.
- `demand_number`: número de demanda.
- `request_date`: fecha de solicitud.
- `status`: estado.
- `notes`: observaciones.

### 3.5. Detalle de demandas (`demand_details`)

Almacena los productos y cantidades solicitadas.

Atributos:

- `id`: identificador.
- `demand_id`: demanda asociada.
- `product_id`: producto solicitado.
- `quantity_requested`: cantidad solicitada.

### 3.6. Solicitudes de compra (`purchase_requests`)

Registra las necesidades de compra de componentes.

Atributos:

- `id`: identificador.
- `request_number`: número de solicitud.
- `request_date`: fecha.
- `status`: estado.

### 3.7. Detalle de compras (`purchase_details`)

Almacena los componentes y las cantidades solicitadas.

Atributos:

- `id`: identificador.
- `purchase_request_id`: solicitud asociada.
- `product_id`: componente.
- `quantity_requested`: cantidad solicitada.
- `unit_cost`: costo estimado de compra.

### 3.8. Recepciones de compra (`purchase_receipts`)

Registra la entrada física de los materiales comprados.

Atributos:

- `id`: identificador.
- `purchase_request_id`: solicitud relacionada.
- `receipt_date`: fecha de recepción.
- `status`: estado.

### 3.9. Detalle de recepciones (`purchase_receipt_details`)

Registra las cantidades efectivamente recibidas.

Atributos:

- `id`: identificador.
- `receipt_id`: recepción asociada.
- `purchase_detail_id`: detalle de compra relacionado.
- `quantity_received`: cantidad recibida.
- `unit_cost`: costo real unitario de recepción.

### 3.10. Órdenes de producción (`production_orders`)

Registra las órdenes de fabricación.

Atributos:

- `id`: identificador.
- `order_number`: número de orden.
- `demand_id`: demanda asociada.
- `product_id`: producto terminado.
- `recipe_id`: versión de receta utilizada.
- `quantity_planned`: cantidad planeada.
- `quantity_produced`: cantidad terminada acumulada.
- `status`: estado de la orden.
- `created_at`: fecha de creación.

### 3.11. Reservas (`reservations`)

Registra los materiales comprometidos para cada orden.

Atributos:

- `id`: identificador.
- `production_order_id`: orden asociada.
- `product_id`: componente reservado.
- `quantity_reserved`: cantidad reservada.
- `quantity_consumed`: cantidad consumida.
- `status`: activa, consumida o liberada.

### 3.12. Avances de producción (`production_advances`)

Registra cada avance realizado sobre una orden.

Atributos:

- `id`: identificador.
- `production_order_id`: orden relacionada.
- `advance_date`: fecha del avance.
- `quantity_completed`: unidades terminadas en el avance.
- `notes`: observaciones.

### 3.13. Consumos de producción (`production_consumptions`)

Almacena los materiales efectivamente utilizados en cada avance.

Atributos:

- `id`: identificador.
- `production_advance_id`: avance asociado.
- `product_id`: componente consumido.
- `quantity_consumed`: cantidad consumida.
- `unit_cost`: costo unitario aplicado.

### 3.14. Existencias (`stock_balances`)

Almacena el saldo actual de cada producto.

Atributos:

- `id`: identificador.
- `product_id`: producto.
- `physical_quantity`: cantidad física.
- `updated_at`: fecha de actualización.

La cantidad reservada se obtiene de las reservas activas. La cantidad disponible se calcula así:

**Disponible = Existencia física − Cantidad reservada.**

### 3.15. Movimientos de inventario (`inventory_movements`)

Conserva el historial de entradas, salidas y ajustes.

Atributos:

- `id`: identificador.
- `product_id`: producto.
- `movement_type`: entrada, salida o ajuste.
- `quantity`: cantidad.
- `unit_cost`: costo unitario aplicado.
- `reference_type`: tipo de documento relacionado.
- `reference_id`: identificador del documento relacionado.
- `movement_date`: fecha del movimiento.

## 4. Relaciones entre entidades

- Un producto terminado puede tener muchas versiones de receta.
- Una receta puede contener varios componentes.
- Un componente puede estar presente en diferentes recetas.
- Una demanda puede tener varios detalles.
- Una demanda puede generar varias órdenes de producción.
- Una orden de producción utiliza una versión específica de receta.
- Una orden puede tener varias reservas.
- Una orden puede registrar varios avances.
- Un avance puede tener varios registros de consumo.
- Una solicitud de compra puede contener varios componentes.
- Una solicitud de compra puede tener varias recepciones.
- Cada producto puede tener múltiples movimientos de inventario.
- Cada producto tendrá un registro de existencias.

## 5. Representación conceptual

```text
PRODUCTS
   |
   |---- RECIPES ---- RECIPE_DETAILS ---- PRODUCTS
   |
   |---- DEMAND_DETAILS ---- DEMANDS
                                  |
                                  |
                           PRODUCTION_ORDERS
                                  |
                   --------------|--------------
                   |             |              |
              RESERVATIONS  PRODUCTION_ADVANCES |
                                  |              |
                         PRODUCTION_CONSUMPTIONS|
                                                 |
                                           INVENTORY_MOVEMENTS

PURCHASE_REQUESTS
       |
PURCHASE_DETAILS
       |
PURCHASE_RECEIPTS
       |
PURCHASE_RECEIPT_DETAILS
       |
INVENTORY_MOVEMENTS
```

## 6. Reglas de integridad

1. No se permitirá registrar una orden liberada si no existe disponibilidad suficiente de componentes.
2. La creación de una orden no descontará físicamente el inventario.
3. La liberación de una orden generará las reservas correspondientes.
4. Los consumos reales reducirán el inventario físico y la reserva correspondiente.
5. La terminación de unidades generará una entrada al inventario del producto terminado.
6. Las operaciones de consumo y producción se registrarán de forma transaccional.
7. Una compra pendiente no aumentará las existencias.
8. Las recepciones incrementarán las existencias únicamente por las cantidades recibidas.
9. Las recetas utilizadas por órdenes existentes no cambiarán cuando se cree una nueva versión.
10. Los movimientos históricos no se eliminarán directamente.

## 7. Consideraciones técnicas

- Se utilizarán claves primarias para identificar los registros.
- Se utilizarán claves foráneas para relacionar las entidades.
- Se habilitarán las restricciones de integridad referencial de SQLite.
- Las cantidades y costos se almacenarán con precisión decimal apropiada para evitar errores de cálculo.
- Las operaciones críticas utilizarán transacciones de base de datos.
- Se utilizará una estrategia de costo promedio ponderado para las entradas de componentes en el MVP.
- El costo real de producción se calculará con base en los consumos registrados y sus costos unitarios históricos.

## 8. Consideraciones de demostración

La base de datos se inicializará automáticamente con los productos y componentes de la lámpara de escritorio.

La estructura será genérica y permitirá crear nuevos productos, componentes y recetas desde la aplicación.

Se implementará una función de restauración que recuperará el escenario inicial de demostración.

---

**Nota:** Este modelo representa el diseño lógico inicial. Los nombres definitivos de columnas, tipos de datos, restricciones e índices se establecerán durante la implementación de SQLite.
