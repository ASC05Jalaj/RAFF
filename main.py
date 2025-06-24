from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import pandas as pd
import os
 
PORT = int(os.environ.get("PORT", 5000))
 
app = FastAPI()
 
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Load ZIP code data
ZIP_FILE_PATH = "Zipcodes.csv"
df = pd.read_csv(ZIP_FILE_PATH)
 
# --- Models ---
class ZipCodeOnlyRequest(BaseModel):
    zip_code: str
 
class ZipCodeWithGenderRequest(BaseModel):
    zip_code: str
    gender: Literal["Male", "Female", "Others"] = Field(default="Male")
 
# --- Utility Function ---
def getPlansByZipCode(zipcode: str):
    try:
        return df[df["ZIP Code"] == int(zipcode)].iloc[0].to_dict()
    except (IndexError, Exception):
        return {}
 
# --- Endpoints ---
 
# Step 1: ZIP Validation Only
@app.post("/api/validate-zip")
async def validate_zip(data: ZipCodeOnlyRequest):
    plans_data = getPlansByZipCode(data.zip_code.strip())
    if plans_data:
        return {
            "response": {
                "message": "ZIP code is valid."
            }
        }
    else:
        return {
            "response": {
                "message": "ZIP code not found."
            }
        }
 
# Step 2: ZIP + Gender-Based Plan Retrieval
@app.post("/api/get-plans")
async def get_plans(data: ZipCodeWithGenderRequest):
    plans_data = getPlansByZipCode(data.zip_code.strip())
   
    if not plans_data:
        return {
            "response": {
                "message": "ZIP code not found."
            },
            "data": {
                "plans": []
            }
        }
 
    # Filter plan names that are "Yes"
    plans = [key for key, value in plans_data.items() if value == "Yes"]
 
    # Apply gender-based filtering
    if data.gender != "Female" and "SCAN Inspired" in plans:
        plans.remove("SCAN Inspired")
    if data.gender != "Others" and "SCAN Affirm" in plans:
        plans.remove("SCAN Affirm")
 
    return {
        "response": {
            "message": "Plans retrieved successfully."
        },
        "data": {
            "plans": plans
        }
    }
 
@app.get("/")
async def root():
    return {"message": "ZIP Code Validator API is running", "status": "healthy"}
 
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ZIP Code Validator API"}
 
# Entry point
if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI ZIP Code Validator API is running on port {PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT)