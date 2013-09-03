NAME = mp3

PIP_NAME = mp3
PIP_REQ = requirements.txt

MAIN ?= mp3.main

PKG = core sh

STATIC_DIRS = conf web run

_test: test

test-db: MAIN=mp3.db
test-db: test

