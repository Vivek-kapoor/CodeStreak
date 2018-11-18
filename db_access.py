"""
This file contains the code that connects the backend to database
Run this file to check if the connection to database works
If it doesn't throw an error, it works!
(OLD) Connect from cmd: psql -h codestreak.postgres.database.azure.com -p 5432 -U codestreak@codestreak codestreak
Connect from cmd: psql -h codestreaknew.postgres.database.azure.com -p 5432 -U codestreak@codestreaknew codestreak

CONTENTS
    0. destroy_connections: Closes all connections from connection pool
    1. random_alnum: Generates a random alphanumeric of given length with a prefix
    2. connect_db: Connects to the postgres database
    3. _execute_query: Helper function to execute any query and fetches all rows
    4. validate_student: Validates login credential for student
    5. validate_professor: Validates login credential for professor
    6. get_question_details: Gets all details for a given question
    7. submit_code: Submits the code, makes an entry in submission
    8. get_unevaluated_submission: Gets the oldest unevaluated code
    9. set_evaluated_submission: Saves the evaluated submission to the database
    10. get_questions_by_prof: Gets all the questions created by the given professor
    11. get_questions: Gets all the questions in descending order of the time it was created
    12. create_contest: Creates a contest with a random contest id
    13. get_future_contest_student: Gets a list of future contests for the given student
    14. get_active_contest_student: Gets a list of active contests for the given student
    15. get_archived_contest_student: Gets a list of archived contests for the given student
    16. get_archived_contest_professor: Gets all the archived contest for given p_id
    17. get_active_contest_professor: Gets all the active contest for given p_id
    18. get_contest_details: Get all the details of a contest
    19. get_student_details: Gets all student details including rating, best rating, rank, batch rank, class rank from database
    20. get_submission_distribution: Distribution of all submissions to create pie chart
    21. get_questions_by_contest: Fetches questions of a particular contest
    22. set_contest_location: Sets the location of a contest
    23. create_question: Adds a question to the database with a random question id
    24. get_submissions_by_student: Gets the submissions made by a student for a particular question for a particular contest
    25. get_submissions_by_contest: Gets all the submissions for a contest for the professor to see
    26. get_leaderboard: Gets the leaderboard of a contest
    27. get_plagiarism_code: Gets the candidate submissions to be detected for plagiarism
    28. get_plagiarism_report: Returns the plagiarism report for a given contest
    29. set_plagiarism_report: Saves the plagiarism report in the database
    30. get_unassigned_contests: Gets labs whose locations have not been assigned
    31. get_unallocated_locations: Gets locations that have not been assigned for given time
"""

import psycopg2
import psycopg2.pool
import logging
import random
import string
import re
import json
import atexit
from time import time

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

none_list = ['None', None, False, {}, [], set(), 'null', 'NULL', 0, "0", tuple(), (None,)]
# connect_str = "dbname='codestreak' user='codestreak@codestreak' host='codestreak.postgres.database.azure.com' password='Student123' port='5432' "
connect_str = "dbname='codestreak' user='codestreak@codestreaknew' host='codestreaknew.postgres.database.azure.com' password='Student123' port='5432'"
pool = psycopg2.pool.SimpleConnectionPool(2, 10, connect_str)
logging.info('Successfully established connection pool')


@atexit.register
def destroy_connections() -> None:
    """
    Closes all connections from connection pool
    :return: None
    """
    global pool
    if pool:
        pool.closeall()
        logging.info('Closed all connections with database')


def random_alnum(prefix: str = "", length: int = 4) -> str:
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

    except psycopg2.OperationalError as e:
        logging.error('Check your connection %s', e)
        return None

    except psycopg2.DatabaseError as e:
        logging.error('Failed to connect to database %s', e)
        return None


def _execute_query(query: str, json_output: bool = False, data=None) -> any:
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
            if data:
                cur.execute(query, data)
            else:
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
            return res

        except psycopg2.ProgrammingError as e:
            logging.error('Something went wrong with the query: %s', e)
            return None

        except psycopg2.IntegrityError as e:
            logging.error('Something went wrong with the query: %s', e)
            return None

        except psycopg2.OperationalError as e:
            logging.error('Operational error: %s', e)
            return None

        finally:
            if conn:  # if an error occurred after picking a connection
                pool.putconn(conn)

    return None


