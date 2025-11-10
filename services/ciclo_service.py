from app.database.connection import DatabaseConnection

class CicloService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def crear_ciclo(self, ciclo_data):
        query = """
        INSERT INTO Ciclo (ID_Grupo, fecha_inicio, fecha_cierre, ID_Estado_Ciclo)
        VALUES (%s, %s, %s, %s)
        """
        params = (ciclo_data['ID_Grupo'], ciclo_data['fecha_inicio'], ciclo_data['fecha_cierre'], 1)
        return self.db.execute_query(query, params)
