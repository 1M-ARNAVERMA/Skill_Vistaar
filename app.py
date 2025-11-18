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

@app.route('/api/skill-gap', methods=['POST'])
def analyze_skill_gap_api():
    """
    New skill-gap endpoint using Google Gemini (genai).
    Expects JSON: { company, position, skills }
    Returns JSON: { title, required, missing, recommendations, notes }
    """
    data = request.get_json(silent=True) or {}
    company = (data.get('company') or '').strip()
    position = (data.get('position') or '').strip()
    skills_raw = (data.get('skills') or '').strip()

    if not position or not skills_raw:
        return jsonify({"error": "position and skills are required."}), 400

    # Normalize user skills as short list (comma separated)
    user_skills = [s.strip() for s in re.split(r',|\n|;', skills_raw) if s.strip()]

    # Build prompt: ask for JSON output describing required skills, missing skills, recommendations
    prompt = f"""
You are an expert hiring/career advisor. A candidate provided:
- Target company: {company or 'Not specified'}
- Position: {position}
- Current skills: {', '.join(user_skills)}

Please analyze typical job requirements for this role (generalized, and include company-specific notes if company was specified).
Return ONLY valid JSON with these keys:
- title (string) e.g. "Skill gap analysis for Software Engineer"
- required (array of strings) - the core required skills for the role
- missing (array of strings) - which required skills the user does NOT currently have
- recommendations (array of short strings) - prioritized practical next steps (3-6 items)
- notes (string) - optional notes about company-specific expectations

Be concise and practical.
"""

    # choose model name you have access to
    model_name = "gemini-2.5-flash"  # change if necessary

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[{"parts": [{"text": prompt}]}],
        )
    except Exception as e:
        return jsonify({"error": f"AI service error (request failed): {str(e)}"}), 500

    # Extract text robustly (reuse the same robust extraction logic)
    raw_text = ""
    if hasattr(response, "text") and isinstance(response.text, str) and response.text.strip():
        raw_text = response.text.strip()
    else:
        try:
            resp_obj = json.loads(json.dumps(response))
        except Exception:
            resp_obj = response

        def find_first_string(obj):
            if isinstance(obj, str):
                return obj if obj.strip() else None
            if isinstance(obj, dict):
                for key in ("candidates", "output", "response", "content", "text", "message", "messages"):
                    if key in obj:
                        found = find_first_string(obj[key])
                        if found:
                            return found
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
        raw_text = (found or "").strip()

    # Parse JSON from raw_text
    parsed = {}
    if raw_text:
        try:
            parsed = json.loads(raw_text)
        except Exception:
            m = re.search(r"\{(?:[^{}]|\n|\r|\s)*\}", raw_text)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = {}
            else:
                parsed = {}

    # If parsing failed, respond with fallback helpful message
    if not parsed:
        return jsonify({"error": "AI returned no parseable JSON. Raw response: " + (raw_text[:1000] or "empty")}), 500

    # Normalize fields
    title = parsed.get("title") or f"Skill gap analysis for {position}"
    required = parsed.get("required") or []
    missing = parsed.get("missing") or []
    recommendations = parsed.get("recommendations") or parsed.get("recommendations", []) or []
    notes = parsed.get("notes") or ""

    # Ensure arrays are lists of strings
    def ensure_list_of_strings(x):
        if isinstance(x, list):
            return [str(i) for i in x]
        if isinstance(x, str):
            # try splitting on newline or semicolon
            return [s.strip() for s in re.split(r'\n|;|\.', x) if s.strip()]
        return []

    required = ensure_list_of_strings(required)
    missing = ensure_list_of_strings(missing)
    recommendations = ensure_list_of_strings(recommendations)

    return jsonify({
        "title": title,
        "required": required,
        "missing": missing,
        "recommendations": recommendations,
        "notes": notes
    })

