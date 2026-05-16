from flask import Flask, render_template, request
import pdfplumber
import docx
import re
import spacy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

nlp = spacy.load('en_core_web_sm')


# Extract text from PDF
def extract_pdf_text(path):

    text = ''

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

    return text


# Extract text from DOCX
def extract_docx_text(path):

    doc = docx.Document(path)

    text = ''

    for para in doc.paragraphs:
        text += para.text + '\n'

    return text


# Extract Information
def extract_information(text):

    # Better Name Extraction
    lines = text.split('\n')

    name = 'Not Found'

    for line in lines[:5]:

        line = line.strip()

        if len(line.split()) >= 2 and len(line) < 30:

            if not any(skill.lower() in line.lower() for skill in ['python', 'java', 'sql', 'html']):

                name = line
                break

    # Email Extraction
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)

    # Phone Number Extraction
    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)

    # Skills Extraction
    skills_list = [
        'Python',
        'Java',
        'SQL',
        'HTML',
        'CSS',
        'JavaScript',
        'React',
        'AI',
        'Machine Learning',
        'C',
        'C++'
    ]

    found_skills = []

    for skill in skills_list:

        if skill.lower() in text.lower():

            found_skills.append(skill)

    return {

        'name': name,

        'email': email,

        'phone': phone,

        'skills': found_skills
    }


@app.route('/', methods=['GET', 'POST'])
def index():

    data = None

    if request.method == 'POST':

        file = request.files['resume']

        if file:

            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            file.save(path)

            # PDF File
            if file.filename.endswith('.pdf'):

                text = extract_pdf_text(path)

            # DOCX File
            elif file.filename.endswith('.docx'):

                text = extract_docx_text(path)

            else:

                text = 'Unsupported File'

            data = extract_information(text)

    return render_template('index.html', data=data)


if __name__ == '__main__':

    if not os.path.exists('uploads'):

        os.makedirs('uploads')

    app.run(debug=True)