

from database import get_connection


def get_recipes():
    """Consulta las recetas y sus productos terminados."""

    conn = get_connection()

    recipes = conn.execute("""
        SELECT
            r.id,
            r.product_id,
            p.name AS product_name,
            r.version,
            r.name AS recipe_name,
            r.active
            r.created_at
        FROM recipes r
        JOIN products p ON r.product_id = p.id
        ORDER BY p.name, r.version DESC
    """).fetchall()

    conn.close()
    return [dict(recipe) for recipe in recipes]


def get_recipe_details(recipe_id):
    """Consulta los componentes de una receta."""

    conn = get_connection()

    details = conn.execute("""
        SELECT
            rd.component_id,
            p.code,
            p.name,
            p.unit,
            rd.quantity,
            p.unit_cost,
            (rd.quantity * p.unit_cost) AS total_cost
        FROM recipe_details rd
        JOIN products p ON rd.component_id = p.id
        WHERE rd.recipe_id = ?
    """, (recipe_id,)).fetchall()

    conn.close()
    return [dict(detail) for detail in details]


def calculate_recipe_cost(recipe_id):
    """Calcula el costo estimado de materiales por unidad."""

    conn = get_connection()

    result = conn.execute("""
        SELECT SUM(rd.quantity * p.unit_cost)
        FROM recipe_details rd
        JOIN products p ON rd.component_id = p.id
        WHERE rd.recipe_id = ?
    """, (recipe_id,)).fetchone()

    conn.close()
    return result[0] or 0

#-----------


def create_recipe(product_id, recipe_name, components):
    """
    Crea una nueva versión de la receta.

    components debe tener esta estructura:
    [(component_id, quantity), ...]
    """

    if not components:
        raise ValueError("La receta debe tener al menos un componente.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Identificar la última versión
        last_version = cursor.execute("""
            SELECT MAX(version)
            FROM recipes
            WHERE product_id = ?
        """, (product_id,)).fetchone()[0]

        new_version = (last_version or 0) + 1

        # Desactivar la versión anterior
        cursor.execute("""
            UPDATE recipes
            SET active = 0
            WHERE product_id = ?
        """, (product_id,))

        # Crear la nueva versión
        cursor.execute("""
            INSERT INTO recipes
            (product_id, version, name, active, created_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (product_id, new_version, recipe_name))

        recipe_id = cursor.lastrowid

        # Registrar sus componentes
        cursor.executemany("""
            INSERT INTO recipe_details
            (recipe_id, component_id, quantity)
            VALUES (?, ?, ?)
        """, [
            (recipe_id, component_id, quantity)
            for component_id, quantity in components
        ])

        conn.commit()
        return recipe_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

