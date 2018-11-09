import mosspy
from scraper import *
userid = 881220386
from db_access import get_plagiarism_code

'''
TODO: Database fetch
RETURN : A dictionary of all the codes : 
 	key : USN
	value : code as a string

'''
# return value ( (q_id:USN) -> code)
c_id = "c_dOHYbn"
submissions = get_plagiarism_code(c_id)
print(submissions)

for usn in submissions.keys():
 	with open("submission/"+str(usn[1])+".c", "w") as text_file:
 		text_file.write(submissions[usn]['code'])


m = mosspy.Moss(userid, "c")
# can add a base file(skeleton code which need not be compared)
#m.addBaseFile("submission/a01.py")

# Submission Files
m.addFilesByWildcard("submission/*.c")

url = m.send() # Submission Report URL

print ("Report Url: " + url)

# Save report file
m.saveWebPage(url, "submission/report.html")

# Download whole report locally including code diff links


mosspy.download_report(url, "submission/report/", connections=8)

scrape_display(url)