@app.route('/predict_salary', methods=['POST'])
def predict_salary():
    """
    AI-only salary forecasting using Google Gemini (genai).
    Always returns API-driven result or an error (no local fallback).
    Output JSON shape (on success): { job, min, avg, max, missing_skills, note }
    On failure returns: {"error": "<message>"} with status 500.
    """
    data = request.get_json(silent=True) or {}
    job_input = (data.get('job') or '').strip()
    location = (data.get('location') or '').strip()
    experience = data.get('experience', 0)
    skills_raw = (data.get('skills') or '').strip()
    current_skills = [s.strip().lower() for s in re.split(r',|\n|;', skills_raw) if s.strip()]

    # Build prompt (strict JSON requested)
    prompt = f"""
You are a careful, data-driven salary forecasting assistant. Given a job title, location, years of experience,
and current skills, return a strict JSON object (no extra text) with these keys:
- job: canonical job name (string)
- min: estimated minimum salary in INR (integer)
- avg: estimated average salary in INR (integer)
- max: estimated maximum salary in INR (integer)
- missing_skills: array of short strings (skills that would increase salary)
- note: optional short note about location or assumptions

User data:
job_title: {job_input or 'Not specified'}
location: {location or 'Not specified'}
years_experience: {experience}
current_skills: {', '.join(current_skills) or 'None'}

Return only valid JSON. Use reasonable, conservative estimates and prioritize practical skill recommendations.
"""

    model_name = "gemini-2.5-flash"  # change if your account requires a different model

    # Call Gemini API
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[{"parts": [{"text": prompt}]}],
        )
    except Exception as e:
        # API request failed — return as error to frontend
        err_msg = f"AI service request failed: {str(e)}"
        return jsonify({"error": err_msg}), 500

    # Robustly extract text
    raw_text = ""
    if hasattr(response, "text") and isinstance(response.text, str) and response.text.strip():
        raw_text = response.text.strip()
    else:
        try:
            resp_obj = json.loads(json.dumps(response))
        except Exception:
            resp_obj = response

        def find_first_string(obj):
            if isinstance(obj, str):
                return obj if obj.strip() else None
            if isinstance(obj, dict):
                # try common nested keys first
                for key in ("candidates", "output", "response", "content", "text", "message", "messages"):
                    if key in obj:
                        found = find_first_string(obj[key])
                        if found:
                            return found
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
        raw_text = (found or "").strip()

    if not raw_text:
        return jsonify({"error": "AI returned an empty response."}), 500

    # Parse JSON from the model output
    parsed = {}
    try:
        parsed = json.loads(raw_text)
    except Exception:
        m = re.search(r"\{(?:[^{}]|\n|\r|\s)*\}", raw_text)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = {}
        else:
            parsed = {}

    # Validate parsed output contains numeric salary fields
    if not isinstance(parsed, dict) or not all(k in parsed for k in ("min", "avg", "max")):
        # return raw model text as error for debugging
        return jsonify({"error": "AI returned unparseable JSON output.", "raw": raw_text[:200]}), 500

    # Normalize numeric fields
    def to_int(val):
        try:
            if isinstance(val, int):
                return val
            if isinstance(val, float):
                return int(val)
            s = str(val)
            s = re.sub(r'[^\d.-]', '', s)
            return int(float(s)) if s else 0
        except Exception:
            return 0

    job_out = parsed.get("job") or job_input or parsed.get("title") or "role"
    min_salary = to_int(parsed.get("min"))
    avg_salary = to_int(parsed.get("avg"))
    max_salary = to_int(parsed.get("max"))

    missing_skills = parsed.get("missing_skills") or parsed.get("missing") or []
    if isinstance(missing_skills, str):
        missing_skills = [s.strip() for s in re.split(r',|\n|;', missing_skills) if s.strip()]
    else:
        missing_skills = [str(x).strip() for x in missing_skills]

    note = parsed.get("note") or parsed.get("notes") or ""
    if location and note and location not in note:
        note = note + f" This estimate is for {location}."

    result = {
        "job": job_out,
        "min": min_salary,
        "avg": avg_salary,
        "max": max_salary,
        "missing_skills": missing_skills,
        "note": note
    }

    return jsonify(result)


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
