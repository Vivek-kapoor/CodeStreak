from db_access import get_active_contest, get_archived_contest
from flask import render_template


def contest_list(usn):

	#active_contests = get_active_contest(usn)
	#archivef_contests = get_archived_contest(usn)
	active_contests = [{'name': "kys", 'time': "now", 'active': 1},{'name': "gabe", 'time': "now", 'active': 1}]
	archived_contests = [{'name': "kys1", 'time': "now", 'active': 0},{'name': "gabe1", 'time': "now", 'active': 0}]
	contests = active_contests + archived_contests
	
	
	return render_template("Student Dashboard.html", contests = contests)
	





if __name__ == "__main__":
	contest_list("skfj")
