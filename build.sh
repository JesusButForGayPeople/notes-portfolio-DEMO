#!/bin/bash

# Build the site
bundle exec jekyll build

# Copy the generated search.json to the root directory for GitHub Pages
cp _site/search.json .

echo "Build complete. search.json has been copied to the root directory." 