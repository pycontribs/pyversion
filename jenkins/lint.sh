#!/bin/bash
mkdir -p ./test_output
python setup.py flake8 > ./test_output/flake8.txt