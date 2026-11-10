# SYNTHEX — Diccionario de comandos Python, SQLite y Google Colab

**Versión:** 1.0  
**Proyecto:** SYNTHEX — Gestión de fabricación e inventarios  
**Objetivo:** Documentar los comandos y estructuras utilizados durante la construcción de la base de datos y las pruebas del sistema.

---

# 1. Librerías e importaciones de Python

Las librerías permiten incorporar funcionalidades desarrolladas previamente y utilizarlas dentro de nuestro código.

| Comando | Objetivo | Aplicación en SYNTHEX |
|---|---|---|
| `import sqlite3` | Importa la librería para trabajar con bases de datos SQLite. | Crear y consultar la base de datos. |
| `import math` | Importa funciones matemáticas. | Calcular capacidades máximas de fabricación. |
| `from google.colab import files` | Importa las herramientas para gestionar archivos en Colab. | Descargar la base de datos. |

**Ejemplos:**

```python
import sqlite3
import math
from google.colab import files
```

# 2. Variables y estructuras de datos

Permiten almacenar información temporalmente para procesarla y utilizarla en las operaciones.

| Elemento | Objetivo | Ejemplo |
|---|---|---|
| Variable | Almacena un valor. | `cantidad = 20` |
| Texto (`str`) | Representa nombres, códigos y estados. | `"Lámpara de escritorio"` |
| Entero (`int`) | Almacena números enteros. | `cantidad = 15` |
| Decimal (`float`) | Almacena cantidades decimales. | `cantidad = 1.5` |
| Lista (`list`) | Agrupa varios elementos. | `productos = [...]` |
| Tupla (`tuple`) | Agrupa valores ordenados. | `producto = ("MP001", 30)` |
| Diccionario (`dict`) | Organiza información mediante claves y valores. | `{"codigo": "MP001", "stock": 30}` |
| `None` | Representa la ausencia de un valor. | Resultado de una consulta sin registros. |

**Ejemplo utilizado para cargar productos:**

```python
productos = [
    ("MP001", "Base metálica", "COMPONENT", "Unidad", 12000),
    ("MP002", "Brazo articulado", "COMPONENT", "Unidad", 8000)
]
```

Cada tupla representa un producto con su código, nombre, tipo, unidad y costo.

# 3. Conexión y administración de SQLite

SQLite es el motor de base de datos utilizado para almacenar la información de SYNTHEX.

| Comando | Objetivo | Aplicación |
|---|---|---|
| `sqlite3.connect()` | Crea una conexión o abre una base de datos existente. | Conectar con `synthex.db`. |
| `conexion.execute()` | Ejecuta una instrucción SQL. | Crear tablas, insertar, actualizar o consultar información. |
| `conexion.executemany()` | Ejecuta una misma instrucción SQL para varios registros. | Cargar los siete productos iniciales. |
| `conexion.commit()` | Confirma y guarda los cambios realizados. | Persistir los registros y modificaciones. |
| `conexion.close()` | Cierra la conexión con la base de datos. | Liberar recursos. |
| `conexion.execute("PRAGMA foreign_keys = ON")` | Activa las restricciones de relaciones entre tablas. | Evitar referencias a productos inexistentes. |
| `conexion.execute("PRAGMA table_info(products)")` | Consulta la estructura de una tabla. | Verificar los campos creados. |
| `cursor.lastrowid` | Obtiene el identificador del último registro insertado. | Recuperar el ID de una orden o avance. |
| `fetchone()` | Recupera una fila de una consulta. | Consultar el ID de un producto. |
| `fetchall()` | Recupera todas las filas de una consulta. | Consultar el inventario completo. |

**Ejemplo:**

```python
conexion = sqlite3.connect("synthex.db")

resultado = conexion.execute("""
    SELECT name FROM products
""").fetchall()

conexion.close()
```

# 4. Instrucciones SQL utilizadas

