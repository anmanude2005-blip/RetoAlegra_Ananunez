
from database import get_connection
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

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


def get_inventory_movements(
    product_id=None,
    start_date=None,
    end_date=None
):
    """Consulta movimientos de inventario con filtro de fechas."""

    conn = get_connection()

    query = """
        SELECT
            m.id,
            m.created_at,
            p.code,
            p.name,
            p.product_type,
            p.unit,
            m.movement_type,
            m.quantity,
            m.reference,
            m.unit_cost,
            (m.quantity * m.unit_cost) AS movement_value
        FROM inventory_movements m
        JOIN products p ON m.product_id = p.id
    """

    conditions = []
    parameters = []

    colombia_tz = ZoneInfo("America/Bogota")

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=colombia_tz
        ).astimezone(timezone.utc)

        conditions.append("m.created_at >= ?")
        parameters.append(
            start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=colombia_tz
        ).astimezone(timezone.utc)

        conditions.append("m.created_at < ?")
        parameters.append(
            end_datetime.strftime("%Y-%m-%d %H:%M:%S")
        )

    if product_id is not None:
        conditions.append("m.product_id = ?")
        parameters.append(product_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY m.created_at DESC, m.id DESC"

    try:
        rows = conn.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    finally:
        conn.close()
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
