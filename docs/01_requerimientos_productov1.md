SYNTHEX --- Documento de Requerimientos del Producto
Versión: 1.1
Estado: MVP en desarrollo y validación
Tipo de documento: Requerimientos funcionales y no funcionales
1. Descripción del proyecto
SYNTHEX busca incorporar una primera experiencia de fabricación dentro
de su módulo actual de inventarios.

La solución permitirá a pequeñas y medianas empresas gestionar la
transformación de materias primas y componentes en productos terminados,
conectando los procesos de demanda, compras, producción e inventario.

Actualmente, estos procesos suelen gestionarse mediante hojas de cálculo
o registros independientes. El objetivo es centralizar la información y
ofrecer trazabilidad sobre los materiales utilizados, las cantidades
producidas y los costos asociados.
2. Objetivo general
Diseñar y desarrollar un prototipo funcional que permita gestionar el
proceso básico de fabricación de productos, desde la definición de sus
componentes y recetas hasta la producción y actualización de
inventarios.

La solución deberá ser intuitiva, interactiva, escalable y demostrar el
uso de inteligencia artificial en una funcionalidad concreta.
3. Usuario objetivo
Para esta primera versión se manejará un único perfil:

Administrador: tendrá acceso a todos los módulos y podrá crear,
consultar, modificar y gestionar la información del sistema.

La gestión de múltiples usuarios y permisos diferenciados se considera
una mejora posterior.
4. Alcance funcional --- Fase 1 (MVP)
4.1. Panel principal
- Visualizar indicadores generales de inventario y producción.
- Consultar órdenes de producción pendientes y terminadas.
- Identificar alertas de materiales insuficientes.
- Acceder a los módulos mediante tarjetas y navegación sencilla.
4.2. Catálogo de productos
- Crear productos terminados y componentes.
- Registrar código, nombre, unidad de medida, tipo y costo.
- Consultar y modificar artículos.
- Inactivar artículos que tengan movimientos históricos, evitando
  eliminar su trazabilidad.
4.3. Recetas de fabricación (BOM)
- Asociar componentes a un producto terminado.
- Definir las cantidades necesarias de cada componente.
- Calcular el costo estimado de materiales por unidad.
- Permitir modificaciones de recetas mediante nuevas versiones.
- Conservar la receta utilizada por cada orden de producción.
4.4. Gestión de demanda
- Registrar solicitudes de fabricación por producto y cantidad.
- Consultar las existencias disponibles de productos terminados.
- Calcular la necesidad neta de fabricación, descontando las
  existencias no comprometidas.
- Calcular los requerimientos de componentes según la receta.
- Identificar faltantes y determinar la cantidad máxima que puede
  fabricarse con los materiales disponibles.
- Permitir generar producción parcial y gestionar la cantidad
  pendiente.
4.5. Compras y recepción
- Generar solicitudes de compra para componentes faltantes.
- Consultar las cantidades solicitadas.
- Registrar la recepción de materiales.
- Actualizar el inventario únicamente cuando se confirme la recepción.
- Permitir gestionar cantidades recibidas parcialmente.
4.6. Órdenes de producción
- Crear órdenes de producción relacionadas con una demanda.
- Permitir órdenes parciales o totales.
- Reservar los componentes al liberar una orden.
- Registrar avances de producción.
- Registrar las cantidades reales consumidas y las unidades
  terminadas.
- Mantener las órdenes abiertas cuando exista producción pendiente.
4.7. Inventario y movimientos
- Consultar existencias físicas, reservadas y disponibles.
- Registrar entradas de compras y salidas por consumo de producción.
- Registrar entradas de productos terminados.
- Consultar el historial de movimientos.
- Mantener trazabilidad de las transacciones.
4.8. Costos y reportes básicos
- Calcular el costo estimado de materiales por producto.
- Calcular el costo real de materiales según el consumo registrado.
- Consultar cantidades producidas y materiales consumidos.
- Visualizar indicadores de órdenes de producción: totales,
  pendientes, en producción y completadas.
- Visualizar indicadores de compras: solicitudes registradas,
  pendientes y recibidas.
- Presentar información mediante tarjetas, tablas y gráficos.
- Consultar el detalle de consumo de componentes por orden de
  producción.
