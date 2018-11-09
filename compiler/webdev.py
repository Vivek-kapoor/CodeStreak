from flask import Flask, render_template, request
from runcode import runcode
import socket
app = Flask(__name__)
app._static_folder = "../compiler/templates/static"
import code
import random
from db_access import get_questions_by_contest
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

def get_data(c_id):
    return {
        "name" : "Sherlock and Cost",
        "problem" : "In this challenge, you will be given an array  and must determine an array . There is a special rule: For all , . That is,  can be any number you choose such that . Your task is to select a series of  given  such that the sum of the absolute difference of consecutive pairs of  is maximized. This will be the array's cost, and will be represented by the variable  below.",
        "difficulty": "Medium",
        "time" : "2s",
        "memory" : "256kB",
        "tags" : ["Dynamic programming","Strings"]
    }


def get_question(contest_id):
    #Get all questions in a contest
    #return: list of dicts. Each dict represents on question
    #check for the relevant question 
    # output_dict wil be a list of dicts, one dict for each question, 
    output_dict = get_questions_by_contest(contest_id)
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

@app.route("/")
@app.route("/runc", methods=['POST', 'GET'])
def runc():
    contest_id = 'c_dOHYbn' 
    #Get c_id from session
    #contest_id=session['c_id']
    question =  get_question(contest_id)
    if request.method == 'POST':
        code = request.form['code']
        resinput = format(request.form['resinput'])
        global Index
        Index += 1
        ID = Index
        instr = "./running/input"+str(ID)+".txt"
        f = open(instr,"w")
        f.write(resinput)
        f.close()  
        run = runcode.RunCCode(question,code,Index)
        rescompil, resrun, test_case_output = run.run_c_code()
        print(test_case_output)
       
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_c_code
        resrun = 'No result!'
        rescompil = ''
        test_case_output=""
    
    
    return render_template("main.html",
                           question= question,
                           code=code,    
                           target="runc",
                           resrun=resrun,
                           test_case_output=test_case_output,
                           rescomp=rescompil,
                           rows=default_rows, cols=default_cols)


@app.route("/submission", methods = ['POST'])

def submission():
        output=runcode.RunCCode()
        test_case_output=output.all_submissions()
        l=test_case_output.split('\n')
        print(l)
        return render_template("Table/table.html",output=l)


@app.route("/cpp")
@app.route("/runcpp", methods=['POST', 'GET'])
def runcpp():
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

@app.route("/py")
@app.route("/runpy", methods=['POST', 'GET'])
def runpy():
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

if __name__ == "__main__":
    app.run(host='0.0.0.0',port="5000")
