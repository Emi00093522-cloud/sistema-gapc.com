from app.database.connection import DatabaseConnection

class MiembroService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_miembros_por_grupo(self, id_grupo):
        query = """
        SELECT m.*, r.nombre_rol, e.estado, g.nombre as grupo_nombre
        FROM Miembro m
        JOIN Rol r ON m.ID_Rol = r.ID_Rol
        JOIN Estado e ON m.ID_Estado = e.ID_Estado
        JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
        WHERE m.ID_Grupo = %s
        ORDER BY m.nombre
        """
        return self.db.execute_query(query, (id_grupo,), fetch=True)
    
    def crear_miembro(self, miembro_data):
        query = """
        INSERT INTO Miembro (DUI, ID_Grupo, nombre, email, telefono, ID_Rol, ID_Estado, fecha_inscripcion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            miembro_data['DUI'], miembro_data['ID_Grupo'], miembro_data['nombre'],
            miembro_data['email'], miembro_data['telefono'], miembro_data['ID_Rol'],
            1, miembro_data['fecha_inscripcion']
        )
        return self.db.execute_query(query, params)
