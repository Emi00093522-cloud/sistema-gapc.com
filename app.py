import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.database import get_connection, test_connection
from utils.auth import authenticate_user, get_user_role
from utils.charts import create_savings_trend_chart, create_loan_status_chart, create_income_expense_chart

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS
def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass  # Si no existe el CSS, continuar sin estilos

load_css()

# Sistema de autenticación
def login_section():
    st.title("🔐 Sistema de Gestión GAPC")
    st.markdown("### **Sistema de Grupos de Ahorro y Préstamo Comunitario**")
    
    # Verificar conexión a BD
    if test_connection():
        st.success("✅ Conectado a la base de datos")
    else:
        st.error("❌ No se pudo conectar a la base de datos")
        st.info("💡 Verifica la configuración en secrets.toml")
    
    st.info("""
    **Credenciales de prueba:**
    - 👨‍💼 **Administrador:** usuario: `admin` | contraseña: `admin123`
    - 👥 **Promotor:** usuario: `promotor1` | contraseña: `promotor123` 
    """)
    
    with st.form("login_form"):
        username = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("🚀 Ingresar al Sistema")
        
        if submit:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.session_state.role = get_user_role(user[0])
                    st.success(f"✅ ¡Bienvenido(a), {user[1]}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor ingresa usuario y contraseña")

# Dashboard para Administrador CON GRÁFICOS
def show_admin_dashboard():
    st.title("🏢 Panel de Administración")
    
    conn = get_connection()
    if conn is None:
        st.error("No hay conexión a la base de datos")
        return
    
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
    
    # Gráficos consolidados
    st.subheader("📊 Analytics del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de grupos por distrito
        distritos_data = pd.read_sql("""
        SELECT d.nombre_distrito, COUNT(g.ID_Grupo) as cantidad_grupos
        FROM Distrito d
        LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito
        GROUP BY d.nombre_distrito
        """, conn)
        
        if not distritos_data.empty:
            fig = px.pie(distritos_data, values='cantidad_grupos', names='nombre_distrito', 
                         title="📍 Distribución de Grupos por Distrito")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de estado de préstamos
        prestamos_data = pd.read_sql("""
        SELECT ep.estado_prestamo, COUNT(*) as cantidad
        FROM Prestamo p
        JOIN Estado_prestamo ep ON p.ID_Estado_prestamo = ep.ID_Estado_prestamo
        GROUP BY ep.estado_prestamo
        """, conn)
        
        if not prestamos_data.empty:
            fig = px.bar(prestamos_data, x='estado_prestamo', y='cantidad',
                        title="📈 Estado de Préstamos Global",
                        color='estado_prestamo')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla resumen
    st.subheader("📋 Resumen Consolidado por Distrito")
    show_consolidado_distritos(conn)
    
    conn.close()

def show_consolidado_distritos(conn):
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
    st.dataframe(data, use_container_width=True)

# Dashboard para Promotor CON GRÁFICOS
def show_promotor_dashboard():
    st.title("👥 Panel del Promotor")
    
    conn = get_connection()
    if conn is None:
        st.error("No hay conexión a la base de datos")
        return
    
    # Obtener grupos del promotor
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
        st.subheader(f"📊 Analytics - {selected_group}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_savings_trend_chart(grupo_id)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de ahorros para mostrar")
        
        with col2:
            chart = create_loan_status_chart(grupo_id)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de préstamos para mostrar")
        
        # Gráfico de ingresos vs egresos
        chart = create_income_expense_chart(grupo_id)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    else:
        st.info("No tienes grupos asignados")
    
    conn.close()

def show_group_dashboard():
    st.title("👥 Panel de Directiva")
    st.info("Utilice el menú lateral para acceder a las funcionalidades específicas")

# Control principal de la aplicación
def main():
    # Inicializar estado de sesión
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
    
    # Mostrar interfaz según estado de login
    if not st.session_state.logged_in:
        login_section()
    else:
        # Barra lateral con información del usuario
        st.sidebar.title(f"👋 ¡Hola, {st.session_state.user[1]}!")
        st.sidebar.write(f"**Rol:** {st.session_state.role}")
        st.sidebar.write(f"**Usuario:** {st.session_state.user[2]}")
        
        # Mostrar dashboard según rol
        if st.session_state.role == "Administrador":
            show_admin_dashboard()
        elif st.session_state.role == "Promotor":
            show_promotor_dashboard()
        else:
            show_group_dashboard()
        
        # Botón de logout
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Cerrar Sesión", type="primary"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

if __name__ == "__main__":
    main()
