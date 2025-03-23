from flask import Flask
import json
import os
from app.extensions import db, bcrypt, login_manager, mail, migrate, init_db_with_retry

def create_app():
    app = Flask(__name__)

    # Load configuration from JSON file
    config_path = os.path.join(os.path.dirname(__file__), "../instance/configExpenseAnalyzer.json")
    with open(config_path, "r") as config_file:
        app.config.update(json.load(config_file))

    # Initialize Flask extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Initialize database with retry logic
    init_db_with_retry(app)  # 🔹 Ensures DB initialization with retries

    # Configure login manager
    login_manager.login_view = "auth.login"

    # Import and register blueprints
    from app.api.routes import api_bp
    from app.auth.routes import auth_bp
    from app.budget.routes import budget_bp
    from app.expenses.routes import expenses_bp
    from app.main.routes import main_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(budget_bp, url_prefix="/budget")
    app.register_blueprint(expenses_bp, url_prefix="/expenses")
    app.register_blueprint(main_bp)

    return app
