NAME = mp3
PKG = env/pip-webob env/pip-mutagen
LIB = lib/core.zip

PYTHONPATH = lib/core.zip

all: $(NAME).zip

$(NAME).zip: $(NAME)/*.py
	zip -r $(NAME).zip $^

test: env $(PKG) $(LIB)
	bash -c ". env/bin/activate ; PYTHONPATH=$(PYTHONPATH) python $(NAME)/__init__.py"

.PHONY: clean really-clean test lib

clean:
	@rm -rfv $(NAME).zip 
	@find $(NAME) -name '*.pyc' -exec rm -v '{}' ';'
	@rm -rfv lib/*.zip
	@make -C lib/core clean
	@rm -rfv build

really-clean: clean
	@rm -rf env/*
	@rm -rfv env

env:
	virtualenv env

env/pip-%: env
	bash -c ". env/bin/activate ; pip install $*"
	@touch env/pip-$*

lib/%.zip:
	make -C lib/$*
	cp lib/$*/$*.zip lib/$*.zip
