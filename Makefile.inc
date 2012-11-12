NAME = mp3

PIP_NAME = jjm.mp3
PIP_REQ = requirements.txt

MAIN ?= jjm.mp3.main

PKG_BASE = file:///home/joost/git
PKG = jjm jjm.core jjm.sh

run-db:
	$(ENV)/bin/python -m mp3.db.main

