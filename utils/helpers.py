import streamlit as st
from datetime import datetime, date

def format_currency(amount):
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"

def format_date(fecha):
    if isinstance(fecha, (datetime, date)):
        return fecha.strftime("%d/%m/%Y")
    return fecha

def show_success_message(message):
    st.success(f"✅ {message}")

def show_error_message(message):
    st.error(f"❌ {message}")

def show_info_message(message):
    st.info(f"ℹ️ {message}")
