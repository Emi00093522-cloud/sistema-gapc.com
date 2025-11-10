import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.database import get_connection
from utils.charts import create_savings_trend_chart, create_loan_status_chart

def main():
    st.title("📈 Reportes y Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard General", "💰 Reporte de Caja", "👥 Reporte por Grupo"])
    
    with tab1:
        show_general_dashboard()
    
    with tab2:
        show_cash_report()
    
    with tab3:
        show_group_report()

def show_general_dashboard():
    st.subheader("Dashboard General del Sistema")
    
    conn = get_connection()
    if conn is None:
        st.error("No hay conexión a la base de datos")
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_grupos = pd.read_sql("SELECT COUNT(*) as total FROM Grupo", conn).iloc[0]['total']
        st.metric("Total Grupos", total_grupos)
    
    with col2:
        total_miembros = pd.read_sql("SELECT COUNT(*) as total FROM Miembro", conn).iloc[0]['total']
        st.metric("Total Miembros", total_miembros)
    
    with col3:
        total_ahorros = pd.read_sql("SELECT COALESCE(SUM(monto_ahorro), 0) as total FROM Ahorro", conn).iloc[0]['total']
        st.metric("Total Ahorros", f"${total_ahorros:,.2f}")
    
    with col4:
        total_prestamos = pd.read_sql("SELECT COALESCE(SUM(monto), 0) as total FROM Prestamo", conn).iloc[0]['total']
        st.metric("Total Préstamos", f"${total_prestamos:,.2f}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de grupos por distrito
        distritos_data = pd.read_sql("""
        SELECT d.nombre_distrito, COUNT(g.ID_Grupo) as cantidad_grupos
        FROM Distrito d
        LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito
        GROUP BY d.nombre_distrito
        """, conn)
        
        if not distritos_data.empty:
            fig = px.bar(distritos_data, x='nombre_distrito', y='cantidad_grupos',
                        title="📍 Grupos por Distrito",
                        color='nombre_distrito')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Estado de préstamos global
        prestamos_data = pd.read_sql("""
        SELECT ep.estado_prestamo, COUNT(*) as cantidad, SUM(p.monto) as monto_total
        FROM Prestamo p
        JOIN Estado_prestamo ep ON p.ID_Estado_prestamo = ep.ID_Estado_prestamo
        GROUP BY ep.estado_prestamo
        """, conn)
        
        if not prestamos_data.empty:
            fig = px.pie(prestamos_data, values='cantidad', names='estado_prestamo',
                        title="📊 Estado de Préstamos Global")
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla resumen por distrito
    st.write("### Resumen Consolidado por Distrito")
    show_resumen_distritos(conn)
    
    conn.close()

def show_resumen_distritos(conn):
    query = """
    SELECT d.nombre_distrito,
           COUNT(DISTINCT g.ID_Grupo) as grupos,
           COUNT(DISTINCT m.ID_Miembro) as miembros,
           COALESCE(SUM(a.monto_ahorro), 0) as total_ahorros,
           COALESCE(SUM(p.monto), 0) as total_prestamos,
           COUNT(DISTINCT r.ID_Reunion) as reuniones
    FROM Distrito d
    LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito
    LEFT JOIN Miembro m ON g.ID_Grupo = m.ID_Grupo
    LEFT JOIN Ahorro a ON m.ID_Miembro = a.ID_Miembro
    LEFT JOIN Prestamo p ON m.ID_Miembro = p.ID_Miembro
    LEFT JOIN Reunion r ON g.ID_Grupo = r.ID_Grupo
    GROUP BY d.nombre_distrito
    """
    
    data = pd.read_sql(query, conn)
    st.dataframe(data, use_container_width=True)

def show_cash_report():
    st.subheader("Reporte de Movimientos de Caja")
    
    conn = get_connection()
    if conn is None:
        st.error("No hay conexión a la base de datos")
        return
    
    # Selector de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio")
    with col2:
        fecha_fin = st.date_input("Fecha Fin")
    
    if fecha_inicio and fecha_fin:
        query = """
        SELECT tm.tipo_movimiento, mc.descripcion, mc.monto, mc.fecha_movimiento,
               g.nombre as grupo, r.fecha as fecha_reunion
        FROM Movimiento_caja mc
        JOIN Tipo_movimiento tm ON mc.ID_Tipo_movimiento = tm.ID_Tipo_movimiento
        JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
        JOIN Grupo g ON r.ID_Grupo = g.ID_Grupo
        WHERE mc.fecha_movimiento BETWEEN %s AND %s
        ORDER BY mc.fecha_movimiento DESC
        """
        
        movimientos = pd.read_sql(query, conn, params=(fecha_inicio, fecha_fin))
        
        if not movimientos.empty:
            # Resumen
            col1, col2, col3 = st.columns(3)
            with col1:
                ingresos = movimientos[movimientos['tipo_movimiento'] == 'ingreso']['monto'].sum()
                st.metric("Total Ingresos", f"${ingresos:,.2f}")
            with col2:
                egresos = movimientos[movimientos['tipo_movimiento'] == 'egreso']['monto'].sum()
                st.metric("Total Egresos", f"${egresos:,.2f}")
            with col3:
                saldo = ingresos - egresos
                st.metric("Saldo Neto", f"${saldo:,.2f}")
            
            # Gráfico de movimientos
            movimientos_agrupados = movimientos.groupby(['fecha_movimiento', 'tipo_movimiento'])['monto'].sum().reset_index()
            
            fig = px.bar(movimientos_agrupados, x='fecha_movimiento', y='monto', color='tipo_movimiento',
                        title="💰 Movimientos de Caja por Fecha", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada
            st.dataframe(movimientos, use_container_width=True)
        else:
            st.info("No hay movimientos en el período seleccionado")
    
    conn.close()

def show_group_report():
    st.subheader("Reporte Detallado por Grupo")
    
    conn = get_connection()
    if conn is None:
        st.error("No hay conexión a la base de datos")
        return
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist())
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        # Métricas del grupo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_miembros = pd.read_sql(
                "SELECT COUNT(*) as total FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Miembros Activos", total_miembros)
        
        with col2:
            total_ahorros = pd.read_sql(
                "SELECT COALESCE(SUM(a.monto_ahorro), 0) as total FROM Ahorro a JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro WHERE m.ID_Grupo = %s",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Total Ahorrado", f"${total_ahorros:,.2f}")
        
        with col3:
            total_prestamos = pd.read_sql(
                "SELECT COALESCE(SUM(p.monto), 0) as total FROM Prestamo p JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro WHERE m.ID_Grupo = %s",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Total Prestado", f"${total_prestamos:,.2f}")
        
        with col4:
            reuniones_count = pd.read_sql(
                "SELECT COUNT(*) as total FROM Reunion WHERE ID_Grupo = %s",
                conn, params=(group_id,)
            ).iloc[0]['total']
            st.metric("Reuniones", reuniones_count)
        
        # Gráficos del grupo
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_savings_trend_chart(group_id)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            chart = create_loan_status_chart(group_id)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        # Detalle de miembros
        st.write("### Detalle de Miembros")
        miembros_detalle = pd.read_sql("""
        SELECT m.nombre, m.DUI, m.telefono, r.nombre_rol, m.ausencias,
               (SELECT COALESCE(SUM(monto_ahorro), 0) FROM Ahorro WHERE ID_Miembro = m.ID_Miembro) as total_ahorrado,
               (SELECT COUNT(*) FROM Prestamo WHERE ID_Miembro = m.ID_Miembro AND ID_Estado_prestamo IN (1,2)) as prestamos_activos
        FROM Miembro m
        JOIN Rol r ON m.ID_Rol = r.ID_Rol
        WHERE m.ID_Grupo = %s AND m.ID_Estado = 1
        """, conn, params=(group_id,))
        
        st.dataframe(miembros_detalle, use_container_width=True)
    
    conn.close()

if __name__ == "__main__":
    main()
