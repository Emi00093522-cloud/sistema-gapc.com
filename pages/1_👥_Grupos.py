import streamlit as st
import pandas as pd
from config.database import get_connection
from utils.database_ops import get_all_groups, create_group, get_members_by_group, create_member

def main():
    st.title("👥 Gestión de Grupos y Miembros")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Grupos", "➕ Crear Nuevo Grupo", "👤 Gestión de Miembros"])
    
    with tab1:
        show_groups_list()
    
    with tab2:
        show_create_group_form()
    
    with tab3:
        show_members_management()

def show_groups_list():
    st.subheader("Lista de Grupos Registrados")
    
    groups = get_all_groups()
    
    if not groups.empty:
        st.dataframe(groups, use_container_width=True)
        
        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Grupos", len(groups))
        with col2:
            active_groups = len(groups[groups['ID_Estado'] == 1])
            st.metric("Grupos Activos", active_groups)
        with col3:
            districts = groups['nombre_distrito'].nunique()
            st.metric("Distritos", districts)
    else:
        st.info("No hay grupos registrados aún")

def show_create_group_form():
    st.subheader("Crear Nuevo Grupo")
    
    conn = get_connection()
    
    # Obtener datos para los selectores
    distritos = pd.read_sql("SELECT * FROM Distrito", conn)
    promotores = pd.read_sql("SELECT * FROM Promotor", conn)
    
    with st.form("create_group_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Grupo*")
            id_distrito = st.selectbox("Distrito*", distritos['ID_Distrito'], 
                                      format_func=lambda x: distritos[distritos['ID_Distrito'] == x]['nombre_distrito'].iloc[0])
            fecha_inicio = st.date_input("Fecha de Inicio*")
            duracion_ciclo = st.selectbox("Duración del Ciclo (meses)*", [6, 12])
        
        with col2:
            periodicidad = st.selectbox("Periodicidad de Reuniones*", ["Semanal", "Quincenal", "Mensual"])
            tasa_interes = st.number_input("Tasa de Interés (%)*", min_value=0.0, max_value=100.0, step=0.1)
            id_promotor = st.selectbox("Promotor Asignado*", promotores['ID_Promotor'],
                                      format_func=lambda x: promotores[promotores['ID_Promotor'] == x]['nombre'].iloc[0])
            reglas = st.text_area("Reglas del Grupo")
        
        submitted = st.form_submit_button("Crear Grupo")
        
        if submitted:
            if nombre and id_distrito and fecha_inicio and tasa_interes:
                if create_group(nombre, id_distrito, fecha_inicio, duracion_ciclo, 
                              periodicidad, tasa_interes, id_promotor, reglas):
                    st.success("Grupo creado exitosamente!")
                    st.rerun()
                else:
                    st.error("Error al crear el grupo")
            else:
                st.warning("Por favor complete todos los campos obligatorios (*)")
    
    conn.close()

def show_members_management():
    st.subheader("Gestión de Miembros")
    
    conn = get_connection()
    
    # Seleccionar grupo primero
    groups = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    
    if not groups.empty:
        selected_group = st.selectbox("Seleccionar Grupo", groups['nombre'].tolist())
        group_id = groups[groups['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            show_members_list(group_id)
        
        with col2:
            show_add_member_form(group_id)
    else:
        st.info("Primero debe crear un grupo para agregar miembros")
    
    conn.close()

def show_members_list(group_id):
    st.write("### Miembros del Grupo")
    
    members = get_members_by_group(group_id)
    
    if not members.empty:
        # Mostrar datos básicos
        display_columns = ['nombre', 'DUI', 'email', 'telefono', 'nombre_rol', 'ausencias']
        st.dataframe(members[display_columns], use_container_width=True)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Miembros", len(members))
        with col2:
            presidentes = len(members[members['nombre_rol'] == 'Presidente'])
            st.metric("Directiva", presidentes)
        with col3:
            total_ausencias = members['ausencias'].sum()
            st.metric("Total Ausencias", total_ausencias)
    else:
        st.info("Este grupo no tiene miembros registrados")

def show_add_member_form(group_id):
    st.write("### Agregar Nuevo Miembro")
    
    conn = get_connection()
    roles = pd.read_sql("SELECT * FROM Rol", conn)
    
    with st.form("add_member_form"):
        nombre = st.text_input("Nombre Completo*")
        dui = st.text_input("DUI")
        direccion = st.text_area("Dirección")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono")
        id_rol = st.selectbox("Rol*", roles['ID_Rol'],
                             format_func=lambda x: roles[roles['ID_Rol'] == x]['nombre_rol'].iloc[0])
        
        submitted = st.form_submit_button("Agregar Miembro")
        
        if submitted:
            if nombre and id_rol:
                from utils.database_ops import create_member
                if create_member(dui, group_id, nombre, direccion, email, telefono, id_rol):
                    st.success("Miembro agregado exitosamente!")
                    st.rerun()
                else:
                    st.error("Error al agregar el miembro")
            else:
                st.warning("Por favor complete los campos obligatorios (*)")
    
    conn.close()

if __name__ == "__main__":
    main()
