# SYNTHEX — Documento de requerimientos del producto

**Versión:** 1.4  
**Fecha:** 12 de noviembre de 2026  
**Estado:** MVP funcional; flujo E2E de producción parcial validado el 12 de noviembre de 2026  
**Tipo:** visión de producto, alcance funcional y roadmap  

---

## 1. Descripción del producto

SYNTHEX es un prototipo web de gestión de inventario y manufactura para pequeñas y medianas empresas. Conecta catálogo, recetas de fabricación, demandas, compras, recepción de materiales, órdenes de producción, consumo e inventario de productos terminados.

El producto busca centralizar información que habitualmente se administra en hojas de cálculo o registros aislados, dar trazabilidad a las operaciones y ofrecer visibilidad de materiales, cantidades producidas y costos directos de fabricación.

## 2. Problema que aborda

Cuando demanda, compras, inventario y producción se administran por separado, se dificulta responder preguntas operativas como:

- ¿Qué producto se necesita fabricar y en qué cantidad?
- ¿Qué componentes requiere la receta?
- ¿Hay existencias suficientes o se deben comprar materiales?
- ¿Qué cantidades están reservadas para producción?
- ¿Cuánto se ha fabricado y cuánto falta?
- ¿Qué materiales se consumieron y cuál fue su costo?

SYNTHEX ofrece un flujo integrado para responder estas preguntas en un escenario de manufactura acotado.

## 3. Objetivo general

Diseñar y entregar un MVP funcional que permita gestionar el flujo básico de fabricación desde el catálogo y la definición de recetas hasta la demanda, abastecimiento, producción, actualización del inventario y consulta de resultados.

## 4. Usuario objetivo y alcance de acceso

El MVP contempla un perfil operativo único: **Administrador**. Este perfil accede a los módulos y puede registrar y consultar las operaciones del prototipo.

No se implementan todavía autenticación multiusuario, roles diferenciados ni atribución de cada movimiento a una persona. La auditoría por usuario es una mejora planificada.

## 5. Alcance implementado — Fase 1 (MVP)

La Fase 1 reúne las capacidades que ya están implementadas en el prototipo y se han revisado mediante escenarios de demostración.

### 5.1. Navegación y panel de inicio

- Navegación lateral por los módulos Inicio, Productos, Recetas, Demandas, Compras, Producción, Inventario y Reportes.
- Identidad visual inicial de SYNTHEX con azul profundo, turquesa y blanco.
- Panel de inicio con indicadores de inventario, compras y producción.
- Desglose de órdenes por estado: borrador, en producción, completada y anulada.

### 5.2. Catálogo de productos

- Registro de productos terminados y componentes.
- Código, nombre, tipo, unidad, costo unitario y existencia inicial.
- Consulta del catálogo y estado activo del producto.
- Conservación del catálogo como referencia común para recetas, demandas, compras y producción.

### 5.3. Recetas de fabricación (BOM)

- Asociación de un producto terminado con sus componentes.
- Registro de cantidades necesarias por unidad fabricada.
- Versionamiento de recetas y consulta de la versión asociada a la orden.
- Cálculo del costo estimado de materiales por unidad.

### 5.4. Demandas

- Registro de demanda por producto y cantidad solicitada.
- Cálculo de cantidades programadas, producidas, pendientes por fabricar y pendientes por programar.
- Cálculo de requerimientos de componentes a partir de la receta.
- Identificación de faltantes frente a las existencias físicas.
- Cálculo del máximo fabricable con inventario disponible, reservas activas y compromisos de órdenes en Borrador.
- Creación de OP independientes asociadas a una misma demanda, cada una limitada a la cantidad fabricable en ese momento.
- Recalculo del saldo después de la recepción de materiales y habilitación de una OP posterior para completar la demanda.
- Visualización de OC asociadas, estado, cantidades solicitadas/recibidas y faltante aún no cubierto, evitando proponer una compra duplicada.
- Explicación de faltantes mediante una función acotada de inteligencia artificial.
- Generación de una solicitud de compra desde el análisis de una demanda.

### 5.5. Compras y recepción

