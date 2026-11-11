
import streamlit as st
import pandas as pd
import sqlite3


from database import init_db, generate_document_code
from products import  create_product, get_products
from inventory import get_inventory, get_inventory_summary
from reports import (
    get_production_summary,
    get_purchase_summary,
    get_material_consumption,
    get_production_costs
)
from recipes import (
    get_recipes,
    get_recipe_details,
    calculate_recipe_cost,
    create_recipe
)
from demands import create_demand, get_demands, get_demand_requirements
from purchases import (
    create_purchase_request,
    get_purchase_requests,
    get_purchase_details,
    receive_purchase,
    create_purchase_from_demand
)
from production import (
    create_production_order,
    release_production_order,
    register_production_advance,
    get_production_orders
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



# DEMANDAS
elif modulo == "Demandas":

    st.title("Planificación de demandas")
    st.caption("Registra necesidades de productos y calcula materiales.")

    products = get_products()

    finished_products = [
        p for p in products
        if p["product_type"] == "Terminado" and p["active"] == 1
    ]

    with st.expander("＋ Registrar nueva demanda", expanded=False):

        if not finished_products:
            st.warning("Primero debes registrar un producto terminado.")

        else:
            with st.form("form_demanda"):

                product_options = {
                    p["id"]: f'{p["code"]} - {p["name"]}'
                    for p in finished_products
                }

                product_id = st.selectbox(
                    "Producto solicitado",
                    options=list(product_options.keys()),
                    format_func=lambda x: product_options[x]
                )

                quantity = st.number_input(
                    "Cantidad adicional requerida",
                    min_value=1,
                    value=20,
                    step=1
                )

                description = st.text_input(
                    "Descripción",
                    placeholder="Ej. Demanda de producción para cliente"
                )

                submitted = st.form_submit_button(
                    "Registrar demanda",
                    use_container_width=True
                )

            if submitted:
                try:
                    code = generate_document_code("DEM", "demands")

                    create_demand(
                        code,
                        description.strip(),
                        [(product_id, quantity)]
                    )

                    st.success(
                        f"Demanda {code} registrada correctamente."
                    )
                    st.rerun()

                except Exception as error:
                    st.error(
                        f"No fue posible registrar la demanda: {error}"
                    )

    st.divider()
    st.subheader("Demandas registradas")

    demands = get_demands()

    if demands:

        for demand in demands:

            with st.expander(
                f'{demand["code"]} | {demand["status"]}'
            ):

                st.write(demand["description"] or "Sin descripción")

                st.write(
                    f'Unidades solicitadas: {demand["total_units"] or 0}'
                )

                requirements = get_demand_requirements(demand["id"])

                if requirements:

                    st.markdown("**Materiales requeridos**")

                    df = pd.DataFrame(requirements)

                    st.dataframe(
                        df[[
                            "code",
                            "name",
                            "required_quantity",
                            "physical_stock",
                            "shortage"
                        ]],
                        use_container_width=True,
                        hide_index=True
                    )

                    total_shortages = sum(
                        item["shortage"] for item in requirements
                    )

                    if total_shortages > 0:

                        st.warning(
                            f"Se identificaron {total_shortages:g} "
                            "unidades faltantes de materiales."
                        )

                        if st.button(
                            "Generar solicitud de compra",
                            key=f'compra_{demand["id"]}'
                        ):
                            try:
                                purchase_code = generate_document_code(
                                    "OC",
                                    "purchase_requests"
                                )

                                purchase_id = create_purchase_from_demand(
                                    demand["id"],
                                    purchase_code
                                )

                                st.success(
                                    f"Solicitud {purchase_code} "
                                    "generada correctamente."
                                )
                                st.rerun()

                            except ValueError as error:
                                st.info(str(error))

                            except Exception as error:
                                st.error(
                                    f"No fue posible generar la compra: {error}"
                                )

                    else:
                        st.success(
                            "Hay existencias físicas suficientes "
                            "para atender los requerimientos."
                        )

                else:
                    st.info(
                        "No se encontraron componentes. "
                        "Verifica que el producto tenga una receta activa."
                    )

    else:
        st.info("Todavía no hay demandas registradas.")



# COMPRAS
elif modulo == "Compras":

    st.title("Gestión de compras")
    st.caption("Solicitudes y recepción de materiales.")

    products = get_products()

    components = [
        p for p in products
        if p["product_type"] == "Componente" and p["active"] == 1
    ]

    with st.expander("＋ Crear solicitud de compra", expanded=False):

        if not components:
            st.warning("No hay componentes registrados.")

        else:
            with st.form("form_compra"):

                code = st.text_input(
                    "Código de solicitud",
                    placeholder="Ej. OC-002"
                )

                component_options = {
                    p["id"]: f'{p["code"]} - {p["name"]}'
                    for p in components
                }

                product_id = st.selectbox(
                    "Material que deseas comprar",
                    options=list(component_options.keys()),
                    format_func=lambda x: component_options[x]
                )

                quantity = st.number_input(
                    "Cantidad solicitada",
                    min_value=1,
                    value=20,
                    step=1
                )

                unit_cost = st.number_input(
                    "Costo unitario estimado (COP)",
                    min_value=0.0,
                    step=100.0
                )

                submitted = st.form_submit_button(
                    "Crear solicitud",
                    use_container_width=True
                )

                if submitted:

                    if not code.strip():
                        st.error("Debes ingresar un código.")

                    else:
                        try:
                            create_purchase_request(
                                code.strip().upper(),
                                [(product_id, quantity, unit_cost)]
                            )

                            st.success("Solicitud creada correctamente.")
                            st.rerun()

                        except Exception as error:
                            st.error(f"No fue posible crear la solicitud: {error}")

    st.divider()
    st.subheader("Solicitudes registradas")

    purchases = get_purchase_requests()

    if purchases:

        for purchase in purchases:

            with st.expander(
                f'{purchase["code"]} | {purchase["status"]}'
            ):

                details = get_purchase_details(purchase["id"])

                if details:
                    st.dataframe(
                        pd.DataFrame(details),
                        use_container_width=True,
                        hide_index=True
                    )

                if purchase["status"] != "Recibida":

                    st.markdown("**Registrar recepción de materiales**")

                    with st.form(f'receipt_{purchase["id"]}'):

                        receipt_code = st.text_input(
                            "Código de recepción",
                            placeholder="Ej. REC-002",
                            key=f'receipt_code_{purchase["id"]}'
                        )

                        receipt_items = []

                        for item in details:

                            pending = (
                                item["requested_quantity"]
                                - item["received_quantity"]
                            )

                            if pending > 0:

                                st.write(
                                    f'{item["code"]} - {item["name"]} '
                                    f'| Pendiente: {pending:g}'
                                )

                                received = st.number_input(
                                    "Cantidad recibida",
                                    min_value=0.0,
                                    max_value=float(pending),
                                    value=float(pending),
                                    step=1.0,
                                    key=f'received_{purchase["id"]}_{item["product_id"]}'
                                )

                                receipt_items.append((
                                    item["product_id"],
                                    received,
                                    item["unit_cost"]
                                ))

                        receive_submitted = st.form_submit_button(
                            "Registrar recepción",
                            use_container_width=True
                        )

                        if receive_submitted:

                            valid_items = [
                                item for item in receipt_items
                                if item[1] > 0
                            ]

                            if not receipt_code.strip():
                                st.error("Debes ingresar un código de recepción.")

                            elif not valid_items:
                                st.error("Ingresa al menos una cantidad recibida.")

                            else:
                                try:
                                    receive_purchase(
                                        receipt_code.strip().upper(),
                                        purchase["id"],
                                        valid_items
                                    )

                                    st.success("Recepción registrada correctamente.")
                                    st.rerun()

                                except Exception as error:
                                    st.error(
                                        f"No fue posible registrar la recepción: {error}"
                                    )

    else:
        st.info("Todavía no hay solicitudes de compra.")

# PRODUCCIÓN
elif modulo == "Producción":

    st.title("Órdenes de producción")
    st.caption("Planifica, libera y registra avances de fabricación.")

    products = get_products()

    finished_products = [
        p for p in products
        if p["product_type"] == "Terminado" and p["active"] == 1
    ]

    demands = get_demands()

    with st.expander("＋ Crear orden de producción", expanded=False):

        if not finished_products:
            st.warning("Primero debes registrar un producto terminado.")

        else:
            with st.form("form_orden_produccion"):

                product_options = {
                    p["id"]: f'{p["code"]} - {p["name"]}'
                    for p in finished_products
                }

                product_id = st.selectbox(
                    "Producto que se va a fabricar",
                    options=list(product_options.keys()),
                    format_func=lambda x: product_options[x]
                )

                code = st.text_input(
                    "Código de la orden",
                    placeholder="Ej. OP-001"
                )

                quantity = st.number_input(
                    "Cantidad planeada",
                    min_value=1,
                    value=15,
                    step=1
                )

                demand_options = {
                    d["id"]: d["code"]
                    for d in demands
                }

                demand_id = st.selectbox(
                    "Demanda relacionada (opcional)",
                    options=[0] + list(demand_options.keys()),
                    format_func=lambda x: (
                        "Sin asociar" if x == 0 else demand_options[x]
                    )
                )

                submitted = st.form_submit_button(
                    "Crear orden",
                    use_container_width=True
                )

                if submitted:

                    if not code.strip():
                        st.error("Debes ingresar un código para la orden.")

                    else:
                        try:
                            create_production_order(
                                code.strip().upper(),
                                product_id,
                                quantity,
                                demand_id if demand_id != 0 else None
                            )

                            st.success("Orden creada en estado borrador.")
                            st.rerun()

                        except Exception as error:
                            st.error(f"No fue posible crear la orden: {error}")

    st.divider()
    st.subheader("Órdenes registradas")

    orders = get_production_orders()

    if orders:

        for order in orders:

            with st.expander(
                f'{order["code"]} | {order["product_name"]} | {order["status"]}'
            ):

                col1, col2, col3 = st.columns(3)

                col1.metric("Cantidad planeada", order["planned_quantity"])
                col2.metric("Cantidad producida", order["produced_quantity"])
                col3.metric("Cantidad pendiente", order["pending_quantity"])

                st.write(f'Producto: {order["product_code"]} - {order["product_name"]}')

                if order["status"] == "Borrador":

                    if st.button(
                        "Liberar orden y reservar materiales",
                        key=f'release_{order["id"]}'
                    ):

                        try:
                            release_production_order(order["id"])

                            st.success("Orden liberada y materiales reservados.")
                            st.rerun()

                        except Exception as error:
                            st.error(f"No fue posible liberar la orden: {error}")

                elif order["status"] == "En producción":

                    st.markdown("**Registrar avance de fabricación**")

                    with st.form(f'avance_{order["id"]}'):

                        advance_code = st.text_input(
                            "Código del avance",
                            placeholder="Ej. ADV-001",
                            key=f'advance_code_{order["id"]}'
                        )

                        advance_quantity = st.number_input(
                            "Unidades fabricadas en este avance",
                            min_value=0.0,
                            max_value=float(order["pending_quantity"]),
                            value=float(order["pending_quantity"]),
                            step=1.0,
                            key=f'advance_quantity_{order["id"]}'
                        )

                        notes = st.text_input(
                            "Observaciones",
                            key=f'advance_notes_{order["id"]}'
                        )

                        advance_submitted = st.form_submit_button(
                            "Registrar avance",
                            use_container_width=True
                        )

                        if advance_submitted:

                            if not advance_code.strip():
                                st.error("Debes ingresar un código para el avance.")

                            elif advance_quantity <= 0:
                                st.error("La cantidad debe ser mayor que cero.")

                            else:
                                try:
                                    register_production_advance(
                                        advance_code.strip().upper(),
                                        order["id"],
                                        advance_quantity,
                                        notes
                                    )

                                    st.success("Avance de producción registrado.")
                                    st.rerun()

                                except Exception as error:
                                    st.error(f"No fue posible registrar el avance: {error}")

                elif order["status"] == "Completada":
                    st.success("Esta orden ya fue completada.")

    else:
        st.info("Todavía no hay órdenes de producción.")


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
    st.caption(
        "Indicadores de producción, compras, consumo de materiales y costos."
    )

    production = get_production_summary()
    purchases = get_purchase_summary()

    # VALORES GENERALES
    total_orders = production.get("total_orders") or 0
    draft_orders = production.get("draft_orders") or 0
    active_orders = production.get("active_orders") or 0
    completed_orders = production.get("completed_orders") or 0
    planned_units = production.get("planned_units") or 0
    produced_units = production.get("produced_units") or 0

    pending_purchases = purchases.get("pending_requests") or 0
    received_purchases = purchases.get("received_requests") or 0
    total_purchases = purchases.get("total_requests") or 0

    # INDICADORES PRINCIPALES
    st.subheader("Resumen general")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Órdenes de producción", total_orders)
    col2.metric("Unidades producidas", produced_units)
    col3.metric("Órdenes completadas", completed_orders)
    col4.metric("Compras pendientes", pending_purchases)

    st.divider()

    # PRODUCCIÓN
    st.subheader("Producción")

    col1, col2, col3 = st.columns(3)

    col1.metric("Unidades planeadas", planned_units)
    col2.metric("Unidades producidas", produced_units)
    col3.metric(
        "Unidades pendientes",
        max(planned_units - produced_units, 0)
    )

    status_df = pd.DataFrame({
        "Estado": ["Borrador", "En producción", "Completada"],
        "Cantidad de órdenes": [
            draft_orders,
            active_orders,
            completed_orders
        ]
    })

    st.markdown("**Órdenes por estado**")
    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True
    )

    production_chart = pd.DataFrame(
        {"Unidades": [planned_units, produced_units]},
        index=["Planeadas", "Producidas"]
    )

    st.markdown("**Cumplimiento de producción**")
    st.bar_chart(production_chart)

    st.divider()

    # COMPRAS
    st.subheader("Compras")

    col1, col2, col3 = st.columns(3)

    col1.metric("Solicitudes registradas", total_purchases)
    col2.metric("Solicitudes pendientes", pending_purchases)
    col3.metric("Solicitudes recibidas", received_purchases)

    st.divider()

    # CONSUMO DE MATERIALES
    st.subheader("Consumo de materiales")

    materials = get_material_consumption()

    if materials:

        materials_df = pd.DataFrame(materials)

        materials_df = materials_df.rename(columns={
            "code": "Código",
            "name": "Material",
            "consumed_quantity": "Cantidad consumida",
            "consumption_cost": "Costo total (COP)"
        })

        total_consumption_cost = materials_df[
            "Costo total (COP)"
        ].sum()

        materials_display = materials_df.copy()

        materials_display["Costo total (COP)"] = (
            materials_display["Costo total (COP)"].map(
                lambda value: (
                    "$ " + f"{value:,.0f}".replace(",", ".") + " COP"
                )
            )
        )

        st.dataframe(
            materials_display,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("**Materiales con mayor consumo**")

        consumption_chart = materials_df.set_index("Material")[
            ["Cantidad consumida"]
        ]

        st.bar_chart(consumption_chart)

        st.metric(
            "Costo total de materiales consumidos",
            "$ " +
            f"{total_consumption_cost:,.0f}".replace(",", ".") +
            " COP"
        )

    else:
        st.info("Aún no hay consumos de materiales registrados.")

    st.divider()

    # COSTOS POR ORDEN
    st.subheader("Costos reales por orden de producción")

    costs = get_production_costs()

   
    if costs:

        costs_df = pd.DataFrame(costs)

        costs_df = costs_df.rename(columns={
            "order_code": "Orden",
            "finished_product": "Producto terminado",
            "planned_quantity": "Cantidad planeada",
            "produced_quantity": "Cantidad producida",
            "estimated_unit_material_cost": "Costo estimado por unidad (COP)",
            "material_cost": "Costo real de materiales (COP)"
        })

        # Las órdenes antiguas no tienen costo estimado histórico
        costs_df["Costo estimado por unidad (COP)"] = (
            costs_df["Costo estimado por unidad (COP)"].apply(
                lambda value: value if value > 0 else None
            )
        )

        # Costo estimado total de la orden
        costs_df["Costo estimado total (COP)"] = costs_df.apply(
            lambda row: (
                row["Costo estimado por unidad (COP)"] *
                row["Cantidad planeada"]
                if pd.notna(row["Costo estimado por unidad (COP)"])
                else None
            ),
            axis=1
        )

        # Costo real por unidad producida
        costs_df["Costo real por unidad (COP)"] = costs_df.apply(
            lambda row: (
                row["Costo real de materiales (COP)"] /
                row["Cantidad producida"]
                if row["Cantidad producida"] > 0 else None
            ),
            axis=1
        )

        # Variación frente al costo estimado de las unidades producidas
        costs_df["Variación (COP)"] = costs_df.apply(
            lambda row: (
                row["Costo real de materiales (COP)"] -
                (
                    row["Costo estimado por unidad (COP)"] *
                    row["Cantidad producida"]
                )
                if (
                    pd.notna(row["Costo estimado por unidad (COP)"])
                    and row["Cantidad producida"] > 0
                )
                else None
            ),
            axis=1
        )

        st.markdown("**Comparación de costos por orden**")

        columns_to_show = [
            "Orden",
            "Producto terminado",
            "Cantidad planeada",
            "Cantidad producida",
            "Costo estimado por unidad (COP)",
            "Costo estimado total (COP)",
            "Costo real de materiales (COP)",
            "Costo real por unidad (COP)",
            "Variación (COP)"
        ]

        costs_display = costs_df[columns_to_show].copy()

        currency_columns = [
            "Costo estimado por unidad (COP)",
            "Costo estimado total (COP)",
            "Costo real de materiales (COP)",
            "Costo real por unidad (COP)",
            "Variación (COP)"
        ]

        for column in currency_columns:
            costs_display[column] = costs_display[column].apply(
                lambda value: (
                    "$ " + f"{value:,.0f}".replace(",", ".") + " COP"
                    if pd.notna(value) else "No disponible"
                )
            )

        st.dataframe(
            costs_display,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "La variación compara el costo real acumulado con el costo "
            "estimado para las unidades efectivamente producidas. "
            "Un valor positivo indica un costo superior al estimado; "
            "uno negativo indica un costo inferior."
        )

        # Gráfico comparativo por unidad
        comparison_chart = costs_df.set_index("Orden")[
            [
                "Costo estimado por unidad (COP)",
                "Costo real por unidad (COP)"
            ]
        ]

        st.markdown("**Costo estimado vs. real por unidad**")
        st.bar_chart(comparison_chart)

    else:
        st.info("Aún no hay órdenes de producción registradas.")


# MÓDULOS PENDIENTES DE INTERFAZ
else:

    st.title(modulo)

    st.info(
        f"El módulo de {modulo.lower()} está conectado "
        "a la estructura del proyecto. "
        "Estamos preparando sus formularios y operaciones."
    )
