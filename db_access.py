"""
This file contains the code that connects the backend to database
Run this file to check if the connection to database works
If it doesn't throw an error, it works!

CONTENTS (not in order):

    1. random_alnum: Generates a random alphanumeric of given length with a prefix
    2. connect_db: Connects to the postgres database
    3. _execute_query:  Helper function to execute any query. WARNING: Don't use directly

    4. validate_student: Validates login credential for student
    5. validate_professor: Validates login credential for professor

    6. create_question: Creates a question and enters in the database with random q_id
    7. create_contest: Creates a contest with random id and enters in database

    8. get_student_details: Gets a dict with all details of a student

    9. get_active_contest: Gets a list of active contests for given USN
    10. get_archived_contest: Gets a list of archived contest for given USN

    11. get_questions_by_prof: Gets all the questions whose creator is p_id
    12. get_questions_by_contest: Gets a list of all questions in a contest

    13. get_testcases_by_question: Gets the test cases for a given question
    14. get_unevaluated_submission: Gets the oldest unevaluated code as a dict
    15. get_submission_distribution: Gets distribution of test case status for pie chart
    
    16. submit_code: Submits code, makes an entry in the submission table
    17. set_evaluated_submission: Sets the test_case_status of given s_id

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


none_list = ['None', None, False, {}, [], set(), 'null', 'NULL', 0, "0", tuple()]


def random_alnum(prefix="", length=6):
    """
    Generates a random alphanumeric of given length with a prefix
    :param prefix: string to be prepended to the alphanumeric
    :param length: length of the random alphanumeric
    :return: a string of the alphanumeric
    """
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


def _execute_query(query: str, json_output: bool = False) -> any:
    """
    Helper function to execute any query and fetches all rows
    :param query: Query string in SQL
    :param json_output: True when return type is expected to be of JSON format
    :return: None if query unsuccessful,
                list of tuples for SELECT query
                number of rows updated for UPDATE query
                number of rows inserted for INSERT query
    """
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        if json_output:
            json_query = """SELECT array_to_json(array_agg(row_to_json(t))) FROM ({}) t;"""
            query = json_query.format(query)
        cur.execute(query)
        logging.info('Executed: '+query)
        res = cur.rowcount
        if re.fullmatch(r"^SELECT.*", query, re.IGNORECASE):
            if json_output:
                res = cur.fetchone()
            else:
                res = cur.fetchall()
        logging.info('Returned: '+str(res))
        conn.commit()
        cur.close()
        conn.close()
        return res
    return None


def validate_student(usn:str, password:str) -> bool:
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


def validate_professor(p_id:str, password:str) -> bool:
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


def get_testcases_by_question(q_id:str ="0"):
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
        return res2[0][0]

    return None


def submit_code(usn, q_id, c_id, code, language, test_case_status="{}"):
    """
    Submits the code, makes an entry in submission
    These entries will be evaluated by compiler
    :param usn: usn of student submitting the code
    :param q_id: question id for which the code is submitted
    :param c_id: contest id for which the code is submitted
    :param code: the code in the form of string
    :param language: language in which the code is submitted
    :return: 1 if successfully inserted else None
    """

    s_id = random_alnum(prefix="s_")
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
    res = _execute_query(query, json_output=True)
    if res in none_list:  # error or nothing to evaluate
        return None
    return res[0]


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


def get_questions_by_prof(p_id):
    """
    Gets all the questions created by the given professor
    in descending order of the time it was created
    :param p_id: unique id of the professor
    :return: list of dict where each question is a dict
    """
    query = """SELECT * from question where p_id = '{}' ORDER BY create_time DESC"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not get any questions for '+p_id)
        return None
    return res[0]


def create_contest(p_id, name, start_time, end_time, questions, semester, section):
    """
    Creates a contest with a random contest id
    :return: 1 if successful else None
    """
    c_id = random_alnum("c_")
    query = """INSERT INTO contest VALUES('{}', '{}','{}','{}','{}','{}','{}', '{}')"""
    query = query.format(c_id, p_id, name, start_time, end_time, questions, semester, section)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not create contest')
        return None
    return res


