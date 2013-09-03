NAME = todo 

PIP_NAME = todo 
PIP_REQ = requirements.txt

PKG = xmlist xhttp

STATIC_DIRS = static

MAIN ?= todo.main

_test: test

data:
	cd $(ENV) ; bin/python -i -m todo.data

clean-model: remove-db model

remove-db:
	rm -vf env/db.dat

model:
	cd $(ENV) ; bin/python -i -m todo.model

include build/Makefile

