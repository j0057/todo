#!/bin/bash

paths=/home/joost/shared/Music/{Ambient,Dub*,Electro*,Exotic,Hip-Hop,Metal*,Trip*,Weird*}
outfile=mp3.json

if [ "$1" == "--check" ]; then
	eval "./mp3lint.py $paths"
else
	eval "./mp3indexer.py $paths" > $outfile.tmp
	mv $outfile.tmp $outfile
fi
