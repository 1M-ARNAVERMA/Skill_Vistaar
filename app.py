from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

@app.route('/analyze_skill_gap', methods=['POST'])
def analyze_skill_gap():
    data = request.get_json()
    company = data['company']
    position = data['position']
    current_skills = [skill.strip().lower() for skill in data['skills'].split(',')]

    # Example: Logic for mock required skills for a position
    job_requirements = {
        "software engineer": ["python", "data structures", "algorithms", "git", "cloud computing", "linux"],
        "data scientist": ["python", "machine learning", "statistics", "data visualization", "sql", "pandas"],
        "web developer": ["html", "css", "javascript", "react", "node.js", "git"]
    }

    role = position.lower()
    required_skills = job_requirements.get(role, ["communication", "teamwork", "problem-solving"])
    
    # Calculate missing skills
    missing_skills = [skill for skill in required_skills if skill not in current_skills]

    return jsonify({"skills": missing_skills})

if __name__ == '__main__':
    app.run(debug=True)
