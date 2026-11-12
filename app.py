
import streamlit as st
import pandas as pd
import sqlite3


from database import init_db, generate_document_code
from products import  create_product, get_products
from inventory import (
    get_inventory,
    get_inventory_summary,
    get_inventory_movements
)
from io import BytesIO
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
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
from demands import (
    create_demand,
    get_demands,
    get_demand_requirements,
    get_demand_production_summary,
    get_demand_orders
)
from purchases import (
    create_purchase_request,
    get_purchase_requests,
    get_purchase_details,
    receive_purchase,
    create_purchase_from_demand,
    get_purchase_receipts
)
from production import (
    create_production_order,
    release_production_order,
    register_production_advance,
    get_production_orders,
    cancel_production_order,
    get_production_advances,
    get_advance_consumptions
)
from ai_assistant import analyze_material_shortages

from date_utils import format_colombia_datetime

# Configuración de la aplicación
st.set_page_config(
    page_title="SYNTHEX | Gestión de fabricación",
    page_icon="⚙️",
    layout="wide"
)

# Inicializar base de datos
init_db()


# NAVEGACIÓN CORPORATIVA
st.sidebar.title("SYNTHEX")
st.sidebar.caption("Gestión inteligente de fabricación")

opciones = [
    "Inicio",
    "Productos",
    "Recetas",
    "Demandas",
    "Compras",
    "Producción",
    "Inventario",
    "Reportes"
]

if "modulo" not in st.session_state:
    st.session_state.modulo = "Inicio"

st.sidebar.markdown("### MENÚ PRINCIPAL")

for opcion in opciones:

    activo = st.session_state.modulo == opcion

    if st.sidebar.button(
        opcion,
        key=f"nav_{opcion}",
        use_container_width=True,
        type="primary" if activo else "secondary"
    ):
        st.session_state.modulo = opcion
        st.rerun()

