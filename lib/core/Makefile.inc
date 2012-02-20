
LIB_TGT = $(addsuffix .zip,$(addprefix dist/lib/,$(LIB)))
LIB_SRC = $(addprefix lib/,$(LIB))

PP = $(subst ,:,$(LIB_TGT))

PKG_FULL = $(addprefix env/pip-,$(PKG))

SRC_FILES = $(shell find py/$(NAME) -name '*.py')

CLEAN = $(addprefix clean-,$(LIB))

.PHONY: default all clean really-clean test runtime vars

default: all test

all: dist/$(NAME).zip $(LIB_TGT)

clean: $(CLEAN)
	@rm -rfv dist
	@find py -name '*.pyc' -exec rm -v '{}' ';'

clean-%:
	@make -C lib/$* clean

really-clean: clean
	@rm -rf env/*
	@rm -rfv env

env:
	virtualenv env

env/pip-%:
	@echo "pip -v install $*"
	@bash -c ". env/bin/activate ; pip -v install $*"
	@touch env/pip-$*

runtime: env $(PKG_FULL)

dist:
	@mkdir -vp dist
	@mkdir -vp dist/lib

dist/lib/%.zip: dist
	@make -C lib/$* dist/$*.zip
	@cp -v lib/$*/dist/$*.zip dist/lib/$*.zip

dist/%.zip: dist $(SRC_FILES)
	cd py ; zip -r ../dist/$*.zip $* -i '*.py'

test: $(LIB_TGT) runtime
	@echo "PYTHONPATH=$(PP) python py/$(NAME)/__init__.py"
	@bash -c ". env/bin/activate ; PYTHONPATH=py:$(PP) python -m $(MAIN)"

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

