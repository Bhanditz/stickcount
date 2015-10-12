#!/usr/bin/env python

import caffe
import glob
import numpy as np
from os import listdir
from os.path import isfile, isdir, join
import sys
import SimpleHTTPServer
import SocketServer

IMAGE_DIR = 'training'
MODEL_FILE = 'lenet_deploy.prototxt'
PRETRAINED = 'soln_iter_*.caffemodel'
LOSS_FILE = 'losses.lst'

def read_mean_proto(filename):
  blob = caffe.proto.caffe_pb2.BlobProto()
  data = open(filename , 'rb').read()
  blob.ParseFromString(data)
  return np.array(caffe.io.blobproto_to_array(blob))

import re

def tryint(s):
  try:
    return int(s)
  except:
    return s

def alphanum_key(s):
  return [tryint(c) for c in re.split('([0-9]+)', s)]

def load_images_in_dir(imagedir):
  # Run the net on all test images from all categories
  categories = [d for d in listdir(imagedir) if isdir(join(imagedir, d))]
  all_files = []
  truth = []
  cats = []
  for c in categories:
    cat_files = [join(IMAGE_DIR, c, f) for f in listdir(join(IMAGE_DIR, c))]
    all_files.extend(cat_files)
    truth.extend([int(c)] * len(cat_files))
    cats.append(int(c))
  cats = sorted(cats)
  bits = [caffe.io.load_image(f, color=False) for f in all_files]
  return [all_files, bits, truth, cats]

def calc_eval_for_model(model, pretrained, cases):
  [all_files, bits, truth, cats] = cases
  net = caffe.Classifier(model, pretrained, image_dims=(64, 64))
  prediction = net.predict(bits)
  samples = 4
  # Now pick the first 4 samples of each hit/mistake in the grid
  hits = {}
  counts = {}
  total = 0
  correct = 0
  for j in range(len(all_files)):
    slot = (truth[j], prediction[j].argmax())
    total += 1
    if slot[0] == slot[1]:
      correct += 1
    if slot not in hits:
      hits[slot] = []
    if len(hits[slot]) < samples:
      hits[slot].append(all_files[j])
    counts[slot] = counts.get(slot, 0) + 1
  return [hits, counts, correct, total]

stride = 10000
def calc_failures_for_model(model, pretrained, cases):
  [all_files, bits, truth, cats] = cases
  result = []
  net = caffe.Classifier(model, pretrained, image_dims=(64, 64))
  for k in range(0, len(all_files), stride):
    partbits = bits[k:k + stride]
    print "Running prediction on %d images at %d" % (stride, k)
    prediction = net.predict(partbits, oversample=False)
    for j in range(stride):
      if truth[k + j] != prediction[j].argmax():
        result.append(all_files[k + j])
        print all_files[k + j], "%d predicted as %d" % (
            truth[k + j], prediction[j].argmax())
  return result

MODEL_COUNT = 2

losses = {}
images = load_images_in_dir(IMAGE_DIR)
pretraineds = sorted(glob.glob(PRETRAINED), key=alphanum_key)[0:MODEL_COUNT]
for p in pretraineds:
  failures = calc_failures_for_model(MODEL_FILE, p, images)
  for loss in failures:
    losses[loss] = losses.get(loss, 0) + 1
with open(LOSS_FILE, 'w') as f:
  for k, v in losses.iteritems():
    print >>f, "%s,%d" % (k, v)
