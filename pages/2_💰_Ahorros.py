import streamlit as st
import pandas as pd
from config.database import get_connection
from utils.database_ops import get_savings_by_member, register_saving
from utils.charts import create_savings_trend_chart

def main():
    st.title("💰 Gestión de Ahorros")
    
    tab1, tab2, tab3 = st.tabs(["📊 Registro de Ahorros", "📈 Estadísticas", "👤 Ahorros por Miembro"])
    
    with tab1:
        show_savings_registration()
    
    with tab2:
        show_savings_statistics()
    
    with tab3:
        show_member_savings()

def show_savings_registration():
    st.subheader("Registrar Aportes de Ahorro")
    
    conn = get_connection()
    
    # Obtener datos para los selectores
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    reuniones = pd.read_sql("SELECT ID_Reunion, fecha, ID_Grupo FROM Reunion ORDER BY fecha DESC", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist(), key="savings_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        # Filtrar reuniones del grupo seleccionado
        reuniones_grupo = reuniones[reuniones['ID_Grupo'] == group_id]
        
        if not reuniones_grupo.empty:
            selected_reunion = st.selectbox("Seleccionar Reunión", 
                                          reuniones_grupo['ID_Reunion'],
                                          format_func=lambda x: f"Reunión {x} - {reuniones_grupo[reuniones_grupo['ID_Reunion'] == x]['fecha'].iloc[0]}")
            
            # Obtener miembros del grupo
            miembros = pd.read_sql(
                "SELECT ID_Miembro, nombre FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1", 
                conn, params=(group_id,)
            )
            
            if not miembros.empty:
                st.write("### Registrar Aportes")
                
                for index, miembro in miembros.iterrows():
                    with st.expander(f"💰 {miembro['nombre']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            monto_ahorro = st.number_input(f"Ahorro Regular", 
                                                         min_value=0.0, 
                                                         key=f"ahorro_{miembro['ID_Miembro']}")
                        with col2:
                            monto_otros = st.number_input(f"Otros Aportes", 
                                                        min_value=0.0, 
                                                        key=f"otros_{miembro['ID_Miembro']}")
                        
                        if st.button("Guardar", key=f"btn_{miembro['ID_Miembro']}"):
                            if monto_ahorro > 0 or monto_otros > 0:
                                if register_saving(miembro['ID_Miembro'], selected_reunion, monto_ahorro, monto_otros):
                                    st.success(f"Aporte registrado para {miembro['nombre']}")
                                else:
                                    st.error(f"Error al registrar aporte para {miembro['nombre']}")
            else:
                st.info("Este grupo no tiene miembros activos")
        else:
            st.info("No hay reuniones registradas para este grupo")
    else:
        st.info("No hay grupos registrados")
    
    conn.close()

def show_savings_statistics():
    st.subheader("Estadísticas de Ahorros")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo para Estadísticas", 
                                    grupos['nombre'].tolist(), 
                                    key="stats_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        # Gráfico de tendencia de ahorros
        chart = create_savings_trend_chart(group_id)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos de ahorros para mostrar")
        
        # Estadísticas numéricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_ahorros = pd.read_sql(
                "SELECT COALESCE(SUM(a.monto_ahorro), 0) as total FROM Ahorro a JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro WHERE m.ID_Grupo = %s",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Total Ahorrado", f"${total_ahorros:,.2f}")
        
        with col2:
            total_miembros = pd.read_sql(
                "SELECT COUNT(*) as total FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Miembros Activos", total_miembros)
        
        with col3:
            ahorro_promedio = total_ahorros / total_miembros if total_miembros > 0 else 0
            st.metric("Ahorro Promedio", f"${ahorro_promedio:,.2f}")
        
        with col4:
            total_reuniones = pd.read_sql(
                "SELECT COUNT(*) as total FROM Reunion WHERE ID_Grupo = %s",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Reuniones", total_reuniones)
    
    conn.close()

def show_member_savings():
    st.subheader("Consulta de Ahorros por Miembro")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist(), key="member_savings_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        miembros = pd.read_sql(
            "SELECT ID_Miembro, nombre FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1", 
            conn, params=(group_id,)
        )
        
        if not miembros.empty:
            selected_member = st.selectbox("Seleccionar Miembro", miembros['nombre'].tolist())
            member_id = miembros[miembros['nombre'] == selected_member]['ID_Miembro'].iloc[0]
            
            # Mostrar historial de ahorros
            savings = get_savings_by_member(member_id)
            
            if not savings.empty:
                st.write(f"### Historial de Ahorros - {selected_member}")
                
                # Resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_ahorro = savings['monto_ahorro'].sum()
                    st.metric("Total Ahorrado", f"${total_ahorro:,.2f}")
                with col2:
                    total_otros = savings['monto_otros'].sum()
                    st.metric("Otros Aportes", f"${total_otros:,.2f}")
                with col3:
                    total_general = total_ahorro + total_otros
                    st.metric("Total General", f"${total_general:,.2f}")
                
                # Tabla detallada
                st.dataframe(savings[['fecha_reunion', 'monto_ahorro', 'monto_otros']], 
                           use_container_width=True)
            else:
                st.info("Este miembro no tiene registros de ahorro")
        else:
            st.info("Este grupo no tiene miembros activos")
    
    conn.close()

if __name__ == "__main__":
    main()
