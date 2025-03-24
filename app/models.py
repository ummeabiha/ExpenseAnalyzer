from .extensions import db, login_manager, mail
from flask_login import UserMixin, current_user
from datetime import datetime, timezone
from sqlalchemy.orm import validates
import time
from flask_mail import Message
from flask_login import current_user
from app.extensions import mail
from flask import current_app

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


class BudgetSingleton:
    """Singleton for managing budgets on a per-user basis."""

    _instances = {}

    def __init__(self, user):
        """Initialize the singleton state for a user."""
        self.user = user
        self.limit = 0
        self.current_total = 0
        self.alert_sent = False
        self.last_accessed = time.time()

    @classmethod
    def get_instance(cls, user_id):
        """Retrieve or create a singleton instance for the user."""
        if user_id not in cls._instances:
            user = User.query.get(user_id)
            if user:
                cls._instances[user_id] = cls(user)
        
        cls._instances[user_id].last_accessed = time.time()
        return cls._instances.get(user_id)

    @classmethod
    def cleanup_expired_instances(cls, timeout=3600):
        """Remove inactive instances after timeout (default: 1 hour)."""
        current_time = time.time()
        expired_keys = [key for key, instance in cls._instances.items()
                        if current_time - instance.last_accessed > timeout]

        for key in expired_keys:
            del cls._instances[key]
            print(f"[DEBUG] Removed expired BudgetSingleton for user {key}")

    def update(self, budget):
        """Update the singleton state."""
        if self.limit == budget.monthly_limit and self.current_total == budget.current_expense_total:
            print("[DEBUG] No changes detected. Skipping unnecessary update.")
            return

        self.limit = budget.monthly_limit
        self.current_total = budget.current_expense_total
        self.alert_sent = budget.alert_sent

        print(f"[DEBUG] Singleton Updated: Limit={self.limit}, Current Total={self.current_total}, Alert Sent={self.alert_sent}")

        if self.current_total <= self.limit and self.alert_sent:
            print("[DEBUG] Budget is under limit. Resetting alert flag.")
            self.alert_sent = False
            budget.alert_sent = False
            db.session.commit()

        if self.current_total > self.limit and not self.alert_sent:
            self.send_alerts()
            self.alert_sent = True
            budget.alert_sent = True
            db.session.commit()

    def send_alerts(self):
        """Send alerts if budget is exceeded."""
        excess_amount = self.current_total - self.limit
        
        self.send_email_alert(excess_amount)
        self.send_sms_alert(excess_amount)
        self.log_budget_update()
        self.update_dashboard()

    def send_email_alert(self, excess_amount):
        """Send an email alert when the budget is exceeded."""
        with current_app.app_context():
            msg = Message(
                "Budget Exceeded Alert!",
                sender="YousifZito4SA3@gmail.com",
                recipients=[current_user.email],
            )
            msg.body = f"Hello {current_user.username},\n\nYou have exceeded your budget by ${excess_amount:.2f}.\n\nThank you!"
            # mail.send(msg)
        print(f"[EMAIL ALERT] Budget exceeded by ${excess_amount:.2f}. Email sent to {current_user.email}")

    def send_sms_alert(self, excess_amount):
        """Simulate sending an SMS alert."""
        print(f"[SMS ALERT] You have exceeded your budget by ${excess_amount:.2f}!")

    def log_budget_update(self):
        """Log budget updates."""
        print(f"[LOG] Budget updated: Limit={self.limit}, Current Total={self.current_total}")

    def update_dashboard(self):
        """Update the frontend dashboard."""
        print(f"[DASHBOARD] Updated: New Limit = {self.limit}, Current Spending = {self.current_total}")

    def set_limit(self, limit):
        """Set the budget limit."""
        self.limit = limit

    def update_total(self, amount):
        """Update the current spending total."""
        self.current_total += amount

    def reset_alert(self):
        """Reset the alert flag."""
        self.alert_sent = False

