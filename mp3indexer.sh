#!/bin/bash

outfile=mp3.json

cd web
if [ "$1" == "--check" ]; then
	eval "./mp3lint.py $paths"
else
    if [ "$1" = "" ]; then
        echo "Error: No directory specified as first argument"
        exit 1
    fi
	eval "../env/bin/python -m mp3.indexer $1" > $outfile.tmp || exit 1
	mv $outfile.tmp $outfile
fi
