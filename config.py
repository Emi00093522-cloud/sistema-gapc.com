
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration (Clever Cloud MySQL)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'bzol0srlvapvtstpnaj3')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = os.getenv('DB_PORT', '3306')
    
    # App Configuration
    APP_TITLE = "Sistema GAPC"
    APP_ICON = "💰"
    APP_VERSION = "1.0.0"

# Instancia global
config = Config()
