from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/pdf'


def safe_join(directory, filename):
    filepath = os.path.join(directory, filename)
    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        abort(403)
    return filepath


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


@app.route('/view/<filename>')
def view_file(filename):
    file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    if filename.lower().endswith('.pdf'):
        return render_template('view_pdf.html', filename=filename)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=6060)
