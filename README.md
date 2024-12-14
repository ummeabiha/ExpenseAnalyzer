# ExpenseAnalyzer

ExpenseAnalyzer is a web-based application designed to help users track and manage their finances effectively. Users can log expenses, set budgets, and monitor their financial health with real-time updates and insights. Key features include adding and categorizing expenses, setting monthly budget limits, receiving budget alerts, and performing real-time currency conversion using an integrated third-party API.

## Features

- Log and categorize expenses
- Set and update monthly budget limits
- Receive alerts when approaching or exceeding budget limits
- Visual analytics for expense tracking and budget management
- Real-time currency conversion using the ExchangeRate API

## Technologies Used

- Python (Flask) for the backend
- SQLAlchemy for ORM and database management
- Azure SQL Database for data storage
- HTML/CSS and Bootstrap for frontend design
- ExchangeRate API for real-time currency conversion

## Prerequisites

- Python 3.10 or above
- Virtual Environment (optional but recommended)

## Getting Started

### 1. Set up a Virtual Environment (optional but recommended)

#### Using `venv`

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

### 3. Install Dependencies

Install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

#### For Linux Users

Create a `configExpenseAnalyzer.json` file in the `/etc/` directory and add the following environment variables:

```json
{
   "SECRET_KEY": "your_secret_key",
   "SQLALCHEMY_DATABASE_URI": "your_database_url",
   "EMAIL_USER": "your_email",
   "EMAIL_PASS": "your_email_app_password",
	"API_KEY": "your_exchangerate_api_key"
}
```

- Replace`your_secret_key`  with your Flask application's secret key for session management and security.
- Replace`your_database_uri` with the database connection URI for your Azure SQL Database or SQLite. For SQLite, this might look like `sqlite:///path_to_db`.db.
- Replace`your_email` and`your_email_password` with the email and app-specific password for the email service used to send notifications (e.g., Gmail, Outlook).
- Replace`your_exchangerate_api_key` with your API key from the [ExchangeRate-API](https://www.exchangerate-api.com/).

#### For Windows 

Place the `configExpenseAnalyzer.json` file in the `instance` folder under the ExpenseAnalyzer directory. Ensure the application code references this path for Windows systems.

### 5. Run the Application

You have two options to run the application:

#### Option 1: Using `flask run`

1. Set the Flask app environment variable:

   ```bash
   export FLASK_APP=run.py
   ```

   On Windows:

   ```bash
   set FLASK_APP=run.py
   ```

2. Run the application:

   ```bash
   flask run
   ```

#### Option 2: Using `python run.py`

Alternatively, you can directly run the app by executing:

```bash
python3 run.py
```

### 6. Access the Application

Open your web browser and navigate to `http://127.0.0.1:5000` to access the ExpenseAnalyzer application.

## Usage

- **Add Expenses** : Navigate to the "Add New Expense" section to log expenses.
- **Set Budget** : Set your monthly budget in the "Set Budget" section.
- **Currency Conversion** : Use the currency conversion feature to perform real-time conversions.
- **View Reports** : Access visual reports for monthly spending and category-based analysis.

## Project Structure

The directory structure of the project is as follows:

```text
ExpenseAnalyzer/
|   requirements.txt          # Lists Python packages required to run the application
|   run.py                    # Entry point for running the application
|   README.md                 # Project documentation and instructions
|
+---instance                  # Folder for instance-specific configuration files
|       configExpenseAnalyzer.json # JSON file for storing environment variables (not included in version control)
|
\---app                       # Main application folder containing configurations, modules, and routes
    |   config.py             # Configuration file for environment variables, database URI, and other settings
    |   currency_loader.py    # Module to load currency data from the YAML file
    |   extensions.py         # Initializes extensions like SQLAlchemy, Mail, Bcrypt, etc.
    |   models.py             # Defines the database models (User, Expense, Budget) used in the app
    |   multiton.py           # Implements Multiton pattern for managing unique instances of expense categories
    |   observers.py          # Defines observer classes for handling notifications and logging (AlertObserver, LoggingObserver)
    |   utils.py              # Utility functions for tasks like currency conversion, email sending, and data processing
    |   __init__.py           # Initializes the Flask app and registers configurations and blueprints
    |
    +---api                   # Blueprint for API-related routes
    |       routes.py         # Handles API routes for currency conversion and forecast
    |
    +---auth                  # Blueprint for authentication (user login, registration) routes
    |       forms.py          # Defines authentication forms for user input
    |       routes.py         # Manages routes for login, registration, and session handling
    |
    +---budget                # Blueprint for budget-related routes
    |       routes.py         # Handles routes for setting, updating, and deleting budget limits
    |
    +---data                  # Folder for storing data files
    |       currencies.yml    # YAML file containing country names and corresponding currency codes
    |
    +---expenses              # Blueprint for expense-related routes
    |       routes.py         # Manages routes for adding, viewing, editing, and deleting expenses
    |
    +---factories             # Contains factory classes for object creation
    |       expense_factory.py # Factory class to create Expense instances based on user input
    |
    +---main                  # Blueprint for main app routes (e.g., homepage)
    |       routes.py         # Manages main routes like the home page
    |
    +---static                # Directory containing static assets for the application.
    |       style.css         # Main stylesheet with custom CSS styles for ExpenseAnalyzer.
    |       favicon.png       # Favicon icon displayed in the browser tab.
    |       icon.128x128.png  # Shortcut icon for speed dial or bookmarks.
    |       logo.512x512.png  # Logo image used on login and registration pages.
    |
    |   +---js                # Directory for JavaScript files within static assets.
    |       interaction_handler.js  # JavaScript for handling flash message animations, form submissions, and preventing duplicate submissions.
    |
    \---templates             # Folder containing HTML templates for the app
            add_expense.html      # Template for adding a new expense
            base.html             # Base template with shared layout elements
            edit_expense.html     # Template for editing an existing expense
            login.html            # Template for user login page
            register.html         # Template for user registration page
            set_budget.html       # Template for setting a new budget
            update_budget.html    # Template for updating an existing budget
            view_expenses.html    # Template for viewing and managing expenses
```

## Design Patterns

ExpenseAnalyzer leverages several design patterns to improve maintainability and scalability:

- Factory Pattern in `ExpenseFactory`: Used to create expense instances efficiently.
- Singleton Pattern in `BudgetSingleton`: Ensures a single source of truth for budget management.
- Observer Pattern with `AlertObserver` and `LoggingObserver` in `observers.py`: Handles alerts and logs actions when budget thresholds are reached or exceeded.
- Multiton Pattern in `ExpenseCategoryMultiton`: Maintains consistency across expense categories.

## License

This project is licensed under the GPL-3.0 License.