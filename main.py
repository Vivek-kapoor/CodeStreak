import sys
from flask import Flask, render_template, request
from db_access import validate_student, validate_professor

app = Flask(__name__)
app._static_folder = "/home/t/CodeStreak/static"


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
			return render_template("check.html")
		else:
			return render_template("login.html")





if __name__ == '__main__':
   app.run(debug = True)




