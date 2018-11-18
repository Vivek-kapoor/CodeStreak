import matplotlib.pyplot as plt


def draw_submission_chart(stats, usn):

	labels = [li['status'] for li in stats]
	values = [li['count'] for li in stats]
	print(labels)

	plt.pie(values, labels=labels, autopct='%1.1f%%')
	plt.axis('equal')
	plt.savefig('static/plots/'+usn)
	


