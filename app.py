from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
import os
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Beschränkung auf 16 MB


def safe_join(directory, filename):
    filepath = os.path.join(directory, filename)
    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        abort(403)
    return filepath


def get_document_text(file_path):
    doc = Document(file_path)
    return '\n'.join([p.text for p in doc.paragraphs])


def save_document_text(file_path, content):
    doc = Document()
    for line in content.split('\n'):
        doc.add_paragraph(line)
    doc.save(file_path)


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
    elif filename.lower().endswith('.doc') or filename.lower().endswith('.docx'):
        doc_content = get_document_text(file_path)
        return render_template('edit_doc.html', filename=filename, doc_content=doc_content)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/edit/<filename>')
def edit_file(filename):
    file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    doc_content = get_document_text(file_path)
    return render_template('edit_doc.html', filename=filename, doc_content=doc_content)


@app.route('/save/<filename>', methods=['POST'])
def save_file(filename):
    file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    content = request.form['content']
    save_document_text(file_path, content)
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and (file.filename.lower().endswith('.pdf') or
                 file.filename.lower().endswith('.doc') or
                 file.filename.lower().endswith('.docx')):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    else:
        return 'Nur PDF, DOC und DOCX Dateien sind erlaubt', 400


if __name__ == '__main__':
    app.run(debug=True)
