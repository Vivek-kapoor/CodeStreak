from flask import Flask, render_template, request
from runcode import runcode
import socket
app = Flask(__name__)
app._static_folder = "/home/sumanth/projects/flask_compiler/codelauncher/static/"
import code
import random
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


@app.route("/")
@app.route("/runc", methods=['POST', 'GET'])
def runc():

   
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
        run = runcode.RunCCode(code,Index)
        rescompil, resrun, test_case_output = run.run_c_code()
        
       
        if not resrun:
            resrun = 'No result!'
    else:
        code = default_c_code
        resrun = 'No result!'
        rescompil = ''
        test_case_output=""
    return render_template("main.html",
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
    app.run(host='0.0.0.0',port="5002")