- Mostrar los costos estimados y reales de fabricación.
- Consultar movimientos de inventario relacionados con compras y
  producción.
Para el MVP, el costo de fabricación contempla materiales. No incluye
mano de obra, depreciación ni costos indirectos.
4.9. Inteligencia artificial
- Se incluirá una funcionalidad acotada de IA que permita interpretar
  y explicar información del proceso de fabricación.
- Ejemplo: explicar por qué una demanda no puede producirse
  completamente, identificar el componente limitante y presentar una
  explicación de las alternativas disponibles.
- El asistente conversacional completo se reserva para la Fase 2.
4.10. Datos de demostración
- Cargar automáticamente desde Python los datos iniciales de una
  lámpara de escritorio.
- Incluir sus componentes, receta, existencias y costos.
- Incorporar un botón para restaurar el escenario inicial de
  demostración.
- Permitir crear productos y componentes adicionales desde la
  aplicación.
- Permitir ejecutar el flujo completo de fabricación con los nuevos
  artículos.
5. Flujo principal del proceso
1. Registrar un producto terminado.
2. Crear su receta y asociar componentes.
3. Registrar una demanda de fabricación.
4. Calcular los materiales requeridos.
5. Comparar requerimientos con existencias disponibles.
6. Identificar faltantes y generar solicitudes de compra.
7. Registrar la recepción de materiales.
8. Crear y liberar órdenes de producción.
9. Reservar los componentes necesarios.
10. Registrar avances y consumos reales.
11. Actualizar inventario de componentes y productos terminados.
12. Consultar resultados, costos y movimientos.
6. Reglas de negocio
RN-01. Disponibilidad de inventario
Inventario disponible = Inventario físico − Inventario reservado.

RN-02. Reservas
Los materiales se reservan al liberar una orden de producción. La
reserva no representa una salida física del inventario.

RN-03. Consumo de materiales
El inventario físico se descuenta cuando se registra el consumo real de
materiales durante un avance de producción.

RN-04. Producción parcial
El sistema debe permitir producir la cantidad posible con los
componentes disponibles y mantener pendiente la cantidad restante.

RN-05. Compras
Una solicitud de compra no incrementa las existencias. El inventario
aumenta únicamente cuando se registra la recepción.

RN-06. Trazabilidad
Los movimientos históricos no deben eliminarse ni modificarse
directamente. Las correcciones se registrarán mediante movimientos de
ajuste.

RN-07. Versionamiento de recetas
Cada orden conserva la versión de receta con la que fue creada. Los
cambios posteriores aplican a nuevas órdenes y no modifican las órdenes
existentes.

RN-08. Eliminación de artículos
Los artículos con movimientos históricos deben inactivarse, no
eliminarse físicamente.

RN-09. Integridad de las transacciones
El registro de un avance debe actualizar de manera consistente el
consumo de componentes, las reservas y las entradas de productos
terminados. No deben quedar actualizaciones incompletas.

RN-10. Restauración del demo
La restauración debe recuperar los datos iniciales de demostración y
eliminar los registros creados durante las pruebas. Debe solicitar
confirmación antes de ejecutarse.
7. Datos iniciales del escenario de demostración
Producto terminado: Lámpara de escritorio.

  Código   Componente           Cantidad por lámpara   Costo unitario
  MP001    Base metálica                           1         $12.000
MP002    Brazo articulado                        1          $8.000
MP003    Cable eléctrico                         1          $3.500
MP004    Interruptor                             1          $2.500
MP005    Bombillo LED                            1          $4.000
MP006    Tornillo                                4            $200

Costo estimado de materiales por lámpara: $30.800 COP.
Inventario inicial de componentes
  Componente           Existencias
  Base metálica                 30
Brazo articulado              25
Cable eléctrico               40
Interruptor                   35
Bombillo LED                  30
Tornillo                      60

Inventario inicial de lámparas terminadas: 10 unidades.

Para la prueba de producción se podrá registrar una demanda de 20
unidades adicionales. Con los inventarios iniciales, la disponibilidad
de tornillos limita la fabricación a 15 unidades, por lo que será
necesario comprar 20 tornillos para completar las 5 restantes.
8. Requerimientos no funcionales
- Usabilidad: interfaz sencilla, intuitiva y con navegación clara.
- Accesibilidad: aplicación disponible mediante un enlace público
  para evaluación.
