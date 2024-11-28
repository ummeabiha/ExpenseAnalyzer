from collections import defaultdict
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
import matplotlib
import numpy as np
matplotlib.use("Agg")  # Using non-GUI backend for Flask
import matplotlib.pyplot as plt
import requests
from sqlalchemy import func
from .models import Expense
from .extensions import mail, db
import io
import base64

def generate_activation_token(user_id):
    """Generate an account activation token for the user."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(user_id, salt="user-activation")

def verify_activation_token(token, expiration=3600):
    """
    Verify the account activation token and return the user ID if valid.
    Return None if the token is invalid or expired.
    The token is valid for `expiration` seconds (default: 1 hour).
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token, salt="user-activation", max_age=expiration)
    except:
        return None
    return user_id

def send_activation_email(user):
    """Send an account activation email to the user."""
    token = generate_activation_token(user.id)
    link = url_for("auth.activate_account", token=token, _external=True)
    msg = Message("Activate Your Account", sender="no-reply@expenseanalyzer", recipients=[user.email])
    msg.body = f"Hello!\n\nPlease activate your account by clicking the following link: {link}"
    mail.send(msg)

def get_currency_conversion(from_currency, to_currency):
    """Fetches conversion rate from `from_currency` to `to_currency`."""
    api_key = current_app.config["API_KEY"]
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency.upper()}"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Try to fetch conversion rate and return None if it’s not found
    conversion_rate = data.get("conversion_rates", {}).get(to_currency.upper())
    # Return the conversion rate as a float
    return float(conversion_rate)

def get_cad_usd_forecast():
    """Fetch the forecast for CAD to USD conversion rate."""
    return get_currency_conversion("CAD", "USD")

def get_monthly_data(user_id):
    """Retrieve monthly expense data for the user."""
    # Retrieve all expenses for the user
    expenses = Expense.query.filter_by(user_id=user_id).all()

    # Group expenses by month and sum up the amounts
    monthly_data = defaultdict(float)
    for expense in expenses:
        month = expense.date.strftime("%Y-%m")  # Format as "YYYY-MM" for grouping by month
        monthly_data[month] += expense.amount

    # Convert the defaultdict to a sorted list of tuples for plotting
    sorted_monthly_data = sorted(monthly_data.items())
    months = [month for month, _ in sorted_monthly_data]
    totals = [total for _, total in sorted_monthly_data]
    # Return the months and total spending for each month
    return months, totals

def get_category_data(user_id):
    """Retrieve category spending data."""
    category_data = db.session.query(
        Expense.category.label("category"),
        func.sum(Expense.amount).label("total")
    ).filter_by(user_id=user_id).group_by("category").all()
    # Return the category data as a list of named tuples (category, total)
    return category_data

def create_pie_chart(category_data):
    """Generates a pie chart showing category spending distribution."""
    labels = [item.category for item in category_data]
    sizes = [item.total for item in category_data]

    # Grouping smaller categories into "Other"
    threshold = 5  # minimum percentage to avoid grouping
    labels, sizes = zip(
        *(
            (label, size) if size / sum(sizes) * 100 > threshold else ("Other", size)
            for label, size in zip(labels, sizes)
        )
    )

    plt.figure(FigureClass=plt.Figure, figsize=(8, 6))
    colors = plt.cm.Paired(np.linspace(0, 1, len(set(labels))))
    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        shadow=True,
        colors=colors,
        explode=[0.1 if size == max(sizes) else 0 for size in sizes],
    )
    plt.title("Category Spending Distribution", fontsize=14, pad=20)
    plt.axis("equal")
    plt.legend(loc="lower right", bbox_to_anchor=(0.64, -0.1, 0.5, 0.5), fontsize=10)
    plt.tight_layout()

    buffer = io.BytesIO() # Create a buffer to hold the image data
    plt.savefig(buffer, format="png") # Save the image data to the buffer
    buffer.seek(0) # Rewind the buffer to the beginning
    pie_chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8") # Encode the image data in base64
    plt.close() # Close the plot to free up memory
    # Return the base64 encoded pie chart data
    return pie_chart_base64


def create_bar_chart(months, totals):
    """Generates a bar chart comparing monthly expenses."""
    plt.figure(FigureClass=plt.Figure, figsize=(10, 6))
    colors = plt.cm.Blues(np.linspace(0.4, 1, len(totals)))
    plt.bar(months, totals, color=colors, edgecolor="black")

    plt.xlabel("Month", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Total Spending", fontsize=12)
    plt.ylim(0, max(totals) + 100)
    plt.yticks(np.arange(0, max(totals) + 100, step=100))
    plt.title("Monthly Expense Comparison", fontsize=14)

    # Add values on top of each bar
    for i, total in enumerate(totals):
        plt.text(i, total + 10, f"{total:.2f}", ha="center", fontsize=9)

    plt.grid(axis="y", linestyle="--", alpha=0.7)

    img = io.BytesIO() # Create a buffer to hold the image data
    plt.savefig(img, format="png") # Save the image data to the buffer
    img.seek(0) # Rewind the buffer to the beginning
    chart_data = base64.b64encode(img.getvalue()).decode() # Encode the image data in base64
    plt.close() # Close the plot to free up memory
    # Return the base64 encoded chart data
    return chart_data
