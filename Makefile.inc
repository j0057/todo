NAME = mp3

PIP_NAME = mp3
PIP_REQ = requirements.txt

MAIN ?= mp3.main

run-db:
	$(ENV)/bin/python -m mp3.db.main

