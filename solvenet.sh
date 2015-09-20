#!/bin/sh

CAFFE_BUILD=../caffe/build

$CAFFE_BUILD/tools/caffe train -solver lenet_solver.prototxt

