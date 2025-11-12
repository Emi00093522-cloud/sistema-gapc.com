import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from modulos.bienvenida import mostrar_bienvenida
from modulos.login import login

# Llamamos a la función mostrar_ahorro para mostrar el mensaje en la app
mostrar_bienvenida()
login()
