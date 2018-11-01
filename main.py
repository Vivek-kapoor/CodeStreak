from flask import Flask, render_template, request

app = Flask(__name__)
app._static_folder = "C:/Users/Varun/Documents/SE/CodeStreak/static"


@app.route('/')
def codestreak():
	return render_template("login.html")



@app.route('/login',methods = ['POST', 'GET'])

def login():

	if request.method == 'POST':
		print("here")
		username = request.form['usn']
		password = request.form['password']

		if username == "usn":
			print(username)
			return render_template("check.html")



if __name__ == '__main__':
   app.run(debug = True)




