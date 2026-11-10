
from database import get_connection


def get_inventory():
    """Consulta existencias físicas, reservas y disponibilidad."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            p.id,
            p.code,
            p.name,
            p.product_type,
            p.unit,
            p.unit_cost,
            COALESCE(s.physical_stock, 0) AS physical_stock,
            COALESCE((
                SELECT SUM(r.quantity - r.consumed_quantity)
                FROM reservations r
                WHERE r.product_id = p.id
                AND r.status = 'Activa'
            ), 0) AS reserved_stock
        FROM products p
        LEFT JOIN stock_balances s
            ON p.id = s.product_id
        WHERE p.active = 1
        ORDER BY p.name
    """).fetchall()

    conn.close()

    inventory = []

    for row in rows:
        item = dict(row)
        item["available_stock"] = (
            item["physical_stock"] - item["reserved_stock"]
        )
        item["inventory_value"] = (
            item["physical_stock"] * item["unit_cost"]
        )
        inventory.append(item)

    return inventory


def get_inventory_movements(product_id=None):
    """Consulta el historial de movimientos."""

    conn = get_connection()

    query = """
        SELECT
            m.id,
            m.created_at,
            p.code,
            p.name,
            m.movement_type,
            m.quantity,
            m.reference,
            m.unit_cost,
            (m.quantity * m.unit_cost) AS movement_value
        FROM inventory_movements m
        JOIN products p ON m.product_id = p.id
    """

    if product_id is not None:
        query += " WHERE m.product_id = ?"
        rows = conn.execute(
            query + " ORDER BY m.id DESC",
            (product_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            query + " ORDER BY m.id DESC"
        ).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_inventory_summary():
    """Calcula indicadores generales de inventario."""

    inventory = get_inventory()

    return {
        "total_references": len(inventory),
        "physical_units": sum(
            item["physical_stock"] for item in inventory
        ),
        "reserved_units": sum(
            item["reserved_stock"] for item in inventory
        ),
        "available_units": sum(
            item["available_stock"] for item in inventory
        ),
        "inventory_value": sum(
            item["inventory_value"] for item in inventory
        ),
        "low_stock_references": sum(
            1 for item in inventory
            if item["available_stock"] <= 0
        )
    }
