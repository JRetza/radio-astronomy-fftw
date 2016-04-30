#! /usr/bin/env python

import radioConfig
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
import numpy as np
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import copy
from glob import glob
import pytz
import time
import calendar
from datetime import datetime, timedelta

#cmapname = 'nipy_spectral'
cmapname = 'jet'
maxcols = 32768

def strinsert(source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

globmax = -9000
globmin = 9000
gotfirsttime = False

sessmin = np.empty(shape=[0, 1])
sessmax = np.empty(shape=[0, 1])
scantimeline = np.empty(shape=[0, 1])

files_in_dir = sorted(glob("*.bin"))
for fname in files_in_dir:
    dbs = np.fromfile(fname, dtype='float32')
    thismin=dbs.min()
    thismax=dbs.max()
    scantime=str(fname)[11:17]
    scandate=str(fname)[3:11]
    print(scandate,scantime,thismin,thismax)
    if thismin < globmin:
        globmin = thismin
    if thismax > globmax:
        globmax = thismax
    sessmin = np.append(sessmin, thismin)
    sessmax = np.append(sessmax, thismax)
    scantime = strinsert(scantime, ":", 2)
    scantime = strinsert(scantime, ":", 5)
    scantimeline = np.append(scantimeline, scantime)

    scanname = fname[:-4]
    metaname = scanname + '.met'
    with open(metaname, 'r') as f:
        linein = f.readline()
        inflds = linein.split()
        metaCols = int( inflds[0] )
        linein = f.readline()
        inflds = linein.split()
        metaRows = int( inflds[0] )
        linein = f.readline()
        inflds = linein.split()
        startFreq = int(inflds[0])
        linein = f.readline()
        inflds = linein.split()
        endFreq = int(inflds[0])
        linein = f.readline()
        inflds = linein.split()
        stepFreq = int(inflds[0])
        linein = f.readline()
        inflds = linein.split()
        effIntTime = float(inflds[0])
        linein = f.readline()
        inflds = linein.split()
        avgScanDur = float(inflds[0])
        linein = f.readline()
        inflds = linein.split()
        firstAcqTimestamp = inflds[0] + ' ' + inflds[1]
        if gotfirsttime == False:
            gotfirsttime = True
            absfirstAcqTimestamp = firstAcqTimestamp
        linein = f.readline()
        inflds = linein.split()
        lastAcqTimestamp = inflds[0] + ' ' + inflds[1]
        linein = f.readline()
        inflds = linein.split()
        samplingRate = inflds[0]
        linein = f.readline()
        inflds = linein.split()
        hops = inflds[0]
        linein = f.readline()
        inflds = linein.split()
        cropPercentage = inflds[0]
        linein = f.readline()
        inflds = linein.split()
        cropExcludedBins = inflds[0]
        linein = f.readline()
        inflds = linein.split()
        cropFreqOffset = inflds[0]

startFreq = startFreq - radioConfig.upconvFreqHz
endFreq = endFreq - radioConfig.upconvFreqHz

overalldbs = np.empty(shape=[metaCols, 0])        
#print "overalldbs.shape: " + str(overalldbs.shape)

mytitle = 'This session signal range: min %.2f .. max %.2f' % (globmin,globmax)
print(mytitle)

files_in_dir = sorted(glob("*.bin"))
howmany = len(files_in_dir)
cntfil = 0
for fname in files_in_dir:
    cntfil = cntfil + 1
    scanname = fname[:-4]
    metaname = scanname + '.met'
    outname =  scanname + '.png'
    thumbname =  scanname + '.gif'
    with open(metaname, 'r') as f:
        linein = f.readline()
        inflds = linein.split()
        metaCols = int( inflds[0] )
        linein = f.readline()
        inflds = linein.split()
        metaRows = int( inflds[0] )

    dbms = np.fromfile( fname, dtype=np.float32 )
    dbms = dbms.reshape(metaRows, metaCols)
    # rotate to match the way matplotlib works
    dbms = np.rot90(dbms,1)
	# reduce the number of samples deleting 1 every 3)
    dbms = np.delete(dbms, list(range(0, dbms.shape[1], 3)), axis=1)
    #print "  dbms.shape: " + str(dbms.shape)
    overalldbs = np.append( overalldbs,dbms,1 )
    #print "  overalldbs.shape: " + str(overalldbs.shape)
    print ("file " + str(cntfil) + " of " + str(howmany) )

print ("\noveralldbs.shape: " + str(overalldbs.shape))
metaRows, metaCols = overalldbs.shape
while metaCols > maxcols:
    print ("...reducing...")
    overalldbs = np.delete(overalldbs, list(range(0, overalldbs.shape[1], 6)), axis=1)
    metaRows, metaCols = overalldbs.shape

print ("overalldbs.shape: " + str(overalldbs.shape))

theExtent = [1,metaRows,1,metaCols]

#print metaRows, metaCols
print("...plotting...")

#ow = metaCols
#oh = metaRows
ow = 6000
oh = ow / 4 * 3

outname = "wholesession"

fig = plt.figure(frameon=False)
fig.set_size_inches( ow, oh )
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(overalldbs, interpolation='nearest', origin='lower', extent=theExtent, aspect='auto', cmap=plt.get_cmap(cmapname) )
fig.savefig(outname + ".png", dpi=1)
print("Whole session plot completed.")

del fig
del overalldbs
del dbms

xmargin = 160
ymargin = 100

# load image and get size info
old_im = Image.open(outname + '.png')
old_size = old_im.size
ow, oh = old_im.size

print("...performing annotation...")
# add enough margin for axis labels
new_size = ( ow + xmargin + xmargin, oh + ymargin + ymargin + 50)
new_im = Image.new("RGB", new_size, color=(255,255,255) )
new_im.paste(old_im, ( xmargin, ymargin ) )

# prepare to draw on canvas
draw = ImageDraw.Draw(new_im)

fonth = 42
midfont = int( fonth / 2 )
font = ImageFont.truetype("Vera.ttf", fonth)

# add title
draw.text((xmargin, ymargin/3), "WHOLE SESSION", (0,0,0),font=font)

fonth = 30
midfont = int( fonth / 2 )
font = ImageFont.truetype("Vera.ttf", fonth)

iniFreq = startFreq / 1000000.0
finFreq = endFreq / 1000000.0
stFreqLab = ( finFreq - iniFreq ) / 10.0

def frange(start, stop, step):
    i = 0
    while (i*step + start <= stop):
        yield i*step + start
        i += 1

# Y axis label:
xlab = xmargin / 3
ylab = ymargin / 2
draw.text((xlab, ylab), "MHz", (0,0,0),font=font)

# add frequencies on Y axis:
xlab = xmargin / 3
ylab = ymargin + oh
ystep = oh / 10
for flab in frange( iniFreq, finFreq, stFreqLab ):
    strflab = '%.2f' % flab
    draw.text((xlab, ylab-midfont), strflab, (0,0,0),font=font)
    draw.line((xmargin-20,ylab, xmargin,ylab), fill=0, width=1)
    ylab = ylab - ystep

def to_datetime_from_utc(time_tuple):
    return datetime.fromtimestamp(calendar.timegm(time_tuple), tz=pytz.utc)

# X axis label:
xlab = (ow / 2) - 30    # middle of image
ylab = ymargin + oh + ymargin   # bottom of image
draw.text((xlab, ylab), "UTC time", (0,0,0),font=font)

# add timeline on X axis
iniTime = to_datetime_from_utc(time.strptime(absfirstAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
endTime = to_datetime_from_utc(time.strptime(lastAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
stepTime = (endTime - iniTime).total_seconds() / 20.0   # we want 11 ticks...

xlab = xmargin
xstep = (ow) / 20
ylab = ymargin + oh
tlab = iniTime
for j in range(0, 21):
    strtlab = tlab.strftime('%H:%M:%S')
    strtdat =  tlab.strftime('%b %d')
    draw.line((xlab,ylab, xlab,ylab+20), fill=0, width=1)
    draw.text((xlab-60, ylab+25), strtlab, (0,0,0),font=font)
    draw.text((xlab-60, ylab+55), strtdat, (0,0,0),font=font)
    xlab = xlab + xstep
    tlab = tlab + timedelta(seconds=stepTime)

print("...performing palette conversion...")
# this is necessary to keep image file size at a minimum
# ( it's also the file mode used by gnuplot )
new_im = new_im.convert('P', palette=Image.ADAPTIVE, colors=256)

print("...adding metadata to image...")
# create and attach info dictionary with metadata
meta = PngImagePlugin.PngInfo()
meta.add_text("ra-stationID", radioConfig.stationID)
meta.add_text("ra-scanTarget", radioConfig.scanTarget)
meta.add_text("ra-FFTbins", str(metaCols))
meta.add_text("ra-FreqStart", str(startFreq))
meta.add_text("ra-FreqEnd", str(endFreq))
meta.add_text("ra-FreqStep", str(stepFreq))
meta.add_text("ra-avgScanDur", str(avgScanDur))
meta.add_text("ra-scanTimestampFirst", absfirstAcqTimestamp)
meta.add_text("ra-scanTimestampLast", lastAcqTimestamp)
meta.add_text("ra-samplingRate", samplingRate)
meta.add_text("ra-upconverterFreq", str(radioConfig.upconvFreqHz))
meta.add_text("ra-hops", hops)
meta.add_text("ra-cropPercentage", cropPercentage)
meta.add_text("ra-cropExcludedBins", cropExcludedBins)
meta.add_text("ra-cropFreqOffset", cropFreqOffset)

# TO DO:  add min and max power level for this image in the meta
# on linux, if you have imagemagick, use this command to view PNG metadata:
#   identify -verbose foo.png

new_im.save(outname + '-annotated.png', "png", pnginfo=meta, optimize=True)

os.remove(outname + '.png')
os.rename(outname + '-annotated.png', outname + '.png')
print("...annotated plot saved.")
