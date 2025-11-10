from app.database.connection import DatabaseConnection

class CajaService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_saldo_actual_grupo(self, id_grupo):
        query_ingresos = """
        SELECT COALESCE(SUM(mc.monto), 0) as total_ingresos
        FROM Movimiento_Caja mc
        JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
        WHERE r.ID_Grupo = %s AND mc.ID_Tipo_Movimiento = 1
        """
        
        query_egresos = """
        SELECT COALESCE(SUM(mc.monto), 0) as total_egresos
        FROM Movimiento_Caja mc
        JOIN Reunion r ON mc.ID_Reunion = r.ID_Reunion
        WHERE r.ID_Grupo = %s AND mc.ID_Tipo_Movimiento = 2
        """
        
        ingresos = self.db.execute_query(query_ingresos, (id_grupo,), fetch_one=True)
        egresos = self.db.execute_query(query_egresos, (id_grupo,), fetch_one=True)
        
        total_ingresos = ingresos['total_ingresos'] if ingresos else 0
        total_egresos = egresos['total_egresos'] if egresos else 0
        
        return total_ingresos - total_egresos
