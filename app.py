from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import re

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/career-guidance')
def career_guidance():
    return render_template('career_guidance.html')

@app.route('/skill-gap')
def skill_gap():
    return render_template('skill_gap.html')

@app.route('/salary-forecasting')
def salary_forecasting():
    return render_template('salary_forecasting.html')

@app.route('/mentorship')
def mentorship():
    return render_template('mentorship.html')

@app.route('/networking')
def networking():
    return render_template('networking.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recommend_career', methods=['POST'])
def recommend_career():
    data = request.get_json() or {}
    # Read answers (safe defaults)
    q1 = (data.get('q1') or '').lower()
    q2 = (data.get('q2') or '').lower()
    q3 = (data.get('q3') or '').lower()
    q4 = (data.get('q4') or '').lower()
    q5 = (data.get('q5') or '').lower()
    q6 = (data.get('q6') or '').lower()
    q7 = (data.get('q7') or '').lower()
    q8 = (data.get('q8') or '').lower()
    q9 = (data.get('q9') or '').lower()
    q10 = (data.get('q10') or '').strip()

    # Basic rule-based scoring to produce a single recommendation
    # (Replace this block with a call to your AI API later.)
    scores = {
        'Software Engineer': 0,
        'Data Scientist': 0,
        'UX Designer': 0,
        'Product Manager': 0,
        'Business / Management': 0,
        'Technical Writer': 0,
        'Frontend Developer': 0,
        'Researcher': 0
    }

    # heuristics
    if q1 == 'programming':
        scores['Software Engineer'] += 3
        scores['Frontend Developer'] += 2
        scores['Data Scientist'] += 1
    if q1 == 'math':
        scores['Data Scientist'] += 3
        scores['Researcher'] += 2
    if q1 == 'design':
        scores['UX Designer'] += 3
        scores['Frontend Developer'] += 1
    if q1 == 'business':
        scores['Product Manager'] += 3
        scores['Business / Management'] += 2
    if q1 == 'writing':
        scores['Technical Writer'] += 3

    if q3 == 'yes':
        scores['Software Engineer'] += 1
        scores['Frontend Developer'] += 1
        scores['Data Scientist'] += 1

    if q5 == 'yes':
        scores['Data Scientist'] += 2
    if q5 == 'sometimes':
        scores['Data Scientist'] += 1

    if q4 == 'high':
        scores['UX Designer'] += 2
    if q6 == 'yes':
        scores['Product Manager'] += 1
        scores['Technical Writer'] += 1

    if q7 == 'startup':
        scores['Software Engineer'] += 1
        scores['Frontend Developer'] += 1
    if q7 == 'academic':
        scores['Researcher'] += 2
        scores['Data Scientist'] += 1

    if q8 == 'tech':
        scores['Software Engineer'] += 2
        scores['Frontend Developer'] += 1
    if q8 == 'insights':
        scores['Data Scientist'] += 2
    if q8 == 'brand':
        scores['UX Designer'] += 2

    if q9 == 'mostly_code':
        scores['Software Engineer'] += 2
        scores['Frontend Developer'] += 1
    if q9 == 'mostly_people':
        scores['Product Manager'] += 2
        scores['Business / Management'] += 1

    # if user provided a keyword in q10, promote matches
    if q10:
        kw = q10.lower()
        for role in list(scores.keys()):
            if re.search(re.escape(role.split()[0].lower()), kw):
                scores[role] += 4

    # choose top scoring
    sorted_roles = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_role, top_score = sorted_roles[0]

    # Prepare a human-friendly response and suggestions
    reasons = []
    reasons.append(f"Based on your answers (subject preference {q1}, work style {q2}, creativity {q4})")
    if top_role in ['Software Engineer', 'Frontend Developer']:
        skills = ['Python', 'Data Structures & Algorithms', 'Git', 'Unit testing', 'Cloud basics']
        steps = ['Build small projects', 'Contribute to open-source', 'Practice DS & Algo problems']
    elif top_role == 'Data Scientist':
        skills = ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Data Visualization']
        steps = ['Take a course in ML', 'Do Kaggle projects', 'Learn SQL and data cleaning']
    elif top_role == 'UX Designer':
        skills = ['Design fundamentals', 'Figma', 'User research', 'Prototyping']
        steps = ['Create portfolio case studies', 'Practice user interviews', 'Learn Figma']
    elif top_role == 'Product Manager':
        skills = ['Roadmapping', 'Stakeholder communication', 'Prioritization', 'Metrics']
        steps = ['Study product case studies', 'Practice writing PRDs', 'Talk to PMs']
    elif top_role == 'Technical Writer':
        skills = ['Writing', 'Documentation tools', 'Markdown', 'Explainer videos']
        steps = ['Write tutorials', 'Start a technical blog', 'Learn API docs style']
    elif top_role == 'Researcher':
        skills = ['Statistics', 'Experiment design', 'Academic writing', 'Python/R']
        steps = ['Read papers', 'Reproduce experiments', 'Join a research group']
    else:
        skills = ['Communication', 'Problem-solving', 'Teamwork']
        steps = ['Work on group projects', 'Join internships', 'Build a portfolio']

    reason_text = f"I recommend: {top_role}. " + " ".join(reasons)

    response = {
        "recommendation": top_role,
        "reason": reason_text,
        "skills": skills,
        "steps": steps
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
