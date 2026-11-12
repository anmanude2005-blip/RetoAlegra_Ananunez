# SYNTHEX — Manual de usuario

**Versión:** 1.2  
**Fecha:** 12 de noviembre de 2026  
**Perfil contemplado:** Administrador  

## 1. Ingresar a la aplicación

Abrir el enlace publicado de SYNTHEX. La navegación está disponible en el menú lateral: Inicio, Productos, Recetas, Demandas, Compras, Producción, Inventario y Reportes.

La versión actual usa un solo perfil de trabajo y no solicita inicio de sesión multiusuario.

## 2. Inicio

El panel presenta:

- Referencias del catálogo.
- Unidades físicas del inventario.
- Órdenes activas.
- Compras pendientes.
- Órdenes registradas y unidades programadas, producidas y pendientes.
- Desglose de órdenes por estado: Borrador, En producción, Completada y Anulada.

El total de órdenes debe coincidir con la suma de los cuatro estados. Las unidades programadas y pendientes consideran órdenes vigentes, mientras que las unidades producidas se presentan como acumulado histórico.

## 3. Registrar productos

1. Abrir **Productos**.
2. Expandir **Registrar nuevo producto**.
3. Ingresar código y nombre.
4. Seleccionar tipo: Componente o Terminado.
5. Definir unidad, costo unitario y existencia inicial.
6. Guardar y verificar el producto en la tabla.

El producto terminado puede ser fabricado con una receta; los componentes se utilizan en las listas de materiales.

## 4. Crear una receta

1. Abrir **Recetas**.
2. Expandir **Crear nueva receta**.
3. Seleccionar el producto terminado.
4. Asignar un nombre a la receta.
5. Seleccionar los componentes.
6. Indicar la cantidad de cada componente necesaria para producir una unidad.
7. Guardar la receta.
8. Revisar versión, componentes y costo estimado por unidad.

Las órdenes conservan la versión de receta con la que se crearon.

## 5. Registrar y programar una demanda

1. Abrir **Demandas**.
2. Expandir **Registrar nueva demanda**.
3. Seleccionar el producto terminado, ingresar la cantidad solicitada y una descripción, y guardar.
4. Abrir la DEM creada. Revisar los indicadores: Solicitadas, Programadas, Fabricadas, Pendientes por fabricar y Pendientes por programar.
5. En **Programar nueva orden de producción**, revisar el máximo fabricable que muestra SYNTHEX con el inventario disponible. La cantidad propuesta no puede superar el saldo pendiente por programar.
6. Crear la OP por la cantidad indicada. La DEM conserva su cantidad total; el saldo no programado permanece pendiente.
7. Revisar la tabla **Materiales requeridos**. Compara requerimiento total, stock inicial, compra recibida, consumo, stock actual y faltante.
8. Si hay faltantes, consultar **Solicitudes de compra asociadas**. La pantalla muestra el código de OC, estado, material, cantidad solicitada, cantidad recibida y saldo pendiente de recibir. No se ofrece generar otra solicitud cuando la compra vinculada ya cubre el faltante.
9. Si hace falta abastecimiento adicional, generar la OC solo por el faltante no cubierto. La solicitud no incrementa el inventario.
10. Cuando se registre la recepción REC, volver a la DEM. SYNTHEX recalcula la capacidad y permite crear otra OP por el saldo pendiente.
11. Repetir programación/abastecimiento hasta que Pendientes por programar sea 0.

La IA puede explicar los faltantes con el contexto calculado por el sistema. No crea compras ni modifica stock por su cuenta.

### Cómo leer la tabla de materiales

- **Requerido:** cantidad total de componente necesaria para la demanda completa, según la receta activa consultada.
- **Stock inicial:** existencia reconstruida para el momento de creación de la demanda a partir de los movimientos registrados después de esa fecha.
- **Compra recibida:** cantidad recibida en OC asociadas a la demanda.
- **Consumido:** material consumido por los avances de las OP asociadas a la demanda.
- **Stock actual:** existencia física actual del componente.
- **Faltante:** necesidad de material que aún no queda cubierta.

El stock inicial es una reconstrucción histórica, no una instantánea guardada en una tabla independiente. Su exactitud depende de que los cambios posteriores de inventario estén registrados en `inventory_movements`.

