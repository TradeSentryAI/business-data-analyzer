import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ------------------- Utility Functions ------------------- #

def try_parse_date(date):
    try:
        return pd.to_datetime(date, errors='coerce', infer_datetime_format=True)
    except Exception as e:
        print(f"❌ Error parsing date '{date}': {e}")
        return None

def map_column(possible_names, df_columns):
    for name in possible_names:
        for col in df_columns:
            if name in col:
                return col
    return None

def get_output_paths():
    date_str = datetime.today().strftime('%Y-%m-%d')
    report_dir = f'reports/{date_str}'
    chart_dir = f'charts/{date_str}'
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(chart_dir, exist_ok=True)
    return report_dir, chart_dir

# ------------------- Data Preprocessing ------------------- #

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    date_col = map_column(['date', 'timestamp', 'order date', 'sale date'], df.columns)
    sales_col = map_column(['sales', 'revenue', 'amount', 'total'], df.columns)
    expenses_col = map_column(['expenses', 'cost', 'spend', 'expenditure'], df.columns)

    if not date_col:
        raise ValueError("❌ Could not detect a valid 'Date' column.")
    if not sales_col:
        raise ValueError("❌ Could not detect a valid 'Sales' column.")
    if not expenses_col:
        print("⚠️ Expenses column not found. Defaulting to 0.")

    df[date_col] = df[date_col].apply(try_parse_date)
    df.dropna(subset=[date_col], inplace=True)

    df.sort_values(by=date_col, inplace=True)
    df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    df['expenses'] = pd.to_numeric(df.get(expenses_col, 0), errors='coerce').fillna(0)
    df['profit'] = df['sales'] - df['expenses']
    df.rename(columns={date_col: 'date'}, inplace=True)

    return df

# ------------------- Report Generation ------------------- #

def generate_report(data, report_type, filename=None):
    report_dir, _ = get_output_paths()
    if not filename:
        filename = os.path.join(report_dir, 'business_analysis_report.pdf')

    resample_map = {'weekly': 'W', 'monthly': 'M', 'quarterly': 'Q', 'yearly': 'A-DEC'}
    if report_type not in resample_map:
        raise ValueError("❌ Invalid report type. Choose from weekly, monthly, quarterly, or yearly.")

    data_resampled = data.resample(resample_map[report_type], on='date').sum()

    total_revenue = data['sales'].sum()
    total_expenses = data['expenses'].sum()
    profit = total_revenue - total_expenses
    avg_revenue = data['sales'].mean()
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

    # Extra metrics
    highest = data_resampled['sales'].idxmax()
    lowest = data_resampled['sales'].idxmin()
    std_dev = data_resampled['sales'].std()

    # AI Insights
    insights = []
    if profit_margin < 20:
        insights.append("📌 Profit margins are below 20%. Consider adjusting pricing or reducing costs.")
    if len(data_resampled) > 3 and (data_resampled['sales'].pct_change().dropna() < 0).sum() >= 3:
        insights.append("⚠️ Sales have been dropping for multiple periods. Consider launching promotions.")
    if data_resampled['sales'].iloc[-1] > data_resampled['sales'].iloc[0]:
        insights.append("📈 Revenue is increasing over time.")
    elif data_resampled['sales'].iloc[-1] < data_resampled['sales'].iloc[0]:
        insights.append("📉 Revenue has decreased over the observed period.")
    if std_dev > data_resampled['sales'].mean() * 0.5:
        insights.append("📊 Revenue is highly volatile. Consider strategies to stabilize income.")

    # PDF generation
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    font_path = os.path.join("fonts", "NotoSans-Regular.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Noto", font_path))
        font_name = "Noto"
    else:
        font_name = "Helvetica"

    c.setFont(font_name, 16)
    y = height - inch
    c.drawString(inch, y, f"{report_type.capitalize()} Business Report")
    y -= 0.5 * inch

    c.setFont(font_name, 12)
    c.drawString(inch, y, f"💰 Total Revenue: ${total_revenue:,.2f}")
    y -= 0.3 * inch
    c.drawString(inch, y, f"📊 Avg Revenue per {report_type}: ${avg_revenue:,.2f}")
    y -= 0.3 * inch
    c.drawString(inch, y, f"💸 Total Expenses: ${total_expenses:,.2f}")
    y -= 0.3 * inch
    c.drawString(inch, y, f"🏆 Profit Margin: {profit_margin:.2f}%")
    y -= 0.3 * inch
    c.drawString(inch, y, f"🔺 Highest Revenue Period: {highest.strftime('%Y-%m-%d')} (${data_resampled['sales'].max():,.2f})")
    y -= 0.3 * inch
    c.drawString(inch, y, f"🔻 Lowest Revenue Period: {lowest.strftime('%Y-%m-%d')} (${data_resampled['sales'].min():,.2f})")
    y -= 0.3 * inch
    c.drawString(inch, y, f"📈 Revenue Volatility (Std Dev): ${std_dev:,.2f}")
    y -= 0.5 * inch

    if insights:
        c.setFont(font_name, 12)
        c.drawString(inch, y, "🤖 AI Business Recommendations:")
        y -= 0.3 * inch
        for insight in insights:
            c.drawString(inch + 15, y, f"- {insight}")
            y -= 0.25 * inch
            if y < inch:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - inch

    c.save()
    print(f"✅ PDF report saved to {filename}")

# ------------------- Chart Generation ------------------- #

def plot_revenue_trends(data, report_type):
    if 'sales' not in data.columns:
        raise ValueError("❌ 'Sales' column is missing. Ensure your file contains revenue data.")

    resample_map = {'weekly': 'W', 'monthly': 'M', 'quarterly': 'Q', 'yearly': 'A-DEC'}
    if report_type not in resample_map:
        raise ValueError("❌ Invalid report type. Choose from weekly, monthly, quarterly, or yearly.")

    revenue_data = data.resample(resample_map[report_type], on='date').sum()
    _, chart_dir = get_output_paths()
    chart_path = os.path.join(chart_dir, f'sales_{report_type}_plot.png')

    plt.figure(figsize=(10, 6))
    plt.bar(revenue_data.index.strftime('%Y-%m-%d'), revenue_data['sales'], color='teal')
    plt.title(f'Total Sales by {report_type.capitalize()}')
    plt.xlabel(f'{report_type.capitalize()}')
    plt.ylabel('Sales')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    print(f"📊 Revenue trend chart saved to {chart_path}")
