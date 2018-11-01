from flask import Flask, render_template, redirect, url_for, request, session
import psycopg2

# from werkzeug import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '59d3ca27e6701d3fd06eb960ca5866a5'

try:
    conn = psycopg2.connect("dbname='temp' user='postgres' host='localhost' password='welcomeback'")
    print("connected")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

@app.route("/")
@app.route("/home",methods = ["POST","GET"])
def home():
	return render_template('front_login.html')

@app.route("/student_login", methods = ["GET", "POST"])
def student_login():
	data = request.form.to_dict(flat=False)
	# verify the credentail of users
	if(data):
		response = query_student_login(data)
		if(response):
			session['usn'] = data['usn']
			return "successfully loggedin"
		else:
			return render_template('student_login.html')
	return render_template('student_login.html')
if(__name__ == "__main__"):
	app.run(debug=True)