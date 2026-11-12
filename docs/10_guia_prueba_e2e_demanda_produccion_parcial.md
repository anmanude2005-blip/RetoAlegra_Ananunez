# SYNTHEX — Guía de prueba end-to-end (E2E)

**Versión:** 1.0  
**Fecha de ejecución:** 12 de noviembre de 2026  
**Escenario:** AL001 — Reto / DEM-008 — Stock Mínimo  
**Objetivo:** demostrar el recorrido completo desde el alta de artículos y receta hasta la fabricación parcial en OP independientes y la conciliación final de inventario.

Los códigos DEM-008, OP-009, OP-010, OP-011, OC-007, ADV-006 y ADV-007 son los consecutivos de esta ejecución observada. En una repetición nueva, SYNTHEX asignará los siguientes consecutivos disponibles.

## 1. Resultado esperado

Una demanda por 10 unidades de AL001 debe resolverse con dos órdenes independientes porque el inventario inicial solo permite fabricar 7 unidades. Se compra y recibe el faltante neto de 5 unidades de MP007 y, tras la recepción, se programa una segunda OP por las 3 unidades restantes.

Al cierre, DEM-008 debe mostrar 10 solicitadas, 10 programadas, 10 fabricadas, 0 pendientes por fabricar y 0 pendientes por programar. OC-007 debe figurar Recibida y la tabla de materiales debe conciliar stock inicial, compra recibida, consumo y stock actual.

## 2. Maestros del escenario

### 2.1. Artículos

| Código | Nombre | Tipo | Unidad | Costo unitario | Stock al crear DEM |
|---|---|---|---|---:|---:|
| AL001 | Reto | Terminado | Unidad | COP 1.000 | 0 |
| MP005 | Bombillo LED | Componente | Unidad | COP 4.000 | 30 |
| MP003 | Cable eléctrico | Componente | Unidad | COP 3.500 | 40 |
| MP007 | Prueba | Componente | Unidad | COP 1.000 | 15 |

Los costos y existencias de esta tabla corresponden al entorno de prueba observado. MP007 fue un artículo creado para el ejercicio, no parte del catálogo semilla original.

### 2.2. Receta

La receta activa de AL001 requiere por cada unidad terminada:

| Componente | Cantidad por AL001 |
|---|---:|
| MP005 — Bombillo LED | 2 |
| MP003 — Cable eléctrico | 2 |
| MP007 — Prueba | 2 |

Por tanto, la DEM por 10 unidades necesita 20 unidades de cada componente.

## 3. Procedimiento E2E

### Paso 1 — Crear artículos

En **Productos**, registrar los componentes MP005, MP003 y MP007 con sus costos y existencias; registrar el producto terminado AL001 — Reto con unidad Unidad. Verificar que AL001 esté clasificado como Terminado y los tres materiales como Componente.

### Paso 2 — Crear la receta

En **Recetas**, crear la receta activa de AL001 y asignar 2 unidades de MP005, 2 de MP003 y 2 de MP007 por unidad fabricada. Guardar y verificar el detalle de la receta.

### Paso 3 — Registrar la demanda DEM-008

En **Demandas**, registrar una demanda por 10 unidades de AL001 con descripción **Stock Mínimo**. Abrir la DEM y revisar los indicadores y requerimientos.

### Paso 4 — Calcular necesidad y cantidad fabricable

| Componente | Requerido para 10 | Stock inicial | Capacidad por stock |
|---|---:|---:|---:|
| MP005 | 20 | 30 | 15 productos |
| MP003 | 20 | 40 | 20 productos |
| MP007 | 20 | 15 | 7 productos completos |

La capacidad de la demanda está limitada por MP007: `min(10, 15 // 2, 40 // 2, 30 // 2) = 7` unidades fabricables inicialmente. Después de asignar 14 unidades de MP007 a esas 7 unidades, queda 1 unidad libre. Para las 3 unidades restantes se requieren 6; al descontar la unidad libre, el faltante neto es 5.

### Paso 5 — Conservar la OP anterior como historial

En la reproducción inicial del problema existía OP-009 por 10 unidades en Borrador. Se anuló desde la aplicación y se conservó el documento en el historial. No se eliminó de la base. Las órdenes anuladas no cuentan en la programación vigente de la DEM.

### Paso 6 — Crear la primera orden OP-010

En la sección **Programar nueva orden de producción** de DEM-008, SYNTHEX muestra que se pueden fabricar hasta 7 unidades. Crear la OP por 7.

Resultado observado: **OP-010 — 7 unidades — Borrador**, asociada a DEM-008. La DEM conserva 3 unidades pendientes por programar.

### Paso 7 — Generar y consultar la compra OC-007

Generar la solicitud de compra por el faltante neto de 5 unidades de MP007. En la sección **Solicitudes de compra asociadas** de DEM-008, comprobar que aparezca OC-007, el estado, el material, las cantidades solicitadas, recibidas y pendientes.

Al existir una OC que cubre el faltante, la interfaz debe informar que no hace falta generar otra solicitud. Una compra pendiente no aumenta el stock físico.

### Paso 8 — Registrar la recepción REC de OC-007

En **Compras**, abrir OC-007 y registrar la recepción de 5 unidades de MP007. La solicitud queda con estado **Recibida** y 0 unidades pendientes de recibir. El inventario físico de MP007 aumenta de 15 a 20.

