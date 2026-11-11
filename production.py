
from database import get_connection


#------------------------
def create_production_order(code, product_id, quantity, demand_id=None):
    """Crea una orden y guarda el costo estimado de materiales."""

    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Buscar la receta activa del producto
        recipe = cursor.execute("""
            SELECT id
            FROM recipes
            WHERE product_id = ? AND active = 1
        """, (product_id,)).fetchone()

        if not recipe:
            raise ValueError("El producto no tiene una receta activa.")

        # Calcular el costo estimado de materiales por unidad
        estimated_cost = cursor.execute("""
            SELECT COALESCE(SUM(rd.quantity * p.unit_cost), 0)
                AS estimated_unit_material_cost
            FROM recipe_details rd
            JOIN products p ON p.id = rd.component_id
            WHERE rd.recipe_id = ?
        """, (recipe["id"],)).fetchone()

        estimated_unit_cost = estimated_cost[
            "estimated_unit_material_cost"
        ]

        # Crear la orden conservando la receta y el costo estimado
        cursor.execute("""
            INSERT INTO production_orders (
                code,
                demand_id,
                product_id,
                recipe_id,
                planned_quantity,
                estimated_unit_material_cost
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            code,
            demand_id,
            product_id,
            recipe["id"],
            quantity,
            estimated_unit_cost
        ))

        order_id = cursor.lastrowid

        conn.commit()
        return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
#--------------------------

def release_production_order(order_id):
    """
    Libera una orden y reserva los componentes necesarios.
    Solo reserva materiales disponibles.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        order = cursor.execute("""
            SELECT *
            FROM production_orders
            WHERE id = ?
        """, (order_id,)).fetchone()

        if not order:
            raise ValueError("La orden no existe.")

        if order["status"] != "Borrador":
            raise ValueError("La orden no está en estado borrador.")

        components = cursor.execute("""
            SELECT
                rd.component_id,
                rd.quantity,
                COALESCE(sb.physical_stock, 0) AS physical_stock,
                COALESCE((
                    SELECT SUM(r.quantity - r.consumed_quantity)
                    FROM reservations r
                    WHERE r.product_id = rd.component_id
                    AND r.status = 'Activa'
                ), 0) AS already_reserved
            FROM recipe_details rd
            LEFT JOIN stock_balances sb
                ON sb.product_id = rd.component_id
            WHERE rd.recipe_id = ?
        """, (order["recipe_id"],)).fetchall()

        # Validar disponibilidad antes de reservar
        for component in components:
            required = (
                component["quantity"] *
                order["planned_quantity"]
            )

            available = (
                component["physical_stock"] -
                component["already_reserved"]
            )

            if available < required:
                raise ValueError(
                    f"Stock insuficiente para el componente "
                    f"{component['component_id']}. "
                    f"Requerido: {required}. Disponible: {available}."
                )

        # Crear las reservas
        for component in components:
            required = (
                component["quantity"] *
                order["planned_quantity"]
            )

            cursor.execute("""
                INSERT INTO reservations
                (production_order_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (
                order_id,
                component["component_id"],
                required
            ))

        cursor.execute("""
            UPDATE production_orders
            SET status = 'En producción'
            WHERE id = ?
        """, (order_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def register_production_advance(code, order_id, quantity, notes=""):
    """
    Registra un avance parcial o total de producción.
    Descuenta componentes y aumenta el producto terminado.
    """

    if quantity <= 0:
        raise ValueError("La cantidad producida debe ser mayor que cero.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        order = cursor.execute("""
            SELECT *
            FROM production_orders
            WHERE id = ?
        """, (order_id,)).fetchone()

        if not order:
            raise ValueError("La orden no existe.")

        if order["status"] != "En producción":
            raise ValueError("La orden no está habilitada para producir.")

        remaining = (
            order["planned_quantity"] -
            order["produced_quantity"]
        )

        if quantity > remaining:
            raise ValueError(
                f"Solo puedes producir {remaining} unidades pendientes."
            )

        # Consultar los componentes de la receta
        components = cursor.execute("""
            SELECT component_id, quantity
            FROM recipe_details
            WHERE recipe_id = ?
        """, (order["recipe_id"],)).fetchall()

        # Validar todas las reservas antes de consumir
        for component in components:
            required = component["quantity"] * quantity

            reservation = cursor.execute("""
                SELECT *
                FROM reservations
                WHERE production_order_id = ?
                AND product_id = ?
                AND status = 'Activa'
            """, (order_id, component["component_id"])).fetchone()

            if not reservation:
                raise ValueError(
                    f"No existe reserva activa para el componente "
                    f"{component['component_id']}."
                )

            available_reserved = (
                reservation["quantity"] -
                reservation["consumed_quantity"]
            )

            if available_reserved < required:
                raise ValueError(
                    f"Reserva insuficiente para el componente "
                    f"{component['component_id']}."
                )

            stock = cursor.execute("""
                SELECT physical_stock
                FROM stock_balances
                WHERE product_id = ?
            """, (component["component_id"],)).fetchone()

            if not stock or stock["physical_stock"] < required:
                raise ValueError(
                    f"Existencia física insuficiente para el componente "
                    f"{component['component_id']}."
                )

        # Registrar el avance
        cursor.execute("""
            INSERT INTO production_advances
            (code, production_order_id, produced_quantity, notes)
            VALUES (?, ?, ?, ?)
        """, (code, order_id, quantity, notes))

        advance_id = cursor.lastrowid
        total_cost = 0

        # Consumir los componentes realmente utilizados
        for component in components:
            component_id = component["component_id"]
            consumed = component["quantity"] * quantity

            product = cursor.execute("""
                SELECT unit_cost
                FROM products
                WHERE id = ?
            """, (component_id,)).fetchone()

            unit_cost = product["unit_cost"]
            total_cost += consumed * unit_cost

            cursor.execute("""
                INSERT INTO production_consumptions
                (advance_id, product_id, quantity, unit_cost)
                VALUES (?, ?, ?, ?)
            """, (advance_id, component_id, consumed, unit_cost))

            cursor.execute("""
                UPDATE stock_balances
                SET physical_stock = physical_stock - ?
                WHERE product_id = ?
            """, (consumed, component_id))

            cursor.execute("""
                UPDATE reservations
                SET consumed_quantity = consumed_quantity + ?
                WHERE production_order_id = ?
                AND product_id = ?
                AND status = 'Activa'
            """, (consumed, order_id, component_id))

            cursor.execute("""
                UPDATE reservations
                SET status = 'Consumida'
                WHERE production_order_id = ?
                AND product_id = ?
                AND quantity <= consumed_quantity
            """, (order_id, component_id))

            cursor.execute("""
                INSERT INTO inventory_movements
                (product_id, movement_type, quantity, reference, unit_cost)
                VALUES (?, 'SALIDA', ?, ?, ?)
            """, (component_id, consumed, code, unit_cost))

        # Ingresar producto terminado al inventario
        cursor.execute("""
            UPDATE stock_balances
            SET physical_stock = physical_stock + ?
            WHERE product_id = ?
        """, (quantity, order["product_id"]))

        # Costo de materiales por unidad producida
        unit_cost = total_cost / quantity

        cursor.execute("""
            UPDATE products
            SET unit_cost = ?
            WHERE id = ?
        """, (unit_cost, order["product_id"]))

        cursor.execute("""
            INSERT INTO inventory_movements
            (product_id, movement_type, quantity, reference, unit_cost)
            VALUES (?, 'ENTRADA', ?, ?, ?)
        """, (order["product_id"], quantity, code, unit_cost))

        # Actualizar avance y estado de la orden
        new_produced = order["produced_quantity"] + quantity

        new_status = (
            "Completada"
            if new_produced == order["planned_quantity"]
            else "En producción"
        )

        cursor.execute("""
            UPDATE production_orders
            SET produced_quantity = ?, status = ?
            WHERE id = ?
        """, (new_produced, new_status, order_id))

        conn.commit()
        return advance_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

#----------------

def get_production_orders():
    """Consulta las órdenes de producción."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            po.id,
            po.code,
            po.demand_id,
            po.product_id,
            p.code AS product_code,
            p.name AS product_name,
            po.recipe_id,
            po.planned_quantity,
            po.produced_quantity,
            (po.planned_quantity - po.produced_quantity)
                AS pending_quantity,
            po.status,
            po.created_at
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        ORDER BY po.id DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]

