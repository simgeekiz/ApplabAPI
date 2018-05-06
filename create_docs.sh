#!/bin/bash
cd docs
make clean && make html
cd ..
cp -r docs/_build/html/* src/templates/
rm -r src/static/
mv src/templates/_static src/static

# _static
# /static
# AppLabServer/group2api/templates
