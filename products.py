
from database import get_connection


def get_products():
    """Consulta todos los productos registrados."""
    conn = get_connection()

    products = conn.execute("""
        SELECT
            p.id,
            p.code,
            p.name,
            p.product_type,
            p.unit,
            p.unit_cost,
            p.active,
            p.created_at,
            COALESCE(s.physical_stock, 0) AS physical_stock
        FROM products p
        LEFT JOIN stock_balances s
            ON p.id = s.product_id
        ORDER BY p.name
    """).fetchall()

    conn.close()
    return [dict(product) for product in products]


def create_product(code, name, product_type, unit, unit_cost, initial_stock=0):
    """Registra un producto y su existencia inicial."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (code, name, product_type, unit, unit_cost, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (code, name, product_type, unit, unit_cost))

        product_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO stock_balances
            (product_id, physical_stock)
            VALUES (?, ?)
        """, (product_id, initial_stock))

        conn.commit()
        return product_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
#----------

def update_product(product_id, name, unit, unit_cost):
    """Actualiza los datos básicos de un producto."""

    conn = get_connection()

    try:
        conn.execute("""
            UPDATE products
            SET name = ?, unit = ?, unit_cost = ?
            WHERE id = ?
        """, (name, unit, unit_cost, product_id))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def deactivate_product(product_id):
    """Inactiva un producto sin eliminar su historial."""

    conn = get_connection()

    try:
        conn.execute("""
            UPDATE products
            SET active = 0
            WHERE id = ?
        """, (product_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
