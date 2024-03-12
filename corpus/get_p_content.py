#!/bin/python3

import sys, os

from bs4 import BeautifulSoup

file = sys.argv[1]

#if not os.path.exists(new_folder):
#	os.mkdir(new_folder)

#for corpus in os.listdir(folder):
with open(file, 'r') as file:
	text = file.read()
	soup = BeautifulSoup(text, 'html.parser')
	all_p = soup.findAll('p', limit=None)
	all_p = '\n'.join([p.get_text() for p in all_p])
	print(all_p)

	#with open(new_folder + corpus, 'w') as file2:
	#	file2.write(all_p)
	#for p in all_p:
	#	print(p.get_text())
	#print(soup.get_text())
