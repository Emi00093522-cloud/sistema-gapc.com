from config.database import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = get_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor()
    
    # En una aplicación real, deberías usar hash para las contraseñas
    hashed_password = hash_password(password)
    
    query = "SELECT * FROM Usuario WHERE nombre_usuario = %s AND password = %s"
    cursor.execute(query, (username, password))  # En producción usar hashed_password
    
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user

def get_user_role(user_id):
    conn = get_connection()
    if conn is None:
        return "Usuario"
        
    cursor = conn.cursor()
    
    query = """
    SELECT c.nombre_cargo 
    FROM Usuario u 
    JOIN Cargo c ON u.ID_Cargo = c.ID_Cargo 
    WHERE u.ID_Usuario = %s
    """
    cursor.execute(query, (user_id,))
    role = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return role[0] if role else "Usuario"

def create_user(username, password, email, cargo_id, tipo_usuario_id):
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        query = """
        INSERT INTO Usuario (nombre_usuario, password, email, ID_Cargo, ID_Tipo_usuario)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, password, email, cargo_id, tipo_usuario_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
