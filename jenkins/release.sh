#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/clean.sh
. $DIR/configure.sh
. $DIR/virtualenv.sh

if [[ "${PYPI_NAME}" == "" ]]
then 
  PYPI_NAME=pypi
fi

if [[ -e "./setup.py" ]]
then
  python setup.py tag register -r ${PYPI_NAME} sdist bdist_egg bdist_wheel upload -r ${PYPI_NAME}
fi