"""
This file contains the code that connects the backend to database
Run this file to check if the connection to database works
If it doesn't throw an error, it works!
"""

import psycopg2
import logging

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

codestreak=# \d professor;
                     Table "public.professor"
  Column  |         Type          | Collation | Nullable | Default
----------+-----------------------+-----------+----------+---------
 p_id     | character varying(50) |           | not null |
 name     | character varying(50) |           |          |
 password | character varying(50) |           |          |
 email    | character varying(50) |           |          |
Indexes:
    "professor_pkey" PRIMARY KEY, btree (p_id)
Referenced by:
    TABLE "contest" CONSTRAINT "contest_p_id_fkey" FOREIGN KEY (p_id) REFERENCES professor(p_id)
    TABLE "question" CONSTRAINT "question_p_id_fkey" FOREIGN KEY (p_id) REFERENCES professor(p_id)
"""


def connect_db():
    """
    Connects to the postgres database
    :return: postgres connection object
    """
    connect_str = "dbname='codestreak' user='codestreak@codestreak' host='codestreak.postgres.database.azure.com' password='Student123' port='5432'"
    try:
        conn = psycopg2.connect(connect_str)
        return conn

    except:
        logging.error('Failed to connect to database')
        return None


def validate_student(usn, password):
    """
    Validates login credential for student
    :param usn: student's usn, e.g. 01FB15ECS342
    :param password: student's password, e.g. 01FB15ECS342
    :return: False if usn does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT '""" + usn + """' IN (SELECT usn FROM student)) AND (SELECT (SELECT password FROM student where usn = '""" + usn + """') = '""" + password + """');"""
    conn = connect_db()
    res = False
    if conn:
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        conn.close()
    return res


def validate_professor(p_id, password):
    """
    Validates login credential for professor
    :param p_id: professor's id, e.g. 01FB15ECS342
    :param password: professor's password, e.g. 01FB15ECS342
    :return: False if p_id does not exist or password doesn't match. Else True
    """
    query = """SELECT (SELECT '""" + p_id + """' IN (SELECT p_id FROM professor)) AND (SELECT (SELECT password FROM professor where p_id = '""" + p_id + """') = '""" + password + """');"""
    conn = connect_db()
    res = False
    if conn:
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        conn.close()
    return res


if __name__ == "__main__":
    print(validate_professor('abcd', 'pqrs'))
