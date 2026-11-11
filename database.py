
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "synthex.db"


def get_connection():
    """Abre la conexión con la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas y carga los datos iniciales."""

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Catálogo de productos y componentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            product_type TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'Unidad',
            unit_cost REAL NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # 2. Existencias físicas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER UNIQUE NOT NULL,
            physical_stock REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 3. Recetas de fabricación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            name TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(product_id, version),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 4. Componentes de cada receta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (component_id) REFERENCES products(id)
        )
    """)

    # 5. Demandas de productos terminados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Pendiente',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Productos solicitados en cada demanda
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demand_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demand_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            FOREIGN KEY (demand_id) REFERENCES demands(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 7. Solicitudes de compra
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    demand_id INTEGER,
    status TEXT NOT NULL DEFAULT 'Pendiente',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (demand_id) REFERENCES demands(id)
)
    """)

    # 8. Detalle de solicitudes de compra
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (purchase_id) REFERENCES purchase_requests(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 9. Recepciones de compras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            purchase_id INTEGER NOT NULL,
            received_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (purchase_id) REFERENCES purchase_requests(id)
        )
    """)

    # 10. Detalle de recepciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_receipt_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            FOREIGN KEY (receipt_id) REFERENCES purchase_receipts(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 11. Movimientos de inventario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            reference TEXT,
            unit_cost REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 12. Órdenes de producción
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            demand_id INTEGER,
            product_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            planned_quantity REAL NOT NULL,
            produced_quantity REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Borrador',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (demand_id) REFERENCES demands(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    """)

    # 13. Reservas de componentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            production_order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            consumed_quantity REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Activa',
            FOREIGN KEY (production_order_id) REFERENCES production_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 14. Avances de producción
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_advances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            production_order_id INTEGER NOT NULL,
            produced_quantity REAL NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (production_order_id) REFERENCES production_orders(id)
        )
    """)

    # 15. Consumo real de componentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_consumptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            advance_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            FOREIGN KEY (advance_id) REFERENCES production_advances(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    #---------------
    # Agregar demand_id a bases de datos existentes
columns = [
    row["name"]
    for row in cursor.execute(
        "PRAGMA table_info(purchase_requests)"
    ).fetchall()
]

if "demand_id" not in columns:
    cursor.execute("""
        ALTER TABLE purchase_requests
        ADD COLUMN demand_id INTEGER
    """)

    #-------------------------
    # Carga de datos de demostración, solo si el catálogo está vacío
    product_count = cursor.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if product_count == 0:
        products = [
            ("MP001", "Base metálica", "Componente", "Unidad", 12000),
            ("MP002", "Brazo articulado", "Componente", "Unidad", 8000),
            ("MP003", "Cable eléctrico", "Componente", "Unidad", 3500),
            ("MP004", "Interruptor", "Componente", "Unidad", 2500),
            ("MP005", "Bombillo LED", "Componente", "Unidad", 4000),
            ("MP006", "Tornillo", "Componente", "Unidad", 200),
            ("PT001", "Lámpara de escritorio", "Terminado", "Unidad", 30800),
        ]

        cursor.executemany("""
            INSERT INTO products
            (code, name, product_type, unit, unit_cost)
            VALUES (?, ?, ?, ?, ?)
        """, products)

        initial_stock = [30, 25, 40, 35, 30, 60, 10]

        for index, stock in enumerate(initial_stock, start=1):
            cursor.execute("""
                INSERT INTO stock_balances (product_id, physical_stock)
                VALUES (?, ?)
            """, (index, stock))

        # Receta versión 1 de la lámpara
        cursor.execute("""
            INSERT INTO recipes (product_id, version, name)
            VALUES (7, 1, 'Receta inicial de lámpara')
        """)

        recipe_id = cursor.lastrowid

        recipe_components = [
            (recipe_id, 1, 1),
            (recipe_id, 2, 1),
            (recipe_id, 3, 1),
            (recipe_id, 4, 1),
            (recipe_id, 5, 1),
            (recipe_id, 6, 4),
        ]

        cursor.executemany("""
            INSERT INTO recipe_details
            (recipe_id, component_id, quantity)
            VALUES (?, ?, ?)
        """, recipe_components)

    conn.commit()
    conn.close()

#-------------------

def generate_document_code(prefix, table):
    """
    Genera el siguiente código consecutivo de un documento.
    Ejemplo: DEM-001, DEM-002, DEM-003.
    """

    allowed_tables = {
        "demands",
        "purchase_requests",
        "purchase_receipts",
        "production_orders",
        "production_advances"
    }

    if table not in allowed_tables:
        raise ValueError("Tipo de documento no permitido.")

    conn = get_connection()

    try:
        result = conn.execute(
            f"""
            SELECT MAX(
                CAST(SUBSTR(code, ?) AS INTEGER)
            )
            FROM {table}
            WHERE code LIKE ?
            """,
            (len(prefix) + 2, prefix + "-%")
        ).fetchone()

        last_number = result[0] or 0
        next_number = last_number + 1

        return f"{prefix}-{next_number:03d}"

    finally:
        conn.close()
