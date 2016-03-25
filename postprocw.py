#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program is launched with proper parameters by  doscanw.py
# will produce the spectrograms, upload to AWS S3 if enabled, send mqtt notifications if enabled

# BEFORE RUNNING A SESSION SCAN (with bash runw.sh) please set your configuration values in file  radioConfig.py

import paho.mqtt.client as paho
import socket
import ssl
from boto.s3.key import Key
import boto.s3.connection
import csv
import sys
import numpy as np
import os
import subprocess
import time
import radioConfig
from time import sleep
import Image, ImageFont, ImageDraw, PngImagePlugin
import copy
import pytz
import calendar
from datetime import datetime, timedelta

def push_picture_to_s3(id):
    global fileDate
    BUCKET_NAME = 'jupiter-spectrograms'
    AWS_ACCESS_KEY_ID = 'AKIAJLPT7UALEG4PITKA'
    AWS_SECRET_ACCESS_KEY = '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'

    # connect to the bucket
    conn = boto.s3.connect_to_region('eu-central-1',
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True,               # uncommmnt if you are not using ssl
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )

    #print(conn)

    keyname = '%s/%s/%s.png' % (radioConfig.scanTarget,fileDate,id)
    #print(keyname)

    fn = '%s.png' % id
    #print(fn)

    bucket = conn.get_bucket(BUCKET_NAME)
    #print(bucket)

    #print "uploading file"
    key = bucket.new_key(keyname)
    key.set_contents_from_filename(fn)
    print('  file uploaded to aws s3')

    print("  setting acl to public read")
    key.set_acl('public-read')

    # we need to make it public so it can be accessed publicly
    # using a URL like http://s3.amazonaws.com/bucket_name/key
    print("  making key public")
    key.make_public()

