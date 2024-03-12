#!/bin/python3

"""

Script qui récupère les verbes et les noms qui co-occurent avec un mot-clé des routes de la soie (dans le même paragraphe)

"""

import glob
import sys

import spacy
from spacy import displacy
from collections import Counter
import pandas as pd
pd.options.display.max_rows = 600
pd.options.display.max_colwidth = 400


#nlp = spacy.load('zh_core_web_md')
nlp = spacy.load('zh_core_web_trf')

files = glob.glob('../corpus/corpus_gov/paragraph/*.txt')

mots = []
for file in files:
	with open(file, 'r') as f:
		text = f.readlines()
	for paragraph in text:
		if any(keyword in paragraph for keyword in ["丝", "绸", "一带"]):
			document = nlp(paragraph)
			#print(paragraph)

			for token in document:
				if token.pos_ == "VERB" or token.pos_ == "NOUN":
					#print(token.text, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
					mots.append(token.text)

import numpy as np
import pandas as pd

df = pd.value_counts(np.array(mots))
print(df.to_string())
