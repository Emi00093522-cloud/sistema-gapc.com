from app.database.connection import DatabaseConnection

class PrestamoService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_prestamos_por_grupo(self, id_grupo):
        query = """
        SELECT p.*, m.nombre as miembro_nombre, ep.estado_prestamo, g.nombre as grupo_nombre
        FROM Prestamo p
        JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
        JOIN Estado_Prestamo ep ON p.ID_Estado_Prestamo = ep.ID_Estado_Prestamo
        JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
        WHERE m.ID_Grupo = %s
        ORDER BY p.fecha_desembolso DESC
        """
        return self.db.execute_query(query, (id_grupo,), fetch=True)
    
    def crear_prestamo(self, prestamo_data):
        query = """
        INSERT INTO Prestamo (ID_Miembro, fecha_desembolso, monto, total_interes, ID_Estado_Prestamo, plazo, proposito)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            prestamo_data['ID_Miembro'], prestamo_data['fecha_desembolso'],
            prestamo_data['monto'], prestamo_data['total_interes'],
            2, prestamo_data['plazo'], prestamo_data['proposito']
        )
        return self.db.execute_query(query, params)
