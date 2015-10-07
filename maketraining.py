#!/usr/bin/env python

from PIL import Image, ImageDraw
import random
import os, os.path

dim = 28
training = 20000
test = 100


def randloc():
  return random.randrange(0, dim)

def filename(prefix, stickcount, samplenum):
  return "%s/%d/%s_%d_%d.jpg" % (
      prefix, stickcount, prefix, stickcount, samplenum)

def makelines(count):
  x = sorted([randloc() for _ in xrange(count * 2)])
  x = random.sample(x[:count], count) + random.sample(x[count:], count)
  x = [[x[j], x[j + count]] for j in xrange(count)]
  y = sorted([randloc() for _ in xrange(count * 2)])
  y = [random.sample(y[j * 2:j * 2 + 2], 2) for j in xrange(count)]
  return [(x[j][0], y[j][0], x[j][1], y[j][1]) for j in xrange(count)]

def genimages(prefix, stickcount, samples):
  im = Image.new('L', (dim, dim), 'white')
  draw = ImageDraw.Draw(im) 
  for x in xrange(samples):
    im.paste(random.randrange(230, 256), (0, 0, dim, dim))
    # im.paste('white', (0, 0, dim, dim))
    lines = makelines(stickcount)
    for line in lines:
      w = random.randrange(1, 7)
      c = random.randrange(0, 200)
      # c = 'black'
      draw.line(line, fill=c, width=w)
    f = filename(prefix, stickcount, x)
    if not os.path.exists(os.path.dirname(f)):
      os.makedirs(os.path.dirname(f))
    im.save(filename(prefix, stickcount, x), "JPEG", quality=80, optimize=True)
    # im.save(filename(prefix, stickcount, x), "PNG")

for s in xrange(0, 5):
  genimages('training', s, training)
  genimages('test', s, test)
