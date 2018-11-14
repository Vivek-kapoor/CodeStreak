
from bs4 import BeautifulSoup

import requests

output_dict = [] 

def scrape_display(url):
	# outputs a dictionary 	
	r  = requests.get(url)
		
	data = r.text

	soup = BeautifulSoup(data, "lxml")


	for link in soup.find_all('tr'):
		ind_list = []
		for heading in link.find_all('th'):
			ind_list.append(heading.text) 
			print(heading.text,end="        ")
		output_dict.append(output_dict)
	for link in soup.find_all('tr'):
		ind_list = []
	    for data in link.find_all('td'):
			ind_list.append(data.text.strip())
	    	print(data.text.strip(),end=" ")
	    print()

	
	  
	   
print(output_dict)