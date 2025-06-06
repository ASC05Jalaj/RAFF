from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# Load ZIP codes on startup
ZIP_FILE_PATH = "uszips.csv"
zip_data = pd.read_csv(ZIP_FILE_PATH, dtype={"zip": str})
zip_set = set(zip_data["zip"].astype(str))


class ZipCodeRequest(BaseModel):
    zip_code: str


@app.post("/api/validate-zip")
async def validate_zip(data: ZipCodeRequest):
    zip_code = data.zip_code.strip()
    if zip_code in zip_set:
        return {
            "zip_code": zip_code,
            "valid": True,
            "message": "ZIP code is valid."
        }
    else:
        return {
            "zip_code": zip_code,
            "valid": False,
            "message": "ZIP code not found."
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
