# Name: Yousif Zito
# Date: 2024-11-04
# Purpose: 4SA3 Project - ExpenseAnalyzer Application
# Description: This code is part of the ExpenseAnalyzer application, a web-based
# platform designed for tracking and managing personal or business expenses. The
# application allows users to log expenses, set monthly budget limits,
# categorize spending, and receive alerts when approaching or exceeding their
# budget. Key features include real-time currency conversion via an integrated
# third-party API, visual analytics, and budget tracking. The project
# incorporates multiple design patterns, such as Singleton, Observer, and
# Factory, to ensure modularity, maintainability, and scalability.
# ExpenseAnalyzer is built using Flask with SQLAlchemy ORM, storing data on an
# Azure SQL Database, and providing a user-friendly interface through structured
# routing and templating.
from app import create_app

app = create_app()

# Run the app
if __name__ == "__main__":
    app.run(debug=False)