SQL (*Structured Query Language*) es el lenguaje que permite comunicarse con la base de datos.

## 4.1. Creación de estructuras

| Instrucción | Objetivo | Aplicación |
|---|---|---|
| `CREATE TABLE` | Crea una tabla. | Crear productos, inventarios, recetas y órdenes. |
| `IF NOT EXISTS` | Evita crear una tabla si ya existe. | Permite ejecutar nuevamente el código de creación. |
| `PRIMARY KEY` | Define el identificador principal de un registro. | Identificar cada producto u orden. |
| `AUTOINCREMENT` | Genera identificadores numéricos consecutivos automáticamente. | Asignar IDs. |
| `FOREIGN KEY` | Relaciona una tabla con otra. | Vincular inventario con productos. |
| `NOT NULL` | Impide que un campo quede vacío. | Exigir código y nombre del producto. |
| `UNIQUE` | Evita valores duplicados. | Evitar códigos de producto repetidos. |
| `DEFAULT` | Define un valor predeterminado. | Establecer un estado inicial. |
| `CHECK` | Establece una condición que debe cumplir un dato. | Evitar cantidades negativas. |

**Ejemplo:**

```sql
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    unit_cost INTEGER DEFAULT 0
);
```

## 4.2. Registro y modificación de información

| Instrucción | Objetivo | Aplicación |
|---|---|---|
| `INSERT INTO` | Inserta un nuevo registro. | Crear una demanda. |
| `INSERT OR IGNORE` | Omite la inserción si existe un conflicto con una restricción. | Evitar duplicados en las cargas iniciales. |
| `UPDATE` | Modifica registros existentes. | Actualizar inventarios y estados de órdenes. |
| `SET` | Indica qué campos se van a modificar. | Cambiar existencias físicas. |
| `WHERE` | Establece las condiciones para seleccionar o modificar registros. | Actualizar un producto específico. |

**Ejemplo:**

```sql
UPDATE stock_balances
SET physical_quantity = physical_quantity + 20
WHERE product_id = 6;
```

Esta instrucción aumenta en 20 unidades la existencia del producto identificado.

## 4.3. Consultas de información

| Instrucción | Objetivo | Aplicación |
|---|---|---|
| `SELECT` | Consulta información. | Consultar productos e inventarios. |
| `FROM` | Indica la tabla de origen. | Consultar la tabla `products`. |
| `INNER JOIN` | Relaciona registros coincidentes de dos tablas. | Consultar productos junto con sus existencias. |
| `LEFT JOIN` | Conserva todos los registros de la tabla izquierda aunque no exista coincidencia. | Consultar productos sin saldo registrado. |
| `ON` | Define la condición de relación entre tablas. | Relacionar productos por su ID. |
| `ORDER BY` | Ordena los resultados. | Ordenar artículos por código. |
| `GROUP BY` | Agrupa registros según uno o varios campos. | Agrupar movimientos por tipo. |
| `AS` | Asigna un nombre temporal a una columna o tabla. | Mostrar un cálculo como `total`. |
| `DISTINCT` | Elimina duplicados en el resultado de una consulta. | Consultar valores únicos. |

**Ejemplo de relación entre tablas:**

```sql
SELECT
    p.name,
    s.physical_quantity
FROM products p
INNER JOIN stock_balances s
    ON s.product_id = p.id;
```

Esta consulta muestra los nombres de los productos junto con sus existencias.

## 4.4. Funciones de cálculo SQL

| Función | Objetivo | Aplicación |
|---|---|---|
| `SUM()` | Suma valores. | Calcular costos o cantidades totales. |
| `COUNT()` | Cuenta registros. | Contar movimientos. |
| `COALESCE()` | Sustituye valores nulos por otro valor. | Considerar cero cuando no existe saldo. |
| `MAX()` | Obtiene el valor máximo. | Identificar cantidades máximas. |
| `MIN()` | Obtiene el valor mínimo. | Identificar cantidades mínimas. |
| `AVG()` | Calcula el promedio. | Analizar costos promedio. |

