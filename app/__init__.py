from flask import Flask
from flask_login import current_user
from .models import BudgetSingleton
from .currency_loader import load_currency_data
from .utils import get_cad_usd_forecast
from .config import Config
from .extensions import db, login_manager, mail, bcrypt, init_db_with_retry
from .auth.routes import auth_bp
from .expenses.routes import expenses_bp
from .budget.routes import budget_bp
from .api.routes import api_bp
from .main.routes import main_bp
from .observers import AlertObserver, LoggingObserver


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Load sorted currency data and assign to app context
    app.currency_data = load_currency_data()

    # Initialize Flask extensions
    init_db_with_retry(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    with app.app_context():
        db.create_all()

        # Register global observers
        alert_observer = AlertObserver()
        logging_observer = LoggingObserver()

        # Attach observers to all BudgetSingletons dynamically
        @app.before_request
        def attach_observers():
            if current_user.is_authenticated:
                budget_singleton = BudgetSingleton.get_instance(current_user.id)
                if alert_observer not in budget_singleton._observers:
                    budget_singleton.add_observer(alert_observer)
                if logging_observer not in budget_singleton._observers:
                    budget_singleton.add_observer(logging_observer)

    # Inject CAD-USD forecast and currency data for template access
    @app.context_processor
    def inject_cad_usd_forecast():
        forecast_rate = get_cad_usd_forecast()
        return dict(cad_usd_forecast=forecast_rate)

    # Inject currency data for template access
    @app.context_processor
    def inject_currency_data():
        return dict(currency_data=app.currency_data)

    # Register blueprints for application routes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(expenses_bp, url_prefix="/expenses")
    app.register_blueprint(budget_bp, url_prefix="/budget")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
