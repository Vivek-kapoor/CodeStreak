# import os
# from flask import Flask, render_template, request
# from db_access import validate_student, validate_professor
# from contest_info import contest_list
import os
from flask import Flask, render_template
from routes import *
# SESSION = dict()

app = Flask(__name__)
app._static_folder = os.path.join(os.getcwd(),"static")
app.config['SECRET_KEY'] = '59d3ca27e6701d3fd06eb960ca5866a5'

@app.route('/')
def codestreak():
	return route_codestreak()


@app.route('/prof_page')
def prof_page():
	return render_template("login.html", name = "Professor")

@app.route('/student_page')
def student_page():
	return render_template("login.html", name = "Student")

@app.route("/student_login", methods=["GET", "POST"])
def student_login():
	return route_student_login()

@app.route("/prof_login", methods=["GET", "POST"])
def prof_login():
	return route_prof_login()

@app.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
	return route_create_assignment()

@app.route("/add_questions", methods=["GET", "POST"])
def add_questions():
	return route_add_questions()

@app.route("/contest_page", methods=["GET", "POST"])
def contest_page():
	return contest_questions()

@app.route("/lab_question", methods=["GET", "POST"])
def lab_question():
	return show_question()



@app.route("/submission", methods = ['POST'])
def submission():
	return route_submission()

@app.route("/cpp")
@app.route("/runcpp", methods=['POST', 'GET'])
def runcpp():
	return route_runcpp()

@app.route("/py")
@app.route("/runpy", methods=['POST', 'GET'])
def runpy():
	return route_runpy()

if (__name__ == "__main__"):
    app.run(debug=True)
# @app.route('/student_login',methods = ['POST', 'GET'])
# def student_login():

# 	if request.method == 'POST':
# 		print("here")
# 		usn = request.form['usn']
# 		password = request.form['password']

# 		if validate_student(usn, password):
# 			return contest_list(usn)
# 		else:
# 			return render_template("check.html")