- Registro de solicitudes de compra con detalle de material, cantidad y costo unitario estimado.
- Asociación opcional de una solicitud con una demanda.
- Registro de recepciones parciales o completas.
- Historial de recepciones con documento REC, fecha y cantidades recibidas.
- Actualización del inventario físico al confirmar la recepción, no al crear la solicitud.

### 5.6. Órdenes de producción

- Creación de órdenes relacionadas con una demanda o sin asociación.
- Generación automática de consecutivos para OP.
- Estados: Borrador, En producción, Completada y Anulada.
- Validación de disponibilidad de materiales al liberar la orden.
- Reserva de componentes al liberar la orden.
- Registro de avances parciales o totales con documentos ADV.
- Registro de consumo real de materiales y entrada de producto terminado.
- Cierre automático al alcanzar la cantidad planeada.
- Anulación permitida para órdenes en borrador, conservando el documento histórico.
- Fechas de creación, liberación, finalización y anulación cuando existen datos almacenados.

### 5.7. Inventario y movimientos

- Consulta de existencias físicas, reservadas y disponibles.
- Cálculo de disponibilidad: existencias físicas menos reservas activas no consumidas.
- Historial de movimientos de entrada y salida.
- Filtros por fecha inicial y final, interpretados con calendario de Colombia.
- Exportación a Excel con dos hojas: `Detalle movimientos` y `Resumen por producto`.
- En el detalle Excel se incluye una columna Usuario con el texto `No registrado en esta versión`, ya que todavía no existe atribución persistida por usuario.

### 5.8. Reportes

- Resumen de órdenes registradas, unidades producidas, completadas, compras pendientes y anuladas.
- Unidades programadas y pendientes calculadas solo para órdenes vigentes (Borrador y En producción).
- Conteo de órdenes por estado, con las anuladas como categoría independiente.
- Indicadores de solicitudes de compra registradas, pendientes y recibidas.
- Consumo de materiales y costo total de materiales consumidos.
- Comparación de costo estimado y real por orden cuando existe información suficiente.
- Presentación compacta en cuadrícula para Producción/Órdenes por estado y Compras/Consumo de materiales; la sección de costos conserva ancho completo.
- Panel de Producción con sombreado azul claro y panel de Consumo de materiales con sombreado verde agua; se conservan las tablas, gráficos y tarjetas existentes.

### 5.9. Automatización de documentos

La generación automática de consecutivos ya se utiliza en los flujos DEM, OC, REC, OP y ADV. Por tanto, esta capacidad se considera parte de la Fase 1 implementada y deja de figurar como pendiente de la Fase 2.

## 6. Reglas de negocio vigentes

**RN-01. Disponibilidad de inventario**  
Inventario disponible = inventario físico − inventario reservado.

**RN-02. Reserva de materiales**  
La reserva se crea al liberar una orden. La reserva reduce disponibilidad, pero no descuenta por sí sola el inventario físico.

**RN-03. Consumo real**  
El inventario físico de componentes se descuenta al registrar el avance de producción y su consumo real.

**RN-04. Entrada de producto terminado**  
Al registrar un avance, las unidades fabricadas se suman al inventario físico del producto terminado.

**RN-05. Avances parciales de fabricación**  
Una orden en producción puede recibir uno o varios avances parciales. Se mantiene abierta hasta alcanzar la cantidad planeada de esa orden. Esto es distinto de programar varias OP independientes desde una misma demanda.

**RN-06. Programación parcial por disponibilidad**  
El formulario de demanda calcula la cantidad máxima fabricable y limita la cantidad de la nueva OP al menor valor entre el saldo pendiente por programar y la capacidad actual de materiales. La cantidad restante continúa pendiente y puede programarse en otra OP después de recibir los materiales.

**RN-07. Liberación de órdenes**  
La liberación valida la disponibilidad para la cantidad planeada completa de esa OP. Si hay materiales suficientes, crea reservas y cambia el estado a En producción; si no, rechaza la liberación sin consumir inventario físico.

**RN-08. Compras**  
Una solicitud no incrementa existencias. Solo una recepción confirmada genera entradas de inventario. Las recepciones pueden ser parciales.

