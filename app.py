from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import re
import os
from flask import Flask, render_template, request, jsonify
import json
from google import genai

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

app = Flask(__name__, static_folder='static', template_folder='templates')

GENIE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GENIE_API_KEY:
    print("Warning: GEMINI_API_KEY not set")

# configure the genai client to use an API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    if q10:
        kw = q10.lower()
        for role in list(scores.keys()):
            if re.search(re.escape(role.split()[0].lower()), kw):
                scores[role] += 4

    sorted_roles = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_role, top_score = sorted_roles[0]

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

@app.route('/analyze_skill_gap', methods=['POST'])
def analyze_skill_gap():
    data = request.get_json() or {}
    company = (data.get('company') or '').strip()
    position = (data.get('position') or '').strip().lower()
    skills_raw = (data.get('skills') or '').strip().lower()

    current_skills = [s.strip() for s in re.split(r',|\n|;', skills_raw) if s.strip()]

    job_requirements = {
        "software engineer": ["python", "data structures", "algorithms", "git", "unit testing", "linux", "cloud computing"],
        "backend engineer": ["python", "apis", "databases", "sql", "docker", "git"],
        "frontend developer": ["html", "css", "javascript", "react", "responsive design", "accessibility"],
        "data scientist": ["python", "machine learning", "statistics", "sql", "pandas", "data visualization"],
        "data analyst": ["sql", "excel", "data visualization", "python", "statistics"],
        "ux designer": ["user research", "wireframing", "figma", "prototyping", "usability testing"],
        "product manager": ["roadmapping", "stakeholder communication", "metrics", "prioritization"],
        "devops": ["linux", "docker", "kubernetes", "ci/cd", "cloud"],
    }

    matched_key = None
    for key in job_requirements.keys():
        if key in position:
            matched_key = key
            break
    if matched_key is None:
        for key in job_requirements.keys():
            first_word = key.split()[0]
            if first_word in position:
                matched_key = key
                break
    if matched_key is None:
        required_skills = ["communication", "problem-solving", "teamwork"]
    else:
        required_skills = job_requirements[matched_key]

    normalized_current = [s.lower() for s in current_skills]
    missing = [r for r in required_skills if not any(r in s or s in r for s in normalized_current)]

    recommendations = []
    if missing:
        recommendations.append("Study and practice the missing skills listed above.")
        recommendations.append("Build small projects that demonstrate those skills.")
        recommendations.append("Add those keywords to your resume and LinkedIn profile.")
        recommendations.append("Take hands-on courses or labs for the missing topics.")
    else:
        recommendations.append("Your current skills cover the core requirements. Strengthen via projects and interview practice.")

    notes = ""
    if company:
        notes = f"Hiring requirements at {company} may include extra topics (system design, domain tools). Check company job descriptions to refine this list."

    response = {
        "title": f"Skill gap analysis for {position.title() if position else 'role'}",
        "required": required_skills,
        "missing": missing,
        "recommendations": recommendations,
        "notes": notes
    }
    return jsonify(response)

@app.route('/predict_salary', methods=['POST'])
def predict_salary():
    data = request.get_json() or {}
    job = (data.get('job') or '').strip().lower()
    location = (data.get('location') or '').strip()
    experience = data.get('experience', 0)
    skills_raw = (data.get('skills') or '').strip().lower()
    current_skills = [s.strip() for s in re.split(r',|\n|;', skills_raw) if s.strip()]

    salary_data = {
        "software engineer": {"min": 400000, "avg": 800000, "max": 1500000, "boost": ["system design", "cloud computing", "data structures & algorithms", "unit testing"]},
        "data scientist": {"min": 500000, "avg": 950000, "max": 1700000, "boost": ["machine learning", "deep learning", "sql", "statistics"]},
        "web developer": {"min": 300000, "avg": 600000, "max": 1200000, "boost": ["react", "node.js", "rest apis", "javascript"]},
        "frontend developer": {"min": 350000, "avg": 650000, "max": 1250000, "boost": ["react", "javascript", "css", "accessibility"]},
        "backend engineer": {"min": 380000, "avg": 720000, "max": 1400000, "boost": ["apis", "databases", "docker", "sql"]},
        "data analyst": {"min": 250000, "avg": 450000, "max": 900000, "boost": ["sql", "excel", "data visualization", "python"]},
    }

    matched = None
    for key in salary_data.keys():
        if key in job:
            matched = key
            break
    if matched is None:
        for key in salary_data.keys():
            if key.split()[0] in job:
                matched = key
                break

    if matched is None:
        matched = "software engineer"

    entry = salary_data[matched]
    boost_skills = entry.get("boost", [])
    missing = [s for s in boost_skills if not any(s in cs or cs in s for cs in current_skills)]

    # small adjustment by experience (very simple)
    try:
        exp = float(experience)
    except Exception:
        exp = 0.0
    multiplier = 1.0 + min(max(exp - 1.0, 0.0) * 0.06, 0.6)

    min_salary = int(entry["min"] * multiplier)
    avg_salary = int(entry["avg"] * multiplier)
    max_salary = int(entry["max"] * multiplier)

    note = ""
    if location:
        note = f"Salaries vary by city. This is a rough estimate for {location}."

    response = {
        "job": matched,
        "min": min_salary,
        "avg": avg_salary,
        "max": max_salary,
        "missing_skills": missing,
        "note": note
    }
    return jsonify(response)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/career-recommend', methods=['POST'])
