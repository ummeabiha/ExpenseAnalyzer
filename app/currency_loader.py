import yaml

def load_currency_data():
    """Load currency data from YAML, sorted by country name."""
    with open("app/data/currencies.yml", "r") as file:
        currency_data = yaml.safe_load(file)
    # Sort currencies by country name
    currency_data["currencies"].sort(key=lambda x: x["country"])
    # Return the sorted currency data dictionary for processing in the application
    return currency_data