from flask import Flask, request, send_file, render_template, redirect, url_for
from pdf2docx import Converter
from pdf2image import convert_from_path
import pytesseract
from docx import Document
import fitz  # PyMuPDF
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# Page individuelle pour chaque outil
@app.route('/pdf-to-word')
def pdf_to_word_page():
    return render_template('pdf_to_word.html')

@app.route('/pdf-to-word-ocr')
def pdf_to_word_ocr_page():
    return render_template('pdf_to_word_ocr.html')

@app.route('/pdf-to-pdf-ocr')
def pdf_to_pdf_ocr_page():
    return render_template('pdf_to_pdf_ocr.html')

@app.route('/pdf-editor')
def pdf_editor_page():
    return render_template('pdf_editor.html')

# Traitements
@app.route('/convert/pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return "Aucun fichier reçu", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = input_path.replace('.pdf', '.docx')
    file.save(input_path)

    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Erreur conversion PDF → Word : {str(e)}", 500


@app.route('/convert/pdf-to-word-ocr', methods=['POST'])
def convert_pdf_to_word_ocr():
    if 'file' not in request.files:
        return "Aucun fichier reçu", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = input_path.replace('.pdf', '-ocr.docx')
    file.save(input_path)

    try:
        images = convert_from_path(input_path)
        doc = Document()

        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='eng+fra')
            doc.add_paragraph(text)
            if i < len(images) - 1:
                doc.add_page_break()

        doc.save(output_path)
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Erreur OCR → Word : {str(e)}", 500


@app.route('/convert/pdf-to-pdf-ocr', methods=['POST'])
def convert_pdf_to_pdf_ocr():
    if 'file' not in request.files:
        return "Aucun fichier reçu", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = input_path.replace('.pdf', '-ocr.pdf')
    temp_folder = os.path.join(UPLOAD_FOLDER, 'ocr_pages')
    os.makedirs(temp_folder, exist_ok=True)
    file.save(input_path)

    try:
        images = convert_from_path(input_path)
        page_paths = []

        for i, image in enumerate(images):
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang='eng+fra', extension='pdf')
            page_path = os.path.join(temp_folder, f'page_{i + 1}.pdf')
            with open(page_path, 'wb') as f:
                f.write(pdf_bytes)
            page_paths.append(page_path)

        final_pdf = fitz.open()
        for path in page_paths:
            with fitz.open(path) as page_doc:
                final_pdf.insert_pdf(page_doc)
        final_pdf.save(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Erreur OCR PDF → PDF : {str(e)}", 500


# Pour dev local uniquement
#if __name__ == '__main__':
#   app.run(debug=True)
