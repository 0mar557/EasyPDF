from flask import Flask, request, send_file, render_template
from pdf2docx import Converter
from pdf2image import convert_from_path
import pytesseract
from docx import Document
import fitz  # PyMuPDF
import os

app = Flask(__name__)

# Configuration des chemins
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

POPPLER_PATH = r"C:\poppler\Library\bin"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/convert/pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    """Conversion directe PDF → DOCX (texte éditable, pas d'OCR)"""
    if 'file' not in request.files:
        return "Aucun fichier reçu sous la clé 'file'", 400

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
        return f"Erreur lors de la conversion PDF → Word : {str(e)}", 500


@app.route('/convert/pdf-to-word-ocr', methods=['POST'])
def convert_pdf_to_word_ocr():
    """OCR : PDF image → texte brut → Word éditable"""
    if 'file' not in request.files:
        return "Aucun fichier reçu sous la clé 'file'", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = input_path.replace('.pdf', '-ocr.docx')
    file.save(input_path)

    try:
        images = convert_from_path(input_path, poppler_path=POPPLER_PATH)
        doc = Document()

        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='eng+fra')
            doc.add_paragraph(text)
            if i < len(images) - 1:
                doc.add_page_break()

        doc.save(output_path)
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Erreur OCR vers Word : {str(e)}", 500


@app.route('/convert/pdf-to-pdf-ocr', methods=['POST'])
def convert_pdf_to_pdf_ocr():
    """OCR avec mise en page conservée : PDF image → PDF avec texte sélectionnable"""
    if 'file' not in request.files:
        return "Aucun fichier reçu sous la clé 'file'", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = input_path.replace('.pdf', '-ocr.pdf')
    temp_folder = os.path.join(UPLOAD_FOLDER, 'ocr_pages')
    os.makedirs(temp_folder, exist_ok=True)
    file.save(input_path)

    try:
        # Étape 1 : PDF → images
        images = convert_from_path(input_path, poppler_path=POPPLER_PATH)
        page_paths = []

        # Étape 2 : OCR sur chaque page (format PDF avec layout)
        for i, image in enumerate(images):
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang='eng+fra', extension='pdf')
            page_path = os.path.join(temp_folder, f'page_{i + 1}.pdf')
            with open(page_path, 'wb') as f:
                f.write(pdf_bytes)
            page_paths.append(page_path)

        # Étape 3 : Fusion de toutes les pages OCR en un seul PDF
        final_pdf = fitz.open()
        for path in page_paths:
            with fitz.open(path) as page_doc:
                final_pdf.insert_pdf(page_doc)
        final_pdf.save(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Erreur OCR avec mise en page : {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
