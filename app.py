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
    skills = data['skills']

    # Temporary response
    return jsonify({
        "skills": ["AI", "Cloud Computing", "Leadership"]  # mock response
    })

if __name__ == '__main__':
    app.run(debug=True)
