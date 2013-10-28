NAME = xhttptest

PIP_NAME = xhttptest
PIP_REQ = requirements.txt

MAIN ?= xhttptest

PKG = xmlist xhttp

PY_VERSION ?= python3.3

STATIC_DIRS = conf

include build/Makefile
