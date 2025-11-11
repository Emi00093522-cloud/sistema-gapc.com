import streamlit as st
import sys
import os

# Agregar el directorio app al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from auth.authentication import check_authentication, session_manager
from config import config
from database.connection import test_connection

def main():
    # Configuración de la página
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Verificar conexión a la base de datos
    if not test_connection():
        st.error("❌ No se pudo conectar a la base de datos. Verifica la configuración.")
        st.stop()
    
    # Verificar autenticación
    check_authentication()
    
    # Obtener usuario actual
    user = session_manager.get_user()
    
    # Sidebar con navegación
    with st.sidebar:
        st.title(f"💰 {config.APP_TITLE}")
        st.markdown("---")
        
        # Información del usuario
        st.success(f"👤 **{user['nombre']}**")
        st.info(f"🏷️ {user['cargo_nombre']} | {user['tipo_usuario']}")
        st.markdown("---")
        
        # Menú de navegación
        st.subheader("📋 Navegación")
        
        # Diferentes menús según el rol
        if user['cargo_nombre'] == 'administrador':
            show_admin_menu()
        elif user['cargo_nombre'] == 'promotora':
            show_promotor_menu()
        else:
            show_group_menu(user)
        
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            session_manager.logout()
            st.rerun()
    
    # Contenido principal del dashboard
    show_dashboard_content(user)

def show_admin_menu():
    """Menú de navegación para administradores"""
    menu_options = {
        "📊 Dashboard": "app.py",
        "👥 Grupos": "pages/02_grupos.py",
        "👤 Miembros": "pages/03_miembros.py", 
        "📅 Reuniones": "pages/04_reuniones.py",
        "💰 Ahorros": "pages/05_ahorros.py",
        "🏦 Préstamos": "pages/06_prestamos.py",
        "💵 Caja": "pages/07_caja.py",
        "📈 Reportes": "pages/09_reportes.py",
        "⚙️ Administración": "pages/10_administracion.py"
    }
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_promotor_menu():
    """Menú de navegación para promotores"""
    menu_options = {
        "📊 Mi Dashboard": "app.py",
        "👥 Mis Grupos": "pages/02_grupos.py",
        "👤 Mis Miembros": "pages/03_miembros.py",
        "📅 Mis Reuniones": "pages/04_reuniones.py", 
        "💰 Ahorros": "pages/05_ahorros.py",
        "🏦 Préstamos": "pages/06_prestamos.py",
        "💵 Caja": "pages/07_caja.py",
        "📈 Reportes": "pages/09_reportes.py"
    }
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_group_menu(user):
    """Menú de navegación para directiva de grupo"""
    menu_options = {
        "📊 Dashboard": "app.py",
        "👤 Miembros": "pages/03_miembros.py",
        "📅 Reuniones": "pages/04_reuniones.py",
        "💰 Ahorros": "pages/05_ahorros.py", 
        "🏦 Préstamos": "pages/06_prestamos.py",
        "💵 Caja": "pages/07_caja.py"
    }
    
    # Agregar opciones adicionales según el rol específico
    if user['cargo_nombre'] in ['presidente', 'secretaria', 'tesorera']:
        menu_options["📋 Asistencias"] = "pages/04_reuniones.py"
        menu_options["📊 Reportes Grupo"] = "pages/09_reportes.py"
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_dashboard_content(user):
    """Contenido principal del dashboard según el rol"""
    st.title(f"🏠 Dashboard Principal - {user['cargo_nombre']}")
    st.markdown("---")
    
    # Mostrar métricas según el rol
    if user['cargo_nombre'] == 'administrador':
        show_admin_metrics()
    elif user['cargo_nombre'] == 'promotora':
        show_promotor_metrics()
    else:
        show_group_metrics(user)
    
    # Acciones rápidas
    st.markdown("### 🚀 Acciones Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Nueva Reunión", use_container_width=True):
            st.switch_page("pages/04_reuniones.py")
    
    with col2:
        if st.button("💰 Registrar Ahorro", use_container_width=True):
            st.switch_page("pages/05_ahorros.py")
    
    with col3:
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.switch_page("pages/09_reportes.py")

def show_admin_metrics():
    """Métricas para administrador"""
    from database.queries import get_grupos_por_distrito, get_prestamos_activos
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        grupos_df = get_grupos_por_distrito()
        st.metric("🏘️ Total Grupos", len(grupos_df))
    
    with col2:
        grupos_activos = len(grupos_df[grupos_df['ID_Estadio'] == 1])
        st.metric("✅ Grupos Activos", grupos_activos)
    
    with col3:
        st.metric("👥 Total Miembros", "350")  # Esto sería una consulta real
    
    with col4:
        prestamos_df = get_prestamos_activos()
        total_prestamos = prestamos_df['monto'].sum() if not prestamos_df.empty else 0
        st.metric("🏦 Préstamos Activos", f"Q {total_prestamos:,.2f}")
    
    # Gráficas rápidas
    st.markdown("### 📈 Vista Rápida")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**📊 Distribución por Distrito**")
        # Aquí iría una gráfica de distribución
    
    with col2:
        st.info("**📅 Actividad Reciente**")
        # Aquí iría una gráfica de actividad

def show_promotor_metrics():
    """Métricas para promotor"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Mis Grupos", "5")
    
    with col2:
        st.metric("✅ Miembros Activos", "85")
    
    with col3:
        st.metric("🏦 Cartera Vigente", "Q 45,000")
    
    st.info("💡 **Resumen de mis grupos** - Aquí iría un resumen específico del promotor")

def show_group_metrics(user):
    """Métricas para directiva de grupo"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Ahorro Total", "Q 25,000")
    
    with col2:
        st.metric("🏦 Préstamos Activos", "Q 18,500")
    
    with col3:
        st.metric("👥 Miembros", "25")
    
    st.success(f"🎯 Eres **{user['cargo_nombre']}** del grupo. Usa el menú lateral para gestionar las operaciones.")

if __name__ == "__main__":
    main()
