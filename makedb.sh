#!/bin/sh

CAFFE_BUILD=../caffe/build

for dir in training test; do
  rm -rf ./$dir.lmdb
  $CAFFE_BUILD/tools/convert_imageset -gray -shuffle ./ $dir.list $dir.lmdb
done
