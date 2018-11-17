"""
This file contains the code to route to different parts of the application
Run this file to start the application and to verify type http://localhost:5000 in browsers url
If it doesn't throw an error, it works!

CONTENTS:
1. codestreak			: Starting point of the application
2. profile_page			: Get the profile page of the student
3. about_us			: Get this application developers info
4. logout			: Logout from the application
5. prof_page			: Loads login page for the professor 
6. student_page			: Loads login page for the Student
7. student_login		: Verify student credentail
8. student_dashboard		: Loads student dashboard page
9. prof_login			: Verify professor credentail
10.professor_dashboard		: Loads professor dashboard page
11.admin_dashboard		: Loads admins dashboard page
12.create_assignment		: Create new lab assignment
13.add_questions		: Adds question to the question library
14.contest_page			: Shows all the questions for the selected contest/lab
15.archive_lab_question		: Shows all the submission for particular question
16.lab_question			: Loads ide for selected question in the contest/lab
17.contest_leaderboard		: Gets the leaderboard for the contest/lab 
18.contest_report		: Called from prof session to get the report for the contest
19.runc				: Loads ide for c code
20.submission			:
21.runcpp			: Loads ide for c code
22.runpy			: Loads ide for c code
"""

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

@app.route('/logout')
def logout():
	return route_logout()

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

@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
	return route_admin_dashboard()

@app.route("/set_location", methods=["GET", "POST"])
def set_location():
	return route_set_location()

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

@app.route('/contest_report/<cid>/<tag>', methods=['POST', 'GET'])
def contest_report(cid,tag):
	return route_contest_report(cid,tag)

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
