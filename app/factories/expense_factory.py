# from app.models import Expense
# from app.multiton import ExpenseCategoryMultiton


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

from app.models import Expense

class ExpenseFactory:
    """
    Factory pattern for creating new expense instances based on provided attributes.
    """

    @staticmethod
    def create_expense(name, amount, category, date, user_id):
        """
        Factory method for generating a new expense entry.

        :param name: str - the expense name
        :param amount: float - the expense amount
        :param category: str - the expense category
        :param date: str - the expense date
        :param user_id: int - ID of the user who created the expense
        :return: Expense instance
        """
        return Expense(
            name=name,
            amount=amount,
            category=category,  # Directly use the category string
            date=date,
            user_id=user_id,
        )
