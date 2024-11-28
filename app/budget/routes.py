from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Budget, BudgetSingleton
from ..extensions import db
from flask_login import login_required, current_user

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/set", methods=["GET", "POST"])
@login_required
def set_budget():
    """Route to set the budget for the current user."""
    if request.method == "POST":
        monthly_limit = float(request.form["monthly_limit"])
        total_spending = sum(expense.amount for expense in current_user.expenses)

        if current_user.budget:
            current_user.budget.monthly_limit = monthly_limit
            current_user.budget.current_expense_total = total_spending
            current_user.budget.reset_alert()
        else:
            # Create a new budget instance with the current spending total
            current_user.budget = Budget(
                monthly_limit=monthly_limit,
                current_expense_total=total_spending,
                alert_sent=False,
                user_id=current_user.id,
            )
            db.session.add(current_user.budget)

        db.session.commit()

        # Notify observers via Singleton
        BudgetSingleton.get_instance(current_user.id).update(current_user.budget)

        flash("Budget set successfully!", "success")
        return redirect(url_for("expenses.view_expenses"))
    # Render the set budget template
    return render_template("set_budget.html")


@budget_bp.route("/update", methods=["GET", "POST"])
@login_required
def update_budget():
    """Route to update the budget for the current user."""
    if request.method == "POST":
        monthly_limit = float(request.form["monthly_limit"])

        # Update the budget in the database
        current_user.budget.monthly_limit = monthly_limit
        current_user.budget.reset_alert()  # Reset alert flag
        db.session.commit()

        # Synchronize the singleton with the updated budget
        BudgetSingleton.get_instance(current_user.id).update(current_user.budget)

        flash("Budget updated successfully!", "success")
        return redirect(url_for("expenses.view_expenses"))
    # Render the update budget template
    return render_template("update_budget.html")


@budget_bp.route("/delete", methods=["POST"])
@login_required
def delete_budget():
    """Route to delete the budget for the current user if confirmed."""
    if current_user.budget:
        db.session.delete(current_user.budget)

        # Update the BudgetSingleton
        budget_singleton = BudgetSingleton.get_instance(current_user.id)
        budget_singleton.limit = 0
        budget_singleton.current_total = 0
        budget_singleton.reset_alert()  # Reset any alert states

        # Notify observers
        budget_singleton.notify_observers()

        db.session.commit()
        flash("Budget deleted successfully!", "success")
    # Redirect to the view expenses page
    return redirect(url_for("expenses.view_expenses"))
