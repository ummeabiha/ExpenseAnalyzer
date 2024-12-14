from .extensions import db, login_manager, mail
from flask_login import UserMixin
from datetime import datetime, timezone
from .observers import Subject, AlertObserver, LoggingObserver
from sqlalchemy.orm import validates

@login_manager.user_loader  # Register the user loader function.
def load_user(user_id):
    """Load the user object from the database."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for storing user account information."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(150), nullable=False)
    active = db.Column(db.Boolean, default=False)
    # Add a one-to-many relationship with expenses.
    expenses = db.relationship("Expense", backref="user", lazy=True)
    # Add a one-to-one relationship with the budget.
    budget = db.relationship("Budget", backref="user", uselist=False)

    @property # Define a property to check if the user is active.
    def is_active(self):
        # Check if the user is active and return the result.
        return self.active

class Expense(db.Model):
    """Expense model for storing user expenses."""
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False, default=lambda: datetime.utcnow().strftime('%Y-%m-%d'))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Budget(db.Model):
    """Budget model for storing user budget information."""
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, nullable=False)
    current_expense_total = db.Column(db.Float, default=0)
    alert_sent = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def update_total(self, amount):
        """Update the current spending in the database and notify observers."""
        self.current_expense_total += amount
        db.session.commit()
        # Update the singleton instance and notify observers after committing the changes.
        BudgetSingleton.get_instance(self.user_id).update(self)

    def reset_alert(self):
        """Reset the alert flag."""
        self.alert_sent = False
        db.session.commit()
        # Reset the alert flag in the singleton instance and commit the changes.
        BudgetSingleton.get_instance(self.user_id).reset_alert()


class BudgetSingleton(Subject):
    """Singleton for managing budgets on a per-user basis."""

    _instances = {}

    def __init__(self, user):
        """
        Initialize the singleton state.
        limit: Monthly budget limit for the user.
        current_total: Current total spending for the user.
        alert_sent: Flag to indicate if an alert has been sent for exceeding the budget.
        """
        super().__init__()
        self.user = user
        self.limit = 0
        self.current_total = 0
        self.alert_sent = False
        # Register the observers during initialization
        if not any(isinstance(observer, AlertObserver) for observer in self._observers):
            self.add_observer(AlertObserver())
        if not any(isinstance(observer, LoggingObserver) for observer in self._observers):
            self.add_observer(LoggingObserver())

    @classmethod # Define a class method to retrieve or create a singleton instance.
    def get_instance(cls, user_id):
        """Retrieve or create a singleton instance for the user."""
        if user_id not in cls._instances:
            user = User.query.get(user_id)
            if user:
                cls._instances[user_id] = cls(user)
        return cls._instances[user_id]

    def update(self, budget):
        """Update the singleton state and notify observers."""
        # Synchronize the singleton's state with the budget
        self.limit = budget.monthly_limit
        self.current_total = budget.current_expense_total
        self.alert_sent = budget.alert_sent

        # Debugging logs for state update
        print(f"[DEBUG] Singleton Updated: Limit={self.limit}, Current Total={self.current_total}, Alert Sent={self.alert_sent}")

        # Reset the alert if the current total is under the limit and an alert was previously sent
        if self.current_total <= self.limit and self.alert_sent:
            print("[DEBUG] Budget is now under limit. Resetting alert flag.")
            self.alert_sent = False
            budget.alert_sent = False
            db.session.commit()

        # Only trigger alert if the budget limit is exceeded and alert hasn't been sent
        if self.current_total > self.limit and not self.alert_sent:
            self.notify_observers()
            # Update the alert state after notifying observers
            self.alert_sent = True
            budget.alert_sent = True
            db.session.commit()

        # Debugging logs for state update
        print(f"[DEBUG] Singleton Updated: Limit={self.limit}, Current Total={self.current_total}, Alert Sent={self.alert_sent}")

    def set_limit(self, limit):
        """Set the budget limit."""
        self.limit = limit

    def update_total(self, amount):
        """Update the current spending total for the user."""
        self.current_total += amount

    def reset_alert(self):
        """Reset the alert flag."""
        self.alert_sent = False