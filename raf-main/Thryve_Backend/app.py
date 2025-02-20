from flask import Flask, request, jsonify
from flask_cors import CORS
from hccpy.hcc import HCCEngine
import pandas as pd
import re

app = Flask(__name__)
CORS(app)

# Initialize HCC Engines for different versions
hcc_engines = {
    "CMS-HCC V22": HCCEngine("22"),
    "CMS-HCC V23": HCCEngine("23"),
    "CMS-HCC V24": HCCEngine("24"),
    "CMS-HCC V28": HCCEngine("28"),
}

# Load ICD-10 descriptions from CSV
icd10_descriptions = {}
coexisting_conditions_map = {}

# Define probability threshold constant
PROBABILITY_THRESHOLD = 70  # 70% threshold

def load_icd10_descriptions():
    global icd10_descriptions
    try:
        df = pd.read_csv("./data/ICD10codes 1.csv", dtype=str)
        if 'DIAG' in df.columns and 'Description' in df.columns:
            icd10_descriptions = dict(zip(df['DIAG'], df['Description']))
        else:
            print("CSV file missing required columns: 'DIAG' and 'Description'")
    except Exception as e:
        print(f"Error loading ICD-10 descriptions: {e}")

def load_coexisting_conditions():
    global coexisting_conditions_map
    try:
        df = pd.read_csv("./data/ICD to HCC Mapping 2025 - With co-exist.csv", dtype=str)
        coexisting_conditions_map = df.set_index('Diagnosis_Code').to_dict()
    except Exception as e:
        print(f"Error loading coexisting conditions: {e}")

# Load data at startup
load_icd10_descriptions()
load_coexisting_conditions()

def parse_coexisting_diagnoses(coexist_str):
    if not isinstance(coexist_str, str):
        return []
    
    # Parse string like "M069 (25%); M08859 (18%)"
    pattern = r'([A-Z0-9]+)\s*\((\d+)%\)'
    matches = re.findall(pattern, coexist_str)
    # Filter conditions with probability >= PROBABILITY_THRESHOLD
    return [{"code": code, "probability": int(prob)} 
            for code, prob in matches 
            if int(prob) >= PROBABILITY_THRESHOLD]

def get_potential_conditions(diagnosis_code, hcc_engine, profile):
    try:
        df = pd.read_csv("./data/ICD to HCC Mapping 2025 - With co-exist.csv")
        if diagnosis_code not in df['Diagnosis_Code'].values:
            return []
        
        row = df[df['Diagnosis_Code'] == diagnosis_code].iloc[0]
        coexisting = row['Potential Co-existing Diagnoses']
        # Only get conditions that meet the probability threshold
        potential_conditions = parse_coexisting_diagnoses(coexisting)
        
        results = []
        for condition in potential_conditions:
            # Calculate risk score for potential diagnosis
            test_profile = profile.copy()
            test_profile['dx_lst'] = [condition['code']]
            risk_profile = hcc_engine.profile(**test_profile)
            hcc_map = risk_profile.get('hcc_map', {})
            
            if condition['code'] in hcc_map:
                hcc_code = hcc_map[condition['code']]
                if isinstance(hcc_code, list):
                    hcc_code = hcc_code[0]
                
                # Get description from ICD-10 mapping
                description = icd10_descriptions.get(condition['code'], "No description available")
                
                results.append({
                    'diagnosisCode': condition['code'],
                    'description': description,
                    'hccCode': f"{hcc_code}",
                    'rafScore': round(risk_profile['risk_score'], 3),
                    'probability': condition['probability']
                })
        
        return results
    except Exception as e:
        print(f"Error getting potential conditions: {e}")
        return []

@app.route('/api/risk-score', methods=['POST'])
# In app.py, modify the calculate_risk_score function:

