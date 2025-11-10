import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.database.connection import DatabaseConnection

class ReporteService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_consolidado_distritos(self):
        query = """
        SELECT 
            d.nombre_distrito,
            COUNT(DISTINCT g.ID_Grupo) as total_grupos,
            COUNT(DISTINCT m.ID_Miembro) as total_miembros,
            COALESCE(SUM(a.monto_ahorro), 0) as total_ahorros,
            COALESCE(SUM(p.monto), 0) as total_prestamos_activos
        FROM Distrito d
        LEFT JOIN Grupo g ON d.ID_Distrito = g.ID_Distrito AND g.ID_Estado = 1
        LEFT JOIN Miembro m ON g.ID_Grupo = m.ID_Grupo AND m.ID_Estado = 1
        LEFT JOIN Ahorro a ON m.ID_Miembro = a.ID_Miembro
        LEFT JOIN Prestamo p ON m.ID_Miembro = p.ID_Miembro AND p.ID_Estado_Prestamo IN (2,3,4)
        GROUP BY d.ID_Distrito, d.nombre_distrito
        """
        return self.db.execute_query(query, fetch=True)
    
    def obtener_estadisticas_grupo(self, id_grupo):
        query = """
        SELECT 
            g.nombre as grupo_nombre,
            COUNT(DISTINCT m.ID_Miembro) as total_miembros,
            COALESCE(SUM(a.monto_ahorro), 0) as total_ahorros,
            COUNT(DISTINCT p.ID_Prestamo) as total_prestamos,
            COALESCE(SUM(p.monto), 0) as monto_prestamos_activos
        FROM Grupo g
        LEFT JOIN Miembro m ON g.ID_Grupo = m.ID_Grupo AND m.ID_Estado = 1
        LEFT JOIN Ahorro a ON m.ID_Miembro = a.ID_Miembro
        LEFT JOIN Prestamo p ON m.ID_Miembro = p.ID_Miembro AND p.ID_Estado_Prestamo IN (2,3,4)
        WHERE g.ID_Grupo = %s
        GROUP BY g.ID_Grupo, g.nombre
        """
        return self.db.execute_query(query, (id_grupo,), fetch_one=True)
    
    def generar_grafica_ingresos_egresos(self, id_grupo):
        query_ingresos = """
        SELECT 'Ahorros' as categoria, COALESCE(SUM(monto_ahorro), 0) as monto
        FROM Ahorro a
        JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro
        WHERE m.ID_Grupo = %s
        UNION ALL
        SELECT 'Pagos Préstamos' as categoria, COALESCE(SUM(total_cancelado), 0) as monto
        FROM Pago_Prestamo pp
        JOIN Prestamo p ON pp.ID_Prestamo = p.ID_Prestamo
        JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
        WHERE m.ID_Grupo = %s
        """
        
        query_egresos = """
        SELECT 'Desembolsos Préstamos' as categoria, COALESCE(SUM(monto), 0) as monto
        FROM Prestamo p
        JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
        WHERE m.ID_Grupo = %s AND p.ID_Estado_Prestamo IN (2,3)
        """
        
        ingresos = self.db.execute_query(query_ingresos, (id_grupo, id_grupo), fetch=True)
        egresos = self.db.execute_query(query_egresos, (id_grupo,), fetch=True)
        
        fig = go.Figure()
        
        if ingresos:
            for ingreso in ingresos:
                if ingreso['monto'] and float(ingreso['monto']) > 0:
                    fig.add_trace(go.Bar(
                        name=f"💰 {ingreso['categoria']}",
                        x=[ingreso['categoria']],
                        y=[float(ingreso['monto'])],
                        marker_color='#2E8B57'
                    ))
        
        if egresos:
            for egreso in egresos:
                if egreso['monto'] and float(egreso['monto']) > 0:
                    fig.add_trace(go.Bar(
                        name=f"💸 {egreso['categoria']}",
                        x=[egreso['categoria']],
                        y=[float(egreso['monto'])],
                        marker_color='#DC143C'
                    ))
        
        fig.update_layout(
            title="📊 Flujo de Caja - Ingresos vs Egresos",
            xaxis_title="Categorías",
            yaxis_title="Monto ($)",
            barmode='group'
        )
        
        return fig
