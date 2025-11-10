from app.database.connection import DatabaseConnection

class ReunionService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_reuniones_por_grupo(self, id_grupo):
        query = """
        SELECT r.*, er.estado_reunion, g.nombre as grupo_nombre
        FROM Reunion r
        JOIN Estado_Reunion er ON r.ID_Estado_Reunion = er.ID_Estado_Reunion
        JOIN Grupo g ON r.ID_Grupo = g.ID_Grupo
        WHERE r.ID_Grupo = %s
        ORDER BY r.fecha DESC
        """
        return self.db.execute_query(query, (id_grupo,), fetch=True)
    
    def crear_reunion(self, reunion_data):
        query = """
        INSERT INTO Reunion (ID_Grupo, fecha, ID_Estado_Reunion)
        VALUES (%s, %s, %s)
        """
        params = (reunion_data['ID_Grupo'], reunion_data['fecha'], 1)
        return self.db.execute_query(query, params)
