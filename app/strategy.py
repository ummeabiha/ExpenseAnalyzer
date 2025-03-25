class ExpenseCategory:
    """ Abstract category class defining category-specific behaviors. """
    def __init__(self, name):
        self.name = name

    def calculate_tax(self, amount):
        """ Default tax calculation (can be overridden). """
        return amount * 0.1  # Default 10% tax

class FoodExpense(ExpenseCategory):
    def calculate_tax(self, amount):
        return amount * 0.05  # 5% tax for food items

class TravelExpense(ExpenseCategory):
    def calculate_tax(self, amount):
        return amount * 0.15  # 15% tax for travel

class EntertainmentExpense(ExpenseCategory):
    def calculate_tax(self, amount):
        return amount * 0.2  # 20% tax for entertainment
