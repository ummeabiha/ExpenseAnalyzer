from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from tenacity import retry, stop_after_attempt, wait_exponential

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

# Retry logic with exponential backoff for database initialization (10 attempts)
@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, max=40))
def init_db_with_retry(app):
    """Initialize the SQLAlchemy database with retry logic."""
    db.init_app(app)
