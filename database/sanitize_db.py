from json import dumps
import db_access as db

query = """SELECT q_id FROM question"""
update_query = """UPDATE question SET test_cases = \'{}\' WHERE q_id = \'{}\'"""
res = db._execute_query(query)

for q_id_tup in res:
    q_id = q_id_tup[0]
    question_details = db.get_question_details(q_id)
    test_cases = question_details['test_cases']
    for i in range(len(test_cases)):
        test_case = test_cases[i]
        if "point" in test_case:
            test_case["points"] = test_case["point"]
            del test_case["point"]
        if "score" in test_case:
            test_case["points"] = test_case["score"]
            del test_case["score"]
        test_cases[i] = test_case
    test_cases = dumps(test_cases)
    query = update_query.format(test_cases, q_id)
    print(bool(db._execute_query(query)))
