import code
import random
import logging
import re
logging.basicConfig(level="CRITICAL")
from flask import render_template, redirect, url_for, request, session, flash
from graph import draw_submission_chart

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
    print("------------------------------------")
    print("Session in route_codestreak ",session)
    print("------------------------------------")
    return render_template("index.html")

def route_profile_page():

    student_details = db.get_student_details(session['usn'], get_ranks=False)
    rating = student_details['rating']
    best_rating = student_details['best']
    semester = student_details['semester']
    section = student_details['section']
    usn = session['usn']
    name = session['name']
    img_path = "plots/"+ usn + ".png"
    
    
    


    stats = db.get_submission_distribution(usn)
    draw_submission_chart(stats, usn)

    return render_template("Student_profile.html", rating=rating, best_rating=best_rating, semester=semester, section=section, usn=usn, name=name, img_path=img_path)

def route_about_us():
    return render_template("AboutUS.html")

def route_logout():
    session.clear()
    return render_template("index.html")


def route_student_dashboard():
    print("------------------------------------")
    print("Session in Student ",session)
    print("------------------------------------")
    active_contests = db.get_active_contest_student(session['usn'])
    archived_contests = db.get_archived_contest_student(session['usn'])
    #active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
    #archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
    #contests = active_contests + archived_contests    
    return render_template("Student Dashboard.html", active_contests = active_contests, archived_contests = archived_contests, name = session['name'])

