import streamlit as st
import pandas as pd
from config.database import get_connection
from datetime import datetime

def main():
    st.title("📅 Gestión de Reuniones")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Reuniones", "➕ Nueva Reunión", "✅ Control de Asistencia"])
    
    with tab1:
        show_meetings_list()
    
    with tab2:
        show_new_meeting_form()
    
    with tab3:
        show_attendance_control()

def show_meetings_list():
    st.subheader("Historial de Reuniones")
    
    conn = get_connection()
    
    query = """
    SELECT r.ID_Reunion, g.nombre as grupo, r.fecha, er.estado_reunion,
           COUNT(DISTINCT a.ID_Miembro) as miembros_asistieron,
           (SELECT COUNT(*) FROM Miembro m WHERE m.ID_Grupo = g.ID_Grupo AND m.ID_Estado = 1) as total_miembros
    FROM Reunion r
    JOIN Grupo g ON r.ID_Grupo = g.ID_Grupo
    JOIN Estado_reunion er ON r.ID_Estado_reunion = er.ID_Estado_reunion
    LEFT JOIN Ahorro a ON r.ID_Reunion = a.ID_Reunion
    GROUP BY r.ID_Reunion, g.nombre, r.fecha, er.estado_reunion
    ORDER BY r.fecha DESC
    """
    
    meetings = pd.read_sql(query, conn)
    
    if not meetings.empty:
        st.dataframe(meetings, use_container_width=True)
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            total_reuniones = len(meetings)
            st.metric("Total Reuniones", total_reuniones)
        with col2:
            reuniones_realizadas = len(meetings[meetings['estado_reunion'] == 'Realizada'])
            st.metric("Realizadas", reuniones_realizadas)
        with col3:
            porcentaje_asistencia = (meetings['miembros_asistieron'].sum() / meetings['total_miembros'].sum()) * 100 if meetings['total_miembros'].sum() > 0 else 0
            st.metric("Asistencia Promedio", f"{porcentaje_asistencia:.1f}%")
    else:
        st.info("No hay reuniones registradas")
    
    conn.close()

def show_new_meeting_form():
    st.subheader("Programar Nueva Reunión")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo WHERE ID_Estado = 1", conn)
    estados_reunion = pd.read_sql("SELECT * FROM Estado_reunion", conn)
    
    if not grupos.empty:
        with st.form("new_meeting_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                id_grupo = st.selectbox("Grupo*", grupos['ID_Grupo'],
                                       format_func=lambda x: grupos[grupos['ID_Grupo'] == x]['nombre'].iloc[0])
                fecha = st.date_input("Fecha de Reunión*", datetime.now())
            
            with col2:
                id_estado = st.selectbox("Estado*", estados_reunion['ID_Estado_reunion'],
                                        format_func=lambda x: estados_reunion[estados_reunion['ID_Estado_reunion'] == x]['estado_reunion'].iloc[0])
                notas = st.text_area("Notas u Observaciones")
            
            submitted = st.form_submit_button("Programar Reunión")
            
            if submitted:
                if id_grupo and fecha:
                    cursor = conn.cursor()
                    try:
                        query = """
                        INSERT INTO Reunion (ID_Grupo, fecha, ID_Estado_reunion)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(query, (id_grupo, fecha, id_estado))
                        conn.commit()
                        st.success("Reunión programada exitosamente!")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error al programar la reunión: {e}")
                    finally:
                        cursor.close()
                else:
                    st.warning("Por favor complete todos los campos obligatorios (*)")
    else:
        st.info("No hay grupos activos registrados")
    
    conn.close()

def show_attendance_control():
    st.subheader("Control de Asistencia y Aportes")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo WHERE ID_Estado = 1", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist(), key="attendance_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        # Obtener reuniones del grupo
        reuniones = pd.read_sql(
            "SELECT ID_Reunion, fecha FROM Reunion WHERE ID_Grupo = %s ORDER BY fecha DESC", 
            conn, params=(group_id,)
        )
        
        if not reuniones.empty:
            selected_reunion = st.selectbox("Seleccionar Reunión", 
                                          reuniones['ID_Reunion'],
                                          format_func=lambda x: f"Reunión - {reuniones[reuniones['ID_Reunion'] == x]['fecha'].iloc[0]}")
            
            # Obtener miembros del grupo
            miembros = pd.read_sql(
                "SELECT ID_Miembro, nombre, ausencias FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1", 
                conn, params=(group_id,)
            )
            
            if not miembros.empty:
                st.write("### Registro de Asistencia y Aportes")
                
                for index, miembro in miembros.iterrows():
                    with st.expander(f"👤 {miembro['nombre']} (Ausencias: {miembro['ausencias']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            asistio = st.checkbox("Asistió", key=f"asistio_{miembro['ID_Miembro']}")
                        
                        with col2:
                            monto_ahorro = st.number_input("Ahorro", min_value=0.0, 
                                                         key=f"ahorro_att_{miembro['ID_Miembro']}")
                        
                        with col3:
                            if st.button("Registrar", key=f"registrar_{miembro['ID_Miembro']}"):
                                # Registrar asistencia y ahorro
                                if asistio and monto_ahorro > 0:
                                    cursor = conn.cursor()
                                    try:
                                        # Registrar ahorro
                                        query_ahorro = """
                                        INSERT INTO Ahorro (ID_Miembro, ID_Reunion, fecha, monto_ahorro)
                                        VALUES (%s, %s, CURDATE(), %s)
                                        """
                                        cursor.execute(query_ahorro, (miembro['ID_Miembro'], selected_reunion, monto_ahorro))
                                        
                                        # Actualizar ausencias si no asistió
                                        if not asistio:
                                            query_ausencia = """
                                            UPDATE Miembro SET ausencias = ausencias + 1 WHERE ID_Miembro = %s
                                            """
                                            cursor.execute(query_ausencia, (miembro['ID_Miembro'],))
                                        
                                        conn.commit()
                                        st.success(f"Datos registrados para {miembro['nombre']}")
                                    except Exception as e:
                                        conn.rollback()
                                        st.error(f"Error al registrar datos: {e}")
                                    finally:
                                        cursor.close()
            else:
                st.info("Este grupo no tiene miembros activos")
        else:
            st.info("Este grupo no tiene reuniones programadas")
    else:
        st.info("No hay grupos activos")
    
    conn.close()

if __name__ == "__main__":
    main()
