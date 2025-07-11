from flask import Flask, request, render_template
import os
import docx2txt
import PyPDF2
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

model = SentenceTransformer('all-MiniLM-L6-v2')  # Load BERT model

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""

@app.route("/")
def matchresume():
    return render_template('matchresume.html')

@app.route('/matcher', methods=['POST'])
def matcher():
    if request.method == 'POST':
        job_description = request.form['job_description']
        resume_files = request.files.getlist('resumes')

        resumes = []
        for resume_file in resume_files:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
            resume_file.save(filename)
            resumes.append(extract_text(filename))

        if not resumes or not job_description:
            return render_template('matchresume.html', message="Please upload resumes and enter a job description.")

        # Use BERT embeddings
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        resume_embeddings = model.encode(resumes, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.cos_sim(job_embedding, resume_embeddings)[0].cpu().tolist()

        # Get top 5 matches
        top_indices = sorted(range(len(cosine_scores)), key=lambda i: cosine_scores[i], reverse=True)[:5]
        top_resumes = [resume_files[i].filename for i in top_indices]
        similarity_scores = [round(cosine_scores[i], 2) for i in top_indices]

        return render_template('matchresume.html', message="Top matching resumes:", top_resumes=top_resumes, similarity_scores=similarity_scores)

    return render_template('matchresume.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

