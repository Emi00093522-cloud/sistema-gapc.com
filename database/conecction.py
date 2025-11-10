import mysql.connector
from mysql.connector import Error
import streamlit as st
from config.settings import Config

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'port': Config.DB_PORT,
            'charset': 'utf8mb4'
        }
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            st.error(f"❌ Error conectando a MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        connection = self.get_connection()
        if connection is None:
            return None
            
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            elif fetch_one:
                result = cursor.fetchone()
            else:
                connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            connection.close()
            return result
            
        except Error as e:
            st.error(f"❌ Error ejecutando query: {e}")
            connection.rollback()
            return None
    
    def test_connection(self):
        try:
            conn = self.get_connection()
            if conn and conn.is_connected():
                conn.close()
                return True
            return False
        except Error:
            return False
