import streamlit as st
from modulos.config.conexion import obtener_conexion

def verificar_usuario(usuario, contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠ No se pudo conectar a la base de datos.")
        print("❌ Error: no se pudo obtener conexión en verificar_usuario()")
        return None
    else:
        st.session_state["conexion_exitosa"] = True
        print("✅ Conexión establecida correctamente en verificar_usuario()")

    try:
        cursor = con.cursor()
        query = "SELECT Usuario, Contra, Tipo FROM Empleados WHERE Usuario = %s AND Contra = %s"
        cursor.execute(query, (usuario, contra))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Usuario encontrado: {result[0]}, tipo: {result[2]}")
            return result[2]
        else:
            print("⚠ Usuario o contraseña incorrectos.")
            return None
    except Exception as e:
        print(f"❌ Error al verificar usuario: {e}")
        st.error(f"Error al verificar usuario: {e}")
        return None
    finally:
        con.close()
        print("🔒 Conexión cerrada en verificar_usuario()")

def inicializar_usuarios():
    """Función para inicializar los usuarios en la base de datos"""
    print("🟡 Inicializando usuarios...")  
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo obtener conexión")  
        return False
        
    try:
        cursor = con.cursor()
        print("✅ Conexión abierta, creando tabla...") 
        
        # Crear tabla de empleados si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Empleados (
                ID_Empleado INT AUTO_INCREMENT PRIMARY KEY,
                Usuario VARCHAR(50) UNIQUE NOT NULL,
                Contra VARCHAR(100) NOT NULL,
                Tipo ENUM('secretaria', 'presidente', 'lector') NOT NULL,
                Nombre VARCHAR(100) NOT NULL
            )
        """)
        print("✅ Tabla verificada o creada.")  
        
        # Insertar usuarios por defecto si no existen
        usuarios_default = [
            ('secretaria', 'secretaria123', 'secretaria', 'Ana García - Secretaria'),
            ('presidente', 'presidente456', 'presidente', 'Carlos López - Presidente'),
            ('lector', 'lector789', 'lector', 'María Rodríguez - Lector')
        ]
        
        for usuario, contra, tipo, nombre in usuarios_default:
            print(f"➡ Insertando usuario: {usuario}")  
            cursor.execute(
                "INSERT IGNORE INTO Empleados (Usuario, Contra, Tipo, Nombre) VALUES (%s, %s, %s, %s)",
                (usuario, contra, tipo, nombre)
            )
        
        con.commit()
        print("✅ Usuarios inicializados correctamente.")  
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar usuarios: {e}")  
        st.error(f"Error al inicializar usuarios: {e}")
        return False
    finally:
        con.close()
        print("🔒 Conexión cerrada.")  # <--- nuevo

def login():
    st.title("Inicio de sesión")

    if st.session_state.get("usuarios_inicializados") is None:
        print("🚀 Inicializando usuarios por primera vez...")
        if inicializar_usuarios():
            st.session_state["usuarios_inicializados"] = True
            print("✅ Usuarios inicializados correctamente.")
        else:
            st.error("❌ Error al inicializar los usuarios en la base de datos.")
            print("❌ Falló la inicialización de usuarios.")

    if st.session_state.get("conexion_exitosa"):
        st.success("✅ Conexión a la base de datos establecida correctamente.")
        print("🔗 Estado: conexión exitosa registrada en session_state.")

    usuario = st.text_input("Usuario", key="usuario_input")
    contra = st.text_input("Contraseña", type="password", key="contra_input")

    if st.button("Iniciar sesión"):
        if not usuario or not contra:
            st.error("❌ Por favor, ingrese usuario y contraseña.")
            print("⚠ Campos vacíos al intentar iniciar sesión.")
            return
            
        tipo_usuario = verificar_usuario(usuario, contra)
        if tipo_usuario:
            st.session_state["usuario"] = usuario
            st.session_state["tipo_usuario"] = tipo_usuario
            st.session_state["sesion_iniciada"] = True
            print(f"✅ Sesión iniciada correctamente para: {usuario} ({tipo_usuario})")
            
            if tipo_usuario == "secretaria":
                st.success(f"👩‍💼 Bienvenida Secretaria ({usuario})")
            elif tipo_usuario == "presidente":
                st.success(f"👨‍💼 Bienvenido Presidente ({usuario})")
            elif tipo_usuario == "lector":
                st.success(f"👁 Bienvenido Lector ({usuario}) - Modo solo lectura")
            
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")
            print("❌ Credenciales incorrectas en login().")
