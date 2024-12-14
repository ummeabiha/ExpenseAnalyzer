from flask import Blueprint, redirect, url_for
from flask_login import current_user
from app.models import User
from flask_login import login_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    """Route for the homepage."""
    # If the user is already logged in, redirect to the view expenses page
    if current_user.is_authenticated:
        return redirect(url_for("expenses.view_expenses"))
    
    # If not logged in, log in as the guest user
    guest_user = User.query.filter_by(username="Guest").first()
    if guest_user:
        login_user(guest_user)
        return redirect(url_for("expenses.view_expenses"))

    # If no guest user is found, redirect to the login page
    return redirect(url_for("auth.login"))