import streamlit as st
import pandas as pd

def mostrar_metricas_grupo(estadisticas):
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

def form_crear_grupo():
    with st.form("crear_grupo"):
        st.subheader("📋 Crear Nuevo Grupo")
        
        nombre = st.text_input("Nombre del Grupo*")
        
        # Obtener distritos y promotores
        from app.services.grupo_service import GrupoService
        grupo_service = GrupoService()
        
        distritos = grupo_service.db.execute_query("SELECT * FROM Distrito", fetch=True) or []
        promotores = grupo_service.db.execute_query("SELECT * FROM Promotor", fetch=True) or []
        
        id_distrito = st.selectbox("Distrito*", distritos, format_func=lambda x: x['nombre_distrito']) if distritos else None
        fecha_inicio = st.date_input("Fecha de Inicio*")
        duracion_ciclo = st.selectbox("Duración del Ciclo*", [6, 12], format_func=lambda x: f"{x} meses")
        periodicidad = st.selectbox("Periodicidad de Reuniones*", ["Semanal", "Quincenal", "Mensual"])
        tasa_interes = st.number_input("Tasa de Interés (%)*", min_value=0.0, max_value=50.0, step=0.1)
        id_promotor = st.selectbox("Promotor Asignado", promotores, format_func=lambda x: x['nombre']) if promotores else None
        reglas = st.text_area("Reglas del Grupo")
        
        submitted = st.form_submit_button("✅ Crear Grupo")
        
        if submitted and nombre and id_distrito and tasa_interes is not None:
            return {
                'nombre': nombre,
                'ID_Distrito': id_distrito['ID_Distrito'],
                'fecha_inicio': fecha_inicio,
                'duracion_ciclo': duracion_ciclo,
                'periodicidad_reuniones': periodicidad,
                'tasa_interes': tasa_interes,
                'ID_Promotor': id_promotor['ID_Promotor'] if id_promotor else None,
                'reglas': reglas
            }
        elif submitted:
            st.error("Por favor complete todos los campos obligatorios (*)")
    
    return None
