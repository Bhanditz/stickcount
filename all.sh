#!/bin/sh

set -x

# Synthetic image classification problem.
# A first try at making a net do something it wasn't designed to do, to
# try to help build intuition.
# To use it, run each of these steps.

  rm -rf test training
  ./maketraining.py   # make the training and test data
  ./makelists.sh      # build textfiles listing image files and classifications
  ./makedb.sh         # load the data into a lmdb database
  ./solvenet.sh       # run the training procedure.

