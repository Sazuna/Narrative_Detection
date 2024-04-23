#!/bin/python3


import sys
import os
import glob
import jieba # tokenisation du chinois
from collections import defaultdict
from tqdm import tqdm


import subprocess

from math import log10
from math import fabs

def specif_to_cache(f, F, t, T):
	"""
	Transforme les quatre paramètres du calcul de spécificité en nom de cache
	f: int, nombre d'occurrences du terme dans la partie focus.
	F: int, nombre total de mots de la partie focus.
	t: int, nombre d'occurrences du terme dans la partie window.
	T: int, nombre total de mots dans la partie window.
	return: str, le lien du fichier à enregistrer dans le cache.
	"""
	return "cache/specif-" + str(f) + "-" + str(F) + "-" + str(t) + "-" + str(T)

def specif(f, F, t, T):
	"""
	Calcul du score de spécificité. Enregistre ces scores dans un cache afin de ne pas avoir à refaire le calcul pour des valeurs identiques.
	f: int, nombre d'occurrences du terme dans la partie focus.
	F: int, nombre total de mots de la partie focus.
	t: int, nombre d'occurrences du terme dans la partie window.
	T: int, nombre total de mots dans la partie window.
	return: float, le score de spécificité.
	"""
	# cache des spécificités
	specif_file = specif_to_cache(f, F, t, T)
	if os.path.exists(specif_file):
		#print("\nArchive trouvée dans le cache : " + webarchive)
		with open(specif_file, "r") as f:
			score = float(f.readlines()[0].strip())
			return score

	command = "R --vanilla -s -e 'library(\"textometry\", lib=\".\"); res <- specificities.distribution.plot({f},{F},{t},{T}); print(res[\"mode\"]); print(res[\"pfsum\"][[1]][[{f}+1]]);'".format(f=f, t=t, F=F, T=T+F) # il faut faire T + F car la commande R va faire T - F et pourrait avoir un chiffre négatif, ce qui fait crasher la commande.
	try:
		res = subprocess.check_output(command, shell=True, text=True)
		res = res.split('\n')
		mode = float(res[1].split()[1])
		proba = float(res[3].split()[1]) # Mais proba est toujours = 10.0
		if mode <= f:
			score = fabs(log10(fabs(proba)))
		else:
			score = -fabs(log10(fabs(proba)))
		with open(specif_file, "w") as f:
			f.write(str(score))
		return score
	except:
		print("Erreur en calculant la spécificité pour f={f}, F={F}, t={t}, T={T}".format(f=f, F=F, t=t, T=T))



def specificity(window_dict: dict, focus_dict: dict, corpus_nom1: str, corpus_nom2: str):
	"""
	calcule et affiche le score de spécificité des mots du focus par rapport aux mots du window. N'affiche que les 10 plus spécifiques et les 10 moins spécifiques.
	window_dict: dict, les fréquences des lemmes dans le corpus de référence.
	focus_dict: dict, les fréquences des lemmes dans le corpus à comparer.
	corpus_nom1: le nom du corpus 1 pour l'enregistrement du fichier de résultats
	corpus_nom2: le nom du corpus 2 pour l'enregistrement du fichier de résultats
	"""
	vocabulaire = set(window_dict.keys()).union(set(focus_dict.keys()))
	T = sum(window_dict.values())
	F = sum(focus_dict.values())
	specificities = {}
	for mot in tqdm(list(vocabulaire), desc="Calcul des spécificités", bar_format="{l_bar}{bar:"+str(len(vocabulaire))+"}{r_bar}"):
		f = focus_dict.get(mot) or 0
		t = window_dict.get(mot) or 0
		specificities[mot] = specif(f, F, t, T)
	# Récupération des 10 scores de spécificités des mots les plus et les moins spécifiques
	spec = sorted(specificities.items(), key=lambda x: x[1])

	most_specific = spec[-10:]
	less_specific = spec[0:10]

	print("Moins spécifiques")
	for l in less_specific:
		print("  " + str(l[0]) + ' ' + str(l[1]))
	print("Plus spécifiques")
	for m in most_specific:
		print("  " + str(m[0]) + ' ' + str(m[1]))

	with open("specif-" + corpus_nom1 + "-" + corpus_nom2 + ".tsv", "w") as file:
		file.write("token\tspecif\n")
		for line in spec:
			file.write(line[0].strip() + "\t" + str(line[1]) + "\n")

def get_mots(fichiers, mots_dict):
	for fichier in fichiers:
		with open (fichier, 'r') as f:
			lignes = f.readlines() 
		for ligne in lignes:
			#mots = jieba.cut_for_search(ligne)
			mots = jieba.cut(ligne)
			for mot in mots:
				mots_dict[mot] += 1

def main(corpus1, corpus2):
	if not os.path.exists("cache/"):
		os.mkdir("cache")
	fichiers1 = glob.glob(corpus1 + "/paragraph/*")
	fichiers2 = glob.glob(corpus2 + "/paragraph/*")
	mots1 = defaultdict(int)
	mots2 = defaultdict(int)
	get_mots(fichiers1, mots1)
	get_mots(fichiers2, mots2)

	corpus_nom1 = corpus1.split('/')[:-1][-1]
	corpus_nom2 = corpus2.split('/')[:-1][-1]
	specificity(mots1, mots2, corpus_nom1, corpus_nom2)
	"""


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
	"""

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Pas le bon nombre d'arguments.")
		print("Usage:")
		print("\t./mots_communs.py CORPUS1 CORPUS2")
		print("- CORPUS: nom de dossier valide avec des fichiers textes")
		sys.exit(1)
	corpus1, corpus2 = sys.argv[1], sys.argv[2]
	main(corpus1, corpus2)
