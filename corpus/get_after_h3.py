#!/bin/python3


# Script utile pour le corpus extrait de ciis.

import sys, os

from bs4 import BeautifulSoup

file = sys.argv[1]

#for corpus in os.listdir(folder):
with open(file, 'r') as file:
	text = file.read()
	soup = BeautifulSoup(text, 'html.parser')
	h3 = soup.find("h3") # contexte de publication
	if h3:
		next_sibling = h3.next_sibling
		#content = h3.next_sibling()
		while next_sibling and next_sibling.name == None:
			next_sibling = next_sibling.next_sibling
		text = next_sibling.get_text(separator='\n', strip=True)
		print(text)
	else:
		#print("No <h3> was found on this page ! Maybe not a ciis corpus ?")
		print("")
