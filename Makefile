VERSION = $(shell python setup.py --version)
BUILD_DIR = docs/_build/html
PROTOBUF_PYTHON_PATH=gutter/client/interfaces

test:
	python setup.py flake8
	python setup.py nosetests

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	git push origin master
	python setup.py sdist upload

watch:
	bundle exec guard

interfaces:
	protoc --python_out=${PROTOBUF_PYTHON_PATH} interfaces.proto

docs:
	cd docs && make html

docs.tar: docs
	- rm $(BUILD_DIR)/docs.tar
	cd docs/_build/html && tar -cf docs.tar *

disqus.github.io/gutter: docs.tar
	git co gh-pages
	tar -xf $(BUILD_DIR)/docs.tar
	# Ignore jekyll since we're rolling our own
	touch .nojekyll
	git add -A
	# Ignore errors if there isn't anything to commit
	- git commit -am "Docs for $(VERSION)"
	git push origin gh-pages
	git co master

.PHONY: test release watch docs gh-pages
