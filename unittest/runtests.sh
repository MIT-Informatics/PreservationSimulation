#!/bin/bash
# runtests.sh
# Run all Python files that plausibly look like unit tests, 
#  i.e., named like "test_foo.py".

for ff in test_*.py
do
    timestamp=$(date +%Y%m%d_%H%M%S.%3N)
    echo "====== $timestamp Running tests $ff:"
    python -m unittest $(basename $ff .py)
done

exit 0

#END
