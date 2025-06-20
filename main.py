from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
import pandas as pd
from typing import Literal
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
 
# Load ZIP codes on startup
# ZIP_FILE_PATH = "uszips.csv"
ZIP_FILE_PATH = "Zipcodes.csv"
# zip_data = pd.read_csv(ZIP_FILE_PATH, dtype={"zip": str})
# zip_set = set(zip_data["zip"].astype(str))
df=pd.read_csv(ZIP_FILE_PATH)
 
class ZipCodeRequest(BaseModel):
    zip_code: str
    gender:Literal["Male","Female","Others"]=Field(default="M")
 
 
def getPlansByZipCodes(zipcode:str):
    try:
        return df[df["ZIP Code"]==int(zipcode)].iloc[0].to_dict()
    except (IndexError,Exception) as e:
        return {}
 
@app.post("/api/validate-zip")
async def validate_zip(data: ZipCodeRequest):
    plans = [key for key, value in getPlansByZipCodes(data.zip_code.strip()).items() if value == "Yes"]

    if data.gender != "Female" and "SCAN Inspired" in plans:
        plans.remove("SCAN Inspired")
    if data.gender != "Others" and "SCAN Affirm" in plans:
        plans.remove("SCAN Affirm")

    if plans:
        return {
            "response": {
                "message": "ZIP code is valid."
            },
            "data": {
                "plans": plans
            }
        }
    else:
        return {
            "response": {
                "message": "ZIP code not found or no matching plans available."
            },
            "data": {
                "plans": []
            }
        }

@app.get("/")
async def root():
    return {"message": "ZIP Code Validator API is running", "status": "healthy"}
 
 
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ZIP Code Validator API"}


if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI ZIP Code Validator API is running on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
