from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import RegistrationForm, LoginForm
from ..models import User
from ..extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required
from flask import flash, redirect, url_for
from ..utils import send_activation_email, verify_activation_token


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Route to register a new user."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the email and/or username already exists in the database
        existing_user = User.query.filter_by(email=form.email.data).first()
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_username:
            flash("The email and username are already taken.<br>Please choose a different email and username.", "danger")
            return redirect(url_for("auth.register"))
        if existing_user:
            flash("This email is already registered.<br>Please log in or use a different email.", "danger")
            return redirect(url_for("auth.register"))
        if existing_username:
            flash("The username is already taken.<br>Please choose a different username.", "danger")
            return redirect(url_for("auth.register"))
        # Hash the password and add the user to the database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash("Please check your email to activate your account.", "info")
        return redirect(url_for("auth.login"))
    # Render the registration form
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Route to log in a user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("No account found with that email.<br>Please check your email or register for a new account.", "warning")
            return redirect(url_for("auth.login"))
        if not user.active:
            flash("Please activate your account first!", "info")
            return redirect(url_for("auth.login"))
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("expenses.view_expenses"))
        flash("Login unsuccessful!<br>Please check email and password.", "danger")
    # Render the login form
    return render_template("login.html", form=form)

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Route to log out a user."""
    logout_user()
    # Redirect to the login page
    return redirect(url_for("auth.login"))

@auth_bp.route("/activate/<token>")
def activate_account(token):
    """Route to activate a user account using an activation token."""
    user_id = verify_activation_token(token)
    if user_id is None:
        flash("The activation link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if user.active:
        flash("Account already activated! Please log in.", "info")
    else:
        user.active = True
        db.session.commit()
        flash("Your account has been activated!<br>You can now log in.", "success")
    # Redirect to the login page
    return redirect(url_for("auth.login"))