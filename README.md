# SYNTHEX – Sistema de Manufactura e Inventarios

**Repositorio:** RetoAlegra_Ananunez

## 1. Descripción del proyecto

SYNTHEX es una aplicación web desarrollada en Python y Streamlit que integra la gestión de inventarios con un proceso básico de fabricación.

Su objetivo es facilitar el control de productos, componentes, recetas de fabricación, demandas, compras, órdenes de producción y movimientos de inventario, permitiendo mantener la trazabilidad de los materiales y de los productos terminados.

El proyecto corresponde al MVP desarrollado para el reto de Alegra.

## 2. Funcionalidades implementadas

- **Catálogo de productos:** creación, consulta y administración de productos terminados y componentes.
- **Recetas de fabricación (BOM):** definición de componentes, cantidades necesarias y versiones de recetas.
- **Gestión de demandas:** registro de solicitudes de fabricación y cálculo de necesidades de materiales.
- **Compras y recepciones:** generación de solicitudes de compra y registro de recepciones parciales o completas.
- **Órdenes de producción:** creación de órdenes parciales o totales y reserva de componentes.
- **Avances de producción:** registro de cantidades fabricadas y consumos reales.
- **Control de inventario:** consulta de existencias físicas, reservadas y disponibles, junto con el historial de movimientos.
- **Costos y reportes:** consulta de costos estimados y reales de materiales, indicadores y resultados de producción.
- **Asistente de inteligencia artificial:** explicación de faltantes de materiales y situaciones del proceso productivo.

## 3. Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Python | Lógica y procesamiento del sistema |
| Streamlit | Interfaz web |
| SQLite | Persistencia de información |
| Pandas | Gestión y análisis de datos |
| Plotly | Visualizaciones e indicadores |
| GitHub | Control de versiones y documentación |
| Streamlit Community Cloud | Publicación de la aplicación |

## 4. Estructura del repositorio

```text
RetoAlegra_Ananunez/
│
├── app.py                  # Aplicación principal e interfaz Streamlit
├── database.py             # Conexión y gestión de la base de datos
│
├── products.py             # Gestión del catálogo de productos
├── recipes.py              # Recetas y componentes de fabricación
├── demands.py              # Gestión de demandas
├── purchases.py            # Solicitudes de compra y recepciones
├── production.py            # Órdenes y avances de producción
├── inventory.py            # Control de inventarios y movimientos
├── reports.py              # Indicadores y reportes
├── ai_assistant.py         # Funcionalidad de inteligencia artificial
├── date_utils.py           # Manejo y conversión de fechas
│
├── requirements.txt        # Dependencias del proyecto
│
├── data/                   # Datos de demostración
│
├── docs/                   # Documentación funcional y técnica
│   ├── 01_requerimientos_producto.md
│   ├── 02_modelo_datos_y_relaciones.md
│   ├── 03_diccionario_comandos_python_sqlite.md
│   ├── 04_arquitectura_tecnica.md
│   ├── 05_manual_usuario.md
│   ├── 06_plan_pruebas_y_validacion.md
│   ├── 07_diagrama_proceso.*
│   ├── 08_diagrama_entidad_relacion.mmd
│   ├── 09_hallazgos_validacion_y_backlog.md
│   └── 10_guia_prueba_e2e_demanda_produccion_parcial.md
│   └── 11_guia_construccion_y_configuracion_synthex.md
└── README.md
```

## 5. Acceso a la aplicación

SYNTHEX se encuentra desplegada en Streamlit Community Cloud y puede consultarse directamente desde el navegador.

**[INGRESAR A APP SYNTHEX](https://retoalegraananunez-ntkzwtil2ucpinirtcqkjl.streamlit.app/)**

**[INGRESAR A REPOSITORIO](https://github.com/anmanude2005-blip/RetoAlegra_Ananunez/edit/main/)**

**[INGRESAR A REPOSITORIO](https://drive.google.com/file/d/1cjJMEjXxTwafZnHHCveMIZSKeJ2qSKcO/view?usp=sharing)**

No requiere instalación ni configuración local.

## 6. Documentación

La carpeta `docs/` contiene la documentación del proyecto:

- Requerimientos funcionales y no funcionales.
- Modelo de datos y relaciones.
- Diccionario de comandos Python y SQLite.
- Arquitectura técnica.
- Manual de usuario.
- Plan de pruebas y validación.
- Diagramas de procesos y entidad-relación.
- Hallazgos y resultados de validación.
- Guía de prueba integral del flujo de demanda y producción parcial.
- Guía de construcción y configuración de SYNTHEX, con el paso a paso de los módulos y herramientas utilizados ([Guía](docs/11_guia_construccion_y_configuracion_synthex.md), [Diagrama PNG](docs/11_diagrama_construccion_synthex.png), [Diagrama editable](docs/11_diagrama_construccion_synthex.mmd)).
    

## 7. Alcance de la entrega

SYNTHEX demuestra la integración de los procesos de inventario, abastecimiento y fabricación en un prototipo funcional.

La entrega comprende la aplicación, su código fuente, la base de datos y la documentación técnica y funcional correspondiente al MVP.
