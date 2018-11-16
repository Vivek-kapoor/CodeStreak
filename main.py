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

@app.route('/profile_page')
def profile_page():
	return route_profile_page()

@app.route('/about_us')
def about_us():
	return route_about_us()


@app.route('/prof_page')
def prof_page():
	return render_template("login.html", name = "Professor")

@app.route('/student_page')
def student_page():
	return render_template("login.html", name = "Student")

@app.route("/student_login", methods=["GET", "POST"])
def student_login():
	return route_student_login()

@app.route("/student_dashboard", methods=["GET", "POST"])
def student_dashboard():
	return route_student_dashboard()

@app.route("/prof_login", methods=["GET", "POST"])
def prof_login():
	return route_prof_login()

@app.route("/professor_dashboard", methods=["GET", "POST"])
def professor_dashboard():
	return route_professor_dashboard()

@app.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
	return route_create_assignment()

@app.route("/add_questions", methods=["GET", "POST"])
def add_questions():
	return route_add_questions()

@app.route("/contest_page/<cid>", methods=["GET", "POST"])
def contest_page(cid):
	return contest_questions(cid)


@app.route("/archive_lab_question/<qid>", methods=["GET", "POST"])
def archive_lab_question(qid):
	session['q_id'] = qid
	return route_submission()


@app.route("/lab_question/<qid>")
def lab_question(qid):
	return show_question(qid)

@app.route("/contest_leaderboard")
def contest_leaderboard():
	cid = session['c_id']
	return route_contest_leaderboard(cid)



@app.route('/contest_report/<cid>', methods=['POST', 'GET'])
def contest_report(cid):
	return route_contest_report(cid)

@app.route("/runc", methods=['POST', 'GET'])
def runc():
	return route_runc("1")

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
