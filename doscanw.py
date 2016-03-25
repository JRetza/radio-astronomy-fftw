#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# to start a scan session you MUST enter:    bash runw.sh
# runw.sh is the shell script that will start this python program in the proper way

# BEFORE RUNNING THIS PROGRAM please set your configuration values in file  radioConfig.py

# this program executes the radio scans using rtl_power_fftw by Klemen Blokar and Andrej Lajovic
# in parallel with rtl_power_fftw, it will run  postprocw.py  that will produce the spectrograms,
# upload to AWS S3 if enabled, send mqtt notifications if enabled

# at the end of session it will run also  findsessionrangew.py  that will determine the overall
# range of signal strengths received during the whole session. Its output will be stored in 2 files:
# dbminmax.txt and session-overview.png . The first contains two rows of text with just the maximum
# and minimum of the whole session. The second contains a chart of all the min and max values for each of
# the scan files

from datetime import datetime
import subprocess
import os
import radioConfig

#build scan filename

cmdstring = "rtl_power_fftw"

freqstart = radioConfig.freqCenter - (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
freqstop  = radioConfig.freqCenter + (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
sfreqstart = '%0.3fM' % (freqstart/1000000.0)
sfreqstop = '%0.3fM' % (freqstop/1000000.0)

freqbins = (freqstop - freqstart) / radioConfig.binSizeHz

datagathduration = str(radioConfig.dataGatheringDurationMin) + "m"
truefreqstart = '%0.3fM' % ((radioConfig.freqCenter - (radioConfig.freqBandwidth/2))/1000000.0)
truefreqstop  = '%0.3fM' % ((radioConfig.freqCenter + (radioConfig.freqBandwidth/2))/1000000.0)

cmdstring = cmdstring + " -f " + str(freqstart)
cmdstring = cmdstring + ":" + str(freqstop)

cmdstring = cmdstring + " -b " + str(freqbins)
cmdstring = cmdstring + " -n " + str(radioConfig.integrationScans)
cmdstring = cmdstring + " -g " + str(radioConfig.gain * 10)

cmdstring = cmdstring + " -p " + str(radioConfig.tunerOffsetPPM)
#cmdstring = cmdstring + " -c " + str(radioConfig.fftCropPercentage)
cmdstring = cmdstring + " -e " + datagathduration
cmdstring = cmdstring + " -q"

numscans = radioConfig.sessionDurationMin / radioConfig.dataGatheringDurationMin

scancnt = 1
while scancnt <= numscans:
    scantimestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    scanname = "UTC" + scantimestamp + "-" + radioConfig.scanTarget + "-" + truefreqstart + "-" + truefreqstop + "-n" + str(radioConfig.integrationScans) + "-g" + str(radioConfig.gain) + "-e" + datagathduration

    completecmdstring = cmdstring + " -m " + scanname

    print(completecmdstring)

    print('\nrunning scan %d of %d\n' % (scancnt,numscans))
    #print(completecmdstring)
    #run the scan and wait for completion
    scanp = subprocess.Popen(completecmdstring, shell = True)
    os.waitpid(scanp.pid, 0)

#get event probability info
#process the scan adding probability info

    if radioConfig.plotWaterfall:
        chartcmdstring = "python postprocw.py " + scanname
        #run gnuplot WITHOUT waiting for completion
        genchrtp = subprocess.Popen(chartcmdstring, shell = True)
        print('processing complete for scan %d of %d\n' % (scancnt,numscans))

    # go on with next scan:
    scancnt = scancnt + 1

chartcmdstring = "python findsessionrangew.py"
genchrtp = subprocess.Popen(chartcmdstring, shell = True)
