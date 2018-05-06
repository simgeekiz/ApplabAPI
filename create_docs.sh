#!/bin/bash
source group2api/setenvvar.sh
cd docs
make clean && make html
cd ..
cp -r docs/_build/html/* group2api/templates/
rm -r group2api/static/
mv group2api/templates/_static group2api/static

# _static
# /static
# AppLabServer/group2api/templates
