test:
	python setup.py nosetests

watch:
	bundle exec guard

.PHONY: test watch