**RN-09. Recetas versionadas**  
La orden conserva el identificador de la receta con que fue creada. Los cambios posteriores en recetas no deben alterar la receta ya asociada a una orden existente.

**RN-10. Estados de orden**  
Las órdenes se contabilizan por estado. El total histórico debe reconciliarse como Borrador + En producción + Completada + Anulada.

**RN-11. Indicadores vigentes**  
Unidades programadas y pendientes consideran solo órdenes Borrador y En producción. Unidades producidas se reportan como acumulado histórico.

**RN-12. Trazabilidad**  
Los documentos y movimientos se conservan como historial. Las fechas de eventos se muestran cuando se han almacenado; para registros históricos anteriores a la migración puede aparecer `No disponible`.

**RN-13. Costos**  
El costo estimado se calcula con cantidades de la receta y costos unitarios registrados. El costo real se calcula a partir del consumo registrado. El MVP cubre materiales directos solamente.

## 7. Datos base del escenario demostrativo

Producto terminado: **Lámpara de escritorio** (PT001).

| Código | Componente | Cantidad por lámpara | Costo unitario inicial |
|---|---|---:|---:|
| MP001 | Base metálica | 1 | COP 12.000 |
| MP002 | Brazo articulado | 1 | COP 8.000 |
| MP003 | Cable eléctrico | 1 | COP 3.500 |
| MP004 | Interruptor | 1 | COP 2.500 |
| MP005 | Bombillo LED | 1 | COP 4.000 |
| MP006 | Tornillo | 4 | COP 200 |

Costo estimado inicial de materiales: **COP 30.800 por lámpara**.

Existencias iniciales documentadas: base metálica 30, brazo articulado 25, cable eléctrico 40, interruptor 35, bombillo LED 30, tornillo 60 y producto terminado 10 unidades.

Estas cantidades describen el escenario de inicialización. Durante las pruebas se agregaron otros productos de ensayo (por ejemplo MP007, MP008 y MP009), por lo que no deben confundirse con el catálogo semilla original.

## 8. Requerimientos no funcionales

- **Usabilidad:** navegación clara y lenguaje comprensible.
- **Consistencia:** estados y cifras deben reconciliarse entre Inicio, Producción y Reportes.
- **Integridad:** operaciones que consumen o reciben materiales deben mantener consistentes existencias, reservas y movimientos.
- **Trazabilidad:** conservar documentos y movimientos; fechas visibles cuando estén registradas.
- **Mantenibilidad:** separar interfaz, lógica de negocio y acceso a datos por módulos.
- **Persistencia:** utilizar SQLite para la base de datos del prototipo.
- **Despliegue:** disponibilidad mediante Streamlit Community Cloud.
- **Seguridad básica:** guardar las claves de servicios externos en secretos, nunca en el repositorio.

## 8.1. Validación E2E de producción parcial — 12 de noviembre de 2026

La brecha de programación parcial por disponibilidad de materiales quedó corregida y validada mediante el escenario AL001 / DEM-008. La DEM solicitó 10 unidades; el inventario permitía fabricar inicialmente 7, se abastecieron 5 unidades de MP007 y se creó una segunda OP por las 3 unidades restantes.

- OP-009, creada previamente por 10 unidades en el escenario de prueba, se anuló y se conservó como antecedente histórico; no se contabilizó como programación vigente.
- OP-010 se creó por 7 unidades y OP-011 por 3 unidades.
- OC-007 se registró por 5 unidades de MP007; la pantalla de demanda mostró el documento y su estado, y evitó sugerir otra OC para el mismo faltante cubierto.
- Tras la recepción de OC-007, MP007 pasó de 15 a 20 unidades físicas. Se liberaron las dos OP y se reservaron 20 unidades de cada componente en total.
- ADV-006 fabricó 7 unidades y consumió 14 unidades de cada componente; costo de materiales COP 119.000.
- ADV-007 fabricó 3 unidades y consumió 6 unidades de cada componente; costo de materiales COP 51.000.
- La DEM-008 quedó Completada: 10 solicitadas, 10 programadas, 10 fabricadas, 0 pendientes por fabricar y 0 pendientes por programar.

