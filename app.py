
import streamlit as st
import pandas as pd
import sqlite3


from database import init_db
from products import  create_product, get_products
from inventory import get_inventory, get_inventory_summary
from reports import (
    get_production_summary,
    get_purchase_summary
)
from recipes import (
    get_recipes,
    get_recipe_details,
    calculate_recipe_cost,
    create_recipe
)

# Configuración de la aplicación
st.set_page_config(
    page_title="SYNTHEX | Gestión de fabricación",
    page_icon="⚙️",
    layout="wide"
)

# Inicializar base de datos
init_db()

# Navegación
st.sidebar.title("SYNTHEX")
st.sidebar.caption("Gestión inteligente de fabricación")

modulo = st.sidebar.radio(
    "NAVEGACIÓN",
    [
        "Inicio",
        "Productos",
        "Recetas",
        "Demandas",
        "Compras",
        "Producción",
        "Inventario",
        "Reportes"
    ]
)

# PANTALLA DE INICIO
if modulo == "Inicio":

    st.title("Panel de control")
    st.caption("Resumen general de la operación")

    inventory = get_inventory_summary()
    production = get_production_summary()
    purchases = get_purchase_summary()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Referencias",
        inventory["total_references"]
    )

    col2.metric(
        "Unidades físicas",
        inventory["physical_units"]
    )

    col3.metric(
        "Órdenes activas",
        production["active_orders"] or 0
    )

    col4.metric(
        "Compras pendientes",
        purchases["pending_requests"] or 0
    )

    st.divider()

    st.subheader("Inventario disponible")

    stock = get_inventory()

    if stock:
        df = pd.DataFrame(stock)

        st.dataframe(
            df[[
                "code",
                "name",
                "physical_stock",
                "reserved_stock",
                "available_stock"
            ]],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Estado de producción")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Órdenes totales",
        production["total_orders"] or 0
    )

    col2.metric(
        "Unidades planeadas",
        production["planned_units"] or 0
    )

    col3.metric(
        "Unidades producidas",
        production["produced_units"] or 0
    )



# CATÁLOGO DE PRODUCTOS
elif modulo == "Productos":

    st.title("Catálogo de productos")
    st.caption("Administra productos terminados y componentes.")

    with st.expander("＋ Registrar nuevo producto", expanded=False):

        with st.form("form_producto"):

            col1, col2 = st.columns(2)

            with col1:
                code = st.text_input("Código de referencia")
                name = st.text_input("Nombre del producto")
                product_type = st.selectbox(
                    "Tipo de producto",
                    ["Componente", "Terminado"]
                )

            with col2:
                unit = st.selectbox(
                    "Unidad de medida",
                    ["Unidad", "Kilogramo", "Litro", "Metro", "Caja"]
                )
                unit_cost = st.number_input(
                    "Costo unitario (COP)",
                    min_value=0.0,
                    step=100.0
                )
                initial_stock = st.number_input(
                    "Existencia inicial",
                    min_value=0.0,
                    step=1.0
                )

            submitted = st.form_submit_button(
                "Guardar producto",
                use_container_width=True
            )

            if submitted:

                if not code.strip() or not name.strip():
                    st.error("Debes ingresar el código y el nombre.")

                else:
                    try:
                        create_product(
                            code.strip().upper(),
                            name.strip(),
                            product_type,
                            unit,
                            unit_cost,
                            initial_stock
                        )

                        st.success("Producto registrado correctamente.")
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.error(
                            "Este código ya existe. "
                            "Verifica la referencia."
                        )

                    except Exception as error:
                        st.error(f"No fue posible registrar el producto: {error}")

    st.divider()
    st.subheader("Productos registrados")

    products = get_products()

    if products:
        df = pd.DataFrame(products)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Todavía no hay productos registrados.")

