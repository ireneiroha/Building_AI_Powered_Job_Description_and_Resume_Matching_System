from flask import Flask, request, render_template, session, redirect, url_for
import os
import docx2txt
import PyPDF2
from sentence_transformers import SentenceTransformer, util
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Uploads/'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:password123@localhost/flask_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)
db = SQLAlchemy(app)

model = SentenceTransformer('all-MiniLM-L6-v2')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    mentorships_as_mentor = db.relationship('Mentorship', foreign_keys='Mentorship.mentor_id', backref='mentor', lazy=True)
    mentorships_as_mentee = db.relationship('Mentorship', foreign_keys='Mentorship.mentee_id', backref='mentee', lazy=True)
    resume_matches = db.relationship('ResumeMatch', backref='user', lazy=True)
    user_skills = db.relationship('UserSkill', backref='user', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(120), nullable=True)
    linkedin = db.Column(db.String(120), nullable=True)
    github = db.Column(db.String(120), nullable=True)
    member_since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Mentorship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    sessions = db.relationship('MentorshipSession', backref='mentorship', lazy=True)

class MentorshipSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentorship_id = db.Column(db.Integer, db.ForeignKey('mentorship.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='scheduled')
    topic = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

class ResumeMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    change_amount = db.Column(db.Float, nullable=True)
    change_date = db.Column(db.DateTime, nullable=True)

# Text extraction functions
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

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            # Initialize profile if not exists
            if not Profile.query.filter_by(user_id=user.id).first():
                profile = Profile(
                    user_id=user.id,
                    name=username,
                    email=user.email,
                    location='Unknown',
                    role='Job Seeker',
                    bio='',
                    website='Not provided',
                    linkedin='Not provided',
                    github='Not provided',
                    member_since=datetime.utcnow()
                )
                db.session.add(profile)
            # Add sample mentorship and skill data for "sky"
            if username == 'sky' and not Mentorship.query.filter_by(mentor_id=user.id).first():
                mentee1 = User.query.filter_by(username='mentee1').first() or User(username='mentee1', email='mentee1@example.com', password='password')
                mentee2 = User.query.filter_by(username='mentee2').first() or User(username='mentee2', email='mentee2@example.com', password='password')
                db.session.add(mentee1)
                db.session.add(mentee2)
                db.session.commit()
                mentorship1 = Mentorship(mentor_id=user.id, mentee_id=mentee1.id, start_date=datetime.now() - timedelta(days=30))
                mentorship2 = Mentorship(mentor_id=user.id, mentee_id=mentee2.id, start_date=datetime.now() - timedelta(days=15))
                db.session.add(mentorship1)
                db.session.add(mentorship2)
                db.session.commit()
                session1 = MentorshipSession(mentorship_id=mentorship1.id, session_date=datetime.now() + timedelta(days=1), topic='Career Advice')
                session2 = MentorshipSession(mentorship_id=mentorship1.id, session_date=datetime.now() - timedelta(days=7), status='completed', topic='Resume Review', notes='Discussed resume improvements')
                session3 = MentorshipSession(mentorship_id=mentorship2.id, session_date=datetime.now() + timedelta(days=3), topic='Technical Interview Prep')
                db.session.add(session1)
                db.session.add(session2)
                db.session.add(session3)
                db.session.commit()
            if not UserSkill.query.filter_by(user_id=user.id).first():
                skills = ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Data Engineering']
                for skill_name in skills:
                    skill = Skill.query.filter_by(name=skill_name).first()
                    if not skill:
                        skill = Skill(name=skill_name)
                        db.session.add(skill)
                        db.session.commit()
                    user_skill = UserSkill(
                        user_id=user.id,
                        skill_id=skill.id,
                        score=random.uniform(70, 95),
                        change_amount=random.uniform(2, 8),
                        change_date=datetime.now() - timedelta(days=random.randint(1, 29))
                    )
                    db.session.add(user_skill)
                db.session.commit()
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('login.html', message="Invalid credentials.")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not email:
            return render_template('signup.html', message="Email is required.")
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return render_template('signup.html', message="Username or email already exists.")
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        profile = Profile(
            user_id=new_user.id,
            name=username,
            email=email,
            location='Unknown',
            role='Job Seeker',
            bio='',
            website='Not provided',
            linkedin='Not provided',
            github='Not provided',
            member_since=datetime.utcnow()
        )
        db.session.add(profile)
        db.session.commit()
        session['user_id'] = new_user.id
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Job Matches
    all_matches = ResumeMatch.query.filter_by(user_id=user_id).all()
    job_matches = len(all_matches)
    one_week_ago = datetime.now() - timedelta(days=7)
    job_matches_this_week = sum(1 for match in all_matches if match.timestamp > one_week_ago)
    matched_results = [(m.filename, m.score) for m in sorted(all_matches, key=lambda m: m.score, reverse=True)[:5]]
    # Courses Enrolled (placeholder)
    courses_enrolled = 0
    courses_enrolled_this_week = 1
    # Mentorship Sessions
    upcoming_sessions = MentorshipSession.query.join(Mentorship).filter(
        Mentorship.mentor_id == user_id,
        MentorshipSession.session_date > datetime.now(),
        MentorshipSession.status == 'scheduled'
    ).count()
    next_session = MentorshipSession.query.join(Mentorship).filter(
        Mentorship.mentor_id == user_id,
        MentorshipSession.session_date > datetime.now(),
        MentorshipSession.status == 'scheduled'
    ).order_by(MentorshipSession.session_date.asc()).first()
    next_mentorship = next_session.session_date.strftime('%Y-%m-%d %H:%M') if next_session else 'No upcoming sessions'
    # Skill Score
    user_skills = UserSkill.query.filter_by(user_id=user_id).all()
    if user_skills:
        total_score = sum(us.score for us in user_skills)
        skill_score = total_score / len(user_skills)
    else:
        skill_score = 0
    one_month_ago = datetime.now() - timedelta(days=30)
    total_increase = db.session.query(db.func.sum(UserSkill.change_amount)).filter(
        UserSkill.user_id == user_id,
        UserSkill.change_date > one_month_ago
    ).scalar() or 0
    number_of_skills = len(user_skills)
    increase_this_month = total_increase / number_of_skills if number_of_skills > 0 else 0
    return render_template('dashboard.html', username=session['username'], profile=session.get('profile', {}),
                           matched_results=matched_results,
                           job_matches=job_matches, job_matches_this_week=job_matches_this_week,
                           courses_enrolled=courses_enrolled, courses_enrolled_this_week=courses_enrolled_this_week,
                           mentorship_sessions=upcoming_sessions, next_mentorship=next_mentorship,
                           skill_score=skill_score, increase_this_month=increase_this_month)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    mentorships = Mentorship.query.filter_by(mentor_id=user_id, status='active').all()
    return render_template('profile.html', username=session['username'], profile=profile, mentorships=mentorships)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        profile.name = request.form.get('name', profile.name)
        profile.email = request.form.get('email', profile.email)
        profile.location = request.form.get('location', profile.location)
        profile.role = request.form.get('role', profile.role)
        profile.bio = request.form.get('bio', profile.bio)
        profile.website = request.form.get('website', profile.website)
        profile.linkedin = request.form.get('linkedin', profile.linkedin)
        profile.github = request.form.get('github', profile.github)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', profile=profile)

@app.route('/matcher', methods=['POST'])
def matcher():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        job_description = request.form['job_description']
        resume_files = request.files.getlist('resumes')
        resumes = []
        for resume_file in resume_files:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
            resume_file.save(filename)
            resumes.append(extract_text(filename))
        if not resumes or not job_description:
            return render_template('dashboard.html', username=session['username'], profile=session.get('profile', {}), message="Please upload resumes and enter a job description.")
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        resume_embeddings = model.encode(resumes, convert_to_tensor=True)
        cosine_scores = util.cos_sim(job_embedding, resume_embeddings)[0].cpu().tolist()
        for i in range(len(resume_files)):
            match = ResumeMatch(
                user_id=user_id,
                filename=resume_files[i].filename,
                score=round(cosine_scores[i] * 100, 2),
                timestamp=datetime.now()
            )
            db.session.add(match)
        db.session.commit()
        all_matches = ResumeMatch.query.filter_by(user_id=user_id).all()
        job_matches = len(all_matches)
        one_week_ago = datetime.now() - timedelta(days=7)
        job_matches_this_week = sum(1 for match in all_matches if match.timestamp > one_week_ago)
        matched_results = [(m.filename, m.score) for m in sorted(all_matches, key=lambda m: m.score, reverse=True)[:5]]
        courses_enrolled = 0
        courses_enrolled_this_week = 1
        upcoming_sessions = MentorshipSession.query.join(Mentorship).filter(
            Mentorship.mentor_id == user_id,
            MentorshipSession.session_date > datetime.now(),
            MentorshipSession.status == 'scheduled'
        ).count()
        next_session = MentorshipSession.query.join(Mentorship).filter(
            Mentorship.mentor_id == user_id,
            MentorshipSession.session_date > datetime.now(),
            MentorshipSession.status == 'scheduled'
        ).order_by(MentorshipSession.session_date.asc()).first()
        next_mentorship = next_session.session_date.strftime('%Y-%m-%d %H:%M') if next_session else 'No upcoming sessions'
        user_skills = UserSkill.query.filter_by(user_id=user_id).all()
        if user_skills:
            total_score = sum(us.score for us in user_skills)
            skill_score = total_score / len(user_skills)
        else:
            skill_score = 0
        one_month_ago = datetime.now() - timedelta(days=30)
        total_increase = db.session.query(db.func.sum(UserSkill.change_amount)).filter(
            UserSkill.user_id == user_id,
            UserSkill.change_date > one_month_ago
        ).scalar() or 0
        number_of_skills = len(user_skills)
        increase_this_month = total_increase / number_of_skills if number_of_skills > 0 else 0
        return render_template('dashboard.html', username=session['username'], profile=session.get('profile', {}), message="Top matching resumes:", matched_results=matched_results,
                               job_matches=job_matches, job_matches_this_week=job_matches_this_week,
                               courses_enrolled=courses_enrolled, courses_enrolled_this_week=courses_enrolled_this_week,
                               mentorship_sessions=upcoming_sessions, next_mentorship=next_mentorship,
                               skill_score=skill_score, increase_this_month=increase_this_month)
    return render_template('dashboard.html', username=session['username'], profile=session.get('profile', {}))

@app.route('/view_all_matches')
def view_all_matches():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    all_matches = ResumeMatch.query.filter_by(user_id=user_id).all()
    if not all_matches:
        return render_template('view_all_matches.html', username=session['username'], message="No matches available. Please run a match first.", all_matches=[])
    return render_template('view_all_matches.html', username=session['username'], all_matches=[(m.filename, m.score) for m in all_matches])

@app.route('/mentorship_management')
def mentorship_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    mentorships = Mentorship.query.filter_by(mentor_id=user_id, status='active').all()
    now = datetime.now()
    return render_template('mentorship_management.html', username=session['username'], mentorships=mentorships, now=now)

@app.route('/mentorship')
def mentorship():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('mentorship_management'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/upskilling')
def upskilling():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('upskilling.html', username=session['username'], message="Upskilling learning paths (under development)")

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
