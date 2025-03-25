from app.models import Expense
from app.multiton import ExpenseCategoryMultiton


# class ExpenseFactory:
#     """
#     Factory pattern for creating new expense instances based on provided attributes.
#     """

#     @staticmethod
#     def create_expense(name, amount, category, date, user_id):
#         """
#         Factory method for generating a new expense entry.

#         :param name: str - the expense name
#         :param amount: float - the expense amount
#         :param category: str - the expense category
#         :param date: str - the expense date
#         :param user_id: int - ID of the user who created the expense
#         :return: Expense instance
#         """
#         category_instance = ExpenseCategoryMultiton(category)
#         return Expense(
#             name=name,
#             amount=amount,
#             category=category_instance.category,
#             date=date,
#             user_id=user_id,
#         )

class ExpenseFactory:
    """
    Factory pattern for creating new expense instances.
    """

    @staticmethod
    def create_expense(name, amount, category, date, user_id):
        """ Create an expense instance with category-specific behavior. """
        category_instance = ExpenseCategoryMultiton(category)
        tax = category_instance.calculate_tax(amount)  # Apply category-based tax
        total_amount = amount + tax  # Include tax in total cost

        return Expense(
            name=name,
            amount=total_amount,
            category=category_instance.name,
            date=date,
            user_id=user_id,
        )
