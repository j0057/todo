
# PKG = pkgname
# LIB = dist/lib1.zip dist/lib2.zip
# PKG = env/pip-pkg1

# NAME = mp3
# LIB = core
# PKG = webob mutagen

LIB_TGT = $(addsuffix .zip,$(addprefix dist/lib/,$(LIB)))
LIB_SRC = $(addprefix lib/,$(LIB))

PP = $(subst ,:,$(LIB_TGT))

PKG_FULL = $(addprefix env/pip-,$(PKG))

CLEAN = $(addprefix clean-,$(LIB))


.PHONY: clean really-clean test runtime vars

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
	@echo "pip install $*"
	@bash -c ". env/bin/activate ; pip install $*"
	@touch env/pip-$*

runtime: env $(PKG_FULL)

dist:
	@mkdir -vp dist
	@mkdir -vp dist/lib

dist/%.zip: dist py/%/*.py
	cd py ; zip -r ../dist/$*.zip $*/*.py

dist/lib/%.zip: dist
	@make -C lib/$* dist/$*.zip
	@cp -v lib/$*/dist/$*.zip dist/lib/$*.zip

test: $(LIB_TGT) runtime
	@echo "PYTHONPATH=$(PP) python py/$(NAME)/__init__.py"
	@bash -c ". env/bin/activate ; PYTHONPATH=$(PP) python py/$(NAME)/__init__.py"

vars:
	@echo "NAME     : $(NAME)"
	@echo "LIB      : $(LIB)"
	@echo "LIB_SRC  : $(LIB_SRC)"
	@echo "LIB_TGT  : $(LIB_TGT)"
	@echo "PP       : $(PP)"
	@echo "PKG      : $(PKG)"
	@echo "PKG_FULL : $(PKG_FULL)"
	@echo "CLEAN    : $(CLEAN)"
