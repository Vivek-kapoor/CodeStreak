import code
import random

from flask import render_template, redirect, url_for, request, session, flash

import db_access as db
from runcode import runcode
qid=0
temp=""
default_c_code = """#include <stdio.h>

int main(int argc, char **argv)
{
    printf("Hello C World!!\\n");
    return 0;
}    
"""

default_cpp_code = """#include <iostream>

using namespace std;

int main(int argc, char **argv)
{
    cout << "Hello C++ World" << endl;
    return 0;
}
"""

default_py_code = """import sys
import os

if __name__ == "__main__":
    print "Hello Python World!!"
"""

default_rows = "15"
default_cols = "60"
Index = 0
test_case_output="hello"

def route_codestreak():
    return render_template("index.html")


def student_dashboard(usn):

    active_contests = db.get_active_contest_student(usn)
    archived_contests = db.get_archived_contest_student(usn)
    #active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
    #archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
    #contests = active_contests + archived_contests    
    return render_template("Student Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)

def professor_dashboard(usn):

    active_contests = db.get_active_contest_professor(usn)
    archived_contests = db.get_archived_contest_professor(usn)
    #active_contests = [{'name': "kys", 'time': "now"},{'name': "gabe", 'time': "now"}]
    #archived_contests = [{'name': "kys1", 'time': "now"},{'name': "gabe1", 'time': "now"}]

    return render_template("Prof_Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)


def get_question(contest_id):
    #Get all questions in a contest
    #return: list of dicts. Each dict represents on question
    #check for the relevant question 
    # output_dict wil be a list of dicts, one dict for each question, 
    output_dict = db.get_questions_by_contest(contest_id)
    print(output_dict)
    data = {}
    # we only need one question , so we match the q_id with the session's q_id
    #DUMMY variable for testing
    session = {}
 

    for each_question in output_dict:
        #comment the next line after testing
        session['q_id'] = each_question['q_id']
        if(each_question['q_id']==session['q_id']):  
            data["name"] = each_question['name']
            data["question"] = each_question['problem']
            data["difficulty"] = each_question['difficulty']
            data["time"] = each_question['time_limit']
            data["memory"] = each_question['memory_limit']
            data["tags"] = each_question['tags'] 
            data["test_cases"]=each_question['test_cases']
    return data

# called when user is student
def route_student_login():
    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data):
        
        data['usn'] = ''.join(data['usn'])
        data['password'] = ''.join(data['usn'])

        response = db.validate_student(**data)
        if (response):
        
            session['usn'] = data['usn']
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
            session['p_id'] = data['p_id']
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
        data['end'] = ''.join(data['end'])


        request_data['p_id'] = session['p_id']
        request_data['name'] = data['contest name']
        request_data['start_time'] = data['begin']
        request_data['end_time'] = data['end']
        request_data['questions'] = set(data['questions'])
        request_data['semester'] = data['sem']
        request_data['section'] = data['sec']
        print("Request Data -> ", request_data)

        db.create_contest(**request_data)

        return professor_dashboard(request_data['p_id'])
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
        # data['tags'] = ''.join(data['tags'])
        data['memory_limit'] = float(''.join(data['memory_limit']))
        data['time_limit'] = float(''.join(data['time_limit']))
        data['languages'] = set(data['languages'])

        num_of_testcases = int(len(files) / 2)
        testcases = []
        request_data = {}
        for i in range(1, num_of_testcases + 1):
            testcases.append({
                "input": files['input' + str(i)].read().decode("utf-8"),
                "output": files['output' + str(i)].read().decode("utf-8"),
                "points": float(data["point" + str(i)][0])
            })
        request_data['p_id'] = session['p_id']
        request_data['test_cases'] = testcases
        # request_data['q_id'] = None
        request_data['test_cases'] = testcases
        request_data['name'] = data['name']
        request_data['problem'] = data['statement']
        request_data['difficulty'] = data['difficulty']
        request_data['time_limit'] = data['time_limit']
        request_data['memory_limit'] = data['memory_limit']
        request_data['languages'] = data['languages']
        # request_data['tags'] = data['tags']
        request_data['tags'] = {"warmup"}

        db.create_question(**request_data)
        flash("Added successfully")
    questions = db.get_questions()
    return render_template("ql.html", questions = questions)


def route_contest_leaderboard(cid):

    leaderboard_by_contest = db.get_leaderboard(cid)
    leaderboard_by_contest = sorted(leaderboard_by_contest, key=lambda k: (-k['score'], k['penalty']))
    return render_template("leaderboard.html", leaderboard = leaderboard_by_contest)



def route_contest_report(cid):
    questions_by_contest = db.get_questions_by_contest(cid)
    submissions_by_contest = db.get_submissions_by_contest(cid)
    leaderboard_by_contest = db.get_leaderboard(cid)
    leaderboard_by_contest = sorted(leaderboard_by_contest, key=lambda k: (-k['score'], k['penalty']))
    print("Submission ->", submissions_by_contest)

    return render_template("prof_Rep.html", questions = questions_by_contest, submissions = submissions_by_contest, 
        leaderboard = leaderboard_by_contest, tag="question")

def show_question(qid):

    #data = request.form.to_dict(flat=False)
    session['q_id'] = qid
    #q_id = session['q_id']
    return route_runc(qid)


def contest_questions():

    data = request.form.to_dict(flat=False)
    if(data):
       c_id = ''.join(data['c_id'])
       c_name = ''.join(data['c_name'])
       s_time = ''.join(data['s_time'])
       e_time = ''.join(data['e_time'])
       status = ''.join(data['status'])
       questions = db.get_questions_by_contest(c_id)
       session['c_id'] = c_id
       return render_template("lab_questions.html", questions=questions, c_name=c_name, s_time=s_time, e_time=e_time, status=status)

qid=0
def route_runc(q_id):
    #The q_id here is the question id which the student clicked on, I have verfied it and it is the right id.
    #You can also access q_id with session['q_id']
    #the control here is passed from show_question
    
    print(q_id)
    global qid
    if(qid == 0 or q_id !="1"):
        qid=q_id
    
    question =  db.get_question_details(qid)
    if request.method == 'POST':
        code = request.form['code']
        print(code)
        resinput = format(request.form['resinput'])
        custom_input = False
        if(len(resinput)>=1):
            print("custom_input is TRUE")
            custom_input = True
        global Index
        Index += 1
        ID = Index
        instr = "./running/input"+str(ID)+".txt"
        f = open(instr,"w")
        f.write(resinput)
        f.close()  
        run = runcode.RunCCode(question,code,custom_input,Index)
        rescompil, resrun , display_outputi = run.run_c_code()
        
       
        if not resrun:
            resrun = 'No result! no run yet.'
    else:
        code = default_c_code
        resrun = 'No result! no run yet.'
        rescompil = ''
        display_outputi={}
    
    return render_template("main.html",
                           question= question,
                           code=code,    
                           target="runc",
                           resrun=resrun,
                           rescomp=rescompil,
                           display_output = display_outputi,
                           rows=default_rows, cols=default_cols)


def route_submission():
        output=runcode.RunCCode(question="")
        test_case_output=output.all_submissions()
        if(test_case_output == None):
            return render_template("Table/table.html",output = [{"status":"No submissions to show", "score":"","test_case_status":"","submit_time":""}])
        return render_template("Table/table.html",output=test_case_output)


def route_runcpp():
    if request.method == 'POST':
        code = request.form['code']
        run = runcode.RunCppCode(code)
        rescompil, resrun = run.run_cpp_code()
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_cpp_code
        resrun = 'No result!'
        rescompil = ''
    return render_template("main.html",
                           code=code,
                           target="runcpp",
                           resrun=resrun,
                           rescomp=rescompil,
                           rows=default_rows, cols=default_cols)


def route_runpy():
    if request.method == 'POST':
        code = request.form['code']
        run = runcode.RunPyCode(code)
        rescompil, resrun = run.run_py_code()
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_py_code
        resrun = 'No result!'
        rescompil = "No compilation for Python"
        
    return render_template("main.html",
                           code=code,
                           target="runpy",
                           resrun=resrun,
                           rescomp=rescompil,#"No compilation for Python",
                           rows=default_rows, cols=default_cols)