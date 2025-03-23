from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()  

def init_db_with_retry(app, retries=3, delay=2):
    """Initialize the database with retry logic."""
    import time
    for attempt in range(retries):
        try:
            db.init_app(app)
            migrate.init_app(app, db)  
            with app.app_context():
                db.create_all()
            print("Database initialized successfully.")
            break
        except Exception as e:
            print(f"Database initialization failed (attempt {attempt + 1}): {e}")
            time.sleep(delay)
