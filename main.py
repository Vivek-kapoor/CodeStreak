import os
from flask import Flask, render_template, request
from db_access import validate_student, validate_professor
from contest_info import active_contest_list

SESSION = dict()

app = Flask(__name__)
app._static_folder = os.path.join(os.getcwd(),"static")


@app.route('/')
def codestreak():
	return render_template("login.html")



@app.route('/student_login',methods = ['POST', 'GET'])

def student_login():

	if request.method == 'POST':
		print("here")
		usn = request.form['usn']
		password = request.form['password']

		if validate_student(usn, password):
			return active_contest_list(usn)
		else:
			return render_template("check.html")





if __name__ == '__main__':
   app.run(debug = True)




