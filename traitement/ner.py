#!/bin/python3

import glob

import spacy
from spacy import displacy
from collections import Counter
import pandas as pd
pd.options.display.max_rows = 600
pd.options.display.max_colwidth = 400


#nlp = spacy.load('zh_core_web_md')
nlp = spacy.load('zh_core_web_trf')

files = glob.glob('../corpus/corpus_gov/paragraph/*.txt')

for file in files:
	with open(file, 'r') as f:
		text = f.read()
	document = nlp(text)

	for named_entity in document.ents:
		print(named_entity, named_entity.label_)
