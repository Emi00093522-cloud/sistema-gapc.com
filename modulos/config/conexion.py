import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='bzol0srlvapvtstpnaj3-mysql.services.clever-cloud.com',
            user='utdew8d69izw1c5a',
            password='Mu2XmtasRmG1lv4Z4HWFa',
            database='beu5uv04siiubuvtnhzp',
            port=3306
        )
        if conexion.is_connected():
            print("✅ Conexión establecida")
            return conexion
        else:
            print("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar: {e}")
        return None
