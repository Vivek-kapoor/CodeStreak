"""
This file contains the code that connects the backend to database
Run this file to check if the connection to database works
If it doesn't throw an error, it works!
Connect from cmd: psql -h codestreak.postgres.database.azure.com -p 5432 -U codestreak@codestreak codestreak

CONTENTS (not in order):

    0. destroy_connections: Closes all the connections of the connection pool
    1. random_alnum: Generates a random alphanumeric of given length with a prefix
    2. connect_db: Connects to the postgres database
    3. _execute_query:  Helper function to execute any query. WARNING: Don't use directly

    4. validate_student: Validates login credential for student
    5. validate_professor: Validates login credential for professor

    6. create_question: Creates a question and enters in the database with random q_id
    7. create_contest: Creates a contest and enters in database with random c_id

    8. get_student_details: Gets a dict with all details of a student

    9. get_active_contest_student: Gets a list of active contests for given USN
    10. get_archived_contest_student: Gets a list of archived contest for given USN
    11. get_active_contest_professor: Gets a list of active contests for given p_id
    12. get_archived_contest_professor: Gets a list of archived contest for given p_id
    13. get_contest_details: Gets all the details of a contest for given c_id

    14. get_questions: Gets all the questions
    15. get_questions_by_prof: Gets all the questions whose creator is p_id
    16. get_questions_by_contest: Gets a list of all questions in a contest
    17. get_question_details: Gets all details for a given question

    18. get_unevaluated_submission: Gets the oldest unevaluated code as a dict
    19. get_submission_distribution: Gets distribution of test case status for pie chart
    20. get_submissions_by_student: Gets all submissions made by a student for given question and contest
    21. get_leaderboard: Gets the leaderboard of a given contest
    22. get_submissions_by_contest: Gets all the submissions for a contest for the professor to see
    23. get_plagiarism_code: Gets the candidate submissions to be detected for plagiarism
    24. get_plagiarism_report: Returns the plagiarism report for a given contest

    25. submit_code: Submits code, makes an entry in the submission table
    26. set_evaluated_submission: Sets the test_case_status of given s_id
    27: set_plagiarism_report: Saves the plagiarism report in the database

"""

import psycopg2
import psycopg2.pool
import logging
import random
import string
import re
import json
import atexit
from time import time, sleep


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
logging.basicConfig(level="INFO")

connect_str = "dbname='codestreak' user='codestreak@codestreak' host='codestreak.postgres.database.azure.com' password='Student123' port='5432' "
pool = psycopg2.pool.SimpleConnectionPool(4, 8, connect_str)
logging.info('Successfully established connection pool')


@atexit.register
def destroy_connections():
    if pool:
        pool.closeall()
        logging.info('Closed all connections with database')


def random_alnum(prefix: str="", length: int=4) -> str:
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
    global pool
    try:
        conn = pool.getconn()
        logging.info('Connection successful')
        return conn

    except psycopg2.OperationalError:
        logging.error('Connection closed unexpectedly. Trying to reconnect')
        pool = psycopg2.pool.SimpleConnectionPool(2, 4, connect_str)
        logging.info('Successfully established connection pool')
        return connect_db()

    except psycopg2.DatabaseError:
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
        try:
            cur = conn.cursor()
            if json_output:
                json_query = """SELECT array_to_json(array_agg(row_to_json(t))) FROM ({}) t"""
                query = json_query.format(query)
            cur.execute(query)
            logging.info('Executed: ' + query)
            res = cur.rowcount
            if re.fullmatch(r"^SELECT.*", query, re.IGNORECASE):
                if json_output:
                    res = cur.fetchone()
                else:
                    res = cur.fetchall()
            logging.info('Returned: ' + str(res))
            conn.commit()
            cur.close()
            pool.putconn(conn)
            return res

        except psycopg2.ProgrammingError:
            logging.error('Something went wrong with the query')
            pool.closeall()
            return None

        except psycopg2.IntegrityError:
            logging.error('Something went wrong with the query')
            pool.closeall()
            return None

        except psycopg2.OperationalError:
            sleep(1)
            return _execute_query(query, json_output)

    return None


