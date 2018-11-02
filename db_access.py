"""
This file contains the code that connects the backend to database
Run this file to check if the connection to database works
If it doesn't throw an error, it works!

CONTENTS:
1. FUNCTIONS AND OBJECTS USED BY MULTIPLE FUNCTIONS
2. QUERIES FOR LOGIN
3. QUERIES FOR COMPILER
"""

import psycopg2
import logging
import random
import string
import json
import re

"""
codestreak=# \d
           List of relations
 Schema |    Name    | Type  |  Owner
--------+------------+-------+----------
 public | contest    | table | postgres
 public | professor  | table | postgres
 public | question   | table | postgres
 public | student    | table | postgres
 public | submission | table | postgres
(5 rows)

"""

# 1. FUNCTIONS AND OBJECTS used by multiple functions

none_list = ['None', None, False, {}, [], set(), 'null', 'NULL', 0, "0"]


def random_alnum(prefix="", length=16):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
    return prefix + x


def connect_db():
    """
    Connects to the postgres database
    :return: postgres connection object
    """
    connect_str = "dbname='codestreak' user='codestreak@codestreak' host='codestreak.postgres.database.azure.com' password='Student123' port='5432'"
    try:
        conn = psycopg2.connect(connect_str)
        logging.info('Connection successful')
        return conn

    except:
        logging.error('Failed to connect to database')
        return None

def _execute_query(query):
    """
    Helper function to execute any query and fetches all rows
    :param query: Query string in SQL
    :return: None if query unsuccessful,
                list of tuples for SELECT query
                number of rows updated for UPDATE query
                number of rows inserted for INSERT query
    """
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute(query)
        logging.info('Executed: '+query)
        res = cur.rowcount
        if re.fullmatch(r"^SELECT.*", query, re.IGNORECASE):
            res = cur.fetchall()
        logging.info('Returned: '+str(res))
        conn.commit()
        cur.close()
        conn.close()
        return res
    return None


# 2. QUERIES FOR LOGIN

def validate_student(usn, password):
    """
    Validates login credential for student
    :param usn: student's usn, e.g. 01FB15ECS342
    :param password: student's password, e.g. 01FB15ECS342
    :return: False if usn does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT '""" + usn + """' IN (SELECT usn FROM student)) AND (SELECT (SELECT password FROM student where usn = '""" + usn + """') = '""" + password + """');"""
    res = _execute_query(query)
    if res not in none_list:
        return res[0][0]
    return False


def validate_professor(p_id, password):
    """
    Validates login credential for professor
    :param p_id: professor's id, e.g. 01FB15ECS342
    :param password: professor's password, e.g. 01FB15ECS342
    :return: False if p_id does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT '""" + p_id + """' IN (SELECT p_id FROM professor)) AND (SELECT (SELECT password FROM professor where p_id = '""" + p_id + """') = '""" + password + """');"""
    res = _execute_query(query)
    if res not in none_list:
        return res[0][0]
    return False


# 3. QUERIES FOR COMPILER
def get_testcases_by_question(q_id=0):
    """
    Gets the test cases for a given question
    :param q_id: the unique identifier for each question in db
    :return: A json object of test cases
    """
    query1 = "SELECT COUNT(*) FROM question where q_id = '{}';".format(q_id)
    query2 = "SELECT test_cases FROM question where q_id = '{}';".format(q_id)
    res1 = _execute_query(query1)
    if res1 in none_list or int(res1[0][0]) == 0:  # checks if q_id exists
        logging.error('Could not find required question')
        return None

    res2 = _execute_query(query2)
    if res2 not in none_list:
        return json.loads(res2[0][0])

    return None


def submit_code(usn, q_id, c_id, code, language, test_case_status="{}"):
    """
    :param usn:
    :param q_id:
    :param c_id:
    :param code:
    :param language:
    :return:
    """

    s_id = random_alnum("s_")
    query = """INSERT INTO submission (s_id, usn, q_id, c_id, code, language, test_case_status) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');"""
    query = query.format(s_id, usn, q_id, c_id, code, language, test_case_status)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Failed to add submission to database')
        return None
    logging.info('Submitted code successfully')
    return res


def get_unevaluated_submission():
    """
    Gets the oldest unevaluated code
    :return: None if nothing to evaluate else a dict with s_id, code and language
    """
    query = """SELECT s_id, code, language FROM submission where is_evaluated = false ORDER BY submit_time DESC LIMIT 1;"""
    res = _execute_query(query)
    if res in none_list:  # error or nothing to evaluate
        return None
    code_to_evaluate = {
        "s_id": res[0][0],
        "code": res[0][1],
        "language": res[0][2]
    }
    return code_to_evaluate


def set_evaluated_submission(s_id, test_case_status):
    """
    Saves the evaluated submission to the database
    :param s_id:
    :param test_case_status:
    :return:
    """
    query = """UPDATE submission SET test_case_status = '{}' WHERE s_id = '{}'"""
    query = query.format(s_id, test_case_status)
    res = _execute_query(query)
    if res not in none_list:
        return res
    logging.error('Could not update test_case_status')
    return None


def add_contest(**dictionary):
    """
    Function used in create_assignment in routes.py

    Add new entry in the contest table
    param: dictionary of columns of a row of contest table
    return : nothing 
    """

def questions_list():
    """
    Function used in create_assignment in routes.py
    
    return list of dictionary, where each dictionary is a row of question table.
    """

def create_contest(p_id, name, start_time, end_time, questions, semester, section):

    c_id = random_alnum("c_")
    query = """INSERT INTO contest VALUES('{}', '{}','{}','{}','{}','{}','{}');"""
    query = query.format(c_id, p_id, name, start_time, end_time, questions, semester, section)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not create contest')
        return None
    return res


logging.basicConfig(level='INFO')
if __name__ == "__main__":
    res = _execute_query("SELECT * from student;")
    print(res, type(res))
    submission = {
        "usn": '01FB15ECS341',
        "q_id": 10,
        "c_id": 15,
        "code": "int main(){;}",
        "language": "c"
    }
    print(submit_code(**submission))
