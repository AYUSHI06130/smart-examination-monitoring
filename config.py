import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, "database", "monitoring.db")


SECRET_KEY = "online_monitoring_system_secret_key"

# ----------------------------------------
# Admin Credentials
# ----------------------------------------

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD = "admin123"