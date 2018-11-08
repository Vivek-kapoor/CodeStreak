from flask import render_template, redirect, url_for, request, session, flash
#from db_access import validate_student, validate_professor, create_contest, get_questions, create_question, get_active_contest_student, get_archived_contest_student
import db_access as db 
def route_codestreak():
    return render_template("index.html")

def student_dashboard(usn):

    #active_contests = db.get_active_contest_student(usn)
    archived_contests = db.get_archived_contest_student(usn)
    active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
    #archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
    #contests = active_contests + archived_contests    
    return render_template("Student Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)

def professor_dashboard(usn):

    #active_contests = get_active_contest_professor(usn)
    #archivef_contests = get_archived_contest_professor(usn)
    active_contests = [{'name': "kys", 'time': "now"},{'name': "gabe", 'time': "now"}]
    archived_contests = [{'name': "kys1", 'time': "now"},{'name': "gabe1", 'time': "now"}]

    return render_template("Prof_Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)




# called when user is student
def route_student_login():
    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data):
        
        data['usn'] = ''.join(data['usn'])
        data['password'] = ''.join(data['usn'])

        response = db.validate_student(**data)
        if (response):
        
            session['id'] = data['usn']
            return student_dashboard(data['usn'])
        else:
            return render_template('login.html', name = "Student")
    return render_template('login.html', name = "Student")


def route_prof_login():

    data = request.form.to_dict(flat=False)

    # verify the credentail of users
    if (data):
                    
        data['p_id'] = ''.join(data['p_id'])
        data['password'] = ''.join(data['password'])

        # del data['usn']
        # del data['p_password']
        # del data['p_usn']

        print("Data-> ", data)

        response = db.validate_professor(**data)
        #if (response):
        if 1:
            print('here')
            session['id'] = data['p_id']
            return professor_dashboard(data['p_id'])
        else:
            return render_template('login.html',name = "Professor")
    return render_template('login.html',name = "Professor")

def route_create_assignment():
    data = request.form.to_dict(flat=False)
    if (data):
        request_data = {}
        # request_data['c_id'] = NULL # this will be created by database

        data['contest name'] = ''.join(data['contest name'])
        data['sem'] = ''.join(data['sem'])
        data['sec'] = ''.join(data['sec'])
        data['begin'] = ''.join(data['begin'])
        data['end'] = ''.join(data['begin'])


        request_data['p_id'] = session['id']
        request_data['name'] = data['contest name']
        request_data['start_time'] = data['begin']
        request_data['end_time'] = data['end']
        request_data['questions'] = set(data['questions'])
        request_data['semester'] = data['sem']
        request_data['section'] = data['sec']
        print("Request Data -> ", request_data)

        db.create_contest(**request_data)
        flash("Contest Created successfully")
        return "Contest Created successfully"
    else:
        # return value of the functions should be list
        # of dicts where each dict is a row of question table
        questions = db.get_questions()
        return render_template("CreateContest_css.html",
                               questions=questions)

def route_add_questions():
    data = request.form.to_dict(flat=False)
    print(data)
    if (data):
        files = request.files

        data['name'] = ''.join(data['name'])
        data['statement'] = ''.join(data['statement'])
        data['difficulty'] = ''.join(data['difficulty'])
        data['tags'] = ''.join(data['tags'])

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

        db.create_question(**request_data)
        flash("Added successfully")
        return render_template("ql.html")
    else:
        questions = db.get_questions()
        return render_template("ql.html", questions = questions)

def contest_questions():

    data = request.form.to_dict(flat=False)
    if(data):
       c_id = ''.join(data['c_id'])
       c_name = ''.join(data['c_name'])
       s_time = ''.join(data['s_time'])
       e_time = ''.join(data['e_time'])
       questions = db.get_questions_by_contest(c_id)
       return render_template("lab_questions.html", questions=questions, c_name=c_name, s_time=s_time, e_time=e_time)
