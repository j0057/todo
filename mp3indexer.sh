#!/bin/bash

paths=/home/joost/shared/Music/{Ambient,Dub*,Electro*,Exotic,Hip-Hop,Metal*,Trip*,Weird*}
outfile=web/mp3.json

if [ "$1" == "--check" ]; then
	eval "./mp3lint.py $paths"
else
	eval "PYTHONPATH=py env/bin/python -m jjm.mp3.mp3indexer $paths" > $outfile.tmp
	mv $outfile.tmp $outfile
fi
