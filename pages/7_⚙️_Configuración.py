import streamlit as st
import pandas as pd
from config.database import get_connection
from utils.auth import create_user

def main():
    st.title("⚙️ Configuración del Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Usuarios", "🏢 Distritos", "🔧 Parámetros", "📊 Datos Maestros"])
    
    with tab1:
        show_users_management()
    
    with tab2:
        show_districts_management()
    
    with tab3:
        show_parameters_management()
    
    with tab4:
        show_master_data_management()

def show_users_management():
    st.subheader("Gestión de Usuarios del Sistema")
    
    conn = get_connection()
    
    # Lista de usuarios existentes
    usuarios = pd.read_sql("""
    SELECT u.ID_Usuario, u.nombre_usuario, u.email, c.nombre_cargo, tu.tipo_usuario
    FROM Usuario u
    JOIN Cargo c ON u.ID_Cargo = c.ID_Cargo
    JOIN Tipo_usuario tu ON u.ID_Tipo_usuario = tu.ID_Tipo_usuario
    """, conn)
    
    if not usuarios.empty:
        st.write("### Usuarios Registrados")
        st.dataframe(usuarios, use_container_width=True)
    
    # Formulario para crear nuevo usuario
    st.write("### Crear Nuevo Usuario")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_usuario = st.text_input("Nombre de Usuario*")
            email = st.text_input("Email")
            password = st.text_input("Contraseña*", type="password")
        
        with col2:
            cargos = pd.read_sql("SELECT * FROM Cargo", conn)
            id_cargo = st.selectbox("Cargo*", cargos['ID_Cargo'],
                                   format_func=lambda x: cargos[cargos['ID_Cargo'] == x]['nombre_cargo'].iloc[0])
            
            tipos_usuario = pd.read_sql("SELECT * FROM Tipo_usuario", conn)
            id_tipo_usuario = st.selectbox("Tipo de Usuario*", tipos_usuario['ID_Tipo_usuario'],
                                          format_func=lambda x: tipos_usuario[tipos_usuario['ID_Tipo_usuario'] == x]['tipo_usuario'].iloc[0])
        
        submitted = st.form_submit_button("Crear Usuario")
        
        if submitted:
            if nombre_usuario and password and id_cargo and id_tipo_usuario:
                if create_user(nombre_usuario, password, email, id_cargo, id_tipo_usuario):
                    st.success("Usuario creado exitosamente!")
                    st.rerun()
                else:
                    st.error("Error al crear el usuario")
            else:
                st.warning("Por favor complete los campos obligatorios (*)")
    
    conn.close()

def show_districts_management():
    st.subheader("Gestión de Distritos")
    
    conn = get_connection()
    
    # Lista de distritos
    distritos = pd.read_sql("SELECT * FROM Distrito", conn)
    
    if not distritos.empty:
        st.write("### Distritos Registrados")
        st.dataframe(distritos, use_container_width=True)
    
    # Formulario para agregar distrito
    st.write("### Agregar Nuevo Distrito")
    
    with st.form("create_district_form"):
        nombre_distrito = st.text_input("Nombre del Distrito*")
        
        submitted = st.form_submit_button("Agregar Distrito")
        
        if submitted:
            if nombre_distrito:
                cursor = conn.cursor()
                try:
                    query = "INSERT INTO Distrito (nombre_distrito) VALUES (%s)"
                    cursor.execute(query, (nombre_distrito,))
                    conn.commit()
                    st.success("Distrito agregado exitosamente!")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error al agregar distrito: {e}")
                finally:
                    cursor.close()
            else:
                st.warning("Por favor ingrese el nombre del distrito")
    
    conn.close()

def show_parameters_management():
    st.subheader("Parámetros del Sistema")
    
    st.info("""
    **Configuración de Parámetros Globales**
    
    Aquí puedes configurar los parámetros generales del sistema GAPC.
    """)
    
    with st.form("parameters_form"):
        st.write("### Configuración General")
        
        tasa_interes_default = st.number_input("Tasa de Interés Default (%)", 
                                             min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        
        max_ausencias_permitidas = st.number_input("Máximo de Ausencias Permitidas", 
                                                 min_value=0, max_value=12, value=3)
        
        monto_multa_ausencia = st.number_input("Monto de Multa por Ausencia", 
                                             min_value=0.0, value=5.0, step=1.0)
        
        periodicidad_reuniones_default = st.selectbox("Periodicidad Default de Reuniones", 
                                                    ["Semanal", "Quincenal", "Mensual"])
        
        if st.form_submit_button("Guardar Configuración"):
            st.success("Configuración guardada exitosamente!")
            # Aquí iría la lógica para guardar en la base de datos

def show_master_data_management():
    st.subheader("Datos Maestros del Sistema")
    
    conn = get_connection()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cargos", "Roles", "Estados", "Tipos de Movimiento"])
    
    with tab1:
        st.write("### Cargos del Sistema")
        cargos = pd.read_sql("SELECT * FROM Cargo", conn)
        st.dataframe(cargos, use_container_width=True)
    
    with tab2:
        st.write("### Roles de Miembros")
        roles = pd.read_sql("SELECT * FROM Rol", conn)
        st.dataframe(roles, use_container_width=True)
    
    with tab3:
        st.write("### Estados del Sistema")
        estados = pd.read_sql("SELECT * FROM Estado", conn)
        st.dataframe(estados, use_container_width=True)
    
    with tab4:
        st.write("### Tipos de Movimiento")
        tipos_movimiento = pd.read_sql("SELECT * FROM Tipo_movimiento", conn)
        st.dataframe(tipos_movimiento, use_container_width=True)
    
    conn.close()

if __name__ == "__main__":
    main()
