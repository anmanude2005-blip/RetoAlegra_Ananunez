
from database import get_connection


def get_production_summary():
    """Resume las órdenes de producción."""

    conn = get_connection()

    result = conn.execute("""
        SELECT
            COUNT(*) AS total_orders,
            SUM(CASE WHEN status = 'Borrador' THEN 1 ELSE 0 END)
                AS draft_orders,
            SUM(CASE WHEN status = 'En producción' THEN 1 ELSE 0 END)
                AS active_orders,
            SUM(CASE WHEN status = 'Completada' THEN 1 ELSE 0 END)
                AS completed_orders,
            COALESCE(SUM(planned_quantity), 0) AS planned_units,
            COALESCE(SUM(produced_quantity), 0) AS produced_units
        FROM production_orders
    """).fetchone()

    conn.close()
    return dict(result)


def get_purchase_summary():
    """Resume las solicitudes de compra."""

    conn = get_connection()

    result = conn.execute("""
        SELECT
            COUNT(*) AS total_requests,
            SUM(CASE WHEN status = 'Pendiente' THEN 1 ELSE 0 END)
                AS pending_requests,
            SUM(CASE WHEN status = 'Recibida' THEN 1 ELSE 0 END)
                AS received_requests
        FROM purchase_requests
    """).fetchone()

    conn.close()
    return dict(result)


def get_material_consumption():
    """Consulta el consumo real de materiales en producción."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            p.code,
            p.name,
            SUM(pc.quantity) AS consumed_quantity,
            SUM(pc.quantity * pc.unit_cost) AS consumption_cost
        FROM production_consumptions pc
        JOIN products p ON pc.product_id = p.id
        GROUP BY p.id, p.code, p.name
        ORDER BY consumption_cost DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_production_costs():
    """Calcula los costos reales registrados por orden."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            po.code AS order_code,
            p.name AS finished_product,
            po.planned_quantity,
            po.produced_quantity,
            COALESCE(SUM(pc.quantity * pc.unit_cost), 0)
                AS material_cost
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        LEFT JOIN production_advances pa
            ON pa.production_order_id = po.id
        LEFT JOIN production_consumptions pc
            ON pc.advance_id = pa.id
        GROUP BY po.id, po.code, p.name,
                 po.planned_quantity, po.produced_quantity
        ORDER BY po.id DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]
