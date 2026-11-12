
from database import get_connection


def create_demand(code, description, products):
    """Registra una demanda con uno o varios productos."""

    if not products:
        raise ValueError("La demanda debe incluir productos.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO demands (code, description)
            VALUES (?, ?)
        """, (code, description))

        demand_id = cursor.lastrowid

        cursor.executemany("""
            INSERT INTO demand_details
            (demand_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, [
            (demand_id, product_id, quantity)
            for product_id, quantity in products
        ])

        conn.commit()
        return demand_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def calculate_demand_status(
    requested_units,
    planned_units,
    produced_units,
    orders_in_production
):
    """Determina el estado real de una demanda."""

    if requested_units <= 0:
        return "Pendiente"

    if produced_units >= requested_units:
        return "Completada"

    if produced_units > 0:
        return "Producción parcial"

    if orders_in_production > 0:
        return "En producción"

    if planned_units > 0:
        return "Programada"

    return "Pendiente"


def get_demand_production_summary(demand_id):
    """
    Consulta las cantidades solicitadas, programadas y producidas
    por producto, excluyendo órdenes anuladas.
    """

    conn = get_connection()

    try:
        demand = conn.execute("""
            SELECT id, code, description
            FROM demands
            WHERE id = ?
        """, (demand_id,)).fetchone()

        if not demand:
            raise ValueError("La demanda no existe.")

        rows = conn.execute("""
            SELECT
                requested.product_id,
                p.code AS product_code,
                p.name AS product_name,
                requested.requested_quantity,

                COALESCE(orders.planned_quantity, 0)
                    AS planned_quantity,

                COALESCE(orders.produced_quantity, 0)
                    AS produced_quantity,

                COALESCE(orders.pending_orders, 0)
                    AS pending_orders,

                COALESCE(orders.active_orders, 0)
                    AS active_orders,

                COALESCE(orders.completed_orders, 0)
                    AS completed_orders

            FROM (
                SELECT
                    product_id,
                    SUM(quantity) AS requested_quantity
                FROM demand_details
                WHERE demand_id = ?
                GROUP BY product_id
            ) requested

            JOIN products p
                ON p.id = requested.product_id

            LEFT JOIN (
                SELECT
                    product_id,
                    SUM(planned_quantity) AS planned_quantity,
                    SUM(produced_quantity) AS produced_quantity,

                    SUM(
                        CASE WHEN status = 'Borrador'
                        THEN 1 ELSE 0 END
                    ) AS pending_orders,

                    SUM(
                        CASE WHEN status = 'En producción'
                        THEN 1 ELSE 0 END
                    ) AS active_orders,

                    SUM(
                        CASE WHEN status = 'Completada'
                        THEN 1 ELSE 0 END
                    ) AS completed_orders

                FROM production_orders
                WHERE demand_id = ?
                  AND status != 'Anulada'
                GROUP BY product_id
            ) orders
                ON orders.product_id = requested.product_id

            ORDER BY p.name
        """, (demand_id, demand_id)).fetchall()

        products = []

        for row in rows:

            item = dict(row)

            item["pending_to_produce"] = max(
                0,
                item["requested_quantity"] -
                item["produced_quantity"]
            )

            item["pending_to_schedule"] = max(
                0,
                item["requested_quantity"] -
                item["planned_quantity"]
            )

            products.append(item)

        requested_units = sum(
            item["requested_quantity"] for item in products
        )

        planned_units = sum(
            item["planned_quantity"] for item in products
        )

        produced_units = sum(
            item["produced_quantity"] for item in products
        )

        pending_to_produce = max(
            0,
            requested_units - produced_units
        )

        pending_to_schedule = sum(
            item["pending_to_schedule"] for item in products
        )

        orders_in_production = sum(
            item["active_orders"] for item in products
        )

        status = calculate_demand_status(
            requested_units,
            planned_units,
            produced_units,
            orders_in_production
        )

        return {
            "demand_id": demand["id"],
            "demand_code": demand["code"],
            "status": status,
            "requested_units": requested_units,
            "planned_units": planned_units,
            "produced_units": produced_units,
            "pending_to_produce": pending_to_produce,
            "pending_to_schedule": pending_to_schedule,
            "products": products
        }

    finally:
        conn.close()


def get_demand_orders(demand_id):
    """Consulta todas las órdenes asociadas, incluidas las anuladas."""

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                po.id,
                po.code,
                po.demand_id,
                po.product_id,
                p.code AS product_code,
                p.name AS product_name,
                po.planned_quantity,
                po.produced_quantity,
                (po.planned_quantity - po.produced_quantity)
                    AS pending_quantity,
                po.status,
                po.created_at
            FROM production_orders po
            JOIN products p
                ON p.id = po.product_id
            WHERE po.demand_id = ?
            ORDER BY po.id
        """, (demand_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_demands():
    """Consulta las demandas con sus estados y avances reales."""

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                d.id,
                d.code,
                d.description,
                d.created_at,
                COUNT(dd.id) AS product_lines,
                COALESCE(SUM(dd.quantity), 0) AS total_units
            FROM demands d
            LEFT JOIN demand_details dd
                ON d.id = dd.demand_id
            GROUP BY d.id
            ORDER BY d.id DESC
        """).fetchall()

        demands = []

        for row in rows:

            demand = dict(row)

            summary = get_demand_production_summary(
                demand["id"]
            )

            demand["status"] = summary["status"]
            demand["planned_units"] = summary["planned_units"]
            demand["produced_units"] = summary["produced_units"]
            demand["pending_to_produce"] = (
                summary["pending_to_produce"]
            )
            demand["pending_to_schedule"] = (
                summary["pending_to_schedule"]
            )

            demands.append(demand)

        return demands

    finally:
        conn.close()


def get_demand_requirements(demand_id):
    """
    Calcula los componentes necesarios para atender
    una demanda, según la receta activa de cada producto.
    """

    conn = get_connection()

    try:
        requirements = conn.execute("""
            SELECT
                component.id AS component_id,
                component.code,
                component.name,
                SUM(dd.quantity * rd.quantity) AS required_quantity,
                COALESCE(stock.physical_stock, 0) AS physical_stock
            FROM demand_details dd
            JOIN products finished
                ON dd.product_id = finished.id
            JOIN recipes r
                ON r.product_id = finished.id
                AND r.active = 1
            JOIN recipe_details rd
                ON rd.recipe_id = r.id
            JOIN products component
                ON component.id = rd.component_id
            LEFT JOIN stock_balances stock
                ON stock.product_id = component.id
            WHERE dd.demand_id = ?
            GROUP BY
                component.id,
                component.code,
                component.name,
                stock.physical_stock
            ORDER BY component.name
        """, (demand_id,)).fetchall()

        return [
            {
                **dict(item),
                "shortage": max(
                    0,
                    item["required_quantity"] -
                    item["physical_stock"]
                )
            }
            for item in requirements
        ]

    finally:
        conn.close()
