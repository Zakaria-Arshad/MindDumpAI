import os

from flask import Flask, request, flash, redirect, render_template_string, url_for, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pytesseract
from ImageProcessor import ImageProcessor
from RagProcessing import RagProcessing
from PIL import Image
load_dotenv()
app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['TXT_DOCS'] = './docs'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def allowed_file(filename):
    file_extension = filename.split(".")[-1]
    return file_extension in ["jpg", "jpeg", "png"]


@app.route('/', methods=['GET', 'POST'])
def upload_file():  # put application's code here
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):  # should add allowed file security later
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


@app.route("/delete", methods=['GET', 'POST'])
def delete_file():
    selected_files = request.form.getlist("selected_files")
    for file in selected_files:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return redirect(url_for('upload_file'))

@app.route("/ocr", methods=['GET', 'POST'])
def ocr():
    imageProcessor = ImageProcessor()
    selected_files = request.form.getlist("selected_files")
    for file in selected_files:
        imageProcessor.processImage(os.path.join("./uploads/", file))
    return redirect(url_for('upload_file'))

@app.route("/query", methods=['GET', 'POST'])
def query():
    processor = RagProcessing()
    for file in os.listdir(app.config['TXT_DOCS']):
        processor.storeInVectorStore(os.path.join(app.config['TXT_DOCS'], file))
    processor.retrieve()
    processor.generate()
    return render_template_string('''
    <!doctype html>
    <head></head>
    <body>
    <h1>Response in logs</h1>
    </body>
    ''')



if __name__ == '__main__':
    app.run()
