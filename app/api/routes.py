from flask import Blueprint, jsonify, render_template, request
from ..currency_loader import load_currency_data
from ..utils import get_currency_conversion, get_cad_usd_forecast

api_bp = Blueprint("api", __name__)

@api_bp.route("/convert_currency")
def convert_currency():
    """Route to convert currency and render the view expenses template."""
    from_currency = request.form.get("from_currency", "CAD")
    to_currency = request.form.get("to_currency", "USD")

    # Fetch conversion rate if a conversion request was submitted
    conversion = None
    if request.method == "POST":
        if from_currency and to_currency:
            conversion = get_currency_conversion(from_currency, to_currency)

    # Render the template with the conversion rate and selected currencies
    return render_template(
        "view_expenses.html",
        conversion_rate=conversion,
        selected_from=from_currency,
        selected_to=to_currency,
        currency_data=load_currency_data(),  # Ensure currency data is loaded
    )

@api_bp.route("/get_forecast")
def get_forecast():
    """Route to get the CAD-USD forecast. Returns a JSON response."""

    forecast = get_cad_usd_forecast()

    # Handle cases if forecast returned an error
    if isinstance(forecast, str) and "Error" in forecast:
        return jsonify({"error": forecast}), 400
    elif forecast == "Currency not found!":
        return jsonify({"error": "Forecast data not available"}), 404

    return jsonify({"forecast": forecast})
