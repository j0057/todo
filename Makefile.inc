NAME = todo 

PIP_NAME = todo 
PIP_REQ = requirements.txt

PKG_BASE = file:///home/joost/git
PKG = xmlist xhttp

STATIC_DIRS = static

MAIN ?= todo.main

_test: test

data:
	cd $(ENV) ; bin/python -i -m todo.data
