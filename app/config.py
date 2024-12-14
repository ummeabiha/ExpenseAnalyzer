import os
import json

# Detect OS and load the JSON config
if os.name == "nt":
    config_path = os.path.join(os.getcwd(),"instance", "configExpenseAnalyzer.json")
else:
    config_path = "/etc/configExpenseAnalyzer.json"

with open(config_path) as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get("EMAIL_USER")
    MAIL_PASSWORD = config.get("EMAIL_PASS")
    API_KEY = config.get("API_KEY")
    # Additional SQLAlchemy configuration for handling idle connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True, # Check the connection before using it
        "pool_recycle": 900,  # Recycle connections after 15 minutes
    }