La evidencia disponible confirma la recepción completa vinculada a OC-007; el consecutivo exacto del documento REC no se transcribe en esta guía porque no fue legible en la captura consultada.

### Paso 9 — Crear la segunda orden OP-011

Volver a DEM-008. Con el material recibido, la pantalla permite programar 3 unidades. Crear una segunda OP por 3.

Resultado observado: **OP-011 — 3 unidades — Borrador**, asociada a DEM-008. El seguimiento muestra 10 programadas y 0 pendientes por programar.

### Paso 10 — Liberar ambas OP y reservar materiales

En **Producción**, liberar OP-010 por 7 y OP-011 por 3. La liberación reserva componentes, pero no descuenta todavía el stock físico.

| Componente | Stock físico antes de avances | Reserva OP-010 | Reserva OP-011 | Reservado total | Disponible después de liberar ambas |
|---|---:|---:|---:|---:|---:|
| MP005 | 30 | 14 | 6 | 20 | 10 |
| MP003 | 40 | 14 | 6 | 20 | 20 |
| MP007 | 20 | 14 | 6 | 20 | 0 |

Ambas órdenes deben quedar en **En producción**. No debe existir reserva superior a la existencia física.

### Paso 11 — Fabricar las 7 unidades de OP-010

En OP-010, registrar un avance de 7 unidades. Resultado observado: documento ADV-006, OP-010 queda Completada, consume 14 unidades de cada componente y registra COP 119.000 de costo de materiales.

Detalle del costo: MP005 14 × COP 4.000 = COP 56.000; MP003 14 × COP 3.500 = COP 49.000; MP007 14 × COP 1.000 = COP 14.000.

### Paso 12 — Fabricar las 3 unidades de OP-011

En OP-011, registrar un avance de 3 unidades. Resultado observado: documento ADV-007, OP-011 queda Completada, consume 6 unidades de cada componente y registra COP 51.000 de costo de materiales.

Detalle del costo: MP005 6 × COP 4.000 = COP 24.000; MP003 6 × COP 3.500 = COP 21.000; MP007 6 × COP 1.000 = COP 6.000.

## 4. Conciliación final de inventario y demanda

### 4.1. Materiales componentes

La tabla de materiales de DEM-008 presenta los datos siguientes:

| Material | Requerido | Stock inicial | Compra recibida | Consumido | Stock actual | Faltante |
|---|---:|---:|---:|---:|---:|---:|
| MP003 — Cable eléctrico | 20 | 40 | 0 | 20 | 20 | 0 |
| MP005 — Bombillo LED | 20 | 30 | 0 | 20 | 10 | 0 |
| MP007 — Prueba | 20 | 15 | 5 | 20 | 0 | 0 |

La conciliación se cumple para cada componente:

`Stock inicial + compra recibida - consumido = stock actual`

### 4.2. Producto terminado

Los dos avances registran una entrada acumulada de 10 unidades de AL001 al inventario de producto terminado. El inventario inicial de AL001 observado antes de la fabricación era 0; por tanto, el saldo esperado después de los dos avances es 10 unidades.

### 4.3. Seguimiento de la demanda

| Indicador de DEM-008 | Valor final |
|---|---:|
| Solicitadas | 10 |
| Programadas | 10 |
| Fabricadas | 10 |
| Pendientes por fabricar | 0 |
| Pendientes por programar | 0 |
| Estado | Completada |

Órdenes asociadas:

- OP-009: 10 unidades, Anulada (histórica; no cuenta en la programación vigente).
- OP-010: 7 unidades, Completada.
- OP-011: 3 unidades, Completada.

Compra asociada: OC-007, 5 unidades de MP007, Recibida.

### 4.4. Costo de materiales

| Orden | Avance | Unidades | Costo de materiales |
|---|---|---:|---:|
| OP-010 | ADV-006 | 7 | COP 119.000 |
| OP-011 | ADV-007 | 3 | COP 51.000 |
| **Total** | — | **10** | **COP 170.000** |

Costo real de materiales por AL001: COP 17.000. La cifra no incluye mano de obra, depreciación ni costos indirectos.

## 5. Qué se debe revisar al repetir la prueba

- La cantidad ofrecida para una nueva OP nunca supera la capacidad fabricable ni el saldo sin programar.
- Las OP asociadas a una misma DEM no suman más que lo solicitado.
- OP anuladas se conservan en historial y no cuentan como programación vigente.
- Las OC asociadas aparecen en la demanda con estado y cantidades solicitadas/recibidas/pendientes.
- Una compra existente que cubre el faltante impide sugerir una OC duplicada.
- La recepción, no la creación de la OC, incrementa stock.
- La liberación crea reservas, pero solo ADV registra el consumo físico.
- Los avances aumentan producto terminado y descuentan componentes.
- La demanda termina con cero unidades pendientes.
- La conciliación de materiales cumple stock inicial + recepciones − consumo = stock actual.

## 6. Nota sobre el stock inicial reconstruido

El campo **Stock inicial** de la tabla de materiales se calcula retrocediendo desde el stock físico actual con los movimientos netos registrados después de la creación de la DEM. No es una instantánea persistida. Para que ese valor sea confiable, todos los ajustes y movimientos de inventario deben quedar registrados en `inventory_movements`; una variación directa de `stock_balances` sin movimiento puede distorsionar el resultado. Para una versión posterior se recomienda guardar snapshot por componente en el momento de crear la demanda.