def route_professor_dashboard():

    print("------------------------------------")
    print("Session in professor ",session)
    print("------------------------------------")
    active_contests = db.get_active_contest_professor(session['p_id'])
    archived_contests = db.get_archived_contest_professor(session['p_id'])
    #active_contests = [{'name': "kys", 'time': "now"},{'name': "gabe", 'time': "now"}]
    #archived_contests = [{'name': "kys1", 'time': "now"},{'name': "gabe1", 'time': "now"}]

    return render_template("Prof_Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)


def get_question(contest_id):
    #Get all questions in a contest
    #return: list of dicts. Each dict represents on question
    #check for the relevant question 
    # output_dict wil be a list of dicts, one dict for each question, 
    print("------------------------------------")
    print("Session in get_question ",session)
    print("------------------------------------")
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

    print("------------------------------------")
    print("Session in route_student_login ",session)
    print("------------------------------------")

    if('usn' in session.keys()):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return redirect(url_for('student_dashboard'))

    data = request.form.to_dict(flat=False)
    # verify the credentail of users
    if (data): #why is it so 
        
        data['usn'] = ''.join(data['usn'])
        data['password'] = ''.join(data['password'])
        print("##############################################################################################################")
        print(data)
        
        response = db.validate_student(**data)
        print('########', response)
        if (response): # this is required in order to validate the user in database. wait. i'll call on whatsapp
            session['usn'] = data['usn'] # wait i will call if i shift my phone my internet goes ok
            student_details = db.get_student_details(data['usn'], get_ranks=False)
            print("###################################")
            session['name'] = student_details['name'] #i think this is correct.no i haven't added the above line. 
            return redirect(url_for('student_dashboard')) 
        else:
            return render_template('login.html', name = "Student")
    return render_template('login.html', name = "Student")


def route_prof_login():

    print("------------------------------------")
    print("Session in route_prof_login ",session)
    print("------------------------------------")

    if('p_id' in session.keys()):
        return redirect(url_for('professor_dashboard'))
    data = request.form.to_dict(flat=False)

    # verify the credentail of users
    if (data):
                    
        data['p_id'] = ''.join(data['p_id'])
        data['password'] = ''.join(data['password'])
        print("Data-> ", data)

        response = db.validate_professor(**data)

        if (response):
            print('here')
            session['p_id'] = data['p_id']
            return redirect(url_for('professor_dashboard'))
    return render_template('login.html',name = "Professor")

def route_create_assignment():
    print("------------------------------------")
    print("Session in route_create_assignment ",session)
    print("------------------------------------")
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

        return redirect(url_for('professor_dashboard'))
    else:
        # return value of the functions should be list
        # of dicts where each dict is a row of question table
        questions = db.get_questions()
        return render_template("CreateContest_css.html",
                               questions=questions)

def route_add_questions():

    print("------------------------------------")
    print("Session in route_add_questions ",session)
    print("------------------------------------")

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
    print("------------------------------------")
    print("Session in route_contest_report ",session)
    print("------------------------------------")

    questions_by_contest = db.get_questions_by_contest(cid)
    submissions_by_contest = db.get_submissions_by_contest(cid)
    leaderboard_by_contest = db.get_leaderboard(cid)
    leaderboard_by_contest = sorted(leaderboard_by_contest, key=lambda k: (-k['score'], k['penalty']))
    print("Submission ->", submissions_by_contest)
    #fetching the plagiarism report
    plag_report = db.get_plagiarism_report(cid)


    if((plag_report[0]['plagiarism'])==None):
        plag_report[0]['plagiarism'] = "empty"
    else:
        for i in range(len(plag_report[0]['plagiarism'])):
            plag_report[0]['plagiarism'][i]["q_id"] = plag_report[0]['plagiarism'][i]["q_id"].split('/')[-1]
            for j in range(len(plag_report[0]['plagiarism'][i]['report'])):
                if(len(plag_report[0]['plagiarism'][i]['report'][j])==3):
                    plag_report[0]['plagiarism'][i]['report'][j][0] = plag_report[0]['plagiarism'][i]['report'][j][0].split('/')[-1]
                    plag_report[0]['plagiarism'][i]['report'][j][1] = plag_report[0]['plagiarism'][i]['report'][j][1].split('/')[-1]
                    print( plag_report[0]['plagiarism'][i]['report'][j][0])
                    print(re.findall("[0-9]*%",plag_report[0]['plagiarism'][i]['report'][j][0]))
                    plag_report[0]['plagiarism'][i]['report'][j].append(re.findall("[0-9]*%",plag_report[0]['plagiarism'][i]['report'][j][0])[0])
                    plag_report[0]['plagiarism'][i]['report'][j][0] = re.sub('\([0-9%]*\)', '',plag_report[0]['plagiarism'][i]['report'][j][0] )
                    plag_report[0]['plagiarism'][i]['report'][j][1] = re.sub('\([0-9%]*\)', '',plag_report[0]['plagiarism'][i]['report'][j][1] )

    return render_template("prof_Rep.html", plag_report = plag_report ,questions = questions_by_contest, submissions = submissions_by_contest, 
        leaderboard = leaderboard_by_contest, tag="question")

def show_question(qid):
    print("------------------------------------")
    print("Session in show_question ",session)
    print("------------------------------------")

    #data = request.form.to_dict(flat=False)
    session['q_id'] = qid
    #q_id = session['q_id']
    return route_runc(qid)

def contest_questions(cid):
    session['c_id'] = cid
    print("------------------------------------")
    print("Session in contest_questions ",session)
    print("------------------------------------")
    contest_info = db.get_contest_details(session['c_id'])
    questions = db.get_questions_by_contest(session['c_id'])

    print("====================================")
    print("start_time ",contest_info['start_time'])
    print("====================================")
    
    return render_template("lab_questions.html", questions=questions, c_name=contest_info['name'], 
        s_time=contest_info['start_time'], e_time=contest_info['end_time'], status = contest_info['status'])

qid=0
def route_runc(q_id):
    #The q_id here is the question id which the student clicked on, I have verfied it and it is the right id.
    #You can also access q_id with session['q_id']
    #the control here is passed from show_question

    print("------------------------------------")
    print("Session in route_runc ",session)
    print("------------------------------------")
    
    print(q_id)
    global qid
    if(qid == 0 or q_id !="1"):
        qid=q_id
    
    question =  db.get_question_details(qid)
    if request.method == 'POST':
        custom_input = False
        resinput = format(request.form['resinput'])
        if request.form['submit']=="Run Code":
            print("custom_input is TRUE")
            custom_input = True
            if(len(resinput)<1):
                resinput="No input!!"
        code = request.form['code']
        print(code)
        global Index
        Index += 1
        ID = Index
        instr = "./running/input"+str(ID)+".txt"
        f = open(instr,"w")
        f.write(resinput)
        f.close()  
        run = runcode.RunCCode(question,code,custom_input,Index)
        rescompil, resrun , display_outputi,test_case_output= run.run_c_code()
        print(test_case_output)
        
       
        if not resrun:
            resrun = 'No result! no run yet.'
    else:
        code = default_c_code
        resrun = 'No result! no run yet.'
        rescompil = ''
        display_outputi={}
        test_case_output="None"
    
    return render_template("main.html",
                           question= question,
                           code=code,    
                           target="runc",
                           resrun=resrun,
                           rescomp=rescompil,
                           test_case_output=test_case_output,
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
