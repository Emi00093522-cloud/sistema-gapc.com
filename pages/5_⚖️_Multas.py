import streamlit as st
import pandas as pd
from config.database import get_connection
from utils.database_ops import get_fines_by_member, register_member_fine

def main():
    st.title("⚖️ Gestión de Multas")
    
    tab1, tab2, tab3 = st.tabs(["📋 Multas Registradas", "➕ Nueva Multa", "💳 Pagar Multa"])
    
    with tab1:
        show_fines_list()
    
    with tab2:
        show_new_fine_form()
    
    with tab3:
        show_pay_fine_form()

def show_fines_list():
    st.subheader("Multas Registradas")
    
    conn = get_connection()
    
    query = """
    SELECT mxm.ID_Miembro, m.nombre as miembro, g.nombre as grupo, 
           mul.descripcion, mxm.monto_a_pagar, mxm.monto_pagado,
           em.estado_multa, mxm.fecha_pago
    FROM Miembro_x_Multa mxm
    JOIN Multa mul ON mxm.ID_Multa = mul.ID_Multa
    JOIN Miembro m ON mxm.ID_Miembro = m.ID_Miembro
    JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
    JOIN Estado_multa em ON mxm.ID_Estado_multa = em.ID_Estado_multa
    ORDER BY mxm.ID_Miembro
    """
    
    fines = pd.read_sql(query, conn)
    
    if not fines.empty:
        st.dataframe(fines, use_container_width=True)
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            total_multas = fines['monto_a_pagar'].sum()
            st.metric("Total Multas", f"${total_multas:,.2f}")
        with col2:
            multas_pendientes = len(fines[fines['estado_multa'] == 'Pendiente'])
            st.metric("Multas Pendientes", multas_pendientes)
        with col3:
            total_pagado = fines['monto_pagado'].sum()
            st.metric("Total Pagado", f"${total_pagado:,.2f}")
    else:
        st.info("No hay multas registradas")
    
    conn.close()

def show_new_fine_form():
    st.subheader("Registrar Nueva Multa")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo WHERE ID_Estado = 1", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist(), key="fine_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        miembros = pd.read_sql(
            "SELECT ID_Miembro, nombre FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1", 
            conn, params=(group_id,)
        )
        
        if not miembros.empty:
            with st.form("new_fine_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    id_miembro = st.selectbox("Miembro*", miembros['ID_Miembro'],
                                            format_func=lambda x: miembros[miembros['ID_Miembro'] == x]['nombre'].iloc[0])
                    monto = st.number_input("Monto de la Multa*", min_value=0.0, step=10.0)
                
                with col2:
                    descripcion = st.text_area("Descripción/Motivo*")
                    tipo_multa = st.selectbox("Tipo de Multa", ["Por inasistencia", "Por mora", "Otra infracción"])
                
                submitted = st.form_submit_button("Registrar Multa")
                
                if submitted:
                    if id_miembro and monto and descripcion:
                        if register_member_fine(id_miembro, None, monto, f"{tipo_multa}: {descripcion}"):
                            st.success("Multa registrada exitosamente!")
                        else:
                            st.error("Error al registrar la multa")
                    else:
                        st.warning("Por favor complete todos los campos obligatorios (*)")
        else:
            st.info("Este grupo no tiene miembros activos")
    else:
        st.info("No hay grupos activos registrados")
    
    conn.close()

def show_pay_fine_form():
    st.subheader("Registrar Pago de Multa")
    
    conn = get_connection()
    
    # Obtener multas pendientes
    multas_pendientes = pd.read_sql("""
    SELECT mxm.ID_Miembro, mxm.ID_Multa, m.nombre as miembro, g.nombre as grupo,
           mul.descripcion, mxm.monto_a_pagar, mxm.monto_pagado,
           (mxm.monto_a_pagar - mxm.monto_pagado) as saldo_pendiente
    FROM Miembro_x_Multa mxm
    JOIN Multa mul ON mxm.ID_Multa = mul.ID_Multa
    JOIN Miembro m ON mxm.ID_Miembro = m.ID_Miembro
    JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
    WHERE mxm.ID_Estado_multa = 1  -- Pendiente
    AND (mxm.monto_a_pagar - mxm.monto_pagado) > 0
    """, conn)
    
    if not multas_pendientes.empty:
        selected_fine = st.selectbox("Seleccionar Multa a Pagar", 
                                   multas_pendientes['ID_Multa'],
                                   format_func=lambda x: f"{multas_pendientes[multas_pendientes['ID_Multa'] == x]['miembro'].iloc[0]} - {multas_pendientes[multas_pendientes['ID_Multa'] == x]['descripcion'].iloc[0]} (Saldo: ${multas_pendientes[multas_pendientes['ID_Multa'] == x]['saldo_pendiente'].iloc[0]:,.2f})")
        
        fine_data = multas_pendientes[multas_pendientes['ID_Multa'] == selected_fine].iloc[0]
        
        st.write(f"**Miembro:** {fine_data['miembro']}")
        st.write(f"**Grupo:** {fine_data['grupo']}")
        st.write(f"**Descripción:** {fine_data['descripcion']}")
        st.write(f"**Monto Original:** ${fine_data['monto_a_pagar']:,.2f}")
        st.write(f"**Ya Pagado:** ${fine_data['monto_pagado']:,.2f}")
        st.write(f"**Saldo Pendiente:** ${fine_data['saldo_pendiente']:,.2f}")
        
        with st.form("pay_fine_form"):
            monto_pago = st.number_input("Monto a Pagar*", 
                                       min_value=0.0, 
                                       max_value=float(fine_data['saldo_pendiente']),
                                       step=10.0)
            
            submitted = st.form_submit_button("Registrar Pago")
            
            if submitted:
                if monto_pago > 0:
                    cursor = conn.cursor()
                    try:
                        # Actualizar monto pagado
                        nuevo_monto_pagado = fine_data['monto_pagado'] + monto_pago
                        
                        # Verificar si se pagó completamente
                        nuevo_estado = 2 if nuevo_monto_pagado >= fine_data['monto_a_pagar'] else 1
                        
                        query = """
                        UPDATE Miembro_x_Multa 
                        SET monto_pagado = %s, 
                            ID_Estado_multa = %s,
                            fecha_pago = CASE WHEN %s = 2 THEN CURDATE() ELSE fecha_pago END
                        WHERE ID_Multa = %s AND ID_Miembro = %s
                        """
                        cursor.execute(query, (nuevo_monto_pagado, nuevo_estado, nuevo_estado, selected_fine, fine_data['ID_Miembro']))
                        conn.commit()
                        st.success("Pago registrado exitosamente!")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error al registrar el pago: {e}")
                    finally:
                        cursor.close()
                else:
                    st.warning("El monto debe ser mayor a 0")
    else:
        st.info("No hay multas pendientes de pago")
    
    conn.close()

if __name__ == "__main__":
    main()
