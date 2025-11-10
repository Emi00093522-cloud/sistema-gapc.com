from config.database import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = get_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor()
    
    try:
        # En producción usar hashed_password
        query = "SELECT ID_Usuario, nombre_usuario, email, ID_Cargo FROM Usuario WHERE nombre_usuario = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        return user
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_role(user_id):
    conn = get_connection()
    if conn is None:
        return "Usuario"
        
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT c.nombre_cargo 
        FROM Usuario u 
        JOIN Cargo c ON u.ID_Cargo = c.ID_Cargo 
        WHERE u.ID_Usuario = %s
        """
        cursor.execute(query, (user_id,))
        role = cursor.fetchone()
        
        return role[0] if role else "Usuario"
    except:
        return "Usuario"
    finally:
        cursor.close()
        conn.close()
