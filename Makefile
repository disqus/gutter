VERSION = $(shell python setup.py --version)
PROTOBUF_PYTHON_PATH=gutter/client/interfaces

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

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	git push origin master
	python setup.py sdist upload

watch:
	bundle exec guard

interfaces:
	protoc --python_out=${PROTOBUF_PYTHON_PATH} interfaces.proto

.PHONY: test test-xunit release watch interfaces