def get_active_contest(usn:str, semester=None, section=None):
    """
    Gets a list of active contests for the given student
    :param usn: usn of the student
    :return: a list of contests with all details in JSON
    """
    if semester is None or section is None:
        student_details = get_student_details(usn, get_ranks=False)
        semester = student_details['semester']
        section = student_details['section']

    query = """SELECT * FROM contest WHERE semester = '{}' AND section  = '{}' AND start_time <= NOW() AND end_time >= NOW() """
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_archived_contest(usn:str, semester=None, section=None):
    """
    Gets a list of active contests for the given student
    :param usn: usn of the student
    :return: a list of contests with all details in JSON
    """
    if semester is None or section is None:
        student_details = get_student_details(usn, get_ranks=False)
        semester = student_details['semester']
        section = student_details['section']

    query = """SELECT * FROM contest WHERE semester = '{}' AND section  = '{}' AND end_time < NOW()"""
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_student_details(usn:str, get_ranks:bool =True):
    """
    Gets all student details including
    rating, best rating, rank, batch rank, class rank from database
    :param usn: usn of student
    :return: json with the all attributes of that student
    """

    query = """SELECT * FROM student WHERE usn = '{}'"""
    query = query.format(usn)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve student information')
        return None

    student_details = res[0][0]

    if get_ranks:
        sem_clause = "semester = " + str(student_details['semester'])
        sec_clause = "section = '" + str(student_details['section']) + "'"
        for attr, clause1, clause2 in [('rank','true', 'true'), ('batch_rank',sem_clause, 'true'), ('class_rank',sem_clause, sec_clause)]:
            query = """SELECT rank from (SELECT usn, rank() over (order by rating desc) as rank from student where {} and {}) as a WHERE usn = '{}'"""
            query = query.format(clause1, clause2, usn)
            res = _execute_query(query)
            student_details[attr] = int(res[0][0])

    return student_details


def get_submission_distribution(usn:str):
    """
    Distribution of all submissions to create pie chart
    :param usn: usn of the student
    :return: json with frequency of all verdicts
    """
    query = """SELECT status, count(*) from submission where usn = '{}' GROUP BY status"""
    query = query.format(usn)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve submission distribution')
        return None
    return res


def get_questions_by_contest(c_id):
    """
    Fetches questions of a particular contest
    :param c_id: contest id
    :return: list of dicts. Each dict represents on question
    """
    query = """SELECT * FROM question WHERE q_id = ANY ((SELECT questions FROM contest WHERE c_id = '{}')::varchar[])"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any questions for contest '+c_id)
        return None
    return res[0]


def create_question(p_id:str, name:str, problem:str, difficulty:str, editorial="N/A", time_limit=1, memory_limit=1024, test_cases="{}", score=0, languages='{"c"}', tags='{}'):
    """
    Adds a question to the database with a random question id
    :return: 1 if successful else None
    """
    query = """INSERT INTO question (p_id, name, problem, difficulty, editorial, time_limit, memory_limit, test_cases, score, languages, tags)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""
    query = query.format(p_id, name, problem, difficulty, editorial, time_limit, memory_limit, test_cases, score, languages, tags)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not create question')
        return None
    return res


logging.basicConfig(level='INFO')


if __name__ == "__main__":
    # temp = (create_contest(
    #     **{"p_id":"01FB15ECS342",
    #        "name": "Simple Trial 1",
    #        "start_time": "2018-11-01 12:00:00",
    #        "end_time": "2018-11-05 18:00:00",
    #        "questions": '{"q_3423km23f"}',
    #        "semester": '7',
    #        "section": 'F'
    #     }
    # ))
    # print(type(temp), temp)

    temp = get_questions_by_contest('c_dOHYbn')
    print(type(temp), temp)

    temp = get_submission_distribution('01FB15ECS342')
    print(type(temp), temp)

    temp = get_active_contest('01FB15ECS342')
    print(type(temp), temp)
