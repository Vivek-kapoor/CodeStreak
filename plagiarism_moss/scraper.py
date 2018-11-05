
from bs4 import BeautifulSoup

import requests

def scrape_display(url):	
	r  = requests.get(url)
		
	data = r.text

	soup = BeautifulSoup(data)

	for link in soup.find_all('tr'):
		for heading in link.find_all('th'):
			print(heading.text,end="        ")

	for link in soup.find_all('tr'):
	    for data in link.find_all('td'):
	    	print(data.text.strip(),end=" ")
	    print()  
	   