def validate_student(usn: str, password: str) -> bool:
    """
    Validates login credential for student
    :param usn: student's usn, e.g. 01FB15ECS342
    :param password: student's password, e.g. 01FB15ECS342
    :return: False if usn does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT \'{0}\' IN (SELECT usn FROM student)) AND (SELECT (SELECT password FROM student WHERE usn = \'{1}\') = \'{2}\')""".format(
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
    query = """SELECT (SELECT \'{0}\' IN (SELECT p_id FROM professor)) AND (SELECT (SELECT password FROM professor WHERE p_id = \'{1}\') = \'{2}\')""".format(
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
    query = """SELECT * FROM question WHERE q_id = \'{}\'"""
    query = query.format(q_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not fetch details for ' + q_id)
        return None
    return res[0][0]


def submit_code(usn: str, q_id: str, c_id: str, code: str, language: str, score: int, status: str,
                test_case_status: list):
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
    query = """INSERT INTO submission (s_id, usn, q_id, c_id, code, language, score, status, test_case_status) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', (%s), \'{}\', \'{}\', \'{}\', \'{}\')"""
    query = query.format(s_id, usn, q_id, c_id, language, score, status, test_case_status)
    res = _execute_query(query, data=(code,))
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
    query = """SELECT s_id, code, language FROM submission WHERE is_evaluated = false ORDER BY submit_time DESC LIMIT 1"""
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
    query = """SELECT * FROM question WHERE p_id = \'{}\' ORDER BY create_time DESC"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not get any questions for ' + p_id)
        return None
    return res[0]


def get_questions() -> list:
    """
    Gets all the questions in descending order of the time it was created
    :return: list of dict where each question is a dict
    """
    query = """SELECT * FROM question ORDER BY create_time DESC"""
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not get any questions')
        return []
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


def get_future_contest_student(usn: str, semester=None, section=None) -> list:
    """
    Gets a list of future contests for the given student
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
            return []

    query = """SELECT * FROM contest WHERE semester = \'{}\' AND section  = \'{}\' AND start_time >= NOW()"""
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
    return res[0]


def get_active_contest_student(usn: str, semester=None, section=None) -> list:
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
            return []

    query = """SELECT * FROM contest WHERE semester = \'{}\' AND section  = \'{}\' AND start_time <= NOW() AND end_time >= NOW() """
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
    return res[0]


def get_archived_contest_student(usn: str, semester=None, section=None) -> list:
    """
    Gets a list of archived contests for the given student
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
            return []

    query = """SELECT * FROM contest WHERE semester = \'{}\' AND section  = \'{}\' AND end_time < NOW()"""
    query = query.format(semester, section)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
    return res[0]


def get_archived_contest_professor(p_id: str) -> list:
    """
    Gets all the archived contest for given p_id
    :param p_id: Professor id
    :return: None if there are no contests, else json
    """
    query = """SELECT * FROM contest WHERE p_id = \'{}\' AND end_time <= NOW()"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
    return res[0]


def get_active_contest_professor(p_id: str) -> list:
    """
    Gets all the active contest for given p_id
    :param p_id: Professor id
    :return: None if there are no contests, else json
    """
    query = """SELECT * FROM contest WHERE p_id = \'{}\' AND end_time >= NOW()"""
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
    return res[0]


def get_contest_details(c_id: str):
    """
    Get all the details of a contest
    :param c_id: contest id
    :return: a dictionary with all contest details if successful, else None
    """
    query = """SELECT * FROM contest WHERE c_id = \'{}\'"""
    query = query.format(c_id)
    res1 = _execute_query(query, json_output=True)
    if res1 in none_list or res1[0] in none_list:
        return None
    query = """SELECT end_time >= NOW() FROM contest WHERE c_id = \'{}\'"""
    query = query.format(c_id)
    res2 = _execute_query(query)
    if res2 in none_list:
        return res1[0][0]
    status = "active" if res2[0][0] else "archived"
    res1[0][0]["status"] = status
    return res1[0][0]


def get_professor_details(p_id: str):
    """
    Gets the details of a professor
    :param p_id: professor id
    :return: dictionary if success, else None
    """
    query = "SELECT * from professor WHERE p_id = \'{}\'"
    query = query.format(p_id)
    res = _execute_query(query, json_output=True)

    if res in none_list or res[0] in none_list:
        logging.error('Could not fetch professor details')
        return None

    return res[0][0]


def get_student_details(usn: str, get_ranks: bool = True):
    """
    Gets all student details including rating, best rating, rank, batch rank, class rank from database
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
            query = """SELECT rank FROM (SELECT usn, rank() over (order by rating desc) as rank FROM student WHERE {} and {}) as a WHERE usn = \'{}\'"""
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
    query = """SELECT status, count(*) FROM submission WHERE usn = \'{}\' GROUP BY status"""
    query = query.format(usn)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve submission distribution')
        return None
    return res[0]


def get_questions_by_contest(c_id: str) -> list:
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
        return []
    return res[0]


def set_contest_location(c_id: str, location: str):
    """
    Sets the location of a contest
    :param c_id: contest id
    :param location: location of the lab
    :return: 1 if successful
    """
    query = """UPDATE contest SET location = \'{}\' WHERE c_id = \'{}\'"""
    query = query.format(location, c_id)
    res = _execute_query(query)
    if res in none_list:
        logging.error("Could not update location")
        return None
    return res


def create_question(p_id: str, name: str, problem: str, difficulty: str, languages: set, tags: set, test_cases: list,
                    editorial: str = "N/A", time_limit: float = 1,
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


def get_submissions_by_student(usn: str, q_id: str = None, c_id: str = None) -> list:
    """
    Gets the submissions made by a student
    :param usn: unique student id
    :param q_id: question id
    :param c_id: contest id
    :return: A list of submissions where each submission is a dict
    """
    if q_id is None and c_id is None:
        query = """SELECT * FROM submission WHERE usn = \'{}\' ORDER BY submit_time DESC"""
        query = query.format(usn)
    elif q_id is None:
        query = """SELECT * from submission WHERE usn = \'{}\' AND c_id = \'{}\' ORDER BY submit_time DESC"""
        query = query.format(usn, c_id)
    else:
        query = """SELECT * FROM submission WHERE usn = \'{}\' AND q_id = \'{}\' AND c_id = \'{}\' ORDER BY submit_time DESC"""
        query = query.format(usn, q_id, c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any submissions')
        return []
    return res[0]


def get_submissions_by_contest(c_id: str) -> list:
    """
    Gets all the submissions for a contest for the professor to see
    :param c_id: contest id
    :return: a list of submissions if successful else None
    """
    query = """SELECT * FROM submission WHERE c_id = \'{}\'"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        logging.error('Could not retrieve any submissions for given contest')
        return []
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
        name = submission["name"]
        if usn not in leaderboard:
            leaderboard[usn] = {"score": 0, "penalty": "0", "name": name}
        leaderboard[usn]["score"] += submission["score"]
        leaderboard[usn]["penalty"] = max(leaderboard[usn]["penalty"], submission["submit_time"])

    leaderboard = [{
        "usn": usn,
        "name": leaderboard[usn]["name"],
        "score": leaderboard[usn]["score"],
        "penalty": leaderboard[usn]["penalty"]
    } for usn in leaderboard]

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
            submission["name"] = get_student_details(submission["usn"], get_ranks=False)["name"]  # add the name
            submissions_to_check[tup] = submission
    return submissions_to_check


def get_plagiarism_report(c_id: str) -> list:
    """
    Returns the plagiarism report for a given contest
    :param c_id: contest id
    :return: report as a list
    """
    query = """SELECT plagiarism FROM contest WHERE c_id=\'{}\'"""
    query = query.format(c_id)
    res = _execute_query(query, json_output=True)
    if res in none_list:
        return []
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


def get_unassigned_contests() -> list:
    """
    Gets labs whose locations have not been assigned
    Note: This does not care if the contest is in the past
    :return: a list of c_ids
    """

    query = """SELECT * from contest WHERE location IS NULL"""
    res = _execute_query(query, json_output=True)

    if res in none_list:
        logging.error("Could not get any unassigned labs")
        return []

    return res[0]


def get_unallocated_locations(start_time, end_time) -> list:
    """
    Gets locations that have not been assigned for given time
    :param start_time: start time of contest
    :param end_time: end time of contest
    :return: A list of locations
    """
    max_location = 9
    locations = set(str(x) for x in range(max_location + 1))
    query = """SELECT location FROM contest WHERE \'{}\' >= start_time AND \'{}\' <= end_time"""
    query = query.format(end_time, start_time)
    res = _execute_query(query)

    if res in none_list:
        logging.error("No locations available")
        return []

    unavailable_locations = set(x[0] for x in res)
    print(unavailable_locations)
    available_locations = locations - unavailable_locations
    return sorted(list(available_locations))


if __name__ == "__main__":
    start = time()

    temp = get_student_details("01FB15ECS342", get_ranks=True)
    print(type(temp), temp)
    quit()

    temp = get_professor_details("0")
    print(type(temp), temp)

    temp = get_plagiarism_code("c_dOHYbn")
    print(type(temp), temp)

    temp = get_unallocated_locations("2018-11-07 04:30:00", "2018-11-11 04:30:00")
    print(type(temp), temp)

    temp = get_unassigned_contests()
    print(type(temp), temp)

    temp = get_future_contest_student("01FB15ECS342")
    print(type(temp), temp)

    temp = get_contest_details("c_34r")
    print(type(temp), temp)

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

    temp = submit_code(
        **{
            "usn": "01FB15ECS341",
            "q_id": "q_3423km23f",
            "c_id": "c_dOHYbn",
            "code": "inp'u't()",
            "language": "python",
            "test_case_status": [],
            "score": 0,
            "status": "AC"
        }
    )

    print("SUBMIT CODE", type(temp), temp)

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

    print(random_alnum())
    print(time() - start)
