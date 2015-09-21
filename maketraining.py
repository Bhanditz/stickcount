#!/usr/bin/env python

from PIL import Image, ImageDraw
import random
import os, os.path

dim = 28
training = 10000
test = 100


def randloc():
  return random.randrange(0, dim)

def filename(prefix, classnum, stickcount, samplenum):
  return "%s/%d/%s_%d_%d.jpg" % (
      prefix, classnum, prefix, stickcount, samplenum)

def genimages(prefix, classnum, stickcount, samples):
  im = Image.new('L', (dim, dim), 'white')
  draw = ImageDraw.Draw(im) 
  for x in xrange(samples):
    # im.paste(random.randrange(50, 256), (0, 0, dim, dim))
    im.paste('white', (0, 0, dim, dim))
    ycoords1 = sorted([randloc() for _ in xrange(stickcount * 2)])
    xcoords = sorted([randloc() for _ in xrange(stickcount * 2)])
    xcoords1 = xcoords[:stickcount]
    xcoords2 = xcoords[stickcount:]
    random.shuffle(xcoords1)
    random.shuffle(xcoords2)
    for y in xrange(stickcount):
      w = random.randrange(2, 4)
      xc = [xcoords1[y], xcoords2[y]]
      random.shuffle(xc)
      p = (xc[0], ycoords1[y * 2], xc[1], ycoords1[y * 2 + 1])
      c = random.randrange(0, 200)
      # c = 'black'
      draw.line(p, fill=c, width=w)
    f = filename(prefix, classnum, stickcount, x)
    if not os.path.exists(os.path.dirname(f)):
      os.makedirs(os.path.dirname(f))
    im.save(
        filename(prefix, classnum, stickcount, x),
        "JPEG", quality=80, optimize=True)
    # im.save(filename(prefix, stickcount, x), "PNG")

for s in xrange(1, 5):
  genimages('training', s - 1, s, training)
  genimages('test', s - 1, s, test)
