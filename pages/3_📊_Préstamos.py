import streamlit as st
import pandas as pd
from config.database import get_connection
from datetime import datetime, timedelta

def main():
    st.title("📊 Gestión de Préstamos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Préstamos Activos", "➕ Nuevo Préstamo", "💳 Registrar Pago", "📈 Estado de Cartera"])
    
    with tab1:
        show_active_loans()
    
    with tab2:
        show_new_loan_form()
    
    with tab3:
        show_payment_registration()
    
    with tab4:
        show_loan_portfolio()

def show_active_loans():
    st.subheader("Préstamos Activos")
    
    conn = get_connection()
    
    # Obtener préstamos activos
    query = """
    SELECT p.ID_Prestamo, m.nombre as miembro, g.nombre as grupo, 
           p.monto, p.fecha_desembolso, p.plazo, ep.estado_prestamo,
           (SELECT COALESCE(SUM(monto_capital), 0) FROM Pago_prestamo WHERE ID_Prestamo = p.ID_Prestamo) as capital_pagado,
           (p.monto - (SELECT COALESCE(SUM(monto_capital), 0) FROM Pago_prestamo WHERE ID_Prestamo = p.ID_Prestamo)) as saldo_pendiente
    FROM Prestamo p
    JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
    JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
    JOIN Estado_prestamo ep ON p.ID_Estado_prestamo = ep.ID_Estado_prestamo
    WHERE p.ID_Estado_prestamo IN (1, 2)  -- Vigente o en Mora
    ORDER BY p.fecha_desembolso DESC
    """
    
    loans = pd.read_sql(query, conn)
    
    if not loans.empty:
        st.dataframe(loans, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_prestamos = loans['monto'].sum()
            st.metric("Total Prestado", f"${total_prestamos:,.2f}")
        with col2:
            saldo_pendiente = loans['saldo_pendiente'].sum()
            st.metric("Saldo Pendiente", f"${saldo_pendiente:,.2f}")
        with col3:
            prestamos_vigentes = len(loans[loans['estado_prestamo'] == 'Vigente'])
            st.metric("Préstamos Vigentes", prestamos_vigentes)
        with col4:
            prestamos_mora = len(loans[loans['estado_prestamo'] == 'Mora'])
            st.metric("En Mora", prestamos_mora)
    else:
        st.info("No hay préstamos activos")
    
    conn.close()

def show_new_loan_form():
    st.subheader("Solicitar Nuevo Préstamo")
    
    conn = get_connection()
    
    grupos = pd.read_sql("SELECT ID_Grupo, nombre FROM Grupo", conn)
    
    if not grupos.empty:
        selected_group = st.selectbox("Seleccionar Grupo", grupos['nombre'].tolist(), key="loan_group")
        group_id = grupos[grupos['nombre'] == selected_group]['ID_Grupo'].iloc[0]
        
        miembros = pd.read_sql(
            "SELECT ID_Miembro, nombre FROM Miembro WHERE ID_Grupo = %s AND ID_Estado = 1", 
            conn, params=(group_id,)
        )
        
        if not miembros.empty:
            with st.form("new_loan_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    id_miembro = st.selectbox("Miembro*", miembros['ID_Miembro'],
                                            format_func=lambda x: miembros[miembros['ID_Miembro'] == x]['nombre'].iloc[0])
                    monto = st.number_input("Monto del Préstamo*", min_value=0.0, step=100.0)
                    plazo = st.selectbox("Plazo (meses)*", [3, 6, 9, 12, 18, 24])
                
                with col2:
                    fecha_desembolso = st.date_input("Fecha de Desembolso*", datetime.now())
                    tasa_interes = st.number_input("Tasa de Interés (%)*", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
                    proposito = st.text_area("Propósito del Préstamo")
                
                submitted = st.form_submit_button("Solicitar Préstamo")
                
                if submitted:
                    if id_miembro and monto and plazo and tasa_interes:
                        total_interes = monto * (tasa_interes / 100) * (plazo / 12)
                        
                        cursor = conn.cursor()
                        try:
                            query = """
                            INSERT INTO Prestamo (ID_Miembro, fecha_desembolso, monto, total_interes, ID_Estado_prestamo, plazo, proposito)
                            VALUES (%s, %s, %s, %s, 1, %s, %s)
                            """
                            cursor.execute(query, (id_miembro, fecha_desembolso, monto, total_interes, plazo, proposito))
                            conn.commit()
                            st.success("Préstamo registrado exitosamente!")
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error al registrar el préstamo: {e}")
                        finally:
                            cursor.close()
                    else:
                        st.warning("Por favor complete todos los campos obligatorios (*)")
        else:
            st.info("Este grupo no tiene miembros activos")
    else:
        st.info("No hay grupos registrados")
    
    conn.close()

def show_payment_registration():
    st.subheader("Registrar Pago de Préstamo")
    
    conn = get_connection()
    
    # Obtener préstamos activos
    prestamos = pd.read_sql("""
    SELECT p.ID_Prestamo, m.nombre as miembro, g.nombre as grupo, p.monto,
           (p.monto - COALESCE(SUM(pp.monto_capital), 0)) as saldo_pendiente
    FROM Prestamo p
    JOIN Miembro m ON p.ID_Miembro = m.ID_Miembro
    JOIN Grupo g ON m.ID_Grupo = g.ID_Grupo
    LEFT JOIN Pago_prestamo pp ON p.ID_Prestamo = pp.ID_Prestamo
    WHERE p.ID_Estado_prestamo IN (1, 2)
    GROUP BY p.ID_Prestamo, m.nombre, g.nombre, p.monto
    HAVING saldo_pendiente > 0
    """, conn)
    
    if not prestamos.empty:
        selected_loan = st.selectbox("Seleccionar Préstamo", 
                                   prestamos['ID_Prestamo'],
                                   format_func=lambda x: f"Préstamo {x} - {prestamos[prestamos['ID_Prestamo'] == x]['miembro'].iloc[0]} (Saldo: ${prestamos[prestamos['ID_Prestamo'] == x]['saldo_pendiente'].iloc[0]:,.2f})")
        
        loan_data = prestamos[prestamos['ID_Prestamo'] == selected_loan].iloc[0]
        
        st.write(f"**Miembro:** {loan_data['miembro']}")
        st.write(f"**Grupo:** {loan_data['grupo']}")
        st.write(f"**Monto Original:** ${loan_data['monto']:,.2f}")
        st.write(f"**Saldo Pendiente:** ${loan_data['saldo_pendiente']:,.2f}")
        
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                fecha_pago = st.date_input("Fecha de Pago*", datetime.now())
                monto_capital = st.number_input("Monto a Capital*", min_value=0.0, max_value=float(loan_data['saldo_pendiente']), step=100.0)
            
            with col2:
                monto_interes = st.number_input("Monto a Interés*", min_value=0.0, step=10.0)
                total_cancelado = monto_capital + monto_interes
                st.write(f"**Total a Cancelar:** ${total_cancelado:,.2f}")
            
            # Obtener reuniones para asociar el pago
            reuniones = pd.read_sql("""
            SELECT r.ID_Reunion, r.fecha 
            FROM Reunion r 
            JOIN Miembro m ON r.ID_Grupo = m.ID_Grupo 
            JOIN Prestamo p ON m.ID_Miembro = p.ID_Miembro 
            WHERE p.ID_Prestamo = %s
            ORDER BY r.fecha DESC
            """, conn, params=(selected_loan,))
            
            id_reunion = None
            if not reuniones.empty:
                id_reunion = st.selectbox("Asociar a Reunión (opcional)", 
                                        reuniones['ID_Reunion'],
                                        format_func=lambda x: f"Reunión {x} - {reuniones[reuniones['ID_R