# RECETAS DE FABRICACIÓN
elif modulo == "Recetas":

    st.title("Recetas de fabricación")
    st.caption("Define los materiales necesarios para fabricar cada producto.")

    products = get_products()

    finished_products = [
        p for p in products
        if p["product_type"] == "Terminado" and p["active"] == 1
    ]

    components_list = [
        p for p in products
        if p["product_type"] == "Componente" and p["active"] == 1
    ]

    with st.expander("＋ Crear nueva receta", expanded=False):

        if not finished_products:
            st.warning("Primero debes registrar un producto terminado.")

        elif not components_list:
            st.warning("Primero debes registrar componentes.")

        else:
            with st.form("form_receta"):

                product_options = {
                    p["id"]: p["name"]
                    for p in finished_products
                }

                product_id = st.selectbox(
                    "Producto que vamos a fabricar",
                    options=list(product_options.keys()),
                    format_func=lambda x: product_options[x]
                )

                recipe_name = st.text_input(
                    "Nombre de la receta",
                    placeholder="Ej. Receta estándar de fabricación"
                )

                st.markdown("**Componentes necesarios por unidad**")

                component_options = {
                    p["id"]: f'{p["code"]} - {p["name"]}'
                    for p in components_list
                }

                selected_components = st.multiselect(
                    "Selecciona los componentes",
                    options=list(component_options.keys()),
                    format_func=lambda x: component_options[x]
                )

                quantities = {}

                for component_id in selected_components:
                    component_name = component_options[component_id]

                    quantities[component_id] = st.number_input(
                        f"Cantidad de {component_name}",
                        min_value=0.01,
                        value=1.0,
                        step=1.0,
                        key=f"quantity_{component_id}"
                    )

                submitted = st.form_submit_button(
                    "Guardar receta",
                    use_container_width=True
                )

                if submitted:

                    if not recipe_name.strip():
                        st.error("Debes ingresar un nombre para la receta.")

                    elif not selected_components:
                        st.error("Selecciona al menos un componente.")

                    else:
                        try:
                            components = [
                                (component_id, quantities[component_id])
                                for component_id in selected_components
                            ]

                            create_recipe(
                                product_id,
                                recipe_name.strip(),
                                components
                            )

                            st.success("Receta creada correctamente.")
                            st.rerun()

                        except Exception as error:
                            st.error(f"No fue posible crear la receta: {error}")

    st.divider()
    st.subheader("Recetas registradas")

    recipes = get_recipes()

    if recipes:

        for recipe in recipes:

            with st.expander(
                f'{recipe["product_name"]} | Versión {recipe["version"]}'
            ):

                details = get_recipe_details(recipe["id"])

                if details:
                    st.dataframe(
                        pd.DataFrame(details),
                        use_container_width=True,
                        hide_index=True
                    )

                    cost = calculate_recipe_cost(recipe["id"])

                    st.metric(
                        "Costo estimado de materiales por unidad",
                        f"${cost:,.0f} COP"
                    )

                st.caption(
                    f'Nombre: {recipe["recipe_name"]} | '
                    f'Estado: {"Activa" if recipe["active"] else "Inactiva"}'
                )

    else:
        st.info("Todavía no hay recetas registradas.")



# INVENTARIO
elif modulo == "Inventario":

    st.title("Control de inventario")

    inventory = get_inventory()

    if inventory:
        st.dataframe(
            pd.DataFrame(inventory),
            use_container_width=True,
            hide_index=True
        )

    summary = get_inventory_summary()

    st.subheader("Indicadores de inventario")

    col1, col2, col3 = st.columns(3)

    col1.metric("Existencias físicas", summary["physical_units"])
    col2.metric("Reservadas", summary["reserved_units"])
    col3.metric("Disponibles", summary["available_units"])


# REPORTES
elif modulo == "Reportes":

    st.title("Reportes de gestión")

    production = get_production_summary()
    purchases = get_purchase_summary()

    st.subheader("Producción")

    st.json(production)

    st.subheader("Compras")

    st.json(purchases)


# MÓDULOS PENDIENTES DE INTERFAZ
else:

    st.title(modulo)

    st.info(
        f"El módulo de {modulo.lower()} está conectado "
        "a la estructura del proyecto. "
        "Estamos preparando sus formularios y operaciones."
    )

