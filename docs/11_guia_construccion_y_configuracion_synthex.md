# SYNTHEX — Guía de construcción y configuración de la aplicación

**Documento:** 11  
**Versión documental:** 1.5  
**Alcance:** MVP presentado para el reto de Alegra  
**Fecha:** 12 de noviembre de 2026

## 1. Propósito

Este documento reúne en una sola secuencia los pasos de construcción, integración, configuración, validación y publicación de SYNTHEX. Complementa los diagramas operativos de fabricación (documentos 07 y 10): no los reemplaza.

La secuencia se reconstruyó a partir de la estructura del proyecto, la arquitectura documentada y las pruebas funcionales que quedaron registradas. Representa el orden lógico de construcción y puesta en marcha; no es una bitácora exacta de cada commit ni pretende asignar fechas a cada cambio de código.

## 2. Secuencia general de construcción

### Paso 1. Definir el alcance del MVP

- Identificar la necesidad: conectar inventarios, demandas, abastecimiento y fabricación.
- Definir el alcance funcional y las reglas de negocio.
- Establecer los criterios de aceptación y los datos necesarios para la demostración.
- Documentar los requerimientos en `docs/01_requerimientos_producto.md`.

**Resultado:** alcance funcional delimitado para la entrega del MVP.

### Paso 2. Organizar el proyecto y el control de versiones en GitHub

- Crear y mantener el repositorio `RetoAlegra_Ananunez`.
- Organizar el código en archivos Python separados por responsabilidad.
- Mantener `requirements.txt` con las dependencias externas.
- Mantener `docs/` con la documentación funcional, técnica y los diagramas.
- Registrar los cambios en GitHub para conservar el historial del proyecto.

**Resultado:** repositorio centralizado con código, dependencias y documentación.

### Paso 3. Construir la persistencia con SQLite

Archivo principal: `database.py`.

- Configurar la conexión SQLite mediante `get_connection()`.
- Configurar el acceso a filas y la activación de claves foráneas.
- Crear las tablas necesarias para productos, recetas, demandas, compras, producción, reservas, avances y movimientos.
- Ejecutar las verificaciones y migraciones de estructura necesarias.
- Inicializar los datos de demostración cuando el catálogo está vacío.

La base de datos de ejecución se identifica como `synthex.db` y se inicializa desde la aplicación.

**Resultado:** capa de persistencia común para los módulos del sistema.

### Paso 4. Desarrollar la lógica funcional por módulos

Cada archivo Python concentra responsabilidades de un dominio y utiliza la conexión centralizada de `database.py`.

| Módulo | Responsabilidad en el MVP |
|---|---|
| `products.py` | Crear y consultar productos terminados y componentes. |
| `recipes.py` | Crear y consultar recetas versionadas y sus componentes. |
| `demands.py` | Registrar demandas y consultar sus requerimientos y seguimiento. |
| `purchases.py` | Crear solicitudes de compra, registrar recepciones y consultar cantidades solicitadas, recibidas y pendientes. |
| `production.py` | Crear órdenes, liberar órdenes, gestionar reservas, registrar avances y consumos. |
| `inventory.py` | Consultar existencias físicas, reservadas y disponibles, y movimientos. |
| `reports.py` | Consolidar indicadores, costos de materiales y reportes. |
| `ai_assistant.py` | Preparar explicaciones de faltantes con el servicio de IA; no ejecuta transacciones de inventario. |
| `date_utils.py` | Normalizar y presentar fechas para la zona horaria de Colombia. |

**Resultado:** lógica de negocio organizada y reutilizable desde la interfaz.

### Paso 5. Integrar los módulos en Streamlit

Archivo principal: `app.py`.

- Construir la navegación y las pantallas del sistema.
- Presentar formularios, tarjetas, métricas, tablas y gráficos.
- Validar las entradas de los formularios.
- Llamar al módulo de dominio correspondiente para consultar o registrar información.
- Mostrar confirmaciones, alertas y resultados al usuario.

La interfaz no sustituye la lógica de negocio: coordina las operaciones que implementan los módulos especializados.

**Resultado:** aplicación web que conecta los módulos funcionales.

### Paso 6. Configurar las librerías e integraciones

Dependencias registradas en `requirements.txt`:

- `streamlit`: interfaz web.
- `pandas`: preparación y procesamiento de datos.
- `plotly`: visualizaciones.
- `google-genai`: integración con Google Gemini.
- `openpyxl`: generación de archivos Excel.

La función de IA utiliza la configuración segura de secretos del entorno de Streamlit para la credencial del servicio. Las claves privadas no deben escribirse en el repositorio.

**Resultado:** bibliotecas disponibles y servicio externo de IA conectado mediante configuración segura.

### Paso 7. Validar los flujos funcionales

- Probar el registro de productos y recetas.
- Probar la creación de demandas y el cálculo de materiales.
- Probar solicitudes de compra y recepciones.
- Probar órdenes de producción, reservas y avances.
- Comprobar los movimientos y saldos de inventario.
- Revisar reportes y explicaciones de IA.
- Ejecutar la prueba integral de demanda y producción parcial documentada en el archivo 10.

Como escenario de validación E2E se documentó AL001 / DEM-008, con OP-010, OC-007, OP-011, ADV-006 y ADV-007.

**Resultado:** flujo integral de producción parcial validado con conciliación de cantidades y materiales.

### Paso 8. Publicar la aplicación

- Mantener el código fuente en GitHub.
- Conectar el repositorio con Streamlit Community Cloud.
- Seleccionar la aplicación principal `app.py` como punto de entrada del despliegue.
- Configurar en los secretos de Streamlit la credencial requerida por la integración de IA.
- Publicar la aplicación y comprobar el acceso desde el navegador.

**Enlace público de SYNTHEX:**

https://retoalegraananunez-ntkzwtil2ucpinirtcqkjl.streamlit.app/

**Resultado:** aplicación disponible para consulta y evaluación desde un enlace público, sin requerir que el evaluador clone el repositorio ni instale dependencias.

## 3. Cómo se conectan los componentes

1. El usuario interactúa con las pantallas de `app.py`.
2. `app.py` llama a la función correspondiente del módulo funcional.
3. El módulo accede a SQLite a través de `database.py`.
4. SQLite conserva los registros y devuelve los resultados.
5. `app.py` presenta la información con Streamlit, Pandas y Plotly.
6. Para la explicación de faltantes, `ai_assistant.py` utiliza Google Gemini con el contexto calculado por el sistema. La IA explica; no cambia inventarios, compras ni órdenes.
7. GitHub conserva el código y la documentación; Streamlit Community Cloud publica la aplicación web.

## 4. Alcance de este documento

Este documento describe únicamente la construcción, integración, validación y publicación del MVP entregado para el reto. No presenta las fases 2 y 3 como actividades ejecutadas ni como entregables de esta entrega.

## 5. Relación con los demás documentos

- `04_arquitectura_tecnica.md`: explica la arquitectura y la responsabilidad de los componentes.
- `07_diagrama_proceso.md`: explica el proceso operativo de demanda, compras y fabricación.
- `10_guia_prueba_e2e_demanda_produccion_parcial.md`: documenta el escenario de validación integral.
- `11_diagrama_construccion_synthex.mmd`: fuente editable del diagrama incluido en esta guía.
