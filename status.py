#!/usr/bin/env python

from os import listdir
from os.path import isfile, isdir, join
import numpy as np
import sys
import caffe
import SimpleHTTPServer
import SocketServer

MODEL_FILE = 'lenet_deploy.prototxt'
PRETRAINED = 'soln_iter_20000.caffemodel'
MEAN_FILE = 'training_mean.binaryproto'

def read_mean_proto(filename):
  blob = caffe.proto.caffe_pb2.BlobProto()
  data = open(filename , 'rb').read()
  blob.ParseFromString(data)
  return np.array(caffe.io.blobproto_to_array(blob))

def prediction_for_images(filenames):
  input_images = [caffe.io.load_image(f, color=False) for f in filenames]
  return net.predict(input_images)

def prediction_for_image(filename):
  return predcition_for_images([filename])[0]

mean = read_mean_proto(MEAN_FILE)
print "Mean shape is", mean.shape
print "Mean first plane shape is", mean[0][0].shape

net = caffe.Classifier(MODEL_FILE, PRETRAINED,
                       # When loaded, the mean file is 1x1x28x28, but we want
                       # just 28x28.  This accomplishes that.
                       mean = mean[0][0],
                       raw_scale=256,
                       image_dims=(28, 28))

IMAGE_DIR = 'test'

# Run the net on all test images from all categories
categories = [d for d in listdir(IMAGE_DIR) if isdir(join(IMAGE_DIR, d))]
all_files = []
truth = []
cats = []
for c in categories:
  cat_files = [join(IMAGE_DIR, c, f) for f in listdir(join(IMAGE_DIR, c))]
  all_files.extend(cat_files)
  truth.extend([int(c)] * len(cat_files))
  cats.append(int(c))
cats = sorted(cats)

prediction = prediction_for_images(all_files)
# This prints all predictions
# for j in range(len(all_files)):
#   print all_files[j], prediction[j]

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

output = ['<!doctype html><html><head>']
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
output.append('</body></html>')

PORT = 8880

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/':
      self.wfile.write('\n'.join(output))
      return
    return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

server = SocketServer.TCPServer(("",PORT), MyRequestHandler)
print "serving at http://localhost:%d" % PORT
try:
  server.serve_forever()
except KeyboardInterrupt:
  pass
server.server_close()
