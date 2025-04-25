import os
import time
import pandas as pd
from Release.analyzer import preprocess_data, generate_report, plot_revenue_trends

def analyze_data(filepath: str, report_type: str = 'monthly') -> dict:
    start_time = time.time()
    print(f"📂 Processing file: {filepath}")

    try:
        # Read the uploaded file
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            return {"error": "❌ Unsupported file type. Please upload a CSV or Excel file."}
    except Exception as e:
        return {"error": f"❌ Failed to read file: {e}"}

    try:
        # Run preprocessing and analysis
        df = preprocess_data(df)
        plot_revenue_trends(df, report_type)
        generate_report(df, report_type)
    except Exception as e:
        return {"error": f"❌ Error during analysis: {e}"}

    # Get output paths
    report_dir, chart_dir = get_output_paths()
    pdf_path = os.path.join(report_dir, "business_analysis_report.pdf")
    chart_path = os.path.join(chart_dir, f"sales_{report_type}_plot.png")

    # Calculate processing time
    end_time = time.time()
    duration = end_time - start_time

    return {
        "summary": f"✅ Analysis complete. Time taken: {duration:.2f} seconds.",
        "pdf_report": pdf_path,
        "chart_image": chart_path
    }
