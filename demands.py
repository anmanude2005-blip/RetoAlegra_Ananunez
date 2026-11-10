
from database import get_connection


def create_demand(code, description, products):
    """
    Registra una demanda.

    products debe tener esta estructura:
    [(product_id, quantity), ...]
    """

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


def get_demands():
    """Consulta las demandas registradas."""

    conn = get_connection()

    demands = conn.execute("""
        SELECT
            d.id,
            d.code,
            d.description,
            d.status,
            d.created_at,
            COUNT(dd.id) AS product_lines,
            SUM(dd.quantity) AS total_units
        FROM demands d
        LEFT JOIN demand_details dd
            ON d.id = dd.demand_id
        GROUP BY d.id
        ORDER BY d.id DESC
    """).fetchall()

    conn.close()
    return [dict(demand) for demand in demands]


def get_demand_requirements(demand_id):
    """
    Calcula los componentes necesarios para atender
    una demanda, según la receta activa de cada producto.
    """

    conn = get_connection()

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
        GROUP BY component.id, component.code, component.name,
                 stock.physical_stock
        ORDER BY component.name
    """, (demand_id,)).fetchall()

    conn.close()

    return [
        {
            **dict(item),
            "shortage": max(
                0,
                item["required_quantity"] - item["physical_stock"]
            )
        }
        for item in requirements
    ]
