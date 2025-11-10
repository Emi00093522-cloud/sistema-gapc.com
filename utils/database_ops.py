import pandas as pd
from config.database import get_connection

# Operaciones para Grupos
def get_all_groups():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
        
    query = """
    SELECT g.*, d.nombre_distrito, p.nombre as promotor
    FROM Grupo g
    LEFT JOIN Distrito d ON g.ID_Distrito = d.ID_Distrito
    LEFT JOIN Promotor p ON g.ID_Promotor = p.ID_Promotor
    """
    data = pd.read_sql(query, conn)
    conn.close()
    return data

def create_group(nombre, distrito_id, fecha_inicio, duracion_ciclo, periodicidad, tasa_interes, promotor_id, reglas):
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO Grupo (nombre, ID_Distrito, fecha_inicio, duracion_ciclo, periodicidad_reuniones, 
                          tasa_interes, ID_Promotor, reglas, ID_Estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        cursor.execute(query, (nombre, distrito_id, fecha_inicio, duracion_ciclo, periodicidad, 
                             tasa_interes, promotor_id, reglas))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Operaciones para Miembros
def get_members_by_group(group_id):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
        
    query = """
    SELECT m.*, r.nombre_rol, g.nombre as grupo
    FROM Miembro m
    JOIN Rol r ON m.ID_Rol = r.ID_Rol
    JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
    WHERE m.ID_Grupo = %s
    """
    data = pd.read_sql(query, conn, params=(group_id,))
    conn.close()
    return data

def create_member(dui, grupo_id, nombre, direccion, email, telefono, rol_id):
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO Miembro (DUI, ID_Grupo, nombre, direccion, email, telefono, ID_Rol, ID_Estado, fecha_inscripcion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, CURDATE())
        """
        cursor.execute(query, (dui, grupo_id, nombre, direccion, email, telefono, rol_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Operaciones para Ahorros
def get_savings_by_member(member_id):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
        
    query = """
    SELECT a.*, r.fecha as fecha_reunion
    FROM Ahorro a
    JOIN Reunion r ON a.ID_Reunion = r.ID_Reunion
    WHERE a.ID_Miembro = %s
    ORDER BY r.fecha DESC
    """
    data = pd.read_sql(query, conn, params=(member_id,))
    conn.close()
    return data

def register_saving(member_id, reunion_id, monto_ahorro, monto_otros=0):
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO Ahorro (ID_Miembro, ID_Reunion, fecha, monto_ahorro, monto_otros)
        VALUES (%s, %s, CURDATE(), %s, %s)
        """
        cursor.execute(query, (member_id, reunion_id, monto_ahorro, monto_otros))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Operaciones para Multas
def get_fines_by_member(member_id):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
        
    query = """
    SELECT mxm.*, m.descripcion, em.estado_multa, mxm.monto_a_pagar, mxm.monto_pagado
    FROM Miembro_x_Multa mxm
    JOIN Multa m ON mxm.ID_Multa = m.ID_Multa
    JOIN Estado_multa em ON mxm.ID_Estado_multa = em.ID_Estado_multa
    WHERE mxm.ID_Miembro = %s
    """
    data = pd.read_sql(query, conn, params=(member_id,))
    conn.close()
    return data

def register_member_fine(member_id, multa_id, monto, descripcion=""):
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Primero crear la multa
        query_multa = """
        INSERT INTO Multa (ID_Reunion, descripcion, monto, ID_Estado)
        VALUES (NULL, %s, %s, 1)
        """
        cursor.execute(query_multa, (descripcion, monto))
        multa_id = cursor.lastrowid
        
        # Luego asignarla al miembro
        query_miembro_multa = """
        INSERT INTO Miembro_x_Multa (ID_Miembro, ID_Multa, monto_a_pagar, ID_Estado_multa)
        VALUES (%s, %s, %s, 1)
        """
        cursor.execute(query_miembro_multa, (member_id, multa_id, monto))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
