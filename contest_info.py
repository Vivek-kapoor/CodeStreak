from db_access import get_active_contest_student, get_archived_contest_professor
from flask import render_template


def contest_list(usn):

	#active_contests = get_active_contest_student(usn)
	#archived_contests = get_archived_contest_student(usn)
	active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
	archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
	#contests = active_contests + archived_contests
	
	
	return render_template("Student Dashboard.html", active_contests = active_contests, archived_contests = archived_contests)
	





if __name__ == "__main__":
	contest_list("skfj")
