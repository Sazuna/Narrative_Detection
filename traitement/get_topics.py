#!/bin/python3

#https://maartengr.github.io/BERTopic/index.html#installation

#pip3 install bertopic

import sys, os

#folder = sys.argv[1]
#corpus = "corpus_discours_xijinping.txt"

text = []


for folder in sys.argv[1:]: # peut avoir plusieurs sous-corpus
	"""
	# Pour travailler par paragraphes
	for corpus in os.listdir(folder):
		with open(folder + corpus, 'r') as file:
			#raw = file.read()
			para = ""
			for line in file.readlines():
				line = line.strip()
				# problème: retours à la ligne. il faut prendre les sauts de ligne comme fin de paragraphe (ligne vide)
				if len(line) == 0: # fin de para
					#if len(para) > 15:
					text.append(para)
					print("#####" + para)
					# else pas un paragraphe, un titre uniquement
					para = ""
				else:
					if '• ' in line or '|' in line or 'bm' in line: # bm est le numéro d'identifiant d'un article pour la censure chinoise
						para = ""
						continue # sommaires etc
					para += line
					
			#text.extend(file.readlines())
	"""

	# Pour travailler par paragraphes récupérés avec BeautifulSoup (dossier corpus/paragraph)
	for corpus in os.listdir(folder):
		with open(folder + corpus, 'r') as file:
			#raw = file.read()
			para = ""
			for line in file.readlines():
				line = line.strip()
				# problème: retours à la ligne. il faut prendre les sauts de ligne comme fin de paragraphe (ligne vide)
				if '• ' in line or '|' in line or 'bm' in line: # bm est le numéro d'identifiant d'un article pour la censure chinoise
					continue # sommaires etc
				if len(line) > 0: # fin de para
					#if len(para) > 15:
					text.append(line)
					# else pas un paragraphe, un titre uniquement
					
			#text.extend(file.readlines())
	"""

	# Pour travailler par documents
	for corpus in os.listdir(folder):
		with open(folder + corpus, 'r') as file:
			#raw = file.read()
			para = ""
			doc = ""
			for line in file.readlines():
				line = line.strip()
				# problème: retours à la ligne. il faut prendre les sauts de ligne comme fin de paragraphe (ligne vide)
				if len(line) == 0: # fin de para
					#if len(para) > 15: # suppression des titres
					doc += para
					print("#####" + para)
					# else pas un paragraphe, un titre uniquement
					para = ""
				else:
					if '• ' in line or '|' in line or 'bm' in line: # bm est le numéro d'identifiant d'un article pour la censure chinoise
						para = ""
						continue # sommaires etc
					para += line
			text.append(doc)
	"""


print("Nombre de documents dans le corpus:", len(text))

#text = [t for t in text if len(t) > 20]

from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic import BERTopic

import jieba # chinese tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from umap import UMAP






# Tokenisation du texte chinois
#text = [' '.join(jieba.cut(t, cut_all=False)).strip() for t in text]
#text = [' '.join(jieba.cut_for_search(t)).strip() for t in text]


#Lastly, we can use a KeyBERT-Inspired model to reduce the appearance of stop words. This also often improves the topic representation:
representation = KeyBERTInspired()

# Tokenisation, suppression des stopwords
def tokenize_zh(text):
	#words = jieba.cut(text)
	words = jieba.lcut(text)
	return words

#stop_words = load_stopwords()

# Count vectorizer. Problème: les topics sont des mots récurrents, pas beaucoup de topics.
vectorizer = CountVectorizer(tokenizer=tokenize_zh)#, stop_words=["，", "的", "、", "。", "”", "“", "和", "在", "了", "与", "是"])

# Tfidf vectorizer.
#vectorizer = TfidfVectorizer(tokenizer=tokenize_zh, stop_words=["，", "的", "、", "。", "”", "“", "和", "在", "了", "与", "是"])

#UMAP is a technique for dimensionality reduction. In BERTopic, it is used to reduce the dimensionality of document embedding into something easier to use with HDBSCAN to create good clusters.
umap = UMAP(n_neighbors=15, n_components=10, metric='cosine', low_memory=False)

# vectorizer. Pour réduire les mots communs.
#There are two parameters worth exploring in the ClassTfidfTransformer, namely bm25_weighting and reduce_frequent_words.
# bm25_weighting: bien pour les petits datasets.
# https://maartengr.github.io/BERTopic/getting_started/ctfidf/ctfidf.html
ctfidf_model = ClassTfidfTransformer(bm25_weighting=True, reduce_frequent_words=True)

# The number of words per topic to extract. Setting this too high can negatively impact topic embeddings as topics are typically best represented by at most 10 words.
#n_words = 5

topic_model = BERTopic(language="chinese (simplified)",
			#top_n_words=n_words,
			vectorizer_model=vectorizer,
			umap_model = umap,
			calculate_probabilities=True,
			representation_model = representation,
			ctfidf_model = ctfidf_model,
			verbose=True)

# fit_transform Fit the models on a collection of documents, generate topics, and return the probabilities and topic per document.
topics, probs = topic_model.fit_transform(text)


print(topic_model.get_topic_info())
print(topics[0])
freq = topic_model.get_topic_info()
freq.head(10)

# Post-traitements
# https://maartengr.github.io/BERTopic/api/bertopic.html#bertopic._bertopic.BERTopic.approximate_distribution

topic_distr, topic_token_distr = topic_model.approximate_distribution(text, calculate_tokens=True)
distributions = [distr[topic] if topic != -1 else 0 for topic, distr in zip(topics, topic_distr)]

document_info = topic_model.get_document_info(text,
                                              metadata={"Topic_distribution": distributions})


print("Distributions:")
print(distributions)

print("\n\nDocument_info:")
print(document_info)

# ajouter un numéro pour avoir le numéro d'un topic en particulier
representative_docs = topic_model.get_representative_docs()

print("\n\nRepresentative_docs")
print(representative_docs)
