from flask import Blueprint, request, jsonify
from models.hcc_calculator import calculate_raf
from utils.validator import validate_input

risk_score_bp = Blueprint("risk_score", __name__)

@risk_score_bp.route("/calculate", methods=["POST"])
def calculate_risk_score():
    data = request.json
    validation_error = validate_input(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        result = calculate_raf(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
