from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

filename = 'anxiety_model (1).pkl'
model = pickle.load(open(filename, 'rb'))

@app.route('/')
def index():
    return render_template("bmi.html")

@app.route('/submit_bmi', methods=['POST'])
def submit_bmi():
    global bmi
    global who_bmi
    bmi = request.form.get("bmi")
    who_bmi = request.form.get("who_bmi")
    bmi = float(bmi)
    who_bmi = float(who_bmi)
    return render_template("GAD_7.html")

@app.route('/submit_gad', methods=['POST'])
def submit_gad():
    global gad_score
    gad_score = request.form.get("gad_score")
    gad_score = int(gad_score)
    print(f"Your GAD score is: {gad_score}")
    return render_template("phq.html")

@app.route('/submit_phq', methods=['POST'])
def submit_phq():
    global phq_score
    phq_score = request.form.get("phq_score")
    phq_score = int(phq_score)  # Convert to integer if needed
    return render_template("test.html")

@app.route('/res', methods=['POST'])
def result():
    global bmi, who_bmi, phq_score, gad_score

    # Get form inputs
    mc1 = request.form.get("gender")
    mc2 = bmi
    mc3 = who_bmi
    mc4 = phq_score
    mc6 = gad_score
    mc7 = request.form.get("sleepiness")
    mc8 = request.form.get("epworth_score")

    # Determine depressiveness score based on PHQ score
    if 0 <= mc4 <= 4:
        depressiveness = 0
    elif 5 <= mc4 <= 14:
        depressiveness = 1
    elif 15 <= mc4 <= 27:
        depressiveness = 3
    else:
        depressiveness = 4

    mc5 = depressiveness

    # Prepare inputs for the model
    inputs = [[float(mc1), float(mc2), float(mc3), float(mc4), float(mc5), float(mc6), float(mc7), float(mc8)]]

    # Make predictions using the pre-trained model
    y_pred = model.predict(inputs)

    # Generate results based on the predictions
    results = []

    # Anxiousness Status
    if y_pred[0][0] == 0:
        results.append("You are not exhibiting signs of anxiety at the moment. Your current state seems calm and stable.")
    elif y_pred[0][0] == 1:
        results.append("You are exhibiting signs of anxiety. It may be beneficial to monitor your emotions and consider coping strategies.")
    else:
        results.append("Anxiety status is unidentified. Please consult a healthcare professional if needed.")

    # Anxiety Severity
    if y_pred[0][1] == 1:
        results.append("You are experiencing mild anxiety. It may not significantly impact your daily life, but managing stress and relaxation techniques could help.")
    elif y_pred[0][1] == 2:
        results.append("You are experiencing moderate anxiety. This level could affect daily activities, and it's advisable to explore anxiety management strategies.")
    elif y_pred[0][1] == 3:
        results.append("You are not experiencing anxiety. Keep maintaining healthy emotional well-being.")
    elif y_pred[0][1] == 4:
        results.append("You are experiencing severe anxiety. This could be debilitating and seeking professional help would be strongly recommended.")
    else:
        results.append("Anxiety severity is unidentified.")

    # Diagnosis Recommendation
    if y_pred[0][2] == 0:
        results.append("No formal anxiety diagnosis is required based on your current condition. However, staying mindful of your emotional health is always beneficial.")
    elif y_pred[0][2] == 1:
        results.append("An anxiety diagnosis is recommended. Seeking professional evaluation might help clarify your mental health status.")
    else:
        results.append("Diagnosis recommendation is unidentified.")

    # Treatment Suggestion
    if y_pred[0][3] == 1:
        results.append("It's advised that you pursue treatment for anxiety. Therapeutic methods or professional guidance could be helpful in managing your condition.")
    elif y_pred[0][3] == 0:
        results.append("You currently don't require specific anxiety treatment, but maintaining mental wellness is important.")
    else:
        results.append("Treatment suggestion is unidentified.")

    # Suicidal Thoughts
    if y_pred[0][4] == 1:
        results.append("There is a potential risk of developing suicidal thoughts. Please seek immediate support from mental health professionals or loved ones.")
    elif y_pred[0][4] == 0:
        results.append("Your mental health appears to be stable with no signs of suicidal thoughts. Continue to care for your emotional well-being.")
    else:
        results.append("Suicidal thoughts status is unidentified.")

    # Display the results on the page
    return "<br>".join(results)

if __name__ == '__main__':
    app.run(debug=True)
