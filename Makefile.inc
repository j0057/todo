
# PKG = pkgname
# LIB = dist/lib1.zip dist/lib2.zip
# PKG = env/pip-pkg1

.PHONY: clean really-clean test runtime vars

PP = $(LIB: =:)

all: dist/$(NAME).zip $(LIB)

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

runtime: env $(PKG)

dist:
	@mkdir -vp dist
	@mkdir -vp dist/lib

dist/%.zip: dist py/%/*.py
	cd py ; zip -r ../dist/$*.zip $*/*.py

dist/lib/%.zip: dist
	@make -C lib/$* dist/$*.zip
	@cp -v lib/$*/dist/$*.zip dist/lib/$*.zip

test: $(LIB) runtime
	@echo "PYTHONPATH=$(PP) python py/$(NAME)/__init__.py"
	@bash -c ". env/bin/activate ; PYTHONPATH=$(PP) python py/$(NAME)/__init__.py"

vars:
	@echo "NAME: $(NAME)"
	@echo "LIB : $(LIB)"
	@echo "PKG : $(PKG)"
	@echo "PP  : $(PP)"
