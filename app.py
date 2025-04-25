from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging
from Release.main import analyze_data

app = FastAPI()

# Optional: Logging for debugging
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the HTML form on the root URL
@app.get("/", response_class=HTMLResponse)
async def serve_form():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Upload Business Data</title>
    </head>
    <body>
        <h2>📁 Upload Your Business Data</h2>
        <form action="http://localhost:8000/analyze/" method="POST" enctype="multipart/form-data">
            <label for="file">Choose a file:</label>
            <input type="file" name="file" id="file" accept=".csv,.xlsx,.xls,.json" required><br><br>

            <label for="report_type">Select Report Type:</label>
            <select name="report_type" id="report_type" required>
                <option value="weekly">Weekly</option>
                <option value="monthly" selected>Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
            </select><br><br>

            <button type="submit">Upload and Analyze</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/analyze/")
async def analyze_file(file: UploadFile = File(...), report_type: str = Form("monthly")):
    try:
        filename = file.filename.lower()
        upload_path = f"uploads/{filename}"
        os.makedirs("uploads", exist_ok=True)

        # ✅ File type validation
        if not filename.endswith((".csv", ".xlsx", ".xls")):
            return {"error": "❌ Only CSV or Excel files are supported."}

        # ✅ Report type validation
        valid_report_types = ["weekly", "monthly", "quarterly", "yearly"]
        if report_type not in valid_report_types:
            return {"error": f"❌ Invalid report type. Choose from: {', '.join(valid_report_types)}"}

        # Save file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logging.info(f"📂 Uploaded: {filename} | 📊 Report type: {report_type}")

        # Analyze
        result = analyze_data(upload_path, report_type=report_type)

        return {
            "pdf_report": result.get("pdf_report"),
            "chart_image": result.get("chart_image"),
            "summary": result.get("summary", "✅ Analysis completed successfully."),
        }

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return {"error": str(e)}

