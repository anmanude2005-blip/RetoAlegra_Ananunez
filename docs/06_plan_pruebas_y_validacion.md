# SYNTHEX — Plan de pruebas y validación del MVP

**Versión:** 1.2  
**Fecha de actualización:** 12 de noviembre de 2026  
**Tipo de pruebas:** validación funcional manual sobre el entorno publicado de demostración

## 1. Objetivo

Dejar evidencia de los casos funcionales probados en SYNTHEX, en particular del flujo E2E de demanda, programación parcial con varias OP, compras, recepción, fabricación y conciliación del inventario.

## 2. Alcance

- Catálogo de componentes y productos terminados.
- Recetas versionadas y cálculo de materiales.
- Demandas, capacidad fabricable y programación en OP independientes.
- Compras, OC asociadas a demanda y recepciones REC.
- Liberación, reservas, avances ADV y consumos reales.
- Inventario de componentes y producto terminado.
- Conciliación de stock inicial, recepciones, consumos y stock actual.
- Reportes, exportación Excel y asistente IA explicativo.

## 3. Casos de prueba y estado

| ID | Escenario | Resultado esperado | Estado observado |
|---|---|---|---|
| CP-01 | Abrir Inicio y navegar a módulos | La aplicación carga y conserva navegación | Validado en capturas recientes |
| CP-02 | Consultar Productos | Se muestra el catálogo con código, nombre, tipo, costo, estado y existencia | Validado |
| CP-03 | Crear y consultar receta | Se almacena receta versionada y detalles de componentes | Validado dentro del escenario E2E AL001 |
| CP-04 | Registrar DEM y calcular requerimientos | Se muestran cantidades solicitadas, programadas, fabricadas y pendientes | Validado con DEM-008 |
| CP-05 | Calcular máximo fabricable | La nueva OP queda limitada por saldo de demanda y materiales disponibles | Validado: máximo inicial 7 para DEM-008 |
| CP-06 | Mostrar compra asociada a demanda | Se ve OC y estado; el botón para otra OC no aparece si el faltante ya está cubierto | Validado con OC-007 |
| CP-07 | Recibir materiales | La recepción aumenta stock físico y actualiza estado de OC | Validado: OC-007 recibió 5 unidades de MP007 y quedó Recibida |
| CP-08 | Crear OP posterior a recepción | Se habilita OP por el saldo pendiente | Validado: OP-011 por 3 unidades |
| CP-09 | Liberar OP y reservar | Se reservan materiales para la cantidad planeada de cada OP | Validado: OP-010 reservó 14 por componente y OP-011 6 por componente |
| CP-10 | Registrar avances ADV | Se descuentan componentes, se actualizan reservas y aumenta stock terminado | Validado con ADV-006 y ADV-007 |
| CP-11 | Completar demanda | 10 de 10 unidades fabricadas; 0 pendientes por fabricar y por programar | Validado con DEM-008 |
| CP-12 | Conciliar materiales | Stock inicial + compra recibida − consumo = stock actual | Validado para MP003, MP005 y MP007 |
| CP-13 | Costear fabricación | Costo real basado en consumos de materiales | Validado: COP 119.000 + COP 51.000 = COP 170.000 |
| CP-14 | Anular OP en Borrador | El documento se conserva y no cuenta como programación vigente | Validado: OP-009 quedó Anulada |
| CP-15 | Analizar materiales con IA | La IA explica consumo, existencias y faltantes sin modificar datos | Validado visualmente con DEM-008 |
| CP-16 | Exportar movimientos a Excel | XLSX tiene Detalle movimientos y Resumen por producto | Validado anteriormente; repetir regresión final |
| CP-17 | Filtrar por fechas en Colombia | Fechas predeterminadas corresponden a `America/Bogota` | Validado visualmente tras corregir fecha local |
| CP-18 | Revisar reportes compactos | Producción/Estados y Compras/Consumo en cuadrícula; costos a ancho completo | Validado visualmente |
| CP-19 | Restaurar escenario semilla desde la UI | Se restablece escenario inicial previa confirmación | Pendiente de verificación explícita en la versión desplegada |
| CP-20 | Normalizar fechas históricas no válidas | Mostrar `No disponible`, no `nan` ni fechas supuestas | Pendiente de regresión |

## 4. Escenario E2E validado: AL001 / DEM-008

### 4.1. Maestros y receta

Se utilizaron los siguientes artículos de ensayo:

- Producto terminado: **AL001 — Reto**.
- Componentes: MP005 — Bombillo LED (costo unitario COP 4.000), MP003 — Cable eléctrico (COP 3.500) y MP007 — Prueba (COP 1.000).
- Receta: 2 unidades de cada componente por cada AL001.
- Stock al crear DEM-008: MP005 = 30; MP003 = 40; MP007 = 15.

### 4.2. Demanda y capacidad inicial

DEM-008, descripción **Stock Mínimo**, solicitó 10 unidades. La necesidad total fue 20 unidades de cada componente.

