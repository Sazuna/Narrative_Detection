#!/bin/bash

#
# ./get.sh [FILE]
#	FILE contains one link per line

#
# This script generates a folder named corpus/
# After the script ends running, please rename the generated corpus with a more specific name to avoid conflicts with future runs.
#

if [[ $# -lt 1 ]]
then
	echo "List of links file missing."
	echo "Use :"
	echo "    ./get.sh [FILE]"
	exit 1
fi


liens=$1
ORIGIN=$(basename $liens | cut -d '.' -f 1)
OUTPUT_NUMBER=1

EXPR_REG="(丝绸之路|一带一路)"

# Metadata files will be saved under this folder
if [ ! -d corpus/ ]
then
	mkdir corpus/
	mkdir corpus/metadata
	mkdir corpus/text
	mkdir corpus/contexts
	mkdir corpus/dump-html
	mkdir corpus/paragraph
else
	echo "An existing corpus has been found ( ./corpus/). This action will remplace it. Continue ? (y/n)"
	read continuer
	if [ ! "$continuer" == "y" ]
	then
		exit 1
	fi
fi

HTML_F="./table.html"

for URL in $(cat $liens); do
	echo "Getting" $URL
	if [[ "$URL" =~ ^https?:// ]]
	then 
		CODES_F="corpus/metadata/$OUTPUT_NUMBER-head.txt"
		# curl -i to get the header of the response before the body response
		# curl -I to get only the header of the response
		#curl -ILs $URL > $OUTPUT_FILE
		# tr -d "\r" corrige les erreurs d'affichage
		RESPONSE=$(curl -ILs $URL | tr -d "\r")
		CODE=$(./get_response_code.sh "$RESPONSE")
		echo "Response: " $CODE
		CHARSET=$(./get_response_charset.sh "$RESPONSE")
		echo "$URL $CODE $CHARSET" > $CODES_F
	else
		echo "$URL is not a valid url."
		continue
	fi

	if [[ $CODE -eq 200 ]]
	then
		# lynx does not work for chinese pages
		# DUMP=$(lynx -dump -nolist -assume_charset=$CHARSET -display_charset=$CHARSET $URL)
		DUMP=$(w3m -cookie "$URL")
		ASPIRATION=$(curl "$URL")
		# We must create the file now so that we can tokenize it (tokenizer words with file, not raw text)
		DUMP_F="corpus/text/$OUTPUT_NUMBER.txt"
		echo "$DUMP" > $DUMP_F
		echo $CHARSET
		if [[ "$CHARSET" -ne "UTF-8" && "$CHARSET" -ne "utf-8" && $CHARSET -ne "" && -n "$DUMP" ]]
		then
			DUMP=$(echo $DUMP | iconv -f $CHARSET -t UTF-8//IGNORE)
			ASPIRATION=$(echo $ASPIRATION | iconv -f $CHARSET -t UTF-8//IGNORE)
		fi
		# In some contexts, the word is cut in two lines.
		#if [[ $NO_SPACES -eq 1 ]]
		#then
			CONTEXT=$(./tokenize_chinese.py $DUMP_F)
			# Keep 20 words (punctuation counts as words with the Chinese tokenizer)
			CONTEXT=$(echo $CONTEXT | egrep -io "([^ ]* ){0,20}[^ ]?$EXPR_REG[^ ]?([^ ]* ){0,20}")
		#else
		#	CONTEXT=$(echo $DUMP | tr '\n' ' '| egrep -io "([^ ]* ){0,20}$EXPR_REG( [^ ]*){0,20}")
		#fi
		
	else
		DUMP=""
		CHARSET=""
		CONTEXT=""
		ASPIRATION=""
	fi
	# File names
	ASPIRATION_F="./corpus/dump-html/$OUTPUT_NUMBER.txt"
	CONTEXT_F="./corpus/contexts/$OUTPUT_NUMBER.txt"
	
	echo "$ASPIRATION" > $ASPIRATION_F
	echo "$CONTEXT" > $CONTEXT_F

	# Beautiful Soup script to keep only <p> inner content text
	PARAGRAPH_F="./corpus/paragraph/$OUTPUT_NUMBER.txt"
	./get_p_content.py $ASPIRATION_F > $PARAGRAPH_F

	# Count of occurrences
	COUNT=$(echo $CONTEXT | tr ' ' '\n' | egrep -ci "$EXPR_REG")
	echo "count : $COUNT"
	# On écrit
	echo -e "<tr><td>$OUTPUT_NUMBER</td><td>$CODE</td><td><a href=\"$URL\">$URL</a></td><td><a href=\"$ASPIRATION_F\">HTML aspiré</a></td><td><a href=\"$DUMP_F\">Texte aspiré</a></td><td>$COUNT</td><td><a href=\"$CONTEXT_F\">Contexte</a></td></tr>" >> $HTML_F
	OUTPUT_NUMBER=$(expr $OUTPUT_NUMBER + 1 )

	#OUTPUT_FILE=$(basename $lien | cut -d '.' -f 1).txt
	#echo $OUTPUT_FILE
	#wget $lien > 
done
