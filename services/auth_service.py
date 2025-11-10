from app.database.connection import DatabaseConnection
import streamlit as st

class AuthService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def login(self, usuario, password, tipo_usuario):
        tipo_map = {"Administrador": 1, "Promotor": 2, "Directiva": 3}
        
        query = """
        SELECT u.*, tu.tipo_usuario, c.nombre_cargo 
        FROM Usuario u
        JOIN Tipo_usuario tu ON u.ID_Tipo_usuario = tu.ID_Tipo_usuario
        JOIN Cargo c ON u.ID_Cargo = c.ID_Cargo
        WHERE u.nombre = %s AND u.ID_Tipo_usuario = %s
        """
        user = self.db.execute_query(query, (usuario, tipo_map.get(tipo_usuario)), fetch_one=True)
        
        if user:
            st.session_state['user'] = user
            st.session_state['logged_in'] = True
            st.session_state['tipo_usuario'] = tipo_usuario
            return True
        return False
