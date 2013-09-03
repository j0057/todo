NAME = oauth

PIP_NAME = oauth
PIP_REQ = requirements.txt

PKG = xmlist xhttp

STATIC_DIRS = conf static 

MAIN ?= oauth.main

export OAUTH_KEYS = conf/keys.json

include build/Makefile
