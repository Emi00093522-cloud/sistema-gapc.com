from app.database.connection import DatabaseConnection

class AhorroService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def registrar_ahorro(self, ahorro_data):
        query = """
        INSERT INTO Ahorro (ID_Miembro, ID_Reunion, fecha, monto_ahorro, monto_otros)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            ahorro_data['ID_Miembro'], ahorro_data['ID_Reunion'], ahorro_data['fecha'],
            ahorro_data['monto_ahorro'], ahorro_data['monto_otros']
        )
        return self.db.execute_query(query, params)
    
    def obtener_total_ahorros_grupo(self, id_grupo):
        query = """
        SELECT SUM(a.monto_ahorro) as total_ahorros, SUM(a.monto_otros) as total_otros
        FROM Ahorro a
        JOIN Miembro m ON a.ID_Miembro = m.ID_Miembro
        WHERE m.ID_Grupo = %s
        """
        return self.db.execute_query(query, (id_grupo,), fetch_one=True)