**Ejemplo:**

```sql
SELECT SUM(quantity_consumed * unit_cost)
FROM production_consumptions;
```

Calcula el costo total de los materiales consumidos durante la producción.

# 5. Estructuras de control de Python

Permiten controlar el orden de ejecución del programa y tomar decisiones.

| Comando | Objetivo | Aplicación en SYNTHEX |
|---|---|---|
| `if` | Ejecuta instrucciones cuando se cumple una condición. | Verificar si existe inventario suficiente. |
| `else` | Ejecuta una alternativa cuando no se cumple la condición. | Informar cuando no existe una reserva. |
| `for` | Recorre los elementos de una lista o colección. | Registrar varios componentes de una receta. |
| `try` | Ejecuta código que podría generar errores. | Procesar una operación de producción. |
| `except` | Captura y gestiona errores. | Informar si falta inventario. |
| `finally` | Ejecuta instrucciones al finalizar el bloque, incluso si ocurre un error. | Cerrar conexiones. |
| `with` | Administra automáticamente un contexto de ejecución. | Gestionar transacciones de SQLite. |
| `raise` | Genera un error intencionalmente. | Detener una producción por falta de materiales. |

**Ejemplo:**

```python
if disponible >= necesario:
    print("Producción posible")
else:
    print("Inventario insuficiente")
```

# 6. Funciones y operaciones matemáticas de Python

| Comando | Objetivo | Aplicación |
|---|---|---|
| `print()` | Muestra información en pantalla. | Mostrar resultados de las pruebas. |
| `math.floor()` | Redondea un número hacia abajo al entero más cercano. | Calcular cuántas unidades pueden fabricarse. |
| `min()` | Obtiene el menor valor de una colección. | Identificar el componente limitante. |
| `max()` | Obtiene el mayor valor. | Comparar cantidades. |
| `sum()` | Suma los valores de una colección. | Calcular costos totales. |
| `len()` | Cuenta elementos de una colección. | Contar registros. |
| `round()` | Redondea un número. | Presentar resultados numéricos. |

**Ejemplo utilizado en el cálculo de capacidad de producción:**

```python
import math

capacidad = math.floor(60 / 4)

print(capacidad)
```

Resultado: 15 lámparas, porque cada una necesita cuatro tornillos.

# 7. Parámetros y formatos de salida

| Elemento | Objetivo | Ejemplo |
|---|---|---|
| `?` | Marcador de posición para parámetros SQL. | `WHERE code = ?` |
| `f-string` | Inserta variables dentro de un texto. | `f"${costo:,.0f} COP"` |
| `\n` | Genera un salto de línea. | Separar resultados. |
| `#` | Introduce un comentario en Python. | Explicar una operación. |
| `"""` | Delimita cadenas de varias líneas. | Escribir consultas SQL dentro de Python. |

**Ejemplo de consulta parametrizada:**

```python
conexion.execute("""
    SELECT * FROM products
    WHERE code = ?
""", ("MP001",))
```

El uso de parámetros evita construir consultas concatenando directamente los valores introducidos por el usuario.

# 8. Transacciones e integridad de datos

Las transacciones permiten ejecutar varias operaciones como una sola unidad lógica.

| Comando | Objetivo | Aplicación |
|---|---|---|
| `with conexion:` | Ejecuta operaciones dentro de una transacción. | Registrar un avance de producción. |
| `commit()` | Confirma los cambios. | Guardar operaciones. |
| `rollback()` | Revierte los cambios de una transacción. | Recuperarse de un error. |

En el proceso de fabricación, una transacción debe garantizar que no se descuente el inventario de componentes sin registrar correctamente el producto terminado y los movimientos correspondientes.

# 9. Comandos específicos de Google Colab

