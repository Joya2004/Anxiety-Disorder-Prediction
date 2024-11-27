from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load the trained model
filename = 'anxiety_model (1).pkl'
model = pickle.load(open(filename, 'rb'))

@app.route('/')
def front():
    return render_template("FrontPage.html")

@app.route('/bmi')
def bmi_page():
    return render_template("BMI2.html")

@app.route('/submit_bmi', methods=['POST'])
def submit_bmi():
    global bmi, who_bmi
    bmi = request.form.get("bmi")
    who_bmi = request.form.get("who_bmi")
    
    try:
        bmi = float(bmi)  # Convert BMI to float
    except ValueError:
        return "Invalid BMI value", 400  # Return error if BMI is not a valid number

    # Data passed to the next page
    return render_template("GAD_71.html")

@app.route('/submit_gad', methods=['POST'])
def submit_gad():
    global gad_score
    gad_score = request.form.get("gad_score")
    try:
        gad_score = int(gad_score)
    except ValueError:
        return "Invalid GAD score", 400
    return render_template("phq.html")

@app.route('/submit_phq', methods=['POST'])
def submit_phq():
    global phq_score
    phq_score = request.form.get("phq_score")
    try:
        phq_score = float(phq_score)
    except ValueError:
        return "Invalid PHQ score", 400
    return render_template("test.html")

@app.route('/res', methods=['POST'])
def result():
    global bmi, who_bmi, phq_score, gad_score

    # Retrieve inputs from the form
    mc1 = request.form.get("gender")  # Gender
    mc7 = request.form.get("sleepiness")  # Sleepiness
    mc8 = request.form.get("epworth_score")  # Epworth Sleepiness Score

    # Map WHO BMI classification to numeric values
    who_bmi_mapping = {
        'Underweight': 0,
        'Normal weight': 1,
        'Overweight': 2,
        'Obesity': 3
    }
    mc3 = who_bmi_mapping.get(who_bmi)
    if mc3 is None:
        return "Invalid WHO BMI classification", 400

    # Determine depressiveness score based on PHQ score
    if 0 <= phq_score <= 4:
        depressiveness = 0
    elif 5 <= phq_score <= 14:
        depressiveness = 1
    elif 15 <= phq_score <= 27:
        depressiveness = 3
    else:
        depressiveness = 4
    mc5 = depressiveness

    # Convert all inputs to float
    try:
        inputs = [[
            float(mc1),  # Gender
            float(bmi),  # BMI
            float(mc3),  # WHO BMI classification
            float(phq_score),  # PHQ score
            float(mc5),  # Depressiveness
            float(gad_score),  # GAD score
            float(mc7),  # Sleepiness
            float(mc8)   # Epworth Sleepiness Score
        ]]
    except ValueError as e:
        return f"Invalid input data: {e}", 400

    # Predict with the model
    y_pred = model.predict(inputs)

    # Generate results
    results = []

    if y_pred[0][0] == 0:
        results.append("You are not exhibiting signs of anxiety at the moment.")
    elif y_pred[0][0] == 1:
        results.append("You are exhibiting signs of anxiety.")
    else:
        results.append("Anxiety status is unidentified.")

    if y_pred[0][1] == 1:
        results.append("You are experiencing mild anxiety.")
    elif y_pred[0][1] == 2:
        results.append("You are experiencing moderate anxiety.")
    elif y_pred[0][1] == 3:
        results.append("You are not experiencing anxiety.")
    elif y_pred[0][1] == 4:
        results.append("You are experiencing severe anxiety.")

    if y_pred[0][2] == 0:
        results.append("No formal anxiety diagnosis is required.")
    elif y_pred[0][2] == 1:
        results.append("An anxiety diagnosis is recommended.")

    if y_pred[0][3] == 1:
        results.append("It's advised that you pursue treatment for anxiety.")
    elif y_pred[0][3] == 0:
        results.append("You currently don't require specific anxiety treatment.")

    if y_pred[0][4] == 1:
        results.append("There is a potential risk of developing suicidal thoughts.")
    elif y_pred[0][4] == 0:
        results.append("Your mental health appears stable with no signs of suicidal thoughts.")

    return render_template("results.html", results="<br>".join(results))

if __name__ == '__main__':
    app.run(debug=True)