El detalle de pasos, cálculos y conciliación se encuentra en `10_guia_prueba_e2e_demanda_produccion_parcial.md`.

### Lectura histórica y actual del inventario

La tabla de materiales distingue Requerido, Stock inicial, Compra recibida, Consumido, Stock actual y Faltante. El stock inicial se reconstruye restando del stock físico actual los movimientos netos registrados después de la creación de la demanda. La compra recibida suma las recepciones vinculadas a esa demanda y el consumo se toma de los avances de sus órdenes.

La reconstrucción del stock inicial depende de que todos los cambios de inventario desde la fecha de creación de la demanda hayan generado movimientos en `inventory_movements`. Los ajustes manuales no registrados, movimientos con marca de tiempo no confiable o eventos históricos fuera de ese registro pueden afectar la reconstrucción. Una mejora futura sería guardar una instantánea explícita del inventario cuando se registra la DEM.

### Hallazgo adicional: fechas de creación antiguas

En el catálogo se observaron valores `nan` en la columna Fecha de creación de registros históricos, mientras un producto nuevo mostraba fecha y hora. La presentación debe normalizar valores nulos o no válidos como `No disponible`; no se deben inventar fechas para registros que no las conservaron.

### Diseño visual consolidado

La actualización visual de Reportes quedó validada: cinco tarjetas en el resumen general; cuadrícula Producción/Órdenes por estado y Compras/Consumo de materiales; fondos diferenciados para Producción y Consumo; tablas conservadas; costos por orden a ancho completo.

## 9. Roadmap actualizado

### Fase 1 — MVP de inventario y manufactura

**Estado: flujo crítico E2E validado en el entorno de demostración.**

Incluye catálogo, recetas, demandas, cálculo de requerimientos, identificación de faltantes, solicitudes y recepciones, órdenes, reservas, avances, consumos, inventario, reportes, exportación Excel, IA explicativa acotada, consecutivos documentales y primera identidad visual corporativa.

### Fase 2 — Robustecimiento operativo, experiencia de usuario e inteligencia asistida

La Fase 2 se enfoca en hacer más robusta la operación y evolucionar el producto con base en el uso y la retroalimentación.

**Abastecimiento y compras**
- Mejorar la auditoría y el versionamiento de movimientos para reconstruir inventarios históricos con mayor precisión.
- Incorporar gestión de proveedores y seguimiento de condiciones comerciales.

**Trazabilidad y seguridad operativa**
- Registrar quién realiza cada operación y asociar usuario a movimientos y documentos.
- Auditoría de cambios y acciones relevantes.
- Incorporar autenticación, múltiples usuarios y roles diferenciados.
- Fortalecer la validación e integridad de las transacciones.

**Inteligencia artificial y operación**
- Evolucionar el análisis puntual de faltantes hacia un asistente conversacional con contexto operativo y límites de acción claros.
- Alertas y notificaciones de abastecimiento y producción.
- Mejoras avanzadas de versionamiento y control de recetas.

**Ajustes de diseño y experiencia de usuario (UX)**
- Consolidar un sistema visual coherente para formularios, tarjetas, tablas, gráficos, estados y mensajes.
- Ajustar la experiencia en pantallas de distintos tamaños.
- Refinar jerarquía visual, densidad de información, navegación, accesibilidad y consistencia de componentes.
- Evaluar los ajustes con usuarios y con los resultados de la demostración.
- Mantener la identidad de SYNTHEX (azul profundo, turquesa, blanco y gris claro), sin confundir estos ajustes visuales con nuevas capacidades funcionales.

### Fase 3 — Planeación avanzada y analítica estratégica

- Pronósticos de demanda.
- Planeación avanzada de demanda y producción.
- Cálculo de días de inventario (DOH), con una definición validada del consumo promedio y el horizonte de cálculo.
- Inventarios de seguridad.
- Recomendaciones automáticas de reabastecimiento.
- Análisis estratégico de inventarios, cobertura, abastecimiento y capacidad.