| Comando o herramienta | Objetivo | Aplicación |
|---|---|---|
| `files.download()` | Descarga un archivo al computador. | Descargar `synthex.db`. |
| `files.upload()` | Permite cargar archivos desde el computador. | Incorporar archivos de prueba. |
| `!` al inicio de una celda | Ejecuta comandos de terminal disponibles en el entorno. | Consultar o administrar archivos. |
| `Archivo → Guardar una copia en Drive` | Conserva una copia del cuaderno. | Respaldar el desarrollo. |
| Botón ▶ | Ejecuta una celda de código. | Probar cada instrucción. |

**Ejemplo utilizado para descargar la base de datos:**

```python
from google.colab import files

files.download("synthex.db")
```

# 10. Conceptos técnicos que debemos dominar

| Concepto | Explicación |
|---|---|
| Base de datos | Sistema organizado para almacenar y consultar información. |
| Tabla | Estructura que almacena registros de una misma entidad. |
| Registro | Fila de información dentro de una tabla. |
| Campo | Columna que representa una característica. |
| Clave primaria | Identificador único de un registro. |
| Clave foránea | Campo que conecta registros de diferentes tablas. |
| Consulta | Instrucción para recuperar información. |
| Integridad referencial | Garantiza relaciones válidas entre tablas. |
| Transacción | Conjunto de operaciones que deben confirmarse o revertirse conjuntamente. |
| CRUD | Crear, consultar, actualizar y eliminar registros. |
| BOM | *Bill of Materials*: lista de materiales necesarios para fabricar un producto. |
| Stock físico | Cantidad realmente existente. |
| Stock reservado | Cantidad comprometida para una operación. |
| Stock disponible | Cantidad física menos las reservas activas. |
| Trazabilidad | Capacidad de conocer el origen y el historial de una operación. |

# 11. Ejemplos prácticos de aplicación en SYNTHEX

| Necesidad del negocio | Herramientas utilizadas |
|---|---|
| Registrar un nuevo producto | `INSERT INTO`, `execute()` |
| Consultar catálogo | `SELECT`, `fetchall()` |
| Crear una receta | `INSERT INTO`, `FOREIGN KEY` |
| Calcular materiales necesarios | `SELECT`, `JOIN`, operaciones matemáticas |
| Identificar faltantes | `if`, `max()` |
| Calcular capacidad de fabricación | `math.floor()`, `min()` |
| Generar una solicitud de compra | `INSERT INTO` |
| Recibir materiales | `UPDATE`, `INSERT INTO` |
| Reservar componentes | `INSERT INTO`, `SUM()` |
| Registrar consumos | `UPDATE`, `INSERT INTO` |
| Calcular costos | `SUM()` |
| Verificar inventarios | `SELECT`, `JOIN` |
| Evitar registros duplicados | `UNIQUE`, `INSERT OR IGNORE` |
| Controlar errores | `try`, `except`, `raise` |
| Proteger operaciones | Transacciones SQLite |

# 12. Recomendaciones de aprendizaje

Para poder explicar técnicamente el desarrollo durante la entrevista, se recomienda dominar primero estos conceptos:

1. Diferencia entre Python y SQL.
2. Cómo conectarse a una base de datos.
3. Cómo crear tablas y relacionarlas.
4. Cómo registrar y consultar información.
5. Cómo utilizar claves primarias y foráneas.
6. Cómo calcular requerimientos de materiales.
7. Cómo controlar inventarios físicos y reservados.
8. Cómo utilizar transacciones para proteger los movimientos.
9. Cómo calcular costos de fabricación.
10. Cómo interpretar los resultados de una consulta.

---

**Nota de alcance:** este diccionario reúne los comandos, funciones e instrucciones utilizados durante las prácticas de construcción de la base de datos de SYNTHEX. No pretende ser un manual completo de Python o SQL, sino una referencia de los elementos aplicados en el proyecto.
