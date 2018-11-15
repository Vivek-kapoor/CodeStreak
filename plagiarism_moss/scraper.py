
from bs4 import BeautifulSoup

import requests



def scrape_display(url):
	# outputs a dictionary 	
	r  = requests.get(url)
	output_dict = [] 
	data = r.text

	soup = BeautifulSoup(data, "lxml")


	for link in soup.find_all('tr'):
		ind_list = []
		for heading in link.find_all('th'):
			ind_list.append(heading.text) 
			
		
	
	for link in soup.find_all('tr'):
		ind_list = []
		for data in link.find_all('td'):
			ind_list.append(data.text.strip())
		output_dict.append(ind_list)
	return output_dict
			
		
	  
	   
