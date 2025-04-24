from flask import Flask, request, render_template, redirect, send_file, flash
import os
from werkzeug.utils import secure_filename
from Release.main import analyze_data
from datetime import datetime

app = Flask(__name__)
app.secret_key = '7054a888487090e6fb07fe7e1e0d4708'  # Change in production

# Folder setup
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
RESULT_FOLDER = os.path.join(os.getcwd(), 'reports')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        uploaded_file = request.files.get('file')

        if not uploaded_file or uploaded_file.filename == '':
            flash('❌ No file selected.')
            return redirect(request.url)

        if not allowed_file(uploaded_file.filename):
            flash('❌ Unsupported file type. Please upload CSV, Excel, JSON, or PDF.')
            return redirect(request.url)

        if not report_type:
            flash('❌ Please select a report type.')
            return redirect(request.url)

        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        uploaded_file.save(saved_path)

        try:
            result = analyze_data(saved_path, report_type)

            if isinstance(result, str) and result.endswith('.pdf') and os.path.exists(result):
                return send_file(result, as_attachment=True)
            else:
                flash(result)
                return redirect(request.url)

        except Exception as e:
            flash(f'❌ Unexpected error during analysis: {e}')
            return redirect(request.url)

    # Pass reordered options to the frontend
    report_options = ["weekly", "monthly", "yearly", "quarterly"]
    return render_template('index.html', report_options=report_options)


if __name__ == "__main__":
    app.run(debug=True)
