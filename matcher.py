from flask import Blueprint, request, jsonify
from utils.ai import match_resumes

matcher = Blueprint('matcher', __name__)

@matcher.route('/match', methods=['POST'])
def match():
    data = request.get_json()
    job = data.get('job_description', '')
    resumes = data.get('resumes', [])
    if not job or not resumes:
        return jsonify(msg="Missing job or resumes"), 400

    scores = match_resumes(job, resumes)
    return jsonify(scores=scores)
