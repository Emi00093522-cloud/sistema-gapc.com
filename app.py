import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.database import get_connection
from utils.auth import authenticate_user, get_user_role

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

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

# Panel principal después del login
def main_dashboard():
    st.sidebar.title(f"👋 Bienvenido, {st.session_state.user[1]}")
    st.sidebar.write(f"Rol: {st.session_state.role}")
    
    # Navegación según el rol
    if st.session_state.role == "Administrador":
        show_admin_dashboard()
    elif st.session_state.role == "Promotor":
        show_promotor_dashboard()
    else:
        show_group_dashboard()

# Dashboard para Administrador
def show_admin_dashboard():
    st.title("🏢 Panel de Administración")
    
    # Obtener datos consolidados
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
    
    # Gráficos consolidados
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ingresos vs Egresos por Distrito")
        chart_ingresos_egresos_distrito()
    
    with col2:
        st.subheader("Distribución de Grupos por Distrito")
        chart_grupos_por_distrito()
    
    # Tabla resumen
    st.subheader("Resumen Consolidado por Distrito")
    show_consolidado_distritos()

# Dashboard para Promotor
def show_promotor_dashboard():
    st.title("👥 Panel del Promotor")
    
    # Obtener grupos del promotor
    conn = get_connection()
    promotor_id = st.session_state.user[0]
    
    grupos = pd.read_sql(
        "SELECT * FROM Grupo WHERE ID_Promotor = %s", 
        conn, 
        params=(promotor_id,)
    )
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist())
        grupo_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        # Métricas del grupo seleccionado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            miembros_count = pd.read_sql(
                "SELECT COUNT(*) as total FROM Miembro WHERE ID_Grupo = %s", 
                conn, 
                params=(grupo_id,)
            ).iloc[0]['total']
            st.metric("Miembros", miembros_count)
        
        with col2:
            ahorros_grupo = pd.read_sql(
                "SELECT COALESCE(SUM(a.monto_ahorro), 0) as total FROM Ahorro a JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro WHERE m.ID_Grupo = %s", 
                conn, 
                params=(grupo_id,)
            ).iloc[0]['total']
            st.metric("Ahorros del Grupo", f"${ahorros_grupo:,.2f}")
        
        with col3:
            prestamos_grupo = pd.read_sql(
                "SELECT COALESCE(SUM(p.monto), 0) as total FROM Prestamo p JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro WHERE m.ID_Grupo = %s", 
                conn, 
                params=(grupo_id,)
            ).iloc[0]['total']
            st.metric("Préstamos Activos", f"${prestamos_grupo:,.2f}")
        
        with col4:
            reuniones_count = pd.read_sql(
                "SELECT COUNT(*) as total FROM Reunion WHERE ID_Grupo = %s", 
                conn, 
                params=(grupo_id,)
            ).iloc[0]['total']
            st.metric("Reuniones", reuniones_count)
        
        # Gráficos del grupo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"Ingresos vs Egresos - {selected_group}")
            chart_ingresos_egresos_grupo(grupo_id)
        
        with col2:
            st.subheader(f"Estado de Préstamos - {selected_group}")
            chart_estado_prestamos_grupo(grupo_id)
    
    conn.close()

# Funciones para gráficos
def chart_ingresos_egresos_distrito():
    conn = get_connection()
    
    query = """
    SELECT d.nombre_distrito, 
           SUM(CASE WHEN tm.tipo_movimiento = 'ingreso' THEN mc.monto ELSE 0 END) as ingresos,
           SUM(CASE WHEN tm.tipo_movimiento = 'egreso' THEN mc.monto ELSE 0 END) as egresos
    FROM Movimiento_caja mc
    JOIN Tipo_movimiento tm ON mc.ID_Tipo_movimiento = tm.ID_Tipo_movimiento
    JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
    JOIN Grupo g ON r.ID_Grupo = g.ID_Grupo
    JOIN Distrito d ON g.ID_Distrito = d.ID_Distrito
    GROUP BY d.nombre_distrito
    """
    
    data = pd.read_sql(query, conn)
    conn.close()
    
    if not data.empty:
        fig = go.Figure(data=[
            go.Bar(name='Ingresos', x=data['nombre_distrito'], y=data['ingresos']),
            go.Bar(name='Egresos', x=data['nombre_distrito'], y=data['egresos'])
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de movimientos para mostrar")

def chart_grupos_por_distrito():
    conn = get_connection()
    
    query = """
    SELECT d.nombre_distrito, COUNT(g.ID_Grupo) as cantidad_grupos
    FROM Distrito d
    LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito
    GROUP BY d.nombre_distrito
    """
    
    data = pd.read_sql(query, conn)
    conn.close()
    
    if not data.empty:
        fig = px.pie(data, values='cantidad_grupos', names='nombre_distrito', 
                     title="Distribución de Grupos por Distrito")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay grupos registrados")

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

def chart_ingresos_egresos_grupo(grupo_id):
    conn = get_connection()
    
    query = """
    SELECT tm.tipo_movimiento, SUM(mc.monto) as total
    FROM Movimiento_caja mc
    JOIN Tipo_movimiento tm ON mc.ID_Tipo_movimiento = tm.ID_Tipo_movimiento
    JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
    WHERE r.ID_Grupo = %s
    GROUP BY tm.tipo_movimiento
    """
    
    data = pd.read_sql(query, conn, params=(grupo_id,))
    conn.close()
    
    if not data.empty:
        fig = px.bar(data, x='tipo_movimiento', y='total', 
                     title="Movimientos de Caja")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay movimientos para este grupo")

def chart_estado_prestamos_grupo(grupo_id):
    conn = get_connection()
    
    query = """
    SELECT ep.estado_prestamo, COUNT(p.ID_Prestamo) as cantidad
    FROM Prestamo p
    JOIN Estado_prestamo ep ON p.ID_Estado_prestamo = ep.ID_Estado_prestamo
    JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
    WHERE m.ID_Grupo = %s
    GROUP BY ep.estado_prestamo
    """
    
    data = pd.read_sql(query, conn, params=(grupo_id,))
    conn.close()
    
    if not data.empty:
        fig = px.pie(data, values='cantidad', names='estado_prestamo',
                     title="Estado de Préstamos")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay préstamos en este grupo")

def show_group_dashboard():
    st.title("👥 Panel de Directiva")
    st.info("Funcionalidades para directiva de grupo en desarrollo")

# Control principal de la aplicación
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_section()
    else:
        main_dashboard()
        
        # Botón de logout
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

if __name__ == "__main__":
    main()
