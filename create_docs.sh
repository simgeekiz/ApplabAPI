#!/bin/bash

# Load the environment variables
source group2api/setenvvar.sh

# Rebuild documentation as html
cd docs
make clean && make html

# Get a copy of html documentation under the app folder
cd ..
cp -r docs/_build/html/* group2api/templates/

# Remove the static folder of the previous doc build
rm -r group2api/static/

# Then rename the new static folder for docs as 'static'
mv group2api/templates/_static group2api/static

# Replace '_static' with '/static' under /group2api/templates
find ./group2api/templates -name .git -prune -o -type f -exec sed -i 's/_static/\/static/g' {} +


