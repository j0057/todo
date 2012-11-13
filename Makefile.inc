NAME = mp3

PIP_NAME = jjm.mp3
PIP_REQ = requirements.txt

MAIN ?= jjm.mp3.main

PKG_BASE = file:///home/joost/git
PKG = jjm jjm.core jjm.sh

STATIC_DIRS = conf web run

run-db: runtime unlink-code deploy-code
	cd $(ENV) ; bin/python -m jjm.mp3.db