def career_recommend_api():
    """
    Robust, cleaned-up career recommendation endpoint for Google Gemini (genai).
    Expects JSON: { "answers": { "q1":"...", ..., "q10":"..." } }
    Returns JSON: { "role": ..., "reason": ..., "recommended_skills": ... }
    """
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})

    # Normalize inputs q1..q10
    q = {f"q{i}": (answers.get(f"q{i}", "") or "").strip() for i in range(1, 11)}
    if not any(q.values()):
        return jsonify({"error": "No answers provided."}), 400

    # Build the prompt asking for strict JSON output
    prompt = f"""You are a concise, practical career counselor.
A student answered 10 short interest-based prompts (1-3 words each).
Using these answers, RECOMMEND a single best-fit job role and provide:
  - role: one short job title (<=5 words)
  - reason: 1-2 sentence explanation
  - recommended_skills: comma-separated list of up to 5 practical skills/next steps

RETURN ONLY valid JSON with keys: role, reason, recommended_skills

User answers:
1) {q['q1']}
2) {q['q2']}
3) {q['q3']}
4) {q['q4']}
5) {q['q5']}
6) {q['q6']}
7) {q['q7']}
8) {q['q8']}
9) {q['q9']}
10) {q['q10']}
"""

    # Choose a model you have access to; adjust if needed
    model_name = "gemini-2.5-flash"

    try:
        # Call Gemini via the genai client (keeps call minimal)
        response = client.models.generate_content(
            model=model_name,
            contents=[{"parts": [{"text": prompt}]}],
        )
    except Exception as e:
        return jsonify({"error": f"AI service error (request failed): {str(e)}"}), 500

    # --- Extract raw text robustly from many possible response shapes ---
    raw_text = ""

    # 1) direct .text attribute (some wrappers)
    if hasattr(response, "text") and isinstance(response.text, str) and response.text.strip():
        raw_text = response.text
    else:
        # 2) attempt to probe common nested keys safely
        try:
            # Convert to plain Python structure so we can search it
            resp_obj = json.loads(json.dumps(response))
        except Exception:
            # If conversion fails, fallback to string representation
            resp_obj = response

        def find_first_string(obj):
            """Recursively find first non-empty string in nested dict/list"""
            if isinstance(obj, str):
                return obj if obj.strip() else None
            if isinstance(obj, dict):
                # Prefer keys likely to contain text
                for key in ("candidates", "output", "response", "content", "text", "message", "messages"):
                    if key in obj:
                        found = find_first_string(obj[key])
                        if found:
                            return found
                # otherwise iterate
                for v in obj.values():
                    found = find_first_string(v)
                    if found:
                        return found
            if isinstance(obj, list):
                for item in obj:
                    found = find_first_string(item)
                    if found:
                        return found
            return None

        found = find_first_string(resp_obj)
        raw_text = found or ""

    raw_text = (raw_text or "").strip()

    # --- Try parsing JSON directly, then attempt extraction via regex ---
    parsed = {}
    if raw_text:
        try:
            parsed = json.loads(raw_text)
        except Exception:
            # extract first {...} block
            m = re.search(r"\{(?:[^{}]|\n|\r|\s)*\}", raw_text)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = {}
            else:
                parsed = {}

    # If parsing failed, but there is raw_text, use it as the reason fallback
    if not parsed:
        parsed = {"role": "", "reason": raw_text or "No usable response from model.", "recommended_skills": ""}

    # Normalize outputs
    role = (parsed.get("role") or "").strip()
    reason = (parsed.get("reason") or "").strip()
    recommended_skills = (parsed.get("recommended_skills") or "").strip()

    # Fallback: if role is empty but reason seems to start with a job title, use first line
    if not role and reason:
        first_line = reason.splitlines()[0].strip()
        # quick heuristic: if first line short, treat as role
        if 1 <= len(first_line.split()) <= 6:
            # If first_line contains punctuation, it's likely not a clean role; still safe to use
            role = first_line

    return jsonify({
        "role": role,
        "reason": reason,
        "recommended_skills": recommended_skills
    })

if __name__ == '__main__':
    app.run(debug=True)
