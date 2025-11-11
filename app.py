import streamlit as st
import sys
import os

# Agregar directorios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'auth'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from auth.authentication import check_authentication, session_manager
from config import config

def main():
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Verificar autenticación
    check_authentication()
    
    # Obtener usuario actual
    user = session_manager.get_user()
    
    # Sidebar con navegación
    with st.sidebar:
        st.title(f"💰 {config.APP_TITLE}")
        st.markdown("---")
        st.success(f"👤 **{user['nombre']}**")
        st.info(f"🏷️ {user['cargo_nombre']}")
        st.markdown("---")
        
        # Menú según rol
        if user['cargo_nombre'] == 'administrador':
            show_admin_menu()
        elif user['cargo_nombre'] == 'promotora':
            show_promotor_menu()
        else:
            show_group_menu(user)
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            session_manager.logout()
            st.rerun()
    
    # Contenido principal
    show_dashboard_content(user)

def show_admin_menu():
    menu_options = {
        "📊 Dashboard": "pages/01_🏠_Dashboard.py",
        "👥 Grupos": "pages/02_👥_Grupos.py",
        "👤 Miembros": "pages/03_👤_Miembros.py",
        "📅 Reuniones": "pages/04_📅_Reuniones.py",
        "💰 Ahorros": "pages/05_💰_Ahorros.py",
        "🏦 Préstamos": "pages/06_🏦_Prestamos.py",
        "💵 Caja": "pages/07_💵_Caja.py",
        "📊 Reportes": "pages/08_📊_Reportes.py",
        "⚙️ Admin": "pages/09_⚙️_Admin.py"
    }
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_promotor_menu():
    menu_options = {
        "📊 Mi Dashboard": "pages/01_🏠_Dashboard.py",
        "👥 Mis Grupos": "pages/02_👥_Grupos.py",
        "👤 Mis Miembros": "pages/03_👤_Miembros.py",
        "📅 Mis Reuniones": "pages/04_📅_Reuniones.py",
        "💰 Ahorros": "pages/05_💰_Ahorros.py",
        "🏦 Préstamos": "pages/06_🏦_Prestamos.py",
        "📊 Reportes": "pages/08_📊_Reportes.py"
    }
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_group_menu(user):
    menu_options = {
        "📊 Dashboard": "pages/01_🏠_Dashboard.py",
        "👤 Miembros": "pages/03_👤_Miembros.py",
        "📅 Reuniones": "pages/04_📅_Reuniones.py",
        "💰 Ahorros": "pages/05_💰_Ahorros.py",
        "🏦 Préstamos": "pages/06_🏦_Prestamos.py"
    }
    
    for option, page in menu_options.items():
        if st.sidebar.button(option, use_container_width=True):
            st.switch_page(page)

def show_dashboard_content(user):
    st.title(f"🏠 Dashboard - {user['cargo_nombre']}")
    st.markdown("---")
    
    # Mostrar contenido según rol
    if user['cargo_nombre'] == 'administrador':
        from services.reporte_service import ReporteService
        ReporteService.show_admin_dashboard()
    elif user['cargo_nombre'] == 'promotora':
        from services.reporte_service import ReporteService
        ReporteService.show_promotor_dashboard(user)
    else:
        st.info(f"🎯 Bienvenido/a {user['nombre']} - Panel de grupo")

if __name__ == "__main__":
    main()
