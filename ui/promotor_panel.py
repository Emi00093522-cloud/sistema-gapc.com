import streamlit as st
import pandas as pd
from app.services.grupo_service import GrupoService
from app.services.reporte_service import ReporteService
from app.services.miembro_service import MiembroService
from app.services.reunion_service import ReunionService
from app.ui.components import mostrar_metricas_grupo

def show_promotor_panel():
    st.title("👩‍💼 Panel de Promotor")
    
    grupo_service = GrupoService()
    reporte_service = ReporteService()
    miembro_service = MiembroService()
    reunion_service = ReunionService()
    
    grupos = grupo_service.obtener_todos_grupos()
    
    if not grupos:
        st.info("No tiene grupos asignados para supervisar")
        return
    
    tab1, tab2 = st.tabs(["📋 Grupos", "📊 Reportes"])
    
    with tab1:
        st.header("Grupos bajo Supervisión")
        
        for grupo in grupos:
            with st.expander(f"🏢 {grupo['nombre']} - {grupo['nombre_distrito']}", expanded=True):
                estadisticas = reporte_service.obtener_estadisticas_grupo(grupo['ID_Grupo'])
                
                if estadisticas:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("👥 Miembros", estadisticas['total_miembros'])
                    with col2:
                        st.metric("💰 Ahorros", f"${estadisticas['total_ahorros']:,.2f}")
                    with col3:
                        st.metric("🏦 Préstamos", estadisticas['total_prestamos'])
                    with col4:
                        st.metric("📊 Activos", f"${estadisticas['monto_prestamos_activos']:,.2f}")
    
    with tab2:
        st.header("Reportes por Grupo")
        
        grupo_seleccionado = st.selectbox(
            "Seleccionar Grupo:",
            grupos,
            format_func=lambda x: f"{x['nombre']} - {x['nombre_distrito']}",
            key="reporte_promotor"
        )
        
        if grupo_seleccionado:
            estadisticas = reporte_service.obtener_estadisticas_grupo(grupo_seleccionado['ID_Grupo'])
            
            if estadisticas:
                st.subheader(f"Reporte: {grupo_seleccionado['nombre']}")
                mostrar_metricas_grupo(estadisticas)
                
                st.subheader("📊 Flujo de Caja")
                fig = reporte_service.generar_grafica_ingresos_egresos(grupo_seleccionado['ID_Grupo'])
                st.plotly_chart(fig, use_container_width=True)
