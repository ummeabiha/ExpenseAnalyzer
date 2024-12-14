class ExpenseCategoryMultiton:
    """
    Multiton class to create only one instance of a class per category name.
    """
    _instances = {}

    def __new__(cls, category):
        """ Create a new instance of the class if it doesn't exist for the given category."""
        if category not in cls._instances: # Check if an instance already exists for the category.
            cls._instances[category] = super().__new__(cls) # Create a new instance if not found for the category name.
            cls._instances[category].category = category # Set the category name for the instance.
        return cls._instances[category] # Return the instance for the category name.

    def __init__(self, category):
        """ Initialize the category attribute for the instance."""
        self.category = category # Set the category attribute for the instance.
