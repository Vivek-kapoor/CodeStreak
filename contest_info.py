from db_access import get_active_contest, get_archived_contest
from flask import render_template


def active_contest_list(usn):

	#active_contests = get_active_contest(usn)
	active_contests = [{'name': "kys", 'time': "now"}]
	
	return render_template("StudentDashboard.html", contests = active_contests)


if __name__ == "__main__":
	active_contest_list("skfj")
