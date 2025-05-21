#!/bin/bash

# pre-commit hook to add missing widget state to Jupyter notebooks
# so they can be rendered in Github

files=$(ls . | grep '\.ipynb$')

for file in $files; do
    if [ -f "$file" ]; then
        tempfile="/tmp/temp.ipynb"
        jq '.metadata.widgets."application/vnd.jupyter.widget-state+json" += {"state": {}}' "$file" > "$tempfile"
        cp "$tempfile" "$file"
        git add "$file"
    fi
done

exit 0