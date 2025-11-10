import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración Base de Datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'sistema_gapc')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Configuración Aplicación
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'gapc_secret_key_2025')
