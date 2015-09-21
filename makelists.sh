#!/bin/sh

# make a LISTFILE for the convert-images tool
for dir in training test; do
  find $dir -name *.jpg -or -name *.png \
    | sed 's/^\.\///' \
    | sed 's/^.*\/\([0-9]\)\/.*$/\0 \1/' \
    > $dir.list
done
