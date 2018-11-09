import subprocess
import sys
from flask import Flask, render_template, request,session
import os
import subprocess
import threading
import socket
import re
from db_access import submit_code
app = Flask(__name__)
test_case_output=""
output = ""
class RunCCode(object):
    
    def __init__(self,question,code=None,index=0):
        self.code = code                        
        self.index =  index
        self.question = question                    
        self.compiler = "gcc"
        if not os.path.exists('running'):
            os.mkdir('running')

    def _compile_c_code(self, filename, prog="./running/a.out"):
        flags =  "-std=gnu99"
        warning = '-O2'
        hel = '-fomit-frame-pointer'
        math = "-lm"

        cmd = [self.compiler, flags, warning, hel, filename, "-Wall", "-o", prog, math]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.wait()
        a, b = p.communicate()
        self.stdout, self.stderr = a.decode("utf-8"), b.decode("utf-8")
        return result


    def fetch_data(self):
        time_limit = 2 
        memory_limit = 100
        #sample_test_case 
        #'test_cases': [{'point': 1.0, 'output': 'dlroW olleH', 'input': 'Hello World'}]
        test_cases = {
            0:{"input":"2 1 2","output":"NO","points":100},
            1:{"input":"2 1 3","output":"YES","points":100},
            2:{"input":"2 7 8","output":"NO","points":100}
        }
        return time_limit, memory_limit,test_cases


    def execute_testcase(self,my_input,memory_limit, time_limit,cmd):
        virtualenvcmd = "./timeout -m "+str(memory_limit)
        cmd = cmd+" "+str(time_limit)
        p = subprocess.Popen(virtualenvcmd+" "+cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell = True)
        a, b = p.communicate(input = my_input.encode())
        return a , b
        
    def update_test_status(self,time,memory,STATUS,test_case_output):
        '''
        fetch the submission for the question
        update the test status
        '''
        test_case_status={"status":STATUS ,"time":time,"memory":memory}
        test_case_output.append(test_case_status)


   

    def _run_c_prog(self, cmd="./running/a.out",idx=0):
        # taking custom input
        # this is only if user says cutom input 
        # my_input = open("./running/input"+str(idx)+".txt","r")
        '''
        fetch the inputs from the database
        loop for the number of test cases
        compare he output and update the score, time and memory
        return the score, time , memory taken 
        to the user in the same format as stored in database
        '''
        memory_limit = self.question['memory']
        time_limit  = self.question['time']
        my_input = self.question['test_cases']
        

        global test_case_output
        test_case_output = {}


        '''Fetching stuff from question'''

        score = 0
        correct_cases = 0
        test_case_output = []
        submission_correctness = True
        total_cases = len(my_input)
        total_time = 0
        total_memory = 0
        for i in range(len(my_input)):
            a , b = self.execute_testcase(my_input[i]["input"],memory_limit, time_limit,cmd)     
            self.stdout, self.stderr = a.decode("utf-8"), b.decode("utf-8")
            target_output=my_input[i]['output']
            print(self.stdout)
            if(target_output==self.stdout):
                score += my_input[i]["point"]
                correct_cases += 1
            else:
                submission_correctness = False    
            #checking if memory exceeded
            arr = self.stderr.split()
            tle_check = self.stdout.split(":")

            #get time and memory
            j=1
            time_taken = 0
            memory_taken = 0
            print(arr)
            while(j < len(arr)):
                if(arr[j]=="CPU"):
                    time_taken = float(arr[j+1])
                elif(arr[j]=="MEM"):
                    memory_taken = float(arr[j+1])
                j += 1



            status = "Running Successful"
            if(tle_check[0]=="TLE"):
                status = "TLE"
                submission_correctness = False
            elif(arr[0] == "MEM"):
                status = "MEMORY LIMIT EXCEEDED"
                submission_correctness = False
            elif(arr[0] == "FINISHED"):
                status = "Running successful"

            self.update_test_status(time_taken,memory_taken,status,test_case_output)
        
            '''
                format the output in order to display the status
            '''
            

            total_time += time_taken
            total_memory += memory_taken   

        if(submission_correctness):
            result = "Correct Answer"
        else:
            result = "Wrong Answer"
        output ="Submission status: "+str(result)+"\n"+str(correct_cases)+"/"+str(total_cases)+" Test Cases Passed\nScore "+str(score)+"\nTime taken ="+str(total_time)+"s"+"\nMemory taken = "+str(total_memory)+"bytes\n"
        return output,test_case_output,score,result
    

    def run_c_code(self, code=None):
        def cleanup_files(index):
            prog_output = "./running/a"+str(self.index)+".out"
            filename = "./running/test"+str(self.index)+".c"
            inputfile = "./running/input"+str(self.index)+".txt"
            if os.path.exists(inputfile):
                os.remove(inputfile)
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(prog_output):
                os.remove(prog_output)
            
            
        idx = self.index
        score=-1
        status="null"
        print(idx)
        prog_output = "./running/a"+str(idx)+".out"
        filename = "./running/test"+str(idx)+".c"
        if not code:
            code = self.code
        result_run = "No run done"
        line_to_add = '#include "../setlimits.c"\n'
        code = line_to_add + code
        code =re.sub(r'main[\s \t \n a-z A-Z ( ) , \* ;\[\]]*{', "main(int argc,char* argv[]){ setlimits(argc,argv);", code)
        
        print(code)
        with open(filename, "w") as f:
            f.write(code)
        
        #self.line_prepender(filename,line_to_add)
        res = self._compile_c_code(filename,prog_output)
        print("COMPILED")
        result_compilation = self.stdout + self.stderr
        print(result_compilation)
        display_output=''
        if res == 0:
            global test_case_output
            global output
            display_output,output,score,status= self._run_c_prog(prog_output,idx)
            '''store into db'''
            print("Storing stuff from here")
            print(score)
            print(output)
            print(status)
            print(code)
            print("Done storing")
            ####Storing Submissions in db   
            #submit_code(session['s_id'], session['q_id'],session['c_id'], code,"C", score, status, test_case_output)
            submit_code('01FB15ECS341',"q_3423km23f","c_dOHYbn", code,"C", score,status,output)
            result_run = self.stdout + self.stderr + display_output
        
   

        cleanup_files(idx)
        return result_compilation, result_run

    def all_submissions(self):
        '''fetch form db'''
        
        global test_case_output
        print("in all submission",output)
        return test_case_output


    def add_limits(code):
        code = re.sub(r'main[\s \t \n a-z A-Z ( ) , \* ;\[\]]*', "main(int argc,char* argv[]){ setlimits(argc,argv);", code)
        return code





