#!/bin/bash

RESPONSE=$1

# commande qui recupère le charset de la reponse
CHARSET=$(echo $RESPONSE | egrep -o "charset=(\w|-)+" | tail -n 1 | cut -d= -f2)
if [ ! $CHARSET ]
then
	CHARSET='utf-8'
fi
echo $CHARSET