## 6. Gestionar compras y recepciones

1. Abrir **Compras**.
2. Crear una solicitud independiente o generar una desde una demanda.
3. Revisar detalle de materiales, cantidad solicitada y costo unitario.
4. En el formulario de recepción, ingresar la cantidad recibida para cada línea.
5. Confirmar la recepción.
6. Revisar el documento REC y el historial de recepciones.

Las recepciones pueden ser parciales. La solicitud no aumenta el inventario hasta que se registra una recepción.

## 7. Gestionar producción

1. Abrir **Producción** para consultar las OP creadas desde una DEM o crear una OP independiente.
2. Las OP creadas desde Demandas aparecen en estado **Borrador** y conservan la DEM asociada.
3. Revisar la cantidad planeada. Una DEM puede tener varias OP independientes; no se cambia la cantidad de una OP después de crearla.
4. Liberar cada OP cuando haya componentes disponibles para toda su cantidad planeada. La liberación crea reservas y cambia el estado a **En producción**; no descuenta todavía el stock físico.
5. En estado **En producción**, registrar un avance con cantidad y observaciones.
6. El sistema registra el consumo real de componentes, actualiza reservas e inventario, y agrega las unidades fabricadas al stock del producto terminado.
7. La orden pasa a **Completada** al alcanzar la cantidad planeada. Si el avance es parcial, puede registrarse otro avance para el saldo de esa misma OP.

Una orden en Borrador puede anularse. Las órdenes anuladas se conservan en el historial y aparecen en los reportes. Una orden en producción no se debe tratar como anulable desde la acción disponible del MVP.

## 8. Consultar inventario y exportar movimientos

1. Abrir **Inventario**.
2. Revisar existencias físicas, reservadas y disponibles.
3. En Historial y descarga de movimientos, seleccionar fecha inicial y final.
4. Confirmar que la fecha inicial no sea posterior a la final.
5. Revisar los movimientos mostrados.
6. Descargar el archivo Excel.

El archivo incluye:

- **Detalle movimientos:** fecha y hora, documento de referencia, código, producto, tipo, cantidad, unidad, costo unitario, valor y columna Usuario.
- **Resumen por producto:** total de entradas, total de salidas y balance neto.

La columna Usuario indica `No registrado en esta versión` porque el prototipo todavía no guarda identidad de usuario por movimiento.

## 9. Consultar reportes

La pantalla Reportes contiene:

- Resumen general en cinco tarjetas con bordes y separación.
- Primera fila compacta: Producción y Órdenes por estado.
- Segunda fila compacta: Compras y Consumo de materiales.
- Panel de Producción con fondo azul claro y panel de Consumo con fondo verde agua.
- Tablas conservadas y gráfico de consumo desplegable.
- Costos por orden en una sección de ancho completo.

En la tabla de estados, Borrador + En producción + Completada + Anulada debe ser igual a Órdenes registradas.

## 10. Interpretación de costos

- Costo estimado por unidad: costo de componentes calculado desde la receta y costos unitarios registrados.
- Costo real: costo de los materiales realmente consumidos en avances.
- Variación positiva: costo real superior al costo estimado de las unidades producidas.
- Variación negativa: costo real inferior al estimado.

Las órdenes antiguas pueden no tener costo estimado almacenado; esos valores se presentan como no disponibles. No se incluyen mano de obra, depreciación ni costos indirectos.

## 11. Buenas prácticas de demostración

- Utilizar un conjunto de prueba identificable y explicar cuáles son datos semilla y cuáles fueron agregados durante las pruebas.
- Mostrar una DEM cubierta con varias OP: una primera OP por la capacidad inicial, compra del faltante neto, recepción y segunda OP por el saldo.
- Mostrar OC asociada a la DEM y validar que la interfaz no ofrezca duplicarla si ya cubre el faltante.
- Registrar los avances y completar ambas OP.
- Mostrar el movimiento de salida de componentes y entrada de producto terminado.
- Mostrar cómo los estados de órdenes se reconcilian en Inicio y Reportes.
- No afirmar que el sistema identifica al usuario que ejecutó un movimiento: esa capacidad no existe todavía.
