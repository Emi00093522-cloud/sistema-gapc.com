from app.database.connection import DatabaseConnection

class MultaService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_multas_por_miembro(self, id_miembro):
        query = """
        SELECT mm.*, m.fecha, r.nombre_regla, em.estado_multa
        FROM Miembro_Multa mm
        JOIN Multa m ON mm.ID_Multa = m.ID_Multa
        JOIN Reglamento r ON m.ID_Reglamento = r.ID_Reglamento
        JOIN Estado_Multa em ON m.ID_Estado_Multa = em.ID_Estado_Multa
        WHERE mm.ID_Miembro = %s
        ORDER BY m.fecha DESC
        """
        return self.db.execute_query(query, (id_miembro,), fetch=True)