modulo = st.session_state.modulo

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

        col1, col2, col3, col4 = st.columns(4)
    
        col1.metric(
            "Órdenes registradas",
            production["total_orders"] or 0
        )
    
        col2.metric(
            "Unidades programadas (vigentes)",
            production["planned_units"] or 0
        )
    
        col3.metric(
            "Unidades producidas (histórico)",
            production["produced_units"] or 0
        )
    
        col4.metric(
            "Unidades pendientes",
            production["pending_units"] or 0
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
                st.error(
                    "Debes ingresar el código y nombre del producto."
                )

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

                except Exception as error:
                    st.error(
                        f"No fue posible registrar el producto: {error}"
                    )

    st.divider()
    st.subheader("Productos registrados")

    products = get_products()

    if products:

        df = pd.DataFrame(products)

        df["created_at"] = df["created_at"].apply(
            format_colombia_datetime
        )

        df = df.rename(columns={
            "code": "Código",
            "name": "Producto",
            "product_type": "Tipo",
            "unit": "Unidad",
            "unit_cost": "Costo unitario",
            "active": "Activo",
            "physical_stock": "Existencia física",
            "created_at": "Fecha de creación"
        })

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

                st.caption(
                    f'Fecha de creación: '
                    f'{format_colombia_datetime(recipe["created_at"])}'
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
                st.caption(
                    f'Fecha de creación: '
                    f'{format_colombia_datetime(demand["created_at"])}'
                )

                st.write(
                    f'Unidades solicitadas: {demand["total_units"] or 0}'
                )

                
                # RESUMEN DE PRODUCCIÓN DE LA DEMANDA
                summary = get_demand_production_summary(demand["id"])

                st.markdown("### Seguimiento de producción")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Solicitadas",
                    summary["requested_units"]
                )

                col2.metric(
                    "Programadas",
                    summary["planned_units"]
                )

                col3.metric(
                    "Fabricadas",
                    summary["produced_units"]
                )

                col4.metric(
                    "Pendientes por fabricar",
                    summary["pending_to_produce"]
                )

                st.caption(
                    f'Pendientes por programar: '
                    f'{summary["pending_to_schedule"]}'
                )

                if summary["requested_units"] > 0:

                    progress = (
                        summary["produced_units"] /
                        summary["requested_units"]
                    )

                    st.progress(min(progress, 1.0))

                # HISTORIAL DE ÓRDENES ASOCIADAS
                st.markdown("### Órdenes de producción asociadas")

                associated_orders = get_demand_orders(demand["id"])

                if associated_orders:

                    orders_df = pd.DataFrame(associated_orders)

                    orders_display = orders_df.rename(columns={
                        "code": "Orden",
                        "product_code": "Código producto",
                        "product_name": "Producto",
                        "planned_quantity": "Cantidad planeada",
                        "produced_quantity": "Fabricadas",
                        "pending_quantity": "Pendientes",
                        "status": "Estado"
                    })

                    st.dataframe(
                        orders_display[[
                            "Orden",
                            "Código producto",
                            "Producto",
                            "Cantidad planeada",
                            "Fabricadas",
                            "Pendientes",
                            "Estado"
                        ]],
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "Esta demanda todavía no tiene órdenes asociadas."
                    )

                # CREAR ÓRDENES DESDE LA DEMANDA
                st.markdown("### Programar nueva orden de producción")

                for item in summary["products"]:

                    pending_schedule = item["pending_to_schedule"]

                    st.markdown(
                        f'**{item["product_code"]} - '
                        f'{item["product_name"]}**'
                    )

                    if pending_schedule > 0:

                        with st.form(
                            f'form_op_demanda_{demand["id"]}_{item["product_id"]}'
                        ):

                            st.caption(
                                f'Cantidad pendiente por programar: '
                                f'{pending_schedule:g} unidades.'
                            )

                            order_quantity = st.number_input(
                                "Cantidad para esta orden",
                                min_value=1,
                                max_value=int(pending_schedule),
                                value=int(pending_schedule),
                                step=1,
                                key=(
                                    f'qty_op_{demand["id"]}_'
                                    f'{item["product_id"]}'
                                )
                            )

                            create_order = st.form_submit_button(
                                "Crear orden de producción",
                                use_container_width=True
                            )

                        if create_order:

                            try:

                                order_code = generate_document_code(
                                    "OP",
                                    "production_orders"
                                )

                                create_production_order(
                                    order_code,
                                    item["product_id"],
                                    order_quantity,
                                    demand["id"]
                                )

                                st.success(
                                    f"Orden {order_code} creada correctamente."
                                )

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    f"No fue posible crear la orden: {error}"
                                )

                    else:

                        st.info(
                            "Este producto ya tiene toda su cantidad programada."
                        )

                st.divider()


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

                    #--------------------------
                    # ANÁLISIS INTELIGENTE DE MATERIALES
                    st.markdown("**Análisis con inteligencia artificial**")

                    if st.button(
                        "Analizar faltantes con IA",
                        key=f"analisis_ia_{demand['id']}",
                        use_container_width=True
                    ):
                        try:
                            analysis_context = {
                                "demand_code": demand["code"],
                                "description": (
                                    demand["description"] or ""
                                ),
                                "total_units_requested": (
                                    demand["total_units"] or 0
                                ),
                                "materials": [
                                    {
                                        "code": item["code"],
                                        "name": item["name"],
                                        "required_quantity": (
                                            item["required_quantity"]
                                        ),
                                        "physical_stock": (
                                            item["physical_stock"]
                                        ),
                                        "shortage": item["shortage"]
                                    }
                                    for item in requirements
                                ],
                                "instructions": (
                                    "Interpreta los faltantes según "
                                    "los cálculos actuales de SYNTHEX. "
                                    "No supongas compras pendientes "
                                    "ni reservas que no estén incluidas."
                                )
                            }

                            with st.spinner(
                                "La inteligencia artificial está "
                                "analizando los materiales..."
                            ):
                                ai_result = analyze_material_shortages(
                                    analysis_context
                                )

                            st.markdown("### Resultado del análisis")
                            st.markdown(ai_result)

                        except Exception as error:
                            st.error(
                                f"No fue posible generar el análisis: {error}"
                            )
