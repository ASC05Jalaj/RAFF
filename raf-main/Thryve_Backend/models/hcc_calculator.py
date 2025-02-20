from hccpy.hcc import HCCEngine  # Correct import
import pandas as pd

def calculate_raf(data):
    """
    Calculate RAF score based on the input data.
    
    :param data: Dictionary containing the patient data with keys:
                 - 'gender': Gender of the patient ('Male' or 'Female')
                 - 'dob': Date of birth
                 - 'eligibility': Eligibility status
                 - 'diagnosis_codes': List of diagnosis codes
    :return: List of results with RAF score
    """
    # Extract input data
    gender = data.get("gender")
    dob = data.get("dob")
    eligibility = data.get("eligibility")
    diagnosis_codes = data.get("diagnosis_codes", [])
    
    # Initialize HCC Engine (use version '22' or the version you require)
    engine = HCCEngine(version="22")

    # Create patient dataframe
    patient_df = pd.DataFrame([{
        "SEX": gender,
        "DOB": dob,
        "ELIGIBILITY": eligibility,
        "DIAG": diagnosis_codes
    }])

    # Calculate RAF scores
    results = engine.profile(patient_df)

    # Return results as a dictionary
    return results.to_dict(orient="records")

