MAIN ?= todo.main

_test: test

data:
	cd $(ENV) ; bin/python -i -m todo.data

clean-model: remove-db model

remove-db:
	rm -vf $(ENV)/db.dat

model:
	cd $(ENV) ; bin/python -i -m todo.model

include build/Makefile

