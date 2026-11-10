
import streamlit as st
import pandas as pd
from products import create_product
import sqlite3

from database import init_db
from products import get_products
from inventory import get_inventory, get_inventory_summary
from reports import (
    get_production_summary,
    get_purchase_summary
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