connflag = False

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("mqtt connection returned result: " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

#def on_log(client, userdata, level, buf):
#    print msg.topic+" "+str(msg.payload)

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

awshost = "A101P9EGJE1N9Z.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "mcawsthings-test2"
thingName = "mcawsthings-test2"
caPath = "./aws-iot-rootCA.crt"
certPath = "./cert.pem"
keyPath = "./privkey.pem"

if radioConfig.sendIoTmsg:
	mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
	mqttc.connect(awshost, awsport, keepalive=5)
	mqttc.loop_start()

off2sub = radioConfig.upconvFreqHz

metaname = './' + sys.argv[1] + '.met'

fileDate = sys.argv[1][3:11]

print("fileDate: ",fileDate)

#these will be present only when post processing at end of session:
if len(sys.argv)==4:
	globmin = float(sys.argv[2])
	globmax = float(sys.argv[3])
else:
	globmin = 0.0
	globmax = 0.0


def diffdates(d1, d2):
    #Date format: %Y-%m-%d %H:%M:%S
    return (time.mktime(time.strptime(d2,"%Y-%m-%d %H:%M:%S")) -
               time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S")))

with open(metaname, 'r') as f:
    linein = f.readline()
    inflds = linein.split()
    bincols = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    binrows = inflds[0]
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
    firstAcqTimestamp = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    lastAcqTimestamp = inflds[0]

matorg = '(' + bincols + ',' + binrows + ')'

startFreq = startFreq - radioConfig.upconvFreqHz
endFreq = endFreq - radioConfig.upconvFreqHz

cmdstring = "gnuplot -e \"scanstart='%s'\" -e \"scanend='%s'\" -e fstart=%d -e fend=%d -e fstep=%d -e singlescandur=%f -e \"matorg='%s'\" -e \"outname='%s'\" -e globmin=%f -e globmax=%f plotmin.gnu" % (firstAcqTimestamp, lastAcqTimestamp, startFreq, endFreq, stepFreq, avgScanDur, matorg, sys.argv[1], globmin, globmax)
print(cmdstring)

print("generating heatmap...")
p = subprocess.Popen(cmdstring, shell = True)
print("...gnuplot running...")
# comment out the following to avoid waiting for gnuplot:
os.waitpid(p.pid, 0)
print("...gnuplot completed...")

outname = sys.argv[1]

xmargin = 160
ymargin = 100

print("...performing annotation...")
# load image and get size info
old_im = Image.open(outname + '.png')
old_size = old_im.size
ow, oh = old_im.size

# add enough margin for axis labels
new_size = ( ow + xmargin, oh + ymargin + ymargin )
new_im = Image.new("RGB", new_size, color=(255,255,255) )
new_im.paste(old_im, ( xmargin, ymargin ) )

# prepare to draw on canvas
draw = ImageDraw.Draw(new_im)

fonth = 42
midfont = int( fonth / 2 )
font = ImageFont.truetype("Vera.ttf", fonth)

# add title
draw.text((xmargin, ymargin/3), "scan: "+outname, (0,0,0),font=font)

fonth = 30
midfont = int( fonth / 2 )
font = ImageFont.truetype("Vera.ttf", fonth)

iniFreq = startFreq / 1000000.0
finFreq = endFreq / 1000000.0
stFreqLab = ( finFreq - iniFreq ) / 10

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
    strflab = '%.1f' % flab
    draw.text((xlab, ylab-midfont), strflab, (0,0,0),font=font)
    draw.line((xmargin-20,ylab, xmargin,ylab), fill=0, width=1)
    ylab = ylab - ystep

def to_datetime_from_utc(time_tuple):
    return datetime.fromtimestamp(calendar.timegm(time_tuple), tz=pytz.utc)

# X axis label:
xlab = ow - (xmargin / 2)
ylab = ymargin + oh + 25
draw.text((xlab, ylab), "UTC time", (0,0,0),font=font)

# add timeline on X axis
iniTime = to_datetime_from_utc(time.strptime(firstAcqTimestamp, "%y%m%d%H%M%S"))
endTime = to_datetime_from_utc(time.strptime(lastAcqTimestamp, "%y%m%d%H%M%S"))
stepTime = (endTime - iniTime).total_seconds() / 11.0

xlab = xmargin
xstep = (ow * 0.875) / 10
ylab = ymargin + oh
tlab = iniTime
for j in range(0, 11):
    strtlab = tlab.strftime('%H:%M:%S')
    #strtlab = tlab.strftime('%H:%M:%S\n%d %b')
    draw.text((xlab-60, ylab+25), strtlab, (0,0,0),font=font)
    draw.line((xlab,ylab, xlab,ylab+20), fill=0, width=1)
    xlab = xlab + xstep
    tlab = tlab + timedelta(seconds=stepTime)

print("...performing palette conversion...")
# this is necessary to keep image file size at a minimum
# ( it's also the file mode used by gnuplot )
new_im = new_im.convert('P', palette=Image.ADAPTIVE, colors=256)

print("...adding metadata to image...")
# create and attach info dictionary with metadata
meta = PngImagePlugin.PngInfo()
meta.add_text("ra-FFTbins", str(bincols))
meta.add_text("ra-scans", str(binrows))
meta.add_text("ra-FreqStart", str(startFreq))
meta.add_text("ra-FreqEnd", str(endFreq))
meta.add_text("ra-FreqStep", str(stepFreq))
meta.add_text("ra-effIntTime", str(effIntTime))
meta.add_text("ra-avgScanDur", str(avgScanDur))
meta.add_text("ra-scanTimestampFirst", firstAcqTimestamp)
meta.add_text("ra-scanTimestampLast", lastAcqTimestamp)

# TO DO:  add min and max power level for this image in the meta
# on linux, if you have imagemagick, use this command to view PNG metadata:
#   identify -verbose foo.png

new_im.save(outname + '-annotated.png', "png", pnginfo=meta, optimize=True)

os.remove(outname + '.png')
os.rename(outname + '-annotated.png', outname + '.png')
print("...annotated plot saved.")

# create thumbnail in gif format
thumb = copy.deepcopy(new_im)
thumb.thumbnail( (ow/10,oh/10) , Image.ANTIALIAS)
thumb.save(outname + '.gif','GIF')

# upload spectrogram file to aws S3
if radioConfig.uploadToS3:
    push_picture_to_s3(sys.argv[1])

if radioConfig.sendIoTmsg:
    # send MQTT notification message
    mqttc.publish("radioscans/" + radioConfig.scanTarget + "/" + fileDate + "/", sys.argv[1]+".png", qos=1)
    print("mqtt notification sent")
    sleep(0.5)
    mqttc.disconnect()
