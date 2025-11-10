import mysql.connector
import streamlit as st

@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=st.secrets["DB_PORT"]
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None
