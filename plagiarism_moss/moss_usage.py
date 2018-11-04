import mosspy
from scraper import *
userid = 881220386

#dummy funciton
def fetch_submissions_for_contest(c_id):
	return {1:"heyyy\nh\nhn\n",2:"heyyheyyy\nh\nhn\n",3:"heyyyyheyyy\nh\nhn\n"}



'''
TODO: Database fetch
RETURN : A dictionary of all the codes : 
 	key : USN
	value : code as a string

'''
c_id = 1
submissions = fetch_submissions_for_contest(c_id)

for usn in submissions.keys():
 	with open("submission/"+str(usn)+".c", "w") as text_file:
 		text_file.write(submissions[usn])


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