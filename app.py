import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Load AI credentials
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = os.getenv("AI_API_URL")

app = Flask(__name__)

def call_ai_api(prompt, system_msg="You are a helpful assistant. Return JSON only."):
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user",  "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }

    response = requests.post(AI_API_URL, headers=headers, json=payload)

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/skill-gap')
def skill_gap():
    return render_template('skill_gap.html')

@app.route('/career-guidance')
def career_guidance():
    return render_template('career_guidance.html')

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


# -------------------- NEW AI-POWERED SKILL GAP --------------------

@app.route('/analyze_skill_gap', methods=['POST'])
def analyze_skill_gap():
    data = request.get_json()

    company = data.get("company", "")
    position = data.get("position", "")
    skills = data.get("skills", "")

    prompt = f"""
    Analyze skill gap for:

    Company: {company}
    Position: {position}
    Current Skills: {skills}

    Return JSON ONLY in this format:
    {{
        "missing_skills": ["skill1", "skill2", ...],
        "recommended_learning_path": ["step1", "step2", ...]
    }}
    """

    try:
        ai_output = call_ai_api(prompt)
        result = json.loads(ai_output)
    except Exception as e:
        return jsonify({"error": "AI processing error", "details": str(e)}), 500

    return jsonify(result)


# ----------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
