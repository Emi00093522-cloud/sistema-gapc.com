import streamlit as st
from app.services.auth_service import AuthService
from app.services.grupo_service import GrupoService
from app.services.reporte_service import ReporteService
from app.database.connection import DatabaseConnection
from app.ui.admin_panel import show_admin_panel
from app.ui.promotor_panel import show_promotor_panel
from app.ui.directiva_panel import show_directiva_panel

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'tipo_usuario' not in st.session_state:
        st.session_state.tipo_usuario = None

def login_page():
    st.title("💰 Sistema de Gestión GAPC")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Iniciar Sesión")
        
        with st.form("login_form"):
            tipo_usuario = st.selectbox(
                "Tipo de Usuario",
                ["Administrador", "Promotor", "Directiva"],
                key="tipo_login"
            )
            
            usuario = st.text_input("Usuario", key="usuario_login")
            password = st.text_input("Contraseña", type="password", key="password_login")
            
            submitted = st.form_submit_button("🚀 Ingresar al Sistema")
            
            if submitted:
                if usuario and password:
                    auth_service = AuthService()
                    if auth_service.login(usuario, password, tipo_usuario):
                        st.success(f"✅ Bienvenido/a {usuario}!")
                        st.session_state.tipo_usuario = tipo_usuario
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas o usuario no existe")
                else:
                    st.error("⚠️ Por favor ingrese usuario y contraseña")
    
    with col2:
        st.info("""
        ### ℹ️ Información del Sistema
        
        **GAPC** - Grupos de Ahorro y Préstamo Comunitario
        
        **Roles disponibles:**
        - 👨‍💼 Administrador
        - 👩‍💼 Promotor  
        - 👥 Directiva
        
        **Funcionalidades:**
        - Gestión de grupos
        - Control de ahorros
        - Administración de préstamos
        - Reportes y análisis
        - Cierre de ciclos
        """)

def main_app():
    st.sidebar.title(f"👋 Bienvenido/a")
    st.sidebar.write(f"**Usuario:** {st.session_state.user['nombre']}")
    st.sidebar.write(f"**Rol:** {st.session_state.tipo_usuario}")
    st.sidebar.markdown("---")
    
    # Navegación principal
    if st.session_state.tipo_usuario == "Administrador":
        show_admin_panel()
    elif st.session_state.tipo_usuario == "Promotor":
        show_promotor_panel()
    elif st.session_state.tipo_usuario == "Directiva":
        show_directiva_panel()
    
    # Footer
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    init_session_state()
    
    # Verificar conexión a BD
    db = DatabaseConnection()
    if not db.test_connection():
        st.error("""
        ❌ No se puede conectar a la base de datos. Verifique:
        1. ✅ XAMPP está ejecutándose
        2. ✅ MySQL está activo en puerto 3306
        3. ✅ La base de datos 'sistema_gapc' existe
        4. ✅ Las credenciales son correctas
        """)
        return
    
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
