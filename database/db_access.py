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
"""

def connect_db():
    """
    Connects to the postgres database
    :return: postgres connection object
    """
    connect_str = "dbname='codestreak' user='postgres' password='student'"
    try:
        conn = psycopg2.connect(connect_str)
        return conn
    except:
        logging.error('Failed to connect to database')
        return None

def validate_student(usn, password):
    query = """SELECT (SELECT password FROM student where usn = '""" + usn + """') = '""" + password + """';"""
    conn = connect_db()
    res = False
    if conn:
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        conn.close()
    return res

def validate_professor(a_id, password):
    query = """SELECT (SELECT password FROM professor where a_id = '""" + a_id + """') = '""" + password + """';"""
    conn = connect_db()
    res = False
    if conn:
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        conn.close()
    return res



if __name__ == "__main__":
    print(validate_student('01FB15ECS342', '01FB15ECS342'))
