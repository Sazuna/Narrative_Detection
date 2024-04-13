#!/bin/python3

# Script qui prend en entrée deux dossiers corpus
# et produit un fichier des mots communs avec le nombre d'occurrences dans chaque corpus
# puis des mots différents avec le nombre d'occurrences dans chaque corpus

import sys
import glob
import jieba # tokenisation du chinois
from collections import defaultdict

def get_mots(fichiers, mots_dict):
	for fichier in fichiers:
		with open (fichier, 'r') as f:
			lignes = f.readlines() 
		for ligne in lignes:
			mots = jieba.cut_for_search(ligne)
			for mot in mots:
				mots_dict[mot] += 1

def main(corpus1, corpus2):
	fichiers1 = glob.glob(corpus1 + "/paragraph/*")
	fichiers2 = glob.glob(corpus2 + "/paragraph/*")
	mots1 = defaultdict(int)
	mots2 = defaultdict(int)
	get_mots(fichiers1, mots1)
	get_mots(fichiers2, mots2)
	corpus_nom1 = corpus1.split('/')[:-1][-1]
	corpus_nom2 = corpus2.split('/')[:-1][-1]


	# Mots communs
	mots_communs = set(mots1).intersection(set(mots2))
	liste = [(mot, mots1[mot], mots2[mot]) for mot in mots_communs]
	liste = sorted(liste, key=lambda x: x[1], reverse=True) # tri sur le nombre de mots dans le premier corpus

	with open('MC_' + corpus_nom1 + '_' + corpus_nom2 + '.tsv', 'w') as f:
		f.write('token\t' + corpus_nom1 + '\t' + corpus_nom2 + '\n')
		for mot in liste:
			f.write(mot[0] + "\t" + str(mot[1]) + "\t" + str(mot[2]) + "\n")

	# Mots différents
	mots_differents = set(mots1).symmetric_difference(set(mots2))
	liste = [(mot, mots1[mot], mots2[mot]) for mot in mots_differents]
	liste = sorted(liste, key=lambda x: x[1], reverse=True) # tri sur le nombre de mots dans le premier corpus

	with open('MD_' + corpus_nom1 + '_' + corpus_nom2 + '.tsv', 'w') as f:
		f.write('token\t' + corpus_nom1 + '\t' + corpus_nom2 + '\n')
		for mot in liste:
			f.write(mot[0] + "\t" + str(mot[1]) + "\t" + str(mot[2]) + "\n")
		

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Pas le bon nombre d'arguments.")
		print("Usage:")
		print("\t./mots_communs.py CORPUS1 CORPUS2")
		print("- CORPUS: nom de dossier valide avec des fichiers textes")
		sys.exit(1)
	corpus1, corpus2 = sys.argv[1], sys.argv[2]
	main(corpus1, corpus2)
