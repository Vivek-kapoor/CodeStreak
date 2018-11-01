import re
from json import load
from string import ascii_uppercase

with open('alcoding_db.json') as f:
    json_db =load(f)

def get_semester(usn):
    year = 15
    old_kids = re.findall(r"01FB\d{2}", usn)
    if old_kids:
        year = int(old_kids[0][4:])
    new_kids = re.findall(r"PES120\d{2}", usn)
    if new_kids:
        year = int(new_kids[0][6:])
    year_sem_dict = {14:9, 15: 7, 16: 5, 17: 3, 18: 1}
    return year_sem_dict[year]

def get_section(usn):
    temp = int(usn[-3:])//60
    return ascii_uppercase[temp]

insert_str = "INSERT INTO student values('{}', '{}', {}, {}, '{}', '{}', {}, '{}');"

for usn in json_db: 
    name = json_db[usn]['name']
    rating = json_db[usn]['rating']
    best = json_db[usn]['best']
    email = json_db[usn]['email']
    password = usn
    semester = get_semester(usn)
    section = get_section(usn)
    insert_command = insert_str.format(usn, name, rating, best, email, password, semester, section)
    print(insert_command)