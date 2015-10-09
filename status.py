#!/usr/bin/env python

import caffe
import glob
import numpy as np
from os import listdir
from os.path import isfile, isdir, join
import sys
import SimpleHTTPServer
import SocketServer

IMAGE_DIR = 'test'
MODEL_FILE = 'lenet_deploy.prototxt'
PRETRAINED = 'soln_iter_*.caffemodel'

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

output = []
def output_start():
  output.append('<!doctype html><html><head>')
  output.append("""
  <style>
  table, body {
    color: #333;
    font-family: Helvetica, Arial, sans-serif;
  }
  table { 
    border-collapse: collapse;
    border-spacing: 0; 
  }
  
  td, th { border: 1px solid #CCC; padding: 2px; }
  td {
    text-align: left;
  }
  </style>
  """)
  output.append('</head><body>')

def output_table(filename, eval, cases):
  [hits, counts, correct, total] = eval
  [all_files, bits, truth, cats] = cases
  output.append('<h3>%s</h3>' % filename)
  output.append('<table>')
  output.append('<tr>')
  output.append('<td></td>')
  for d in cats:
    output.append('<td>predicted %d</td>' % d)
  output.append('</tr>')
  for c in cats:
    output.append('<tr>')
    output.append('<td>actually %d</td>' % c)
    for d in cats:
      if c == d:
        border = 'lightgreen'
      else:
        border = 'transparent'
      output.append('<td style="background:%s">' % border)
      if (c, d) in hits:
        for f in hits[(c, d)]:
          output.append('<img src="%s">' % f)
        output.append(str(counts[(c, d)]))
      output.append('</td>')
    output.append('</tr>')
  output.append('</table>')
  output.append('<p>Total: %d correct out of %d, accuracy %.2f</p>' %
    (correct, total, correct / float(total)))
  output.append('<hr>')

def output_finish():
  output.append('</body></html>')

images = load_images_in_dir(IMAGE_DIR)
output_start()
pretraineds = sorted(glob.glob(PRETRAINED), key=alphanum_key)
for p in pretraineds:
  eval = calc_eval_for_model(MODEL_FILE, p, images)
  output_table(p, eval, images)
output_finish()

PORT = 8880

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/':
      self.wfile.write('\n'.join(output))
      return
    return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

SocketServer.TCPServer.allow_reuse_address = True
server = SocketServer.TCPServer(("",PORT), MyRequestHandler)
print "serving at http://localhost:%d" % PORT
try:
  server.serve_forever()
except KeyboardInterrupt:
  pass
server.server_close()
