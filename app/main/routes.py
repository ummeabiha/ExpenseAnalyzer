from flask import Blueprint, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    """Route for the homepage."""
    # If the user is logged in, redirect to the view expenses page
    if current_user.is_authenticated:
        return redirect(url_for("expenses.view_expenses"))
    # If not logged in, render the login form as the homepage
    return redirect(url_for("auth.login"))
