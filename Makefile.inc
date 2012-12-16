NAME = mp3

PIP_NAME = jjm.mp3
PIP_REQ = requirements.txt

MAIN ?= jjm.mp3.main

PKG_BASE = file://$(shell readlink -f ..)
PKG = jjm jjm.core jjm.sh

STATIC_DIRS = conf web run

test-db: MAIN=jjm.mp3.db
test-db: test

