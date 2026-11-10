
import streamlit as st

# Configuración general de la aplicación
st.set_page_config(
    page_title="SYNTHEX | Gestión de fabricación",
    page_icon="⚙️",
    layout="wide"
)

# Estilos visuales
st.markdown("""
<style>
    .main {
        background-color: #F7F8FA;
    }

    .block-container {
        padding-top: 2rem;
    }

    .module-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        min-height: 145px;
    }

    .module-card h3 {
        color: #183153;
        margin-bottom: 8px;
    }

    .module-card p {
        color: #64748B;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Menú lateral
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

# Pantalla principal
if modulo == "Inicio":

    st.title("Panel de control")
    st.write("Bienvenido a SYNTHEX")
    st.caption(
        "Administra tus productos, materiales y procesos de fabricación "
        "desde un solo lugar."
    )

    st.divider()

    st.subheader("Módulos de gestión")

    # Primera fila
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="module-card">
            <h3>📦 Productos</h3>
            <p>Administra componentes y productos terminados.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <h3>🧩 Recetas</h3>
            <p>Define componentes y cantidades de fabricación.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="module-card">
            <h3>📋 Demandas</h3>
            <p>Registra solicitudes y calcula necesidades.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Segunda fila
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="module-card">
            <h3>🛒 Compras</h3>
            <p>Gestiona solicitudes y recepción de materiales.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="module-card">
            <h3>🏭 Producción</h3>
            <p>Controla órdenes, reservas y avances.</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="module-card">
            <h3>📊 Inventario</h3>
            <p>Consulta existencias y movimientos.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.info("Los módulos se habilitarán progresivamente durante el desarrollo.")

else:
    st.title(modulo)
    st.info(
        f"El módulo de {modulo.lower()} estará disponible "
        "en las siguientes etapas de desarrollo."
    )

st.divider()
st.caption("SYNTHEX | Alianza, Viabilidad y Network")
