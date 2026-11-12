
from database import get_connection


def create_purchase_request(code, items):
    """
    Registra una solicitud de compra.

    items: [(product_id, quantity, unit_cost), ...]
    """

    if not items:
        raise ValueError("La solicitud debe incluir materiales.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO purchase_requests (code)
            VALUES (?)
        """, (code,))

        purchase_id = cursor.lastrowid

        cursor.executemany("""
            INSERT INTO purchase_details
            (purchase_id, product_id, quantity, unit_cost)
            VALUES (?, ?, ?, ?)
        """, [
            (purchase_id, product_id, quantity, unit_cost)
            for product_id, quantity, unit_cost in items
        ])

        conn.commit()
        return purchase_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_purchase_requests():
    """Consulta las solicitudes de compra."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            pr.id,
            pr.code,
            pr.status,
            pr.created_at,
            COUNT(pd.id) AS product_lines,
            SUM(pd.quantity) AS requested_units
        FROM purchase_requests pr
        LEFT JOIN purchase_details pd
            ON pr.id = pd.purchase_id
        GROUP BY pr.id
        ORDER BY pr.id DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def receive_purchase(code, purchase_id, items):
    """
    Registra la recepción de materiales y actualiza inventario.

    items: [(product_id, quantity_received, unit_cost), ...]
    Permite recibir una compra en varias entregas.
    """

    if not items:
        raise ValueError("Debes incluir materiales recibidos.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Validar que exista la solicitud
        purchase = cursor.execute("""
            SELECT id, status
            FROM purchase_requests
            WHERE id = ?
        """, (purchase_id,)).fetchone()

        if not purchase:
            raise ValueError("La solicitud de compra no existe.")

        if purchase["status"] == "Recibida":
            raise ValueError("La solicitud ya fue recibida completamente.")

        # Crear el registro de recepción
        cursor.execute("""
            INSERT INTO purchase_receipts (code, purchase_id)
            VALUES (?, ?)
        """, (code, purchase_id))

        receipt_id = cursor.lastrowid

        for product_id, quantity, unit_cost in items:

            if quantity <= 0 or unit_cost < 0:
                raise ValueError("Cantidad o costo inválido.")

            # Verificar cantidad solicitada y recibida anteriormente
            requested = cursor.execute("""
                SELECT SUM(quantity)
                FROM purchase_details
                WHERE purchase_id = ? AND product_id = ?
            """, (purchase_id, product_id)).fetchone()[0]

            if requested is None:
                raise ValueError("El producto no pertenece a esta compra.")

            previously_received = cursor.execute("""
                SELECT COALESCE(SUM(prd.quantity), 0)
                FROM purchase_receipt_details prd
                JOIN purchase_receipts pr
                    ON prd.receipt_id = pr.id
                WHERE pr.purchase_id = ? AND prd.product_id = ?
            """, (purchase_id, product_id)).fetchone()[0]

            if previously_received + quantity > requested:
                raise ValueError(
                    f"La recepción supera lo solicitado para el producto {product_id}."
                )

            # Consultar existencia y costo promedio anterior
            balance = cursor.execute("""
                SELECT physical_stock
                FROM stock_balances
                WHERE product_id = ?
            """, (product_id,)).fetchone()

            if not balance:
                raise ValueError("El producto no tiene registro de inventario.")

            old_stock = balance["physical_stock"]

            old_cost = cursor.execute("""
                SELECT unit_cost
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()["unit_cost"]

            # Calcular costo promedio ponderado
            new_stock = old_stock + quantity

            if new_stock > 0:
                average_cost = (
                    (old_stock * old_cost) + (quantity * unit_cost)
                ) / new_stock
            else:
                average_cost = unit_cost

            # Registrar detalle de recepción
            cursor.execute("""
                INSERT INTO purchase_receipt_details
                (receipt_id, product_id, quantity, unit_cost)
                VALUES (?, ?, ?, ?)
            """, (receipt_id, product_id, quantity, unit_cost))

            # Actualizar existencias y costo promedio
            cursor.execute("""
                UPDATE stock_balances
                SET physical_stock = ?
                WHERE product_id = ?
            """, (new_stock, product_id))

            cursor.execute("""
                UPDATE products
                SET unit_cost = ?
                WHERE id = ?
            """, (average_cost, product_id))

            # Registrar movimiento de entrada
            cursor.execute("""
                INSERT INTO inventory_movements
                (product_id, movement_type, quantity, reference, unit_cost)
                VALUES (?, 'ENTRADA', ?, ?, ?)
            """, (product_id, quantity, code, unit_cost))

        # Actualizar estado de la solicitud
        pending = cursor.execute("""
            SELECT COUNT(*)
            FROM purchase_details pd
            WHERE pd.purchase_id = ?
            AND pd.quantity > (
                SELECT COALESCE(SUM(prd.quantity), 0)
                FROM purchase_receipt_details prd
                JOIN purchase_receipts pr
                    ON prd.receipt_id = pr.id
                WHERE pr.purchase_id = pd.purchase_id
                AND prd.product_id = pd.product_id
            )
        """, (purchase_id,)).fetchone()[0]

        new_status = "Pendiente" if pending else "Recibida"

        cursor.execute("""
            UPDATE purchase_requests
            SET status = ?
            WHERE id = ?
        """, (new_status, purchase_id))

        conn.commit()
        return receipt_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

#---------------

def get_purchase_details(purchase_id):
    """Consulta los materiales y cantidades de una solicitud."""

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            pd.product_id,
            p.code,
            p.name,
            pd.quantity AS requested_quantity,
            pd.unit_cost,
            COALESCE((
                SELECT SUM(prd.quantity)
                FROM purchase_receipt_details prd
                JOIN purchase_receipts pr
                    ON prd.receipt_id = pr.id
                WHERE pr.purchase_id = pd.purchase_id
                AND prd.product_id = pd.product_id
            ), 0) AS received_quantity
        FROM purchase_details pd
        JOIN products p ON p.id = pd.product_id
        WHERE pd.purchase_id = ?
    """, (purchase_id,)).fetchall()

    conn.close()
    return [dict(row) for row in rows]
#------------------

def create_purchase_from_demand(demand_id, code):
    """
    Genera una solicitud de compra a partir de los faltantes
    reales de una demanda.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Consultar los componentes requeridos por la demanda
        requirements = cursor.execute("""
            SELECT
                component.id AS product_id,
                component.name,
                component.unit_cost,
                SUM(dd.quantity * rd.quantity) AS required_quantity,
                COALESCE(sb.physical_stock, 0) AS physical_stock
            FROM demand_details dd
            JOIN recipes r
                ON r.product_id = dd.product_id
                AND r.active = 1
            JOIN recipe_details rd
                ON rd.recipe_id = r.id
            JOIN products component
                ON component.id = rd.component_id
            LEFT JOIN stock_balances sb
                ON sb.product_id = component.id
            WHERE dd.demand_id = ?
            GROUP BY component.id, component.name,
                     component.unit_cost, sb.physical_stock
        """, (demand_id,)).fetchall()

        if not requirements:
            raise ValueError(
                "No se encontraron componentes para esta demanda."
            )

        purchase_items = []

        for item in requirements:

            # Material reservado para otras órdenes
            reserved = cursor.execute("""
                SELECT COALESCE(
                    SUM(quantity - consumed_quantity), 0
                )
                FROM reservations
                WHERE product_id = ?
                AND status = 'Activa'
            """, (item["product_id"],)).fetchone()[0]

            # Compras pendientes de recibir
            pending_purchase = cursor.execute("""
                SELECT COALESCE(
                    SUM(pd.quantity - COALESCE(received.total, 0)), 0
                )
                FROM purchase_details pd
                JOIN purchase_requests pr
                    ON pr.id = pd.purchase_id
                LEFT JOIN (
                    SELECT
                        prd.product_id,
                        pr.purchase_id,
                        SUM(prd.quantity) AS total
                    FROM purchase_receipt_details prd
                    JOIN purchase_receipts pr
                        ON pr.id = prd.receipt_id
                    GROUP BY pr.purchase_id, prd.product_id
                ) received
                    ON received.purchase_id = pd.purchase_id
                    AND received.product_id = pd.product_id
                WHERE pd.product_id = ?
                AND pr.status != 'Recibida'
            """, (item["product_id"],)).fetchone()[0]

            available = item["physical_stock"] - reserved

            shortage = (
                item["required_quantity"]
                - available
                - pending_purchase
            )

            if shortage > 0:
                purchase_items.append((
                    item["product_id"],
                    shortage,
                    item["unit_cost"]
                ))

        if not purchase_items:
            raise ValueError(
                "No hay faltantes pendientes de compra para esta demanda."
            )

        # Crear la solicitud relacionada con la demanda
        cursor.execute("""
            INSERT INTO purchase_requests (code, demand_id)
            VALUES (?, ?)
        """, (code, demand_id))

        purchase_id = cursor.lastrowid

        cursor.executemany("""
            INSERT INTO purchase_details
            (purchase_id, product_id, quantity, unit_cost)
            VALUES (?, ?, ?, ?)
        """, [
            (purchase_id, product_id, quantity, unit_cost)
            for product_id, quantity, unit_cost in purchase_items
        ])

        conn.commit()
        return purchase_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_purchase_receipts(purchase_id):
    """Consulta el historial de recepciones de una solicitud."""

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                pr.id,
                pr.code,
                pr.purchase_id,
                pr.received_at,
                COUNT(prd.id) AS product_lines,
                COALESCE(SUM(prd.quantity), 0) AS received_units
            FROM purchase_receipts pr
            LEFT JOIN purchase_receipt_details prd
                ON prd.receipt_id = pr.id
            WHERE pr.purchase_id = ?
            GROUP BY pr.id
            ORDER BY pr.id ASC
        """, (purchase_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