def calculate_risk_score():
    data = request.get_json()

    diagnosis_codes = data.get('diagnosis_code', '').split(',')
    gender = data.get('gender', '').lower()
    age = data.get('age', '')
    eligibility = data.get('eligibility', '')
    model_name = data.get('model_name', 'CMS-HCC V28')

    if not diagnosis_codes or not gender or not age or not eligibility or not model_name:
        return jsonify({"error": "All fields are required"}), 400

    if model_name not in hcc_engines:
        return jsonify({"error": f"Model {model_name} is not supported"}), 400

    try:
        hcc_engine = hcc_engines[model_name]
        results = []

        # Calculate main results
        for diagnosis_code in diagnosis_codes:
            # Create individual profile for each diagnosis code
            individual_profile = {
                "dx_lst": [diagnosis_code],  # Only include current diagnosis code
                "age": int(age),
                "sex": "M" if gender == "male" else "F",
                "elig": eligibility
            }

            # Get individual risk profile
            individual_risk_profile = hcc_engine.profile(**individual_profile)
            individual_risk_score = individual_risk_profile['risk_score']
            hcc_map = individual_risk_profile.get('hcc_map', {})

            icd_description = icd10_descriptions.get(diagnosis_code, "No description available")

            if diagnosis_code in hcc_map:
                hcc_codes = hcc_map[diagnosis_code]
                if not isinstance(hcc_codes, list):
                    hcc_codes = [hcc_codes]

                for hcc_code in hcc_codes:
                    try:
                        hcc_description = hcc_engine.describe_hcc(hcc_code)
                        hcc_desc = hcc_description['description']
                    except Exception as e:
                        hcc_desc = f"Error fetching description: {str(e)}"

                    risk_score_detail = {
                        "DIAG": diagnosis_code,
                        "SEX": gender.capitalize(),
                        "ICD_Description": icd_description,
                        "Age": age,
                        "Eligibility": eligibility,
                        "Risk_Score": round(individual_risk_score, 3),
                        "HCC_Code": hcc_code,
                        "HCC_Description": hcc_desc
                    }
                    results.append(risk_score_detail)
            else:
                results.append({
                    "DIAG": diagnosis_code,
                    "SEX": gender.capitalize(),
                    "ICD_Description": icd_description,
                    "Age": age,
                    "Eligibility": eligibility,
                    "Risk_Score": 0,
                    "HCC_Code": "N/A",
                    "HCC_Description": "No HCC code mapped"
                })

        # Calculate potential conditions
        # Create full profile for potential conditions
        full_profile = {
            "dx_lst": diagnosis_codes,
            "age": int(age),
            "sex": "M" if gender == "male" else "F",
            "elig": eligibility
        }

        potential_conditions = []
        for diagnosis_code in diagnosis_codes:
            conditions = get_potential_conditions(diagnosis_code, hcc_engine, full_profile)
            potential_conditions.extend(conditions)

        return jsonify({
            'results': results,
            'potentialConditions': potential_conditions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demographic-risk-score', methods=['POST'])
def calculate_demographic_risk_score():
    data = request.get_json()

    age = data.get('age', '')
    gender = data.get('gender', '').lower()
    eligibility = data.get('eligibility', '')
    model_name = data.get('model_name', 'CMS-HCC V28')

    if not age or not gender or not eligibility or not model_name:
        return jsonify({"error": "All fields are required"}), 400

    if model_name not in hcc_engines:
        return jsonify({"error": f"Model {model_name} is not supported"}), 400

    try:
        hcc_engine = hcc_engines[model_name]

        profile = {
            "dx_lst": [],
            "age": int(age),
            "sex": "M" if gender == "male" else "F",
            "elig": eligibility
        }

        risk_profile = hcc_engine.profile(**profile)
        demographic_risk_score = risk_profile["risk_score"]

        return jsonify({
            "demographicRiskFactor": round(demographic_risk_score, 3),
            "model_name": model_name
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/icd-suggestions', methods=['GET'])
def icd_suggestions():
    query = request.args.get('query', '')
   
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
 
    suggestions = []
   
    try:
        # Search for matching ICD-10 codes in the pre-loaded descriptions dataset
        for code in icd10_descriptions.keys():
            # Check if the query matches the code (case-insensitive)
            if query.lower() in code.lower():
                suggestions.append({"code": code})
 
    except Exception as e:
        return jsonify({"error": f"Error fetching ICD-10 suggestions: {str(e)}"}), 500
   
    return jsonify(suggestions), 200

if __name__ == '__main__':
    app.run(debug=True)