#-----------------------------------
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

                try:
                    purchase_code = generate_document_code(
                        "OC",
                        "purchase_requests"
                    )

                    create_purchase_request(
                        purchase_code,
                        [(product_id, quantity, unit_cost)]
                    )

                    st.success(
                        f"Solicitud {purchase_code} creada correctamente."
                    )
                    st.rerun()

                except Exception as error:
                    st.error(
                        f"No fue posible crear la solicitud: {error}"
                    )

    st.divider()
    st.subheader("Solicitudes registradas")

    purchases = get_purchase_requests()

    if purchases:

        for purchase in purchases:

            with st.expander(
                f'{purchase["code"]} | {purchase["status"]}'
            ):

                #---------- 
                
                st.caption(
                    f'Fecha de creación: '
                    f'{format_colombia_datetime(purchase["created_at"])}'
                )

                # HISTORIAL DE RECEPCIONES
                st.markdown("**Historial de recepciones**")

                receipts = get_purchase_receipts(purchase["id"])

                if receipts:

                    receipts_df = pd.DataFrame(receipts)

                    receipts_df["received_at"] = (
                        receipts_df["received_at"].apply(
                            format_colombia_datetime
                        )
                    )

                    receipts_df = receipts_df.rename(columns={
                        "code": "Documento REC",
                        "received_at": "Fecha de recepción",
                        "product_lines": "Líneas de materiales",
                        "received_units": "Unidades recibidas"
                    })

                    st.dataframe(
                        receipts_df[[
                            "Documento REC",
                            "Fecha de recepción",
                            "Líneas de materiales",
                            "Unidades recibidas"
                        ]],
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "Esta solicitud todavía no tiene recepciones."
                    )
                #----------------------
                details = get_purchase_details(purchase["id"])

                if details:
                    details_df = pd.DataFrame(details)
                
                    details_df = details_df.rename(columns={
                        "code": "Código",
                        "name": "Material",
                        "requested_quantity": "Cantidad solicitada",
                        "unit_cost": "Costo unitario",
                        "received_quantity": "Cantidad recibida"
                    })
                
                    details_df = details_df.drop(
                        columns=["product_id"],
                        errors="ignore"
                    )
                
                    st.dataframe(
                        details_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                if purchase["status"] != "Recibida":

                    st.markdown("**Registrar recepción de materiales**")

                    with st.form(f'receipt_{purchase["id"]}'):

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
                                    key=(
                                        f'received_{purchase["id"]}_'
                                        f'{item["product_id"]}'
                                    )
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

                        if not valid_items:

                            st.error(
                                "Ingresa al menos una cantidad recibida."
                            )

                        else:

                            try:
                                receipt_code = generate_document_code(
                                    "REC",
                                    "purchase_receipts"
                                )

                                receive_purchase(
                                    receipt_code,
                                    purchase["id"],
                                    valid_items
                                )

                                st.success(
                                    f"Recepción {receipt_code} "
                                    "registrada correctamente."
                                )
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

                # codigo para ingreso manual, se pasa a automatico 
                #code = st.text_input(
                 #   "Código de la orden",
                  #  placeholder="Ej. OP-001"
                #)

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
        
            try:
                order_code = generate_document_code(
                    "OP",
                    "production_orders"
                )
        
                create_production_order(
                    order_code,
                    product_id,
                    quantity,
                    demand_id if demand_id != 0 else None
                )
        
                st.success(
                    f"Orden {order_code} creada en estado borrador."
                )
        
                st.rerun()
        
            except Exception as error:
                st.error(
                    f"No fue posible crear la orden: {error}"
                )

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

                st.write(    
                    f'Producto: {order["product_code"]} - {order["product_name"]}'
                )
                st.write(
                    f'Demanda asociada: {order["demand_code"] or "Sin asociar"}'
                )
                st.caption(
                    f'Fecha de creación: '
                    f'{format_colombia_datetime(order["created_at"])}'
                )

                st.caption(
                    f'Fecha de liberación: '
                    f'{format_colombia_datetime(order["released_at"])}'
                )
                
                st.caption(
                    f'Fecha de finalización: '
                    f'{format_colombia_datetime(order["completed_at"])}'
                )
                
                st.caption(
                    f'Fecha de anulación: '
                    f'{format_colombia_datetime(order["cancelled_at"])}'
                )


                # HISTORIAL DE AVANCES DE PRODUCCIÓN
                st.markdown("### Historial de avances")

                advances = get_production_advances(order["id"])

                if advances:

                    advances_df = pd.DataFrame(advances)

                    advances_df["created_at"] = advances_df[
                        "created_at"
                    ].apply(format_colombia_datetime)
                    
                    advances_display = advances_df.rename(columns={
                        "code": "Documento ADV",
                        "created_at": "Fecha de registro",
                        "produced_quantity": "Unidades fabricadas",
                        "material_cost": "Costo de materiales (COP)",
                        "notes": "Observaciones"
                    })

                    advances_display["Costo de materiales (COP)"] = (
                        advances_display["Costo de materiales (COP)"].map(
                            lambda value: (
                                "$ " + f"{value:,.0f}".replace(",", ".") + " COP"
                            )
                        )
                    )

                    st.dataframe(
                        advances_display[[
                            "Documento ADV",
                            "Fecha de registro",
                            "Unidades fabricadas",
                            "Costo de materiales (COP)",
                            "Observaciones"
                        ]],
                        use_container_width=True,
                        hide_index=True
                    )

                    # CONSULTAR DETALLE DE UN AVANCE
                    advance_options = {
                        advance["id"]: (
                            f'{advance["code"]} | '
                            f'{advance["produced_quantity"]:g} unidades'
                        )
                        for advance in advances
                    }

                    selected_advance_id = st.selectbox(
                        "Consultar detalle de materiales consumidos",
                        options=list(advance_options.keys()),
                        format_func=lambda x: advance_options[x],
                        key=f'advance_detail_{order["id"]}'
                    )

                    consumption = get_advance_consumptions(
                        selected_advance_id
                    )

                    if consumption:

                        consumption_df = pd.DataFrame(consumption)

                        consumption_display = consumption_df.rename(
                            columns={
                                "code": "Código material",
                                "name": "Material",
                                "quantity": "Cantidad consumida",
                                "unit_cost": "Costo unitario (COP)",
                                "total_cost": "Costo total (COP)"
                            }
                        )

                        for column in [
                            "Costo unitario (COP)",
                            "Costo total (COP)"
                        ]:
                            consumption_display[column] = (
                                consumption_display[column].map(
                                    lambda value: (
                                        "$ " +
                                        f"{value:,.0f}".replace(",", ".") +
                                        " COP"
                                    )
                                )
                            )

                        st.dataframe(
                            consumption_display,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:
                        st.info(
                            "Este avance no tiene consumos de materiales registrados."
                        )

                else:
                    st.info(
                        "Esta orden todavía no tiene avances registrados."
                    )


                
                if order["status"] == "Borrador":

                    st.warning(
                        "Esta orden todavía no ha iniciado producción."
                    )

                    confirm_cancel = st.checkbox(
                        f"Confirmo que deseo anular la orden {order['code']}",
                        key=f'confirm_cancel_{order["id"]}'
                    )

                    if st.button(
                        "Anular orden",
                        key=f'cancel_{order["id"]}',
                        disabled=not confirm_cancel
                    ):

                        try:
                            cancel_production_order(order["id"])

                            st.success(
                                f'La orden {order["code"]} fue anulada.'
                            )
                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"No fue posible anular la orden: {error}"
                            )

                    if st.button(
                        "Liberar orden y reservar materiales",
                        key=f'release_{order["id"]}'
                    ):

                        try:
                            release_production_order(order["id"])

                            st.success(
                                "Orden liberada y materiales reservados."
                            )
                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"No fue posible liberar la orden: {error}"
                            )


                elif order["status"] == "En producción":

                    st.markdown("**Registrar avance de fabricación**")

                    with st.form(f'avance_{order["id"]}'):

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

                        if advance_quantity <= 0:

                            st.error(
                                "La cantidad debe ser mayor que cero."
                            )

                        else:

                            try:
                                advance_code = generate_document_code(
                                    "ADV",
                                    "production_advances"
                                )

                                register_production_advance(
                                    advance_code,
                                    order["id"],
                                    advance_quantity,
                                    notes
                                )

                                st.success(
                                    f"Avance {advance_code} "
                                    "registrado correctamente."
                                )

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    f"No fue posible registrar el avance: {error}"
                                )

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

    st.divider()
    st.subheader("Historial y descarga de movimientos")
    today_colombia = datetime.now(
        ZoneInfo("America/Bogota")
    ).date()
    col_fecha1, col_fecha2 = st.columns(2)

    with col_fecha1:
        start_date = st.date_input(
            "Fecha inicial",
            value=today_colombia - timedelta(days=30),
            key="movement_start_date"
        )

    with col_fecha2:
        end_date = st.date_input(
            "Fecha final",
            value=today_colombia,
            key="movement_end_date"
        )

    if start_date > end_date:
        st.error(
            "La fecha inicial no puede ser posterior a la fecha final."
        )

    else:
        movements = get_inventory_movements(
            start_date=start_date,
            end_date=end_date
        )

        if movements:

            movements_df = pd.DataFrame(movements)

            # Resumen de entradas y salidas por producto
            movements_summary = movements_df.pivot_table(
                index=["code", "name", "product_type", "unit"],
                columns="movement_type",
                values="quantity",
                aggfunc="sum",
                fill_value=0
            ).reset_index()

            for movement_type in ["ENTRADA", "SALIDA"]:
                if movement_type not in movements_summary.columns:
                    movements_summary[movement_type] = 0

            movements_summary["Balance neto"] = (
                movements_summary["ENTRADA"]
                - movements_summary["SALIDA"]
            )

            # Preparar detalle de movimientos
            movements_df["Usuario"] = (
                "No registrado en esta versión"
            )

            movements_df["created_at"] = (
                movements_df["created_at"].apply(
                    format_colombia_datetime
                )
            )

            movements_display = movements_df.rename(
                columns={
                    "created_at": "Fecha y hora",
                    "code": "Código",
                    "name": "Producto",
                    "product_type": "Tipo de producto",
                    "unit": "Unidad",
                    "movement_type": "Tipo de movimiento",
                    "quantity": "Cantidad",
                    "reference": "Documento de referencia",
                    "unit_cost": "Costo unitario (COP)",
                    "movement_value": "Valor del movimiento (COP)"
                }
            )

            movements_display = movements_display[[
                "Fecha y hora",
                "Documento de referencia",
                "Código",
                "Producto",
                "Tipo de producto",
                "Tipo de movimiento",
                "Cantidad",
                "Unidad",
                "Costo unitario (COP)",
                "Valor del movimiento (COP)",
                "Usuario"
            ]]

            st.dataframe(
                movements_display,
                use_container_width=True,
                hide_index=True
            )

            # Preparar resumen por producto
            summary_display = movements_summary.rename(
                columns={
                    "code": "Código",
                    "name": "Producto",
                    "product_type": "Tipo de producto",
                    "unit": "Unidad",
                    "ENTRADA": "Total entradas",
                    "SALIDA": "Total salidas"
                }
            )

            summary_display = summary_display[[
                "Código",
                "Producto",
                "Tipo de producto",
                "Unidad",
                "Total entradas",
                "Total salidas",
                "Balance neto"
            ]]

            # Crear archivo Excel
            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                movements_display.to_excel(
                    writer,
                    sheet_name="Detalle movimientos",
                    index=False
                )

                summary_display.to_excel(
                    writer,
                    sheet_name="Resumen por producto",
                    index=False
                )

                # Ajustar presentación de las hojas
                for worksheet in writer.sheets.values():

                    worksheet.freeze_panes = "A2"
                    worksheet.auto_filter.ref = worksheet.dimensions

                    for column_cells in worksheet.columns:

                        max_length = max(
                            len(str(cell.value or ""))
                            for cell in column_cells
                        )

                        worksheet.column_dimensions[
                            column_cells[0].column_letter
                        ].width = min(max_length + 2, 35)

            st.download_button(
                label="Descargar movimientos en Excel",
                data=excel_buffer.getvalue(),
                file_name=(
                    f"SYNTHEX_movimientos_{start_date:%Y%m%d}_"
                    f"{end_date:%Y%m%d}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )

            st.caption(
                f"Se encontraron {len(movements_display)} movimientos "
                f"entre {start_date:%d/%m/%Y} "
                f"y {end_date:%d/%m/%Y}."
            )

        else:
            st.info(
                "No hay movimientos registrados en el rango seleccionado."
            )
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
    cancelled_orders = production.get("cancelled_orders") or 0
    planned_units = production.get("planned_units") or 0
    produced_units = production.get("produced_units") or 0

    pending_purchases = purchases.get("pending_requests") or 0
    received_purchases = purchases.get("received_requests") or 0
    total_purchases = purchases.get("total_requests") or 0

    # INDICADORES PRINCIPALES
    st.subheader("Resumen general")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Órdenes de producción", total_orders)
    col2.metric("Unidades producidas", produced_units)
    col3.metric("Órdenes completadas", completed_orders)
    col4.metric("Compras pendientes", pending_purchases)
    col5.metric("Órdenes anuladas", cancelled_orders)

    st.divider()

    # PRODUCCIÓN
    st.subheader("Producción")

    col1, col2, col3 = st.columns(3)

    col1.metric("Unidades planeadas", planned_units)
    col2.metric("Unidades producidas", produced_units)
    col3.metric(
        "Unidades pendientes",
        production.get("pending_units") or 0
    )

    status_df = pd.DataFrame({
    "Estado": [
        "Borrador",
        "En producción",
        "Completada",
        "Anulada"
    ],
    "Cantidad de órdenes": [
        draft_orders,
        active_orders,
        completed_orders,
        cancelled_orders
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