## 10. Fuera del alcance de la Fase 1

- DOH, pronósticos y planeación avanzada.
- Cálculo automático de inventario de seguridad.
- Recomendaciones automáticas de reabastecimiento.
- Gestión completa de proveedores.
- Auditoría por usuario y múltiples roles.
- Mano de obra, depreciación y costos indirectos.
- Asistente conversacional general con capacidad de ejecutar operaciones.

## 11. Criterios de aceptación y cierre del MVP

| ID | Criterio | Estado documental |
|---|---|---|
| AC-01 | Registrar productos terminados y componentes | Implementado en el prototipo |
| AC-02 | Crear recetas versionadas y consultar costo estimado | Implementado en el prototipo |
| AC-03 | Registrar demandas y calcular requerimientos | Implementado en el prototipo |
| AC-04 | Identificar faltantes y presentar análisis explicativo con IA | Implementado; conviene repetir prueba en video |
| AC-05 | Crear solicitudes de compra y registrar recepciones parciales | Implementado y probado en escenarios |
| AC-06 | Crear, liberar y reservar órdenes de producción | Implementado y probado en escenarios |
| AC-07 | Registrar avances, consumos y entradas de producto terminado | Implementado y probado en escenario OP-008/ADV-005 |
| AC-08 | Anular órdenes en borrador y conservar historial | Implementado y probado en escenario OP-007 |
| AC-09 | Reconciliar estados de órdenes en Inicio y Reportes | Validado en un corte histórico previo al E2E: 8 órdenes = 5 completadas + 3 anuladas; DEM-008 se documenta como caso E2E independiente |
| AC-10 | Exportar movimientos con filtro de fechas y dos hojas Excel | Implementado y revisado en Excel |
| AC-11 | Mostrar fechas con calendario de Colombia cuando existen | Implementado; datos históricos antiguos pueden no tener fecha de evento |
| AC-12 | Restaurar el escenario semilla desde la interfaz | Verificar en la versión desplegada antes de marcar como cerrado |
| AC-13 | Publicación y acceso al demo | La aplicación fue abierta y revisada en Streamlit; verificar URL final de entrega |
| AC-14 | Programar una primera OP solo por las unidades fabricables, generar OC por el faltante neto y crear una segunda OP tras la recepción | Validado E2E: DEM-008, OP-010 (7), OC-007 (5 MP007), OP-011 (3), ADV-006 y ADV-007 |
| AC-15 | Mostrar `No disponible` para fechas de creación nulas o inválidas, sin mostrar `nan` ni inventar fechas | Pendiente de corrección y regresión |
| AC-16 | Conciliar stock inicial, compras recibidas, consumo y stock actual por demanda | Validado visualmente con DEM-008; sujeto a trazabilidad completa de `inventory_movements` |

## 12. Entregables del producto

- Aplicación web Streamlit.
- Base SQLite inicializable por código.
- Código fuente organizado en módulos.
- Documentación funcional y técnica.
- Diagrama de proceso y modelo de datos.
- Manual de usuario y plan de pruebas.
- Video de demostración de máximo 8 minutos, de acuerdo con el requerimiento del reto.

## 13. Historial de cambios

- **v1.0:** requerimientos iniciales del MVP.
- **v1.1:** reglas de negocio, datos semilla, criterios de aceptación y roadmap inicial.
- **v1.2:** actualización de estado real de Fase 1; automatización documental trasladada a implementado; roadmap Fase 2/3 revisado; incorporación del apartado de ajustes de diseño y UX en Fase 2; documentación de Excel, estados de órdenes, reportes y límites actuales.
- **v1.3:** incorporación de los hallazgos reproducidos de programación parcial por disponibilidad de materiales, escenario AL001/DEM-008/OP-009/OC-007, brecha de fechas `nan` y diseño final de Reportes.
- **v1.4:** cierre y validación E2E de producción parcial por demanda; incorporación de OP sucesivas, consulta de OC asociadas y conciliación de stock inicial, recepciones, consumo y stock actual; nueva guía práctica y diagrama E2E.
