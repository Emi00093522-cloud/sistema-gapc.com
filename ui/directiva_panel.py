import streamlit as st
import pandas as pd
from app.services.grupo_service import GrupoService
from app.services.miembro_service import MiembroService
from app.services.reunion_service import ReunionService
from app.services.ahorro_service import AhorroService
from app.services.prestamo_service import PrestamoService
from app.ui.components import mostrar_metricas_grupo

def show_directiva_panel():
    st.title("👥 Panel de Directiva")
    
    grupo_service = GrupoService()
    miembro_service = MiembroService()
    reunion_service = ReunionService()
    ahorro_service = AhorroService()
    prestamo_service = PrestamoService()
    
    grupos = grupo_service.obtener_todos_grupos()
    
    if not grupos:
        st.info("No tiene grupos asignados")
        return
    
    grupo_seleccionado = st.selectbox(
        "Seleccionar Grupo:",
        grupos,
        format_func=lambda x: f"{x['nombre']}",
        key="directiva_grupo"
    )
    
    if not grupo_seleccionado:
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "👥 Miembros", "📅 Reuniones", "💰 Ahorros"])
    
    with tab1:
        st.header(f"Resumen: {grupo_seleccionado['nombre']}")
        
        miembros = miembro_service.obtener_miembros_por_grupo(grupo_seleccionado['ID_Grupo'])
        reuniones = reunion_service.obtener_reuniones_por_grupo(grupo_seleccionado['ID_Grupo'])
        prestamos = prestamo_service.obtener_prestamos_por_grupo(grupo_seleccionado['ID_Grupo'])
        total_ahorros = ahorro_service.obtener_total_ahorros_grupo(grupo_seleccionado['ID_Grupo'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Miembros", len(miembros) if miembros else 0)
        with col2:
            st.metric("📅 Reuniones", len(reuniones) if reuniones else 0)
        with col3:
            st.metric("🏦 Préstamos", len(prestamos) if prestamos else 0)
        with col4:
            ahorro_total = total_ahorros['total_ahorros'] if total_ahorros else 0
            st.metric("💰 Ahorros", f"${ahorro_total:,.2f}")
    
    with tab2:
        st.header("Gestión de Miembros")
        
        if st.button("➕ Agregar Miembro", type="primary"):
            st.session_state.agregar_miembro = True
        
        if st.session_state.get('agregar_miembro', False):
            with st.form("agregar_miembro"):
                st.subheader("Nuevo Miembro")
                
                nombre = st.text_input("Nombre Completo*")
                email = st.text_input("Email")
                telefono = st.text_input("Teléfono")
                
                roles = grupo_service.db.execute_query("SELECT * FROM Rol", fetch=True)
                id_rol = st.selectbox("Rol", roles, format_func=lambda x: x['nombre_rol']) if roles else None
                
                submitted = st.form_submit_button("✅ Agregar Miembro")
                if submitted and nombre and id_rol:
                    miembro_data = {
                        'DUI': '',
                        'ID_Grupo': grupo_seleccionado['ID_Grupo'],
                        'nombre': nombre,
                        'email': email,
                        'telefono': telefono,
                        'ID_Rol': id_rol['ID_Rol'],
                        'fecha_inscripcion': '2024-01-01'
                    }
                    resultado = miembro_service.crear_miembro(miembro_data)
                    if resultado:
                        st.success("✅ Miembro agregado exitosamente!")
                        st.session_state.agregar_miembro = False
                        st.rerun()
        
        if miembros:
            st.subheader("Lista de Miembros")
            df_miembros = pd.DataFrame(miembros)
            st.dataframe(df_miembros[['nombre', 'email', 'telefono', 'nombre_rol']], use_container_width=True)
        else:
            st.info("No hay miembros en este grupo")
    
    with tab3:
        st.header("Gestión de Reuniones")
        
        if st.button("➕ Nueva Reunión", type="primary"):
            st.session_state.nueva_reunion = True
        
        if st.session_state.get('nueva_reunion', False):
            with st.form("nueva_reunion"):
                fecha_reunion = st.date_input("Fecha de la Reunión*")
                
                submitted = st.form_submit_button("✅ Crear Reunión")
                if submitted:
                    reunion_data = {
                        'ID_Grupo': grupo_seleccionado['ID_Grupo'],
                        'fecha': fecha_reunion
                    }
                    resultado = reunion_service.crear_reunion(reunion_data)
                    if resultado:
                        st.success("✅ Reunión creada exitosamente!")
                        st.session_state.nueva_reunion = False
                        st.rerun()
        
        if reuniones:
            st.subheader("Reuniones del Grupo")
            df_reuniones = pd.DataFrame(reuniones)
            st.dataframe(df_reuniones[['fecha', 'estado_reunion']], use_container_width=True)
        else:
            st.info("No hay reuniones registradas")
    
    with tab4:
        st.header("Registro de Ahorros")
        
        if miembros and reuniones:
            with st.form("registrar_ahorro"):
                st.subheader("Nuevo Ahorro")
                
                miembro_seleccionado = st.selectbox(
                    "Miembro:",
                    miembros,
                    format_func=lambda x: f"{x['nombre']}"
                )
                
                reunion_seleccionada = st.selectbox(
                    "Reunión:",
                    reuniones,
                    format_func=lambda x: f"{x['fecha']}"
                )
                
                monto_ahorro = st.number_input("Monto de Ahorro ($)", min_value=0.0, step=0.01)
                
                submitted = st.form_submit_button("💰 Registrar Ahorro")
                if submitted and miembro_seleccionado and reunion_seleccionada:
                    ahorro_data = {
                        'ID_Miembro': miembro_seleccionado['ID_Miembro'],
                        'ID_Reunion': reunion_seleccionada['ID_Reunion'],
                        'fecha': reunion_seleccionada['fecha'],
                        'monto_ahorro': monto_ahorro,
                        'monto_otros': 0
                    }
                    resultado = ahorro_service.registrar_ahorro(ahorro_data)
                    if resultado:
                        st.success("✅ Ahorro registrado exitosamente!")
                        st.rerun()
