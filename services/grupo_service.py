from app.database.connection import DatabaseConnection

class GrupoService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todos_grupos(self):
        query = """
        SELECT g.*, d.nombre_distrito, p.nombre as promotor_nombre, e.estado
        FROM Grupo g
        LEFT JOIN Distrito d ON g.ID_Distrito = d.ID_Distrito
        LEFT JOIN Promotor p ON g.ID_Promotor = p.ID_Promotor
        LEFT JOIN Estado e ON g.ID_Estado = e.ID_Estado
        ORDER BY g.nombre
        """
        return self.db.execute_query(query, fetch=True)
    
    def obtener_grupo_por_id(self, id_grupo):
        query = """
        SELECT g.*, d.nombre_distrito, p.nombre as promotor_nombre, e.estado
        FROM Grupo g
        LEFT JOIN Distrito d ON g.ID_Distrito = d.ID_Distrito
        LEFT JOIN Promotor p ON g.ID_Promotor = p.ID_Promotor
        LEFT JOIN Estado e ON g.ID_Estado = e.ID_Estado
        WHERE g.ID_Grupo = %s
        """
        return self.db.execute_query(query, (id_grupo,), fetch_one=True)
    
    def crear_grupo(self, grupo_data):
        query = """
        INSERT INTO Grupo (nombre, ID_Distrito, fecha_inicio, duracion_ciclo, 
                          periodicidad_reuniones, tasa_interes, ID_Promotor, reglas, ID_Estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            grupo_data['nombre'], grupo_data['ID_Distrito'], grupo_data['fecha_inicio'],
            grupo_data['duracion_ciclo'], grupo_data['periodicidad_reuniones'],
            grupo_data['tasa_interes'], grupo_data['ID_Promotor'], grupo_data['reglas'], 1
        )
        return self.db.execute_query(query, params)
