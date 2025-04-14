import matplotlib.pyplot as plt
from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        """Custom header for the PDF report."""
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "Business Data Analysis Report", ln=True, align="C")
        self.ln(10)

    def add_section(self, title, content):
        """Adds a section to the PDF."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, content)
        self.ln(5)

    def add_chart(self, image_path, title):
        """Adds a chart image to the PDF."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)
        self.image(image_path, x=10, w=180)  # Adjust size as needed
        self.ln(10)

def generate_chart(df, column, image_path):
    """Generates a chart for a given numerical column."""
    plt.figure(figsize=(8, 4))
    plt.plot(df["Date"], df[column], marker="o", linestyle="-", color="b")
    plt.xlabel("Date")
    plt.ylabel(column)
    plt.title(f"Trend for {column}")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

def generate_pdf_report(file_name, insights, df):
    """Generates a PDF report with insights and charts."""
    pdf = PDFReport()
    pdf.add_page()

    pdf.add_section("Report Summary", "This report provides insights based on the uploaded business data.")

    for section, content in insights.items():
        pdf.add_section(section, content)

    # Generate and add charts for numerical columns
    chart_folder = "charts"
    os.makedirs(chart_folder, exist_ok=True)

    for col in df.select_dtypes(include=['number']).columns:
        image_path = os.path.join(chart_folder, f"{col}.png")
        generate_chart(df, col, image_path)
        pdf.add_chart(image_path, f"Trend for {col}")

    pdf.output(file_name)