- Integridad: proteger la consistencia de inventarios, reservas y
  movimientos.
- Trazabilidad: conservar el historial de operaciones.
- Mantenibilidad: organizar el código por módulos y
  responsabilidades.
- Escalabilidad: permitir incorporar nuevos productos, componentes
  y recetas sin modificar el código de cada producto.
- Seguridad básica: proteger las operaciones de modificación y
  solicitar confirmación en acciones críticas.
- Persistencia: utilizar SQLite como base de datos inicial.
9. Tecnologías propuestas
  Tecnología                  Uso
  Python                      Lógica del sistema
Streamlit                   Interfaz web interactiva
SQLite                      Almacenamiento de datos
Pandas                      Gestión y procesamiento de información
Plotly                      Indicadores y visualizaciones
GitHub                      Control de versiones y documentación
Streamlit Community Cloud   Publicación del demo
Servicio de IA              Funcionalidad de inteligencia artificial
10. Funcionalidades fuera del alcance del MVP
Fase 2
10.1. Automatización de documentos
- Generación automática y consecutiva de códigos para demandas (DEM).
- Generación automática y consecutiva de códigos para solicitudes de
  compra (OC).
- Generación automática y consecutiva de códigos para recepciones
  (REC).
- Generación automática y consecutiva de códigos para órdenes de
  producción (OP).
- Generación automática y consecutiva de códigos para avances de
  producción (ADV).
- Consolidar y validar la generación automática de códigos para todos
  los documentos del sistema.
Nota de estado: la generación automática de códigos DEM ya está
implementada. En esta fase se completará y validará la automatización de
los demás documentos.
10.2. Mejoras en gestión de demanda y abastecimiento
- Descontar las cantidades cubiertas por solicitudes de compra
  pendientes al calcular los faltantes.
- Diferenciar existencias físicas, compras pendientes y cantidades que
  todavía requieren compra.
- Evitar solicitudes de compra duplicadas.
- Mejorar la visualización del estado de abastecimiento de cada
  demanda.
10.3. Otras funcionalidades
- Asistente conversacional avanzado.
- Gestión de proveedores.
- Alertas y notificaciones avanzadas.
- Auditoría detallada.
- Gestión de múltiples usuarios y roles.
- Mejoras avanzadas en el versionamiento de recetas.
Fase 3
- Pronósticos de demanda.
- Planeación avanzada de producción.
- Cálculo de días de inventario (DOH).
- Inventarios de seguridad.
- Recomendaciones automáticas de reabastecimiento.
- Análisis estratégico de inventarios y abastecimiento.
11. Criterios de aceptación del MVP
El prototipo se considerará funcional cuando se pueda demostrar que:
- El sistema carga automáticamente los datos iniciales de la lámpara.
- Se puede crear un nuevo producto y sus componentes.
- Se puede definir una receta para ese producto.
- Se puede registrar una demanda de fabricación.
- El sistema calcula los materiales necesarios y detecta faltantes.
- Se puede generar una solicitud de compra y registrar su recepción.
- Se pueden crear órdenes de producción parciales o totales.
- El sistema reserva materiales al liberar una orden.
- Se registran los consumos y las entradas de productos terminados.
- Los inventarios se actualizan correctamente.
- Se puede consultar el costo y el historial de movimientos.
- Se pueden consultar indicadores básicos de producción y compras.
- Se puede demostrar una funcionalidad de IA dentro de la aplicación.
- Se puede restaurar el escenario inicial de demostración.
- La aplicación está publicada y puede utilizarse mediante un enlace
  público.
12. Entregables del proyecto
- Aplicación web funcional.
- Base de datos SQLite.
- Código fuente organizado en GitHub.
- Archivo README con instrucciones de instalación y ejecución.
- Documentación de requerimientos y diseño.
- Video de máximo 8 minutos que explique la demostración y las
  decisiones de producto.

Nota: Este documento establece el alcance funcional del producto y
sus fases de evolución. Los detalles técnicos de implementación, el
modelo entidad-relación y las decisiones de arquitectura se documentarán
por separado.
