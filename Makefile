
include Makefile.inc

ENV = env

TARGET = /srv/$(NAME)
TARGET_USER ?= www-data
TARGET_GROUP ?= www-data

DEPLOY_WEB = $(ENV)/web
DEPLOY_CONF = $(ENV)/conf

SRC = file://$(shell pwd)

QUIET ?= --quiet

PIP_CACHE = .cache

.PHONY: run

run: runtime undeploy-code link-code
	@echo '--> $@'
	cd $(ENV) ; bin/python -m $(MAIN)

run-pkg: unlink-code deploy deploy-code 
	@echo '--> $@'
	cd $(ENV) ; bin/python -m $(MAIN)

deploy-live: deploy
	@echo '--> $@'
	virtualenv --relocatable $(ENV) > /dev/null
	sudo chown -R $(TARGET_USER).$(TARGET_GROUP) $(ENV)
	sudo rm -rf $(TARGET)
	sudo mv $(ENV) $(TARGET)

deploy: runtime deploy-code deploy-web deploy-conf touch-conf
	@echo '--> $@'

runtime: $(ENV) deploy-pkgs
	@echo '--> $@'

$(ENV): 
	@echo '--> $@'
	virtualenv $(ENV) $(QUIET)
	$(ENV)/bin/pip install --upgrade --download-cache $(PIP_CACHE) 'distribute>=0.6.30' $(QUIET)
	$(ENV)/bin/pip install --upgrade --download-cache $(PIP_CACHE) --requirement $(PIP_REQ) $(QUIET)

deploy-pkgs: $(addprefix deploy-pkg-,$(PKG))
	@echo '--> $@'

deploy-code: deploy-pkg-$(PIP_NAME)
	@echo '--> $@'

deploy-pkg-%:
	@echo '--> $@'
	$(ENV)/bin/pip install --upgrade $(PKG_BASE)/$(subst deploy-pkg-,,$@) $(QUIET)
	@find $(ENV) -name top_level.txt -path '*$(subst deploy-pkg-,,$@)-*' -exec sh -c 'echo $(subst deploy-pkg-,,$@) > {}' ';'

undeploy-code:
	@echo '--> $@'
	$(ENV)/bin/pip uninstall $(PIP_NAME) --yes $(QUIET) || true

link-code:
	@echo '--> $@'
	ln -sn $(shell pwd)/$(subst .,/,$(PIP_NAME)) $(ENV)/lib/python2.7/site-packages/$(subst .,/,$(PIP_NAME)) || true

unlink-code:
	@echo '--> $@'
	rm -f $(ENV)/lib/python2.7/site-packages/$(subst .,/,$(PIP_NAME)) || true

deploy-web:
	@echo '--> $@'
	@rm -rf $(DEPLOY_WEB)
	cp -r web $(DEPLOY_WEB)

deploy-conf:
	@echo '--> $@'
	@rm -rf $(DEPLOY_CONF)
	cp -r conf $(DEPLOY_CONF)

touch-conf:
	@echo '--> $@'
	ls $(DEPLOY_CONF)/uwsgi/* > /dev/null 2>&1 && touch $(DEPLOY_CONF)/uwsgi/* || true

clean:
	@echo '--> $@'
	rm -rf $(ENV)

really-clean: clean
	@echo '--> $@'
	rm -rf $(PIP_CACHE)

# - rename web to static
# - make repo's relative or something ... referring to file:///home/joost/git/... is not useful in other situations
# - patch up top_level.txt