La cantidad máxima inicial fabricable fue 7 unidades, limitada por MP007: 15 unidades físicas permiten cubrir 7 productos completos con 2 unidades por producto, dejando 1 unidad de MP007 sin asignar. Para las 3 unidades restantes se requieren 6; descontando la unidad libre, el faltante neto fue 5.

OP-009, que había sido creada antes por 10 unidades durante la reproducción inicial del problema, se anuló y se conservó en el historial. No se eliminó.

### 4.3. Programación y abastecimiento

| Documento | Acción | Resultado |
|---|---|---|
| DEM-008 | Demanda total | 10 unidades |
| OP-009 | Orden anterior | Anulada, 10 unidades; excluida de la programación vigente |
| OP-010 | Primera OP | 7 unidades, inicialmente Borrador; luego En producción |
| OC-007 | Compra del faltante | 5 unidades de MP007 |
| REC | Recepción asociada a OC-007 | Se recibieron 5 unidades de MP007; OC-007 quedó Recibida |
| OP-011 | Segunda OP | 3 unidades, luego En producción |

El identificador numérico del documento REC no se transcribe en esta evidencia; la recepción se confirma por el historial de OC-007, que mostró 5 solicitadas, 5 recibidas y 0 pendientes.

La pantalla de Demandas mostró la compra asociada, el estado y las cantidades solicitadas/recibidas/pendientes. Cuando el faltante quedó cubierto por OC-007, el sistema mostró que no era necesario generar otra OC.

### 4.4. Reservas y avances

Después de liberar ambas OP, las reservas acumuladas fueron 20 unidades por componente:

| Componente | Stock físico tras recepción, antes de consumo | Reservado total | Disponible |
|---|---:|---:|---:|
| MP005 | 30 | 20 | 10 |
| MP003 | 40 | 20 | 20 |
| MP007 | 20 | 20 | 0 |

Los avances observados fueron:

| OP | ADV | Unidades fabricadas | Consumo de cada componente | Costo de materiales |
|---|---|---:|---:|---:|
| OP-010 | ADV-006 | 7 | 14 | COP 119.000 |
| OP-011 | ADV-007 | 3 | 6 | COP 51.000 |
| **Total** | — | **10** | **20** | **COP 170.000** |

### 4.5. Conciliación final de materiales

| Material | Requerido | Stock inicial | Compra recibida | Consumido | Stock actual | Faltante |
|---|---:|---:|---:|---:|---:|---:|
| MP003 — Cable eléctrico | 20 | 40 | 0 | 20 | 20 | 0 |
| MP005 — Bombillo LED | 20 | 30 | 0 | 20 | 10 | 0 |
| MP007 — Prueba | 20 | 15 | 5 | 20 | 0 | 0 |

La conciliación cumple: stock inicial + compra recibida − consumo = stock actual para cada componente.

El costo real total de materiales fue **COP 170.000** (COP 17.000 por AL001 fabricado). No incluye mano de obra ni costos indirectos.

La tabla de materiales muestra stock inicial reconstruido mediante movimientos posteriores a la creación de la demanda. La exactitud histórica requiere que todas las variaciones de inventario queden registradas en `inventory_movements`.

### 4.6. Resultado final de DEM-008

| Indicador | Resultado |
|---|---:|
| Solicitadas | 10 |
| Programadas | 10 |
| Fabricadas | 10 |
| Pendientes por fabricar | 0 |
| Pendientes por programar | 0 |
| Estado de DEM-008 | Completada |
| OP completadas | OP-010 (7) y OP-011 (3) |
| OC asociada | OC-007 — Recibida |

## 5. Validaciones históricas adicionales

En un corte anterior de Reportes se observaron 8 órdenes (0 Borrador, 0 En producción, 5 Completadas y 3 Anuladas), 27 unidades producidas históricas y 6 solicitudes de compra recibidas. Ese corte corresponde al estado anterior a la prueba E2E de DEM-008; no debe confundirse con el total posterior de documentos del entorno.

La exportación de movimientos fue revisada previamente: contiene las hojas `Detalle movimientos` y `Resumen por producto`. La columna Usuario se presenta como no registrada porque el prototipo no persiste el usuario que ejecuta cada movimiento.

## 6. Regresiones pendientes y riesgos

- Repetir exportación Excel y filtros de fechas tras los cambios de lógica.
- Verificar restauración del escenario semilla y el acceso público de la aplicación antes de la entrega.
- Corregir presentación de fechas históricas nulas/no válidas (`nan`).
- La reconstrucción de stock inicial depende de la integridad del historial de movimientos; una instantánea en la DEM sería más robusta.
- El costo real incluye únicamente materiales directos.
- La IA depende del secreto/servicio externo configurado y no debe tratarse como autoridad transaccional.
- No hay autenticación multiusuario, roles ni `user_id` registrado en movimientos.

## 7. Criterio de salida

El flujo E2E de creación de artículos, receta, demanda, programación por disponibilidad, compra, recepción, OP sucesiva, liberación, fabricación y conciliación de materiales quedó validado visualmente el 12 de noviembre de 2026 en el entorno de demostración. Antes de la presentación final, repetir las regresiones pendientes de exportación, restauración del demo, fechas históricas y acceso de entrega.
