NAME = oauth

PIP_NAME = oauth
PIP_REQ = requirements.txt

PKG_BASE = file://$(shell readlink -f ..)
PKG = xmlist xhttp

STATIC_DIRS = static

MAIN ?= oauth.main

include Makefile.keys


