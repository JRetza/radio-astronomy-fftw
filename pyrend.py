#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program is launched with proper parameters by  postprocw.py
# will plot a spectrogram, add axes and annotations, using a specified colormap if any

# BEFORE RUNNING A SESSION SCAN (with bash runw.sh) please set your configuration values in file  radioConfig.py

from PIL import Image, ImageDraw
import numpy as np
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import copy


ow = 3000
oh = ow / 4 * 3

vmin = float(sys.argv[2])
vmax = float(sys.argv[3])
#these will be <> 0 only when post processing at end of session:
if vmin==0.0 and vmax==0.0:
	rangespec = False
else:
	rangespec = True

sessionfolder = sys.argv[4]

if len(sys.argv) == 6:
    cmapname = sys.argv[5]
else:
    cmapname = "jet"

metaname = sessionfolder + os.sep + sys.argv[1] + '.met'
binname = sessionfolder + os.sep + sys.argv[1] + '.bin'
outname = sessionfolder + os.sep + sys.argv[1] + '.png'

with open(metaname, 'r') as f:
    linein = f.readline()
    inflds = linein.split()
    metaCols = int( inflds[0] )
    linein = f.readline()
    inflds = linein.split()
    metaRows = int( inflds[0] )

dbms = np.fromfile( binname, dtype=np.float32 )
dbms = dbms.reshape(metaRows, metaCols)

# rotate to match the way matplotlib works
dbms = np.rot90(dbms,1)
dbms = np.flipud(dbms)

theExtent = [1,metaRows,1,metaCols]

#print metaRows, metaCols
print("...plotting...")

fig = plt.figure(frameon=False)
fig.set_size_inches( ow, oh )
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

if rangespec == True:
	ax.imshow(dbms, interpolation='nearest', origin='lower', extent=theExtent, aspect='auto', cmap=plt.get_cmap(cmapname), vmin=vmin, vmax=vmax )
else:
	ax.imshow(dbms, interpolation='nearest', origin='lower', extent=theExtent, aspect='auto', cmap=plt.get_cmap(cmapname) )

fig.savefig(outname, dpi=1)
