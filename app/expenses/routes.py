from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..currency_loader import load_currency_data
from ..utils import (
    get_currency_conversion,
    get_monthly_data,
    get_category_data,
    create_pie_chart,
    create_bar_chart,
)
from ..factories.expense_factory import ExpenseFactory
from ..models import BudgetSingleton, Expense
from ..extensions import db
from flask_login import login_required, current_user

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/view", methods=["GET", "POST"])
@login_required
def view_expenses():
    """Route to view expenses for the current user. Render the view expenses template."""
    # Load BudgetSingleton with current user's budget values if they exist
    budget_singleton = BudgetSingleton.get_instance(current_user.id)
    budget = current_user.budget

    if budget:
        # Ensure BudgetSingleton reflects the latest state of the budget
        budget_singleton.update(budget)

    # Fetch data for charts only if there are expenses
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    has_expenses = len(expenses) > 0
    total = sum(expense.amount for expense in expenses)

    currency_data = load_currency_data()
    # Default values
    conversion_rate = None
    from_currency = request.form.get("from_currency", "CAD")
    to_currency = request.form.get("to_currency", "USD")

    # Fetch conversion rate if form is submitted with currencies
    if request.method == "POST" and from_currency and to_currency:
        conversion_rate = get_currency_conversion(from_currency, to_currency)

    # Generate chart images as base64 strings only if there are expenses
    bar_chart = pie_chart = None
    if has_expenses:
        monthly_data = get_monthly_data(current_user.id)
        category_data = get_category_data(current_user.id)
        # Generate chart images as base64 strings
        pie_chart = create_pie_chart(category_data)
        bar_chart = create_bar_chart(*monthly_data)

    # Render the view expenses template with the data
    return render_template(
        "view_expenses.html",
        expenses=expenses,
        total=total,
        conversion_rate=conversion_rate,
        currency_data=currency_data,
        from_currency=from_currency,
        to_currency=to_currency,
        current_spending=budget_singleton.current_total,
        budget_limit=budget_singleton.limit,
        pie_chart=pie_chart,
        bar_chart=bar_chart,
        has_expenses=has_expenses,
    )


@expenses_bp.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    """Route to delete an expense by ID for the current user."""
    if current_user.username == "Guest":
        flash("Guest users cannot delete expenses.", "warning")
        return redirect(url_for("expenses.view_expenses"))

    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        flash("You do not have permission to delete this expense.", "danger")
        return redirect(url_for("expenses.view_expenses"))

    if current_user.budget:
        # Use update_total to ensure database updates and observer notifications
        current_user.budget.update_total(-expense.amount)

    # Delete the expense
    db.session.delete(expense)
    db.session.commit()

    flash("Expense deleted successfully!", "success")
    # Redirect to the view expenses page after deleting the expense for the user successfully
    return redirect(url_for("expenses.view_expenses"))


@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():
    """Route to add an expense for the current user. Render the add expense template."""
    if current_user.username == "Guest":
        flash("Guest users cannot add new expenses.", "warning")
        return redirect(url_for("expenses.view_expenses"))

    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        date = request.form["date"]
        expense = ExpenseFactory.create_expense(name, amount, category, date, user_id=current_user.id)
        db.session.add(expense)

        if current_user.budget:
            # Use update_total to ensure database updates and observer notifications
            current_user.budget.update_total(amount)

        db.session.commit()

        flash("Expense added successfully!", "success")
        # Redirect to the view expenses page after adding the expense for the user successfully
        return redirect(url_for("expenses.view_expenses"))
    # Render the add expense template for the user to add a new expense to their list of expenses in the database
    return render_template("add_expense.html")


@expenses_bp.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    """Route to edit an expense by ID for the current user. Render the edit expense template."""
    expense = Expense.query.get_or_404(expense_id)

    if request.method == "POST":
        old_amount = expense.amount
        new_amount = float(request.form["amount"])
        expense.name = request.form["name"]
        expense.amount = new_amount
        expense.category = request.form["category"]
        expense.date = request.form["date"]
        db.session.commit()

        # Update the budget with the difference in amount
        if current_user.budget:
            amount_difference = new_amount - old_amount
            current_user.budget.update_total(amount_difference)

            # Sync the singleton with the updated budget
            BudgetSingleton.get_instance(current_user.id).update(current_user.budget)

        flash("Expense updated successfully!", "success")
        # Redirect to the view expenses page after updating the expense for the user
        return redirect(url_for("expenses.view_expenses"))
    # Render the edit expense template with the expense data to be edited by the user
    return render_template("edit_expense.html", expense=expense)


@expenses_bp.route("/delete_all", methods=["POST"])
@login_required
def delete_all_expenses():
    """Route to delete all expenses for the current user if confirmed."""
    if current_user.username == 'Guest':
        flash('Guest users cannot delete expenses.', 'warning')
        return redirect(url_for('expenses.view_expenses'))
    if current_user.budget:
        # Reset the current expense total in the budget
        current_user.budget.current_expense_total = 0
        db.session.commit()

        # Notify observers via Singleton
        BudgetSingleton.get_instance(current_user.id).update(current_user.budget)

    # Delete all expenses for the user
    Expense.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash("All expenses deleted successfully!", "success")
    # Redirect to the view expenses page after deleting all expenses for the user
    return redirect(url_for("expenses.view_expenses"))