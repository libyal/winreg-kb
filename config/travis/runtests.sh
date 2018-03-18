#!/bin/bash
#
# Script to run tests on Travis-CI.
#
# This file is generated by l2tdevtools update-dependencies.py, any dependency
# related changes should be made in dependencies.ini.

# Exit on error.
set -e;

if test "${TARGET}" = "pylint";
then
	pylint --version

	for FILE in `find setup.py winregrc tests -name \*.py`;
	do
		echo "Checking: ${FILE}";

		pylint --rcfile=.pylintrc ${FILE};
	done

elif test "${TRAVIS_OS_NAME}" = "osx";
then
	PYTHONPATH=/Library/Python/2.7/site-packages/ /usr/bin/python ./run_tests.py;

	python ./setup.py build

	python ./setup.py sdist

	python ./setup.py bdist

elif test "${TRAVIS_OS_NAME}" = "linux";
then
	if test -n "${TOXENV}";
	then
		tox --sitepackages ${TOXENV};

	elif test "${TRAVIS_PYTHON_VERSION}" = "2.7";
	then
		coverage erase
		coverage run --source=winregrc --omit="*_test*,*__init__*,*test_lib*" ./run_tests.py
	else
		python ./run_tests.py
	fi

	python ./setup.py build

	python ./setup.py sdist

	python ./setup.py bdist

	TMPDIR="${PWD}/tmp";
	TMPSITEPACKAGES="${TMPDIR}/lib/python${TRAVIS_PYTHON_VERSION}/site-packages";

	mkdir -p ${TMPSITEPACKAGES};

	PYTHONPATH=${TMPSITEPACKAGES} python ./setup.py install --prefix=${TMPDIR};
fi
