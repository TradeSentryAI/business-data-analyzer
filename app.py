from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import logging
from Release.main import analyze_data

app = FastAPI()

# Enable CORS so Wix and other external domains can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), analysis_type: str = Form("monthly")):
    try:
        filename = file.filename.lower()
        upload_path = f"uploads/{filename}"
        os.makedirs("uploads", exist_ok=True)

        # ✅ File type validation
        if not filename.endswith((".csv", ".xlsx", ".xls", ".json")):
            return JSONResponse(
                content={"error": "❌ Only CSV, Excel, or JSON files are supported."},
                status_code=400,
            )

        # ✅ Report type validation
        valid_types = ["weekly", "monthly", "quarterly", "yearly"]
        if analysis_type not in valid_types:
            return JSONResponse(
                content={"error": f"❌ Invalid report type. Choose from: {', '.join(valid_types)}"},
                status_code=400,
            )

        # Save the uploaded file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logging.info(f"📂 Uploaded: {filename} | 📊 Report type: {analysis_type}")

        # Analyze the file
        result = analyze_data(upload_path, analysis_type=analysis_type)

        return {
            "pdf_report": result.get("pdf_report"),
            "chart_image": result.get("chart_image"),
            "summary": result.get("summary", "✅ Analysis completed successfully."),
        }

    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

