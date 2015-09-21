#!/usr/bin/env python

from PIL import Image, ImageDraw
import random
import os, os.path

dim = 28
training = 10000
test = 100


def randloc():
  return random.randrange(0, dim)

def filename(prefix, stickcount, samplenum):
  return "%s/%d/%s_%d_%d.jpg" % (
      prefix, stickcount, prefix, stickcount, samplenum)

def genimages(prefix, stickcount, samples):
  im = Image.new('L', (dim, dim), 'white')
  draw = ImageDraw.Draw(im) 
  for x in xrange(samples):
    im.paste(random.randrange(50, 256), (0, 0, dim, dim))
    # im.paste('white', (0, 0, dim, dim))
    for y in xrange(stickcount):
      w = random.randrange(1, 7)
      p = (randloc(), randloc(), randloc(), randloc())
      c = random.randrange(0, 200)
      # c = 'black'
      draw.line(p, fill=c, width=w)
    f = filename(prefix, stickcount, x)
    if not os.path.exists(os.path.dirname(f)):
      os.makedirs(os.path.dirname(f))
    im.save(filename(prefix, stickcount, x), "JPEG", quality=80, optimize=True)
    # im.save(filename(prefix, stickcount, x), "PNG")

for s in xrange(0, 5):
  genimages('training', s, training)
  genimages('test', s, test)
