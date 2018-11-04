from flask import Flask, render_template, redirect, url_for, request, session, flash
from db_access import create_contest

app = Flask(__name__)
app.config['SECRET_KEY'] = '59d3ca27e6701d3fd06eb960ca5866a5'


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template('front_login.html')


# called when user is student
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data):
        response = validate_student(data)
        if (response):
            session['id'] = data['usn']
            return "successfully loggedin"
        else:
            return render_template('student_login.html')
    return render_template('student_login.html')

@app.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
    data = request.form.to_dict(flat=False)
    if (data):
        request_data = {}
        # request_data['c_id'] = NULL # this will be created by database
        request_data['p_id'] = session['id']
        request_data['name'] = data['name']
        request_data['start_time'] = data['Contest Begin']
        request_data['end_time'] = data['Contest End']
        request_data['questions'] = data['questions']
        request_data['semester'] = data['sem']
        request_data['section'] = data['sec']
        create_contest(**request_data)
        flash("Contest Created successfully")
        return "Contest Created successfully"
    else:
        # return value of the functions should be list
        # of dicts where each dict is a row of question table
        questions = questions_list()
        return render_template("UpdatedcreateLab.html",
                               questions=questions)

@app.route("/add_questions", methods=["GET", "POST"])
def add_questions():
    data = request.form.to_dict(flat=False)
    print(data)
    if (data):
        files = request.files
        num_of_testcases = int(len(files) / 2)
        testcases = []
        request_data = {}
        for i in range(1, num_of_testcases + 1):
            testcases.append({
                "input": files['input' + str(i)].read().decode("utf-8"),
                "output": files['output' + str(i)].read().decode("utf-8"),
                "point": float(data["point" + str(i)][0])
            })
        request_data['q_id'] = None
        request_data['testcases'] = testcases
        request_data['name'] = data['name']
        request_data['problem'] = data['statement']
        request_data['difficulty'] = data['difficulty']
        request_data['tags'] = data['tags']
        create_question(**request_data)
        flash("Added successfully")
        return render_template("ql.html")
    else:
        questions = questions_list()
        return render_template("ql.html", questions = questions)


if (__name__ == "__main__"):
    app.run(debug=True)
