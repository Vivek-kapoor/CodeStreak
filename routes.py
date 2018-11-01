from flask import Flask, render_template, redirect, url_for, request, session

@app.route("/")
@app.route("/home",methods = ["POST","GET"])
def home():
	return render_template('front_login.html')


# called when user is student
@app.route("/student_login", methods = ["GET", "POST"])
def student_login():
	data = request.form.to_dict(flat=False)
	# verify the credentail of users
	if(data):
		response = query_student_login(data)
		if(response):
			session['id'] = data['usn']
			return "successfully loggedin"
		else:
			return render_template('student_login.html')
	return render_template('student_login.html')

@app.route("/create_assignment", methods = ["GET", "POST"])
def create_assignment():
	data = request.form.to_dict(flat=False)
	if(data):
		request_data = {}
		request_data['c_id'] = NULL
		request_data['p_id'] = session['id']
		request_data['name'] = data['name']
		request_data['start_time'] = data['Contest Begin']
		request_data['end_time'] = data['Contest End']
		request_data['q_ids'] = data['questions']
		request_data['semester'] = data['sem']
		request_data['section'] = data['sec']
		add_contest(request_data)
		flash("Contest Created successfully")
		return "Contest Created successfully"
	else:
		# return value of the functions should be list
		# of dicts where each dict is a row of question table
		questions = question_list()
		return render_template("UpdatedcreateLab.html", 
			questions = questions)


if(__name__ == "__main__"):
	app.run(debug=True)