class RunCppCode(object):

    def __init__(self, code=None):
        self.code = code
        self.compiler = "g++"
        if not os.path.exists('running'):
            os.mkdir('running')

    def _compile_cpp_code(self, filename, prog="./running/a.out"):
        cmd = [self.compiler, filename, "-Wall", "-o", prog]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.wait()
        a, b = p.communicate()
        self.stdout, self.stderr = a.decode("utf-8"), b.decode("utf-8")
        return result

    def _run_cpp_prog(self, cmd="./running/a.out"):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.wait()
        a, b = p.communicate()
        self.stdout, self.stderr = a.decode("utf-8"), b.decode("utf-8")
        return result

    def run_cpp_code(self, code=None):
        filename = "./running/test.cpp"
        if not code:
            code = self.code
        result_run = "No run done"
        with open(filename, "w") as f:
            f.write(code)
        res = self._compile_cpp_code(filename)
        result_compilation = self.stdout + self.stderr
        if res == 0:
            self._run_cpp_prog()
            result_run = self.stdout + self.stderr
        return result_compilation, result_run

class RunPyCode(object):
    
    def __init__(self, code=None):
        self.code = code
        if not os.path.exists('running'):
            os.mkdir('running')

    def _run_py_prog(self, cmd="a.py"):
        cmd = [sys.executable, cmd]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.wait()
        a, b = p.communicate()
        self.stdout, self.stderr = a.decode("utf-8"), b.decode("utf-8")
        return result
    
    def run_py_code(self, code=None):
        filename = "./running/a.py"
        if not code:
            code = self.code
        with open(filename, "w") as f:
            f.write(code)
        self._run_py_prog(filename)
        return self.stderr, self.stdout


