import pandas as pd
import json
import os
import time
import pdfplumber
from analyzer import generate_report, plot_revenue_trends, preprocess_data
from typing import Dict

def extract_pdf_tables(file_path: str) -> pd.DataFrame:
    with pdfplumber.open(file_path) as pdf:
        tables = []
        for page in pdf.pages:
            extracted = page.extract_table()
            if extracted:
                tables.extend(extracted)

    if not tables:
        raise ValueError("❌ No readable tables found in the PDF.")

    df = pd.DataFrame(tables[1:], columns=tables[0])
    if len(df.columns) < 3:
        raise ValueError("❌ PDF file does not contain enough data columns.")
    return df

def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    column_aliases = {
        'date': ['date', 'order_date', 'transaction_date'],
        'sales': ['sales', 'revenue', 'income', 'turnover', 'total_sales'],
        'expenses': ['expenses', 'cost', 'costs', 'spending', 'expenditure'],
        'customers': ['customers', 'clients', 'buyers', 'users']
    }

    normalized_cols = {col.lower(): col for col in df.columns}
    detected = {}
    for key, aliases in column_aliases.items():
        for alias in aliases:
            if alias in normalized_cols:
                detected[key] = normalized_cols[alias]
                break

    for req in ['date', 'sales', 'expenses']:
        if req not in detected:
            raise ValueError(f"❌ '{req.capitalize()}' column is missing.")
    return detected

def load_data(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(file_path)
    elif ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    elif ext == '.pdf':
        return extract_pdf_tables(file_path)
    else:
        raise ValueError("❌ Unsupported file format.")

def analyze_data(file_path: str, report_type: str) -> str:
    start_time = time.time()
    try:
        raw_data = load_data(file_path)
        raw_data.columns = [col.strip().lower() for col in raw_data.columns]
        print(f"🧾 Cleaned columns: {raw_data.columns.tolist()}")

        column_mapping = detect_columns(raw_data)
        print(f"📌 Column mapping detected: {column_mapping}")
        raw_data.rename(columns=column_mapping, inplace=True)

        processed_data = preprocess_data(raw_data)
        generate_report(processed_data, report_type)
        plot_revenue_trends(processed_data, report_type)

        elapsed = time.time() - start_time
        return f"✅ Analysis complete in {elapsed:.2f} seconds!"
    except Exception as e:
        return f"❌ Error during analysis: {e}"
