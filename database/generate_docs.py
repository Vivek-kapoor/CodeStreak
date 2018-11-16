import re
import db_access as db
with open("../db_access.py", "r") as f:
    data = f.read()
function_names = re.findall(r"(?<=def )\w+", data)

print(len(function_names), len(set(function_names)), function_names)

for i, function_name in enumerate(function_names):
    function_obj = getattr(db, function_name)
    doc = str(function_obj.__doc__)
    doc_lines = doc.split('\n')
    if len(doc_lines) < 2:
        line = "NO DOC"
    else:
        line = doc_lines[1].strip()
    print(i, ". ", function_name, ": ", line, sep="")