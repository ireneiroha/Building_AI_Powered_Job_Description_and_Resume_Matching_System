🤖✨ AI-Powered-Job-Description-And-Resume-Matching-System
This system uses modern AI and NLP techniques to automatically match job descriptions to resumes based on contextual meaning, not just keywords.

✅ How the AI Works
📌 BERT Embeddings: We use the sentence-transformers library (all-MiniLM-L6-v2 model) — a state-of-the-art, transformer-based model that converts text into semantic vectors.

📌 Semantic Similarity: The system computes cosine similarity between the job description and each resume, comparing the meaning of the text rather than simple word overlap.

📌 Context-Aware Ranking: Unlike classic keyword matching, BERT embeddings understand synonyms, phrasing, and context — giving recruiters better, fairer matches.

Roughly 60% of this project’s technical logic focuses on AI/NLP, with the other 40% supporting backend routing, file handling, and the user interface.

🌍 Supporting SDG 8 — Decent Work and Economic Growth
This project supports the United Nations Sustainable Development Goal 8 by:

✅ Promoting fair and inclusive hiring through skill-based, bias-reduced matching.

✅ Giving equal opportunity to candidates by evaluating resumes on content, not just surface keywords.

✅ Helping recruiters discover hidden talent, encouraging productive employment and economic growth.

🛠️ Technical Stack
Python & Flask: For backend API and routing.

Sentence-Transformers (BERT): For advanced semantic text understanding.

PyPDF2 & docx2txt: For extracting text from various resume formats.

Bootstrap, HTML/CSS: For a simple, responsive frontend.

✅ Example AI Workflow
1️⃣ Input: Recruiter enters a job description.
2️⃣ Upload: Candidates upload resumes (PDF, DOCX, TXT).
3️⃣ Embeddings: The system uses BERT to generate semantic vectors for both.
4️⃣ Similarity: Computes cosine similarity to rank matches.
5️⃣ Output: Displays top resumes with similarity scores.

📌 Responsible AI & Fairness
The matching focuses on skills & context, reducing hidden bias from keyword-only filters.

(Optional) Resumes can be anonymized to remove names/contacts for blind matching.

(Optional) Recruiters can provide candidates feedback to improve employability.

🚀 Run It Locally

pip install -r requirements.txt

python app.py

Visit http://localhost:5000 to try it!

📣 Contribution
We welcome ideas for improving fairness, bias detection, and new AI features to make this system even more inclusive.
  
- PITCH DESK: https://gamma.app/docs/AI-Powered-Recruitment-Job-Description-Resume-Matching-p44048pum1xwkps?mode=doc



