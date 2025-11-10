import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.database import get_connection

def create_savings_trend_chart(group_id):
    conn = get_connection()
    if conn is None:
        return None
        
    query = """
    SELECT r.fecha, SUM(a.monto_ahorro) as total_ahorro
    FROM Ahorro a
    JOIN Reunion r ON a.ID_Reunion = r.ID_Reunion
    JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro
    WHERE m.ID_Grupo = %s
    GROUP BY r.fecha
    ORDER BY r.fecha
    """
    
    data = pd.read_sql(query, conn, params=(group_id,))
    conn.close()
    
    if not data.empty:
        fig = px.line(data, x='fecha', y='total_ahorro', 
                     title="📈 Evolución de Ahorros del Grupo",
                     labels={'fecha': 'Fecha', 'total_ahorro': 'Total Ahorrado'})
        return fig
    return None

def create_loan_status_chart(group_id):
    conn = get_connection()
    if conn is None:
        return None
        
    query = """
    SELECT ep.estado_prestamo, COUNT(*) as cantidad,
           SUM(p.monto) as monto_total
    FROM Prestamo p
    JOIN Estado_prestamo ep ON p.ID_Estado_prestamo = ep.ID_Estado_prestamo
    JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
    WHERE m.ID_Grupo = %s
    GROUP BY ep.estado_prestamo
    """
    
    data = pd.read_sql(query, conn, params=(group_id,))
    conn.close()
    
    if not data.empty:
        fig = px.pie(data, values='cantidad', names='estado_prestamo',
                    title="📊 Distribución de Préstamos por Estado")
        return fig
    return None

def create_income_expense_chart(group_id):
    conn = get_connection()
    if conn is None:
        return None
        
    query = """
    SELECT tm.tipo_movimiento, SUM(mc.monto) as total
    FROM Movimiento_caja mc
    JOIN Tipo_movimiento tm ON mc.ID_Tipo_movimiento = tm.ID_Tipo_movimiento
    JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
    WHERE r.ID_Grupo = %s
    GROUP BY tm.tipo_movimiento
    """
    
    data = pd.read_sql(query, conn, params=(group_id,))
    conn.close()
    
    if not data.empty:
        fig = px.bar(data, x='tipo_movimiento', y='total', 
                     color='tipo_movimiento',
                     title="💰 Ingresos vs Egresos",
                     labels={'tipo_movimiento': 'Tipo', 'total': 'Monto'})
        return fig
    return None
