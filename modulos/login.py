import streamlit as st
from modulos.config.conexion import obtener_conexion

def verificar_usuario(usuario, contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None
    else:
        st.session_state["conexion_exitosa"] = True

    try:
        cursor = con.cursor()
        # Verificar en la tabla de empleados
        query = "SELECT Usuario, Contra, Tipo FROM Empleados WHERE Usuario = %s AND Contra = %s"
        cursor.execute(query, (usuario, contra))
        result = cursor.fetchone()
        
        if result:
            return result[2]  # Retorna el tipo de usuario
        else:
            return None
    finally:
        con.close()

def inicializar_usuarios():
    """Función para inicializar los usuarios en la base de datos"""
    con = obtener_conexion()
    if not con:
        return False
        
    try:
        cursor = con.cursor()
        
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
        
        # Insertar usuarios por defecto si no existen
        usuarios_default = [
            ('secretaria', 'secretaria123', 'secretaria', 'Ana García - Secretaria'),
            ('presidente', 'presidente456', 'presidente', 'Carlos López - Presidente'),
            ('lector', 'lector789', 'lector', 'María Rodríguez - Lector')
        ]
        
        for usuario, contra, tipo, nombre in usuarios_default:
            cursor.execute(
                "INSERT IGNORE INTO Empleados (Usuario, Contra, Tipo, Nombre) VALUES (%s, %s, %s, %s)",
                (usuario, contra, tipo, nombre)
            )
        
        con.commit()
        return True
        
    except Exception as e:
        st.error(f"Error al inicializar usuarios: {e}")
        return False
    finally:
        con.close()

def login():
    st.title("Inicio de sesión")

    # Inicializar usuarios en la base de datos
    if st.session_state.get("usuarios_inicializados") is None:
        if inicializar_usuarios():
            st.session_state["usuarios_inicializados"] = True
        else:
            st.error("❌ Error al inicializar los usuarios en la base de datos.")

    # Mostrar mensaje de conexión exitosa
    if st.session_state.get("conexion_exitosa"):
        st.success("✅ Conexión a la base de datos establecida correctamente.")

    usuario = st.text_input("Usuario", key="usuario_input")
    contra = st.text_input("Contraseña", type="password", key="contra_input")

    if st.button("Iniciar sesión"):
        if not usuario or not contra:
            st.error("❌ Por favor, ingrese usuario y contraseña.")
            return
            
        tipo_usuario = verificar_usuario(usuario, contra)
        if tipo_usuario:
            st.session_state["usuario"] = usuario
            st.session_state["tipo_usuario"] = tipo_usuario
            st.session_state["sesion_iniciada"] = True
            
            # Mensaje de bienvenida según el tipo de usuario
            if tipo_usuario == "secretaria":
                st.success(f"👩‍💼 Bienvenida Secretaria ({usuario})")
            elif tipo_usuario == "presidente":
                st.success(f"👨‍💼 Bienvenido Presidente ({usuario})")
            elif tipo_usuario == "lector":
                st.success(f"👁️ Bienvenido Lector ({usuario}) - Modo solo lectura")
            
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

# Función para verificar permisos en otros módulos
def tiene_permiso_escritura():
    """Verifica si el usuario actual tiene permisos de escritura"""
    return st.session_state.get("tipo_usuario") in ["secretaria", "presidente"]

def obtener_tipo_usuario():
    """Retorna el tipo de usuario actual"""
    return st.session_state.get("tipo_usuario")

# Información de usuarios para referencia
def mostrar_info_usuarios():
    """Función para mostrar información de los usuarios (solo para desarrollo)"""
    if st.sidebar.checkbox("ℹ️ Mostrar información de usuarios (Desarrollo)"):
        st.sidebar.info("**Usuarios de prueba:**")
        st.sidebar.write("**Secretaria:**")
        st.sidebar.write("- Usuario: secretaria")
        st.sidebar.write("- Contraseña: secretaria123")
        st.sidebar.write("- Permisos: Lectura y escritura")
        
        st.sidebar.write("**Presidente:**")
        st.sidebar.write("- Usuario: presidente")
        st.sidebar.write("- Contraseña: presidente456")
        st.sidebar.write("- Permisos: Lectura y escritura")
        
        st.sidebar.write("**Lector:**")
        st.sidebar.write("- Usuario: lector")
        st.sidebar.write("- Contraseña: lector789")
        st.sidebar.write("- Permisos: Solo lectura")
