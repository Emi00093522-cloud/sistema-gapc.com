import streamlit as st
from app.services.auth_service import AuthService
from app.database.connection import DatabaseConnection
from app.ui.admin_panel import show_admin_panel
from app.ui.promotor_panel import show_promotor_panel
from app.ui.directiva_panel import show_directiva_panel

# Configuración de página
st.set_page_config(
    page_title="Comunidad Ahorra - Sistema GAPC",
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

def verificar_conexion_bd():
    db = DatabaseConnection()
    return db.test_connection()

def login_page():
    st.title("💰 Comunidad Ahorra - Sistema GAPC")
    st.markdown("---")
    
    if not verificar_conexion_bd():
        st.error("""
        ❌ No se puede conectar a la base de datos. Verifique:
        1. XAMPP está ejecutándose
        2. MySQL está activo
        3. Base de datos 'sistema_gapc' existe
        """)
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Iniciar Sesión")
        with st.form("login_form"):
            tipo_usuario = st.selectbox("Tipo de Usuario", ["Administrador", "Promotor", "Directiva"])
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("🚀 Ingresar al Sistema")
            
            if submitted and usuario and password:
                auth_service = AuthService()
                if auth_service.login(usuario, password, tipo_usuario):
                    st.success(f"✅ Bienvenido/a {usuario}!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
    
    with col2:
        st.info("""
        ### 👥 Credenciales de Prueba
        
        **Administrador:**
        - Usuario: `Administrador Principal`
        
        **Promotor:**
        - Usuario: `Promotor Ejemplo`
        
        **Directiva:**
        - Usuario: `Directiva Ejemplo`
        
        *Contraseña: cualquier texto*
        """)

def main_app():
    st.sidebar.title(f"👋 Bienvenido/a")
    st.sidebar.write(f"**Usuario:** {st.session_state.user['nombre']}")
    st.sidebar.write(f"**Rol:** {st.session_state.tipo_usuario}")
    st.sidebar.markdown("---")
    
    if st.session_state.tipo_usuario == "Administrador":
        show_admin_panel()
    elif st.session_state.tipo_usuario == "Promotor":
        show_promotor_panel()
    elif st.session_state.tipo_usuario == "Directiva":
        show_directiva_panel()
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
