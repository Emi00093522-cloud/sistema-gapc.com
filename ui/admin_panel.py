import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.grupo_service import GrupoService
from app.services.reporte_service import ReporteService
from app.services.miembro_service import MiembroService
from app.ui.components import mostrar_metricas_grupo, form_crear_grupo

def show_admin_panel():
    st.title("👨‍💼 Panel de Administración")
    
    grupo_service = GrupoService()
    reporte_service = ReporteService()
    miembro_service = MiembroService()
    
    grupos = grupo_service.obtener_todos_grupos()
    consolidado = reporte_service.obtener_consolidado_distritos()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏢 Grupos", "👥 Miembros", "📈 Reportes"])
    
    with tab1:
        st.header("Dashboard Consolidado")
        
        if consolidado:
            df = pd.DataFrame(consolidado)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏛️ Distritos", len(df))
            with col2:
                st.metric("🏢 Grupos", df['total_grupos'].sum())
            with col3:
                st.metric("👥 Miembros", df['total_miembros'].sum())
            with col4:
                st.metric("💰 Ahorros", f"${df['total_ahorros'].sum():,.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                if not df.empty:
                    fig = px.bar(df, x='nombre_distrito', y='total_ahorros', title="Ahorros por Distrito")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if not df.empty:
                    fig = px.pie(df, values='total_grupos', names='nombre_distrito', title="Grupos por Distrito")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de consolidado disponibles")
    
    with tab2:
        st.header("Gestión de Grupos")
        
        if st.button("➕ Nuevo Grupo", type="primary"):
            st.session_state.crear_grupo = True
        
        if st.session_state.get('crear_grupo', False):
            nuevo_grupo = form_crear_grupo()
            if nuevo_grupo:
                resultado = grupo_service.crear_grupo(nuevo_grupo)
                if resultado:
                    st.success("✅ Grupo creado exitosamente!")
                    st.session_state.crear_grupo = False
                    st.rerun()
        
        if grupos:
            st.subheader("Lista de Grupos")
            df_grupos = pd.DataFrame(grupos)
            st.dataframe(df_grupos, use_container_width=True)
        else:
            st.info("No hay grupos registrados")
    
    with tab3:
        st.header("Gestión de Miembros")
        
        if grupos:
            grupo_seleccionado = st.selectbox(
                "Seleccionar Grupo:",
                grupos,
                format_func=lambda x: f"{x['nombre']} - {x['nombre_distrito']}",
                key="miembros_grupo"
            )
            
            if grupo_seleccionado:
                miembros = miembro_service.obtener_miembros_por_grupo(grupo_seleccionado['ID_Grupo'])
                
                if miembros:
                    st.subheader(f"Miembros del Grupo: {grupo_seleccionado['nombre']}")
                    df_miembros = pd.DataFrame(miembros)
                    st.dataframe(df_miembros[['nombre', 'email', 'telefono', 'nombre_rol']], use_container_width=True)
                else:
                    st.info("No hay miembros en este grupo")
        else:
            st.info("Primero debe crear grupos para gestionar miembros")
    
    with tab4:
        st.header("Reportes por Grupo")
        
        if grupos:
            grupo_seleccionado = st.selectbox(
                "Seleccionar Grupo:",
                grupos,
                format_func=lambda x: f"{x['nombre']} - {x['nombre_distrito']}",
                key="reporte_grupo"
            )
            
            if grupo_seleccionado:
                estadisticas = reporte_service.obtener_estadisticas_grupo(grupo_seleccionado['ID_Grupo'])
                if estadisticas:
                    mostrar_metricas_grupo(estadisticas)
                    
                    st.subheader("📊 Flujo de Caja")
                    fig = reporte_service.generar_grafica_ingresos_egresos(grupo_seleccionado['ID_Grupo'])
                    st.plotly_chart(fig, use_container_width=True)
