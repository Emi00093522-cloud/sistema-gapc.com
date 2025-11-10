import streamlit as st
import pandas as pd
from config.database import get_connection
from utils.auth import authenticate_user, get_user_role

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sistema de autenticación
def login_section():
    st.title("🔐 Sistema de Gestión GAPC")
    st.subheader("Inicio de Sesión")
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        
        if submit:
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                st.session_state.logged_in = True
                st.session_state.role = get_user_role(user[0])
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# Dashboard para Administrador
def show_admin_dashboard():
    st.title("🏢 Panel de Administración")
    
    conn = get_connection()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_grupos = pd.read_sql("SELECT COUNT(*) as total FROM Grupo", conn).iloc[0]['total']
        st.metric("Total Grupos", total_grupos)
    
    with col2:
        total_miembros = pd.read_sql("SELECT COUNT(*) as total FROM Miembro", conn).iloc[0]['total']
        st.metric("Total Miembros", total_miembros)
    
    with col3:
        total_ahorros = pd.read_sql("SELECT COALESCE(SUM(monto_ahorro), 0) as total FROM Ahorro", conn).iloc[0]['total']
        st.metric("Total Ahorros", f"${total_ahorros:,.2f}")
    
    with col4:
        total_prestamos = pd.read_sql("SELECT COALESCE(SUM(monto), 0) as total FROM Prestamo", conn).iloc[0]['total']
        st.metric("Total Préstamos", f"${total_prestamos:,.2f}")
    
    conn.close()
    
    # Mostrar datos en tablas
    st.subheader("Resumen Consolidado por Distrito")
    show_consolidado_distritos()

def show_consolidado_distritos():
    conn = get_connection()
    
    query = """
    SELECT d.nombre_distrito,
           COUNT(DISTINCT g.ID_Grupo) as grupos,
           COUNT(DISTINCT m.ID_Miembro) as miembros,
           COALESCE(SUM(a.monto_ahorro), 0) as total_ahorros,
           COALESCE(SUM(p.monto), 0) as total_prestamos
    FROM Distrito d
    LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito
    LEFT JOIN Miembro m ON g.ID_Grupo = m.ID_Grupo
    LEFT JOIN Ahorro a ON m.ID_Miembro = a.ID_Miembro
    LEFT JOIN Prestamo p ON m.ID_Miembro = p.ID_Miembro
    GROUP BY d.nombre_distrito
    """
    
    data = pd.read_sql(query, conn)
    conn.close()
    
    st.dataframe(data, use_container_width=True)

# Dashboard para Promotor
def show_promotor_dashboard():
    st.title("👥 Panel del Promotor")
    st.info("Selecciona un grupo del menú lateral para ver detalles")

def show_group_dashboard():
    st.title("👥 Panel de Directiva")
    st.info("Funcionalidades disponibles en el menú lateral")

# Control principal
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_section()
    else:
        if st.session_state.role == "Administrador":
            show_admin_dashboard()
        elif st.session_state.role == "Promotor":
            show_promotor_dashboard()
        else:
            show_group_dashboard()
        
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

if __name__ == "__main__":
    main()
