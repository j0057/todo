# in: NAME PKG LIB MAIN

# build dist/$NAME.zip
# build dist/lib/*.zip

# intialize runtime environment

# deploy python code
# deploy web files
# deploy configuration

# test: run code from source
# run: run code from dist

ENV ?= /srv/$(NAME)

DEPLOY_CODE = $(ENV)/lib/python2.7/site-packages/local
DEPLOY_WEB = $(ENV)/web
DEPLOY_CONF = $(ENV)/conf

LIB_TGT = $(addsuffix .zip,$(addprefix dist/lib/,$(LIB)))
LIB_SRC = $(addprefix lib/,$(LIB))

PP = $(subst ,:,$(LIB_TGT))

PKG_FULL = $(addprefix $(ENV)/pip-,$(PKG))

SRC_FILES = $(shell find py/$(NAME) -name '*.py')
OBJ_FILES = $(SRC_FILES:.py=.pyc)

CLEAN = $(addprefix clean-,$(LIB))

DEPLOY_TARGETS = deploy-code deploy-web deploy-conf

.PHONY: default all clean really-clean test runtime vars

all: $(LIB_TGT) dist/$(NAME).zip 

#
# build
#

build: $(OBJ_FILES)

%.pyc: %.py
	python -c "from py_compile import compile as c; c('$*.py')"

#
# clean
#

clean: $(CLEAN) 
	rm -rf dist
	find py -name '*.pyc' -delete

clean-%:
	@make -C lib/$* clean

really-clean: clean deploy-clean
	rm -rf $(ENV)

#
# runtime
#

runtime: $(ENV) $(PKG_FULL)

$(ENV):
	sudo mkdir -p $(ENV)
	sudo chown $(shell id -un).$(shell id -gn) $(ENV)
	virtualenv $(ENV)

$(ENV)/pip-%:
	$(ENV)/bin/pip install $*
	@touch $(ENV)/pip-$*

#
# dist
#

.VOLATILE: dist

dist:
	@mkdir -p dist dist/lib

dist/lib/%.zip: dist lib/%
	@make -C lib/$* dist/$*.zip
	cp -u lib/$*/dist/$*.zip dist/lib/$*.zip

dist/%.zip: dist $(SRC_FILES)
	cd py; zip -rq ../dist/$*.zip $* -i '*.py'

#
# test
#

test: $(LIB_TGT) 
	PYTHONPATH=py:$(PP) $(ENV)/bin/python -m $(MAIN)

test-uwsgi: $(LIB_TGT)

test-uwsgi-http: $(LIB_TGT)

#
# deploy
#

deploy: all $(DEPLOY_TARGETS)

deploy-web:
	@rm -rf $(DEPLOY_WEB)
	cp -r web $(DEPLOY_WEB)

deploy-code:
	@rm -rf $(DEPLOY_CODE)
	cp -r dist $(DEPLOY_CODE)
	cd $(DEPLOY_CODE); cd ..; find $(notdir $(DEPLOY_CODE)) -name '*.zip' > $(notdir $(DEPLOY_CODE)).pth

deploy-conf:
	@rm -rf $(DEPLOY_CONF)
	cp -r conf $(DEPLOY_CONF)
	ls $(DEPLOY_CONF)/uwsgi/* > /dev/null 2>&1 && touch $(DEPLOY_CONF)/uwsgi/*

deploy-clean:
	rm -rf $(DEPLOY_CODE) $(DEPLOY_CODE).pth
	rm -rf $(DEPLOY_WEB)

#
# run
#

run: deploy
	cd $(ENV); bin/python -m $(MAIN)

run-uwsgi: deploy
	cd $(ENV); bin/uwsgi --ini ../conf/uwsgi/$(NAME).ini

run-uwsgi-http: deploy
	cd $(ENV); bin/uwsgi --ini ../conf/uwsgi/$(NAME).ini --protocol http --socket :8000

#
# debug
#

vars:
	@echo "NAME     : $(NAME)"
	@echo "LIB      : $(LIB)"
	@echo "LIB_SRC  : $(LIB_SRC)"
	@echo "LIB_TGT  : $(LIB_TGT)"
	@echo "PP       : $(PP)"
	@echo "PKG      : $(PKG)"
	@echo "PKG_FULL : $(PKG_FULL)"
	@echo "CLEAN    : $(CLEAN)"
	@echo "SRC_FILES: $(SRC_FILES)"

