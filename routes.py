from flask import render_template, redirect, url_for, request, session, flash
from db_access import validate_student, validate_professor, create_contest, get_questions, create_question

def route_codestreak():
    return render_template("login.html")

def contest_list(usn):

    #active_contests = get_active_contest(usn)
    #archivef_contests = get_archived_contest(usn)
    active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
    archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
    #contests = active_contests + archived_contests    
    return render_template("Student Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)


# called when user is student
def route_student_login():
    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data):
        response = validate_student(**data)
        if (response):
            session['id'] = data['usn']
            return contest_list(usn)
        else:
            return render_template('login.html')
    return render_template('login.html')


def route_prof_login():
    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data):
        response = validate_professor(**data)
        if (response):
            session['id'] = data['usn']
            return "successfully logged-in"
        else:
            return render_template('login.html')
    return render_template('login.html')

def route_create_assignment():
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
        questions = get_questions()
        return render_template("UpdatedcreateLab.html",
                               questions=questions)

def route_add_questions():
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
        questions = get_questions()
        return render_template("ql.html", questions = questions)