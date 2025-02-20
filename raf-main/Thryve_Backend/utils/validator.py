def validate_input(data):
    if not data.get("gender"):
        return "Gender is required."
    if not data.get("dob"):
        return "Date of Birth is required."
    if not data.get("eligibility"):
        return "Eligibility is required."
    if not isinstance(data.get("diagnosis_codes", []), list):
        return "Diagnosis codes must be a list."
    return None
