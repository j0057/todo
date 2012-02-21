
DEPLOY_CODE = env/lib/python2.7/site-packages/local
DEPLOY_WEB = env/web

LIB_TGT = $(addsuffix .zip,$(addprefix dist/lib/,$(LIB)))
LIB_SRC = $(addprefix lib/,$(LIB))

PP = $(subst ,:,$(LIB_TGT))

PKG_FULL = $(addprefix env/pip-,$(PKG))

SRC_FILES = $(shell find py/$(NAME) -name '*.py')

CLEAN = $(addprefix clean-,$(LIB))

.PHONY: default all clean really-clean test runtime vars

default: all test
	@echo "# $@"

all: dist/$(NAME).zip $(LIB_TGT)
	@echo "# $@"

clean: deploy-clean $(CLEAN)
	@echo "# $@"
	@rm -rfv dist
	@find py -name '*.pyc' -exec rm -v '{}' ';'

clean-%:
	@echo "# $@"
	@make -C lib/$* clean

really-clean: clean
	@echo "# $@"
	@rm -rf env/*
	@rm -rfv env

env:
	@echo "# $@"
	virtualenv env

env/pip-%:
	@echo "# $@"
	@echo "pip -v install $*"
	@bash -c ". env/bin/activate ; pip -v install $*"
	@touch env/pip-$*

runtime: env $(PKG_FULL)
	@echo "# $@"

dist:
	@echo "# $@"
	@mkdir -vp dist
	@mkdir -vp dist/lib

dist/lib/%.zip: dist
	@echo "# $@"
	@make -C lib/$* dist/$*.zip
	@cp -v lib/$*/dist/$*.zip dist/lib/$*.zip

dist/%.zip: dist $(SRC_FILES)
	@echo "# $@"
	cd py ; zip -r ../dist/$*.zip $* -i '*.py'

test: $(LIB_TGT) runtime
	@echo "# $@"
	PYTHONPATH=py:$(PP) env/bin/python -m $(MAIN)

deploy: dist/$(NAME).zip $(LIB_TGT) runtime
	@echo "# $@"
	rm -rf $(DEPLOY_CODE)
	cp -r dist $(DEPLOY_CODE)
	cd $(DEPLOY_CODE) ; cd .. ; find $(notdir $(DEPLOY_CODE)) -name '*.zip' > $(notdir $(DEPLOY_CODE)).pth
	rm -rf $(DEPLOY_WEB)
	cp -r web $(DEPLOY_WEB)

deploy-clean:
	@echo "# $@"
	rm -rf $(DEPLOY_CODE)
	rm -rf $(DEPLOY_CODE).pth
	rm -rf $(DEPLOY_WEB)

run: runtime deploy
	@echo "# $@"
	cd env ; bin/python -m $(MAIN)

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

