# -*- coding: utf-8 -*-
#
# confenv/Makefile - common package maintenance commands
# (c) 2020 Vitaly Protsko <me@protsko.expert>
# Licensed under GPLv3

#
PACKAGE	= django-confenv

# 
all: clean
	python setup.py check
	python setup.py build

test:
	python setup.py test

deb:
	python setup.py --command-packages=stdeb.command bdist_deb

install:
	python setup.py install

clean:
	python setup.py clean
	rm -rf build dist django_confenv.egg-info tests/__pycache__ confenv/__pycache__
	rm -rf deb_dist $(PACKAGE)*.tar.*

build:
	python setup.py sdist bdist_wheel

upload:
	twine check dist/*
	twine upload dist/*


.PHONY: all test deb install clean build upload

# EOF confenv/Makefile
