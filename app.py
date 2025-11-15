import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = os.getenv("AI_API_URL")

app = Flask(__name__, static_folder="static", template_folder="templates")


def call_ai_api(prompt, system_msg="You are a helpful assistant. Return JSON only."):
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.25,
        "max_tokens": 600,
    }
    r = requests.post(AI_API_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    # Parse model output (we expect plain text containing JSON)
    return r.json()["choices"][0]["message"]["content"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/career-guidance")
def career_guidance():
    return render_template("career_guidance.html")


@app.route("/skill-gap")
def skill_gap():
    return render_template("skill_gap.html")


@app.route("/salary-forecasting")
def salary_forecasting():
    return render_template("salary_forecasting.html")


@app.route("/mentorship")
def mentorship():
    return render_template("mentorship.html")


@app.route("/networking")
def networking():
    return render_template("networking.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/analyze_skill_gap", methods=["POST"])
def analyze_skill_gap():
    payload = request.get_json() or {}
    company = payload.get("company", "").strip()
    position = payload.get("position", "").strip()
    skills = payload.get("skills", "").strip()

    if not position:
        return jsonify({"error": "position is required"}), 400

    prompt = f"""
You are an assistant that must return VALID JSON only (no extra text).
Input:
company: "{company}"
position: "{position}"
current_skills: "{skills}"

Return a JSON object exactly in this format:
{{
  "missing_skills": ["skill1", "skill2", ...],
  "recommended_learning_path": ["step1", "step2", ...]
}}
Use concise skill names and short learning steps. Do NOT include any explanatory text outside the JSON.
    """

    try:
        ai_text = call_ai_api(prompt)
        result = json.loads(ai_text)
    except Exception as e:
        return jsonify({"error": "AI processing failed", "detail": str(e)}), 502

    return jsonify(result)


@app.route("/forecast_salary", methods=["POST"])
def forecast_salary():
    payload = request.get_json() or {}
    job = payload.get("job", "").strip()
    location = payload.get("location", "").strip()
    experience = payload.get("experience", "").strip()
    skills = payload.get("skills", "").strip()

    if not job or not location or experience == "":
        return jsonify({"error": "job, location, and experience are required"}), 400

    prompt = f"""
You are an assistant that returns JSON only.
Input:
job: "{job}"
location: "{location}"
experience_years: {experience}
skills: "{skills}"

Return JSON exactly:
{{
  "min_salary": number,
  "avg_salary": number,
  "max_salary": number,
  "recommended_skills": ["skill1", "skill2"],
  "explanation": "short text"
}}
Provide yearly INR salary estimates (rounded to nearest 1000). Do NOT output anything else.
    """

    try:
        ai_text = call_ai_api(prompt)
        result = json.loads(ai_text)
    except Exception as e:
        return jsonify({"error": "AI processing failed", "detail": str(e)}), 502

    return jsonify(result)


@app.route("/career_quiz", methods=["POST"])
def career_quiz():
    payload = request.get_json() or {}
    answers = payload.get("answers", {})

    prompt = f"""
You are an assistant that takes quiz answers and returns a single recommended career with explanation.
Input: answers: {json.dumps(answers)}

Return JSON only:
{{
  "recommended_career": "Career Name",
  "reason": "one-line reason",
  "next_steps": ["step1", "step2"]
}}
    """

    try:
        ai_text = call_ai_api(prompt)
        result = json.loads(ai_text)
    except Exception as e:
        return jsonify({"error": "AI processing failed", "detail": str(e)}), 502

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
