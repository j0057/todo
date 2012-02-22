
ENV = env

DEPLOY_CODE = $(ENV)/lib/python2.7/site-packages/local
DEPLOY_WEB = $(ENV)/web

LIB_TGT = $(addsuffix .zip,$(addprefix dist/lib/,$(LIB)))
LIB_SRC = $(addprefix lib/,$(LIB))

PP = $(subst ,:,$(LIB_TGT))

PKG_FULL = $(addprefix env/pip-,$(PKG))

SRC_FILES = $(shell find py/$(NAME) -name '*.py')
OBJ_FILES = $(SRC_FILES:.py=.pyc)

CLEAN = $(addprefix clean-,$(LIB))

.PHONY: default all clean really-clean test runtime vars

all: $(LIB_TGT) dist/$(NAME).zip 

clean: $(CLEAN) deploy-clean
	rm -rf dist
	find py -name '*.pyc' -delete

clean-%:
	@make -C lib/$* clean

really-clean: clean
	rm -rf $(ENV)

%.pyc: %.py
	$(ENV)/bin/python -c "from py_compile import compile as c; c(\"$*.py\")"

$(ENV):
	virtualenv -q $(ENV)

$(ENV)/pip-%:
	$(ENV)/bin/pip install -q $*
	@touch $(ENV)/pip-$*

runtime: $(ENV) $(PKG_FULL)

dist:
	@mkdir -p dist dist/lib

dist/lib/%.zip: dist lib/%
	@make -C lib/$* dist/$*.zip
	cp lib/$*/dist/$*.zip dist/lib/$*.zip

dist/%.zip: dist $(OBJ_FILES)
	cd py; zip -rq ../dist/$*.zip $* -i '*.pyc'

test: $(LIB_TGT) 
	PYTHONPATH=py:$(PP) $(ENV)/bin/python -m $(MAIN)

deploy: all 
	@rm -rf $(DEPLOY_WEB)
	cp -r web $(DEPLOY_WEB)
	@rm -rf $(DEPLOY_CODE)
	cp -r dist $(DEPLOY_CODE)
	cd $(DEPLOY_CODE); cd ..; find $(notdir $(DEPLOY_CODE)) -name '*.zip' > $(notdir $(DEPLOY_CODE)).pth

deploy-clean:
	rm -rf $(DEPLOY_CODE) $(DEPLOY_CODE).pth
	rm -rf $(DEPLOY_WEB)

run: deploy
	cd $(ENV); bin/python -m $(MAIN)

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

