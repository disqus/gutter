VERSION = $(shell python setup.py --version)

TEST_RESULTS_DIR=test_results
XUNIT_DIR=${TEST_RESULTS_DIR}/xunit
XUNIT_FILE=nosetests.xml
XUNIT_FILENAME=${XUNIT_DIR}/${XUNIT_FILE}

test:
	python setup.py nosetests

test-xunit: ${XUNIT_DIR}
	python setup.py nosetests --verbosity=2 --with-xunit --xunit-file=${XUNIT_FILENAME}

${XUNIT_DIR}:
	mkdir -p ${XUNIT_DIR}

lint:
	python setup.py flake8

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	git push origin master
	python setup.py sdist upload

.PHONY: test test-xunit lint release