def validate_student(usn: str, password: str) -> bool:
    """
    Validates login credential for student
    :param usn: student's usn, e.g. 01FB15ECS342
    :param password: student's password, e.g. 01FB15ECS342
    :return: False if usn does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT \'{0}\' IN (SELECT usn FROM student)) AND (SELECT (SELECT password FROM student where usn = \'{1}\') = \'{2}\')""".format(
        usn, usn, password)
    res = _execute_query(query)
    if res not in none_list:
        return res[0][0]

    return False


def validate_professor(p_id: str, password: str) -> bool:
    """
    Validates login credential for professor
    :param p_id: professor's id, e.g. 01FB15ECS342
    :param password: professor's password, e.g. 01FB15ECS342
    :return: False if p_id does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT \'{0}\' IN (SELECT p_id FROM professor)) AND (SELECT (SELECT password FROM professor where p_id = \'{1}\') = \'{2}\')""".format(
        p_id, p_id, password)
    res = _execute_query(query)
    if res not in none_list:
        return res[0][0]
    return False


def get_question_details(q_id: str = "0"):
    """
    Gets all details for a given question
    :param q_id: the unique identifier for each question in db
    :return: A json object with all question details
    """
    query = """SELECT * from question where q_id = \'{}\'"""
    query = query.format(q_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not fetch details for ' + q_id)
        return None
    return res[0][0]


def submit_code(usn: str, q_id: str, c_id: str, code: str, language: str, score: int, status: str, test_case_status: list):
    """
    Submits the code, makes an entry in submission
    These entries will be evaluated by compiler
    :param usn: usn of student submitting the code
    :param q_id: question id for which the code is submitted
    :param c_id: contest id for which the code is submitted
    :param code: the code in the form of string
    :param language: language in which the code is submitted
    :param score: sum of score of all test cases
    :param status: final status of whole submission
    :param test_case_status: status of each test case with verdict and score
    :return: 1 if successfully inserted else None
    """

    s_id = random_alnum(prefix="s_")
    test_case_status = json.dumps(test_case_status)

    query = """INSERT INTO submission (s_id, usn, q_id, c_id, code, language, score, status, test_case_status) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"""
    query = query.format(s_id, usn, q_id, c_id, code, language, score, status, test_case_status)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Failed to add submission to database')
        return None
    logging.info('Submitted code successfully')
    return res


def get_unevaluated_submission():  # todo remove if not needed
    """
    Gets the oldest unevaluated code
    :return: None if nothing to evaluate else a dict with s_id, code and language
    """
    query = """SELECT s_id, code, language FROM submission where is_evaluated = false ORDER BY submit_time DESC LIMIT 1"""
    res = _execute_query(query, json_output=True)
    if res in none_list:  # error or nothing to evaluate
        return None
    return res[0]


def set_evaluated_submission(s_id: str, test_case_status: list):  # todo remove if not needed
    """
    Saves the evaluated submission to the database
    :param s_id:
    :param test_case_status:
    :return:
    """
    query = """UPDATE submission SET test_case_status = \'{}\' WHERE s_id = \'{}\'"""
    query = query.format(s_id, test_case_status)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not update test_case_status')
        return None
    return res


def get_questions_by_prof(p_id: str):  # todo remove if not needed
    """
    Gets all the questions created by the given professor
    in descending order of the time it was created
    :param p_id: unique id of the professor
    :return: list of dict where each question is a dict
    """
    query = """SELECT * from question where p_id = \'{}\' ORDER BY create_time DESC"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not get any questions for ' + p_id)
        return None
    return res[0]


def get_questions():
    """
    Gets all the questions in descending order of the time it was created
    :return: list of dict where each question is a dict
    """
    query = """SELECT * from question ORDER BY create_time DESC"""
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not get any questions')
        return None
    return res[0]


def create_contest(p_id: str, name: str, start_time: str, end_time: str, questions: set, semester: int, section: str):
    """
    Creates a contest with a random contest id
    :return: 1 if successful else None
    """
    c_id = random_alnum("c_")
    questions = str(questions).replace("'", "")

    query = """INSERT INTO contest VALUES(\'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\', \'{}\')"""
    query = query.format(c_id, p_id, name, start_time, end_time, questions, semester, section)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not create contest')
        return None
    return res


def get_active_contest_student(usn: str, semester=None, section=None):
    """
    Gets a list of active contests for the given student
    :param usn: usn of the student
    :param semester: Optional parameter, student's semester
    :param section: Optional parameter, student's section
    :return: a list of contests with all details in JSON
    """
    if semester is None or section is None:
        student_details = get_student_details(usn, get_ranks=False)
        if student_details not in none_list:
            semester = student_details['semester']
            section = student_details['section']
        else:
            return None

    query = """SELECT * FROM contest WHERE semester = \'{}\' AND section  = \'{}\' AND start_time <= NOW() AND end_time >= NOW() """
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_archived_contest_student(usn: str, semester=None, section=None):
    """
    Gets a list of active contests for the given student
    :param usn: usn of the student
    :param semester: Optional parameter, student's semester
    :param section: Optional parameter, student's section
    :return: a list of contests with all details in JSON
    """
    if semester is None or section is None:
        student_details = get_student_details(usn, get_ranks=False)
        if student_details not in none_list:
            semester = student_details['semester']
            section = student_details['section']
        else:
            return None

    query = """SELECT * FROM contest WHERE semester = \'{}\' AND section  = \'{}\' AND end_time < NOW()"""
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_archived_contest_professor(p_id: str):
    """
    Gets all the archived contest for given p_id
    :param p_id: Professor id
    :return: None if there are no contests, else json
    """
    query = """SELECT * from contest WHERE p_id = \'{}\' AND end_time <= NOW()"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_active_contest_professor(p_id: str):
    """
    Gets all the active contest for given p_id
    :param p_id: Professor id
    :return: None if there are no contests, else json
    """
    query = """SELECT * from contest WHERE p_id = \'{}\' AND end_time >= NOW()"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def get_contest_details(c_id: str):
    """
    Get all the details of a contest
    :param c_id: contest id
    :return: a dictionary with all contest details if successful, else None
    """
    query = """SELECT * from contest WHERE c_id = \'{}\'"""
    query = query.format(c_id)
    res1 = _execute_query(query, json_output=True)
    if res1 in none_list or res1[0] in none_list:
        return None
    query = """SELECT end_time >= NOW() from contest WHERE c_id = \'{}\'"""
    query = query.format(c_id)
    res2 = _execute_query(query)
    if res2 in none_list:
        return res1[0][0]
    status = "active" if res2[0] == "t" else "archived"
    res1[0][0]["status"] = status
    return res1[0][0]


def get_student_details(usn: str, get_ranks: bool = True):
    """
    Gets all student details including
    rating, best rating, rank, batch rank, class rank from database
    :param usn: usn of student
    :param get_ranks: If True, get students rank, batch rank and class rank also. else ignore
    :return: json with the all attributes of that student
    """

    query = """SELECT * FROM student WHERE usn = \'{}\'"""
    query = query.format(usn)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve student information')
        return None

    student_details = res[0][0]

    if get_ranks:
        sem_clause = "semester = " + str(student_details['semester'])
        sec_clause = "section = '" + str(student_details['section']) + "'"
        for attr, clause1, clause2 in [('rank', 'true', 'true'), ('batch_rank', sem_clause, 'true'),
                                       ('class_rank', sem_clause, sec_clause)]:
            query = """SELECT rank from (SELECT usn, rank() over (order by rating desc) as rank from student where \'{}\' and \'{}\') as a WHERE usn = \'{}\'"""
            query = query.format(clause1, clause2, usn)
            res = _execute_query(query)
            student_details[attr] = int(res[0][0])

    return student_details


def get_submission_distribution(usn: str):
    """
    Distribution of all submissions to create pie chart
    :param usn: usn of the student
    :return: json with frequency of all verdicts
    """
    query = """SELECT status, count(*) from submission where usn = \'{}\' GROUP BY status"""
    query = query.format(usn)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve submission distribution')
        return None
    return res[0]


def get_questions_by_contest(c_id: str):
    """
    Fetches questions of a particular contest
    :param c_id: contest id
    :return: list of dicts. Each dict represents on question
    """
    query = """SELECT * FROM question WHERE q_id = ANY ((SELECT questions FROM contest WHERE c_id = \'{}\')::varchar[])"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any questions for contest ' + c_id)
        return None
    return res[0]


def create_question(p_id: str, name: str, problem: str, difficulty: str, languages: set, tags: set, test_cases: list, editorial: str = "N/A", time_limit: float = 1,
                    memory_limit: float = 1024, score: int = 0):
    """
    Adds a question to the database with a random question id
    :return: 1 if successful else None
    """
    q_id = random_alnum(prefix="q_")

    languages = str(languages).replace("'", "")
    tags = str(tags).replace("'", "")
    test_cases = json.dumps(test_cases)

    query = """INSERT INTO question (q_id, p_id, name, problem, difficulty, editorial, time_limit, memory_limit, test_cases, score, languages, tags)
            VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"""
    query = query.format(q_id, p_id, name, problem, difficulty, editorial, time_limit, memory_limit, test_cases, score,
                         languages, tags)
    res = _execute_query(query)
    if res in none_list:
        logging.error('Could not create question')
        return None
    return res


def get_submissions_by_student(usn: str, q_id: str, c_id: str):
    """
    Gets the submissions made by a student for a particular question for a particular contest
    :param usn: unique student id
    :param q_id: question id
    :param c_id: contest id
    :return: A list of submissions where each submission is a dict
    """

    query = """SELECT * from submission WHERE usn = \'{}\' AND q_id = \'{}\' AND c_id = \'{}\' ORDER BY submit_time DESC"""
    query = query.format(usn, q_id, c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any submissions')
        return None
    return res[0]


def get_submissions_by_contest(c_id: str):
    """
    Gets all the submissions for a contest for the professor to see
    :param c_id: contest id
    :return: a list of submissions if successful else None
    """
    query = """SELECT * from submission where c_id = \'{}\'"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any submissions for given contest')
        return None
    return res[0]


def get_leaderboard(c_id: str) -> list:
    """
    Gets the leaderboard of a contest
    :param c_id: contest id
    :return: a list of dicts for the leaderboard
    """
    submissions_to_check = get_plagiarism_code(c_id)
    if submissions_to_check in none_list:
        return []

    res = list(submissions_to_check.values())
    leaderboard = dict()
    for submission in res:
        usn = submission["usn"]
        if usn not in leaderboard:
            leaderboard[usn] = {"score": 0, "penalty": "0"}
        leaderboard[usn]["score"] += submission["score"]
        leaderboard[usn]["penalty"] = max(leaderboard[usn]["penalty"], submission["submit_time"])

    leaderboard = [{"usn": usn, "score": leaderboard[usn]["score"], "penalty": leaderboard[usn]["penalty"]} for usn in leaderboard]
    leaderboard.sort(key=lambda x: x["penalty"])
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard


def get_plagiarism_code(c_id: str):
    """
    Gets the candidate submissions to be detected for plagiarism
    :param c_id: contest id
    :return: None, if the query returns nothing, else a list of dicts
    """
    query = """SELECT q_id, usn, score, submit_time, code FROM submission WHERE c_id = \'{}\' ORDER BY score DESC, submit_time"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list or res[0] in none_list:
        logging.info('Failed to retrieved submissions for ' + c_id)
        return None

    submissions_to_check = {}
    for submission in res[0]:
        tup = (submission["q_id"], submission["usn"])
        if tup not in submissions_to_check:
            submissions_to_check[tup] = submission

    return submissions_to_check


def get_plagiarism_report(c_id: str):
    """
    Returns the plagiarism report for a given contest
    :param c_id: contest id
    :return: report as a list else None
    """
    query = """SELECT plagiarism from contest where c_id=\'{}\'"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return None
    return res[0]


def set_plagiarism_report(c_id: str, report: list):
    """
    Saves the plagiarism report in the database
    :param c_id: contest id
    :param report: list of lists of plagiarism
    :return: 1 if success, else None
    """

    query = """UPDATE contest SET plagiarism = \'{}\' WHERE c_id = \'{}\'"""
    report = json.dumps(report)
    query = query.format(report, c_id)
    res = _execute_query(query)
    if res in none_list:
        return None
    return res


if __name__ == "__main__":

    temp = get_contest_details("c_dOHYbn")
    print(type(temp), temp)
    quit()
    start = time()
    # temp = create_question(**{'test_cases': [{'point': 1.0, 'output': 'dlroW olleH', 'input': 'Hello World'}], 'time_limit': 0.5, 'difficulty': 'Easy', 'problem': 'Reverse given string', 'languages': {'C'}, 'name': 'Reverse String', 'p_id': '01FB15ECS342', 'tags': {'Warmup'}, 'memory_limit': 1.0})
    # print(type(temp), temp)
    # quit()
    # temp = create_contest(**{'start_time': '2018-11-10T03:45', 'name': 'Sample', 'end_time': '2018-11-10T03:45', 'section': 'F', 'questions': str({'q_iBPSXw'}), 'p_id': '01FB15ECS342', 'semester': '7'})
    # print(type(temp), temp)
    # quit()
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

    temp = get_plagiarism_code("c_dOHYbn")
    print(type(temp), temp)

    # temp = submit_code(
    #     **{
    #         "usn": "01FB15ECS341",
    #         "q_id": "q_3423km23f",
    #         "c_id": "c_dOHYbn",
    #         "code": "input()",
    #         "language": "python",
    #         "score": 0,
    #         "status": "AC"
    #     }
    # )
    #
    # print(type(temp), temp)

    # temp = create_question(
    #     **{"p_id": "01FB15ECS342",
    #        "name": "Square the number",
    #        "problem": "Given an integer, find its square. Input: Single line with integer. Output: Single line with the square",
    #        "difficulty": "Cakewalk",
    #        "editorial": "Take the number as input, and multiply it with itself.",
    #        "time_limit": 0.5,
    #        "memory_limit": 128.0,
    #        "test_cases": '[{"id":1, "input":0, "output":0, "score":3}, {"id":2, "input":4, "output":16, "score":3}, {"id":1, "input":-2, "output":4, "score":4}]',
    #        "score": 10,
    #        "languages": '{"c", "python"}',
    #        "tags": '{"arithmetic", "math"}'
    #        })
    #
    # print(type(temp), temp)

    temp = get_questions()
    print(type(temp), temp)

    temp = validate_professor("01FB15ECS342", "01FB15ECS342")
    print(type(temp), temp)

    temp = get_questions()
    print(type(temp), temp)

    temp = get_questions_by_contest('c_dOHYbn')
    print(type(temp), temp)
    
    temp = get_submission_distribution('01FB15ECS342')
    print(type(temp), temp)
          
    temp = get_archived_contest_student('01FB15ECS342')
    print(type(temp), temp)

    temp = get_submissions_by_contest('cwed')
    print(type(temp), temp)

    temp = get_question_details("q_3423km23f")
    print(type(temp), temp)

    temp = get_leaderboard("c_dOHYbn")
    print(type(temp), temp)

    print(random_alnum())
    print(time()-start)
    
