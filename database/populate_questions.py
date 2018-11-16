from db_access import create_question, none_list

question_details = {
    "p_id": "01FB15ECS327",
    "name": "Prime Numbers",
    "problem": "Given an integer in a single line, output YES if it is a prime number, else NO",
    "difficulty": "Easy",
    "languages": {"c"},
    "tags": {"easy", "math", "number theory"},
    "test_cases": [{"input": "1", "output": "NO", "points": 5.0},
                   {"input": "12", "output": "NO", "points": 5.0},
                   {"input": "2", "output": "YES", "points": 5.0}],
    "editorial": "primality testing",
    "time_limit": 0.5,
    "memory_limit": 256,
    "score": 15
}

temp = create_question(**question_details)
if temp in none_list:
    print("Something went wrong, Check the values and try again")
else:
    print("Success! Enter next question")
