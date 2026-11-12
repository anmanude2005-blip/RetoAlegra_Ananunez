# SYNTHEX — Arquitectura técnica

**Versión:** 1.2  
**Fecha:** 12 de noviembre de 2026  

## 1. Vista general

SYNTHEX utiliza una arquitectura monolítica modular: una aplicación Streamlit presenta la interfaz, los módulos Python concentran lógica funcional y consultas de datos, y SQLite conserva la información del prototipo.

```text
Usuario
  │
  ▼
Streamlit (app.py)
  │
  ├── Productos / Recetas / Demandas
  ├── Compras / Producción / Inventario
  ├── Reportes / Navegación
  │
  ▼
Módulos Python de dominio
  │
  ├── products.py      ├── recipes.py
  ├── demands.py       ├── purchases.py
  ├── production.py    ├── inventory.py
  ├── reports.py       ├── ai_assistant.py
  └── date_utils.py
  │
  ▼
database.py ── SQLite (synthex.db)
  │
  └── Tablas relacionadas por claves foráneas

Servicio externo de IA ◄── ai_assistant.py
```

## 2. Capas y responsabilidades

### 2.1. Presentación — `app.py`

- Construye la navegación lateral y mantiene el módulo seleccionado en `st.session_state`.
- Renderiza formularios, métricas, tablas, gráficos y mensajes de estado.
- Invoca funciones de los módulos de dominio para registrar y consultar operaciones.
- No debe convertirse en el lugar donde se duplique lógica de negocio o SQL.

### 2.2. Lógica de dominio

| Módulo | Responsabilidad principal |
|---|---|
| `products.py` | Registro y consulta del catálogo de productos y componentes. |
| `recipes.py` | Creación y consulta de recetas versionadas, detalles y costo estimado. |
| `demands.py` | Registro de demandas, requerimientos de materiales y seguimiento de programación/producción. |
| `purchases.py` | Solicitudes de compra, detalle, recepciones parciales y actualización de existencias. |
| `production.py` | Órdenes, liberación, reservas, avances, consumos y estados de producción. |
| `inventory.py` | Existencias físicas, reservas, disponibilidad, movimientos y resumen. |
| `reports.py` | Indicadores agregados, consumo de materiales y costos por orden. |
| `ai_assistant.py` | Explicación asistida de faltantes de materiales; no debe ejecutar operaciones de inventario. |
| `date_utils.py` | Presentación de marcas de tiempo en zona horaria `America/Bogota`. |

### 2.3. Persistencia — `database.py` y `synthex.db`

- `get_connection()` abre una conexión SQLite, configura `sqlite3.Row` y activa las claves foráneas.
- `init_db()` crea tablas si no existen, aplica migraciones de columnas y carga datos semilla cuando el catálogo está vacío.
- `synthex.db` es el archivo de persistencia del entorno de ejecución.
- Las migraciones revisan columnas existentes con `PRAGMA table_info` antes de ejecutar `ALTER TABLE`.

### 2.4. Servicios externos y despliegue

- **Gemini:** se utiliza para generar una explicación de faltantes a partir de contexto calculado por SYNTHEX. La IA no modifica reservas, inventario, compras ni órdenes.
- **GitHub:** repositorio del código y la documentación.
- **Streamlit Community Cloud:** publicación de la aplicación.
- **Pandas / openpyxl:** preparación de información y generación del archivo Excel de movimientos.

## 3. Flujo de una operación

1. Streamlit valida campos básicos del formulario.
2. `app.py` llama a la función del módulo correspondiente.
3. El módulo abre la conexión SQLite mediante `get_connection()`.
4. La operación consulta y valida registros relacionados.
5. En transacciones que afectan varias tablas, se confirman cambios con `commit()` o se revierten con `rollback()` ante error.
6. La interfaz muestra confirmación, error o consulta actualizada.

## 4. Decisiones técnicas relevantes

### SQLite

Se selecciona por simplicidad y facilidad de despliegue para el MVP. Es suficiente para el prototipo de demostración; una evolución multiusuario o de mayor concurrencia requeriría evaluar una base de datos de servidor.

### Streamlit

Permite construir rápidamente formularios, paneles y tablas de datos con Python. La navegación actual se resuelve con botones de la barra lateral y estado de sesión.

### Integridad de inventario

Las reservas se almacenan separadas del stock físico. Esto permite distinguir cantidad físicamente disponible de cantidad comprometida con órdenes. El consumo se registra al avance, no al reservar.

### Programación parcial de demanda

La interfaz de Demandas llama a `get_max_producible_quantity()` para mostrar el máximo fabricable y limitar la cantidad ingresada en una nueva OP. El cálculo considera el saldo pendiente de la DEM, el stock físico, las reservas activas y los compromisos de órdenes en Borrador. Una DEM puede cubrirse con varias OP independientes; cada OP conserva su cantidad planeada y su receta.

El abastecimiento se conecta mediante `get_demand_purchase_requests()` y `get_demand_material_requirements()`: la interfaz muestra OC asociadas y sus estados, cantidades recibidas y pendientes de recibir. El botón para generar una OC solo se presenta cuando permanecen faltantes no cubiertos por compras vinculadas.

Después de la recepción REC, el inventario físico se actualiza y el cálculo de capacidad se vuelve a ejecutar para programar la OP del saldo. La liberación sigue validando los materiales para la cantidad completa de cada OP individual.

### Costeo

El sistema calcula costo estimado de materiales a partir de la receta y costo real a partir de consumos registrados. El alcance actual excluye mano de obra y costos indirectos.

### Fechas e inventario histórico por demanda

SQLite almacena marcas de tiempo; `date_utils.py` formatea fechas para Colombia. El filtro de movimientos convierte los límites del calendario colombiano a UTC para consultar el rango esperado. La vista de materiales de una DEM reconstruye el stock inicial a partir del stock físico actual y los movimientos netos posteriores a la creación de la demanda; se requiere que los cambios de stock estén registrados en `inventory_movements`. Una instantánea de stock al momento de crear una DEM sería una mejora futura para eliminar esa dependencia.

### Exportación

La exportación de movimientos genera un libro XLSX con detalle y resumen por producto. La columna Usuario se informa como no registrada porque el esquema actual no tiene `user_id` ni tabla de usuarios.

## 5. Seguridad y límites actuales

- Las claves de servicios externos deben residir en secretos de Streamlit, no en archivos del repositorio.
- No existe autenticación multiusuario ni matriz de permisos.
- No se registra la identidad de quien crea cada movimiento.
- La función de IA solo explica información; las decisiones y transacciones siguen bajo control de la lógica determinística del sistema.
- SQLite activa claves foráneas en las conexiones creadas por `get_connection()`.

## 6. Evolución arquitectónica

| Fase | Evolución prevista |
|---|---|
| Fase 1 | Arquitectura modular Python + Streamlit + SQLite; flujo E2E de demanda, OP sucesivas por disponibilidad, compra/recepción, reservas, avances, consumo y conciliación validado. |
| Fase 2 | Auditoría, usuarios/roles, robustecimiento de abastecimiento, UX y asistente IA con contexto ampliado. |
| Fase 3 | Analítica y planeación avanzada; evaluación de servicios de datos para pronósticos y métricas de cobertura. |
