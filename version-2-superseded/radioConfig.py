# scan parameters configured here
# are used by all the scripts

freqCenter = 21000000   # if you want to scan from 17 to 25 MHz you enter here 21000000 as center frequency and 8000000 below as bandwidth
freqBandwidth = 8000000
upconvFreqHz = 125000000    # this is your upconverter offset frequency in Hz

# maximum value successfully tested on the R-PI-3 : 2800000
rtlSampleRateHz = 2000000

# specify one of the two values and set the other to 0
totalFFTbins = 4000	# this is the total number of bins available on a scan (will be divided by number of necessary hops)
binSizeHz = 0 # this is the FFT bin size in Hz, lower values will give you more detail in spectrograms, but larger files to process on the R-PI (gnuplot is memory hungry)

# specify one of the two values and set the other to 0
integrationIntervalSec = 0.5	# see rtl_power_fftw documentation, this is the integration time in seconds. can be < 1 sec 
integrationScans = 0	# see rtl_power_fftw documentation, this is the number of scans that will be averaged for integration purposes. Allows to integrate for less than 1 second.

gain = 30   # maximum gain is about 49, can be too much in certain positions with strong interfering sources
linearPower = False	# flag to calculate linear power values instead of logarithmic
tunerOffsetPPM = 0 # see rtl_power documentation, i can use 0 on my TCXO based dongle, cab be anything from 0 to 60 or more depending on the dongle (use kalibrate to find it out)
fftCropPercentage = 0.2 # see rtl_power documentation, this is my suggested value
dataGatheringDurationMin = 30   # duration of single scan in minutes. 30 minutes is the suggested duration for better chart and limit on memory available on R-PI-2 for gnuplot
sessionDurationMin = 600    # overall session duration in minutes 10 hours = 10 * 60 = 600
scanTarget = "Jupiter"  # this string will be used to create a subfolder under which all sessions spectrograms will be stored (one subfolder per each date)
# the following observer position is used by Jupiter-Io radio emission
# prediction utility to calculate Jupiter apparent position / visibility
# for your site:
stationID = "myName Observatory-myCountry"
stationTimezone = "Europe/Rome"
stationLat = "00.00000 X"  # enter your station latitude here with this string format "00.00000 X"  where X is either N or S (North or Sud)
stationLon = "00.00000 X"  # enter your station longitude here with this string format "00.00000 X"  where X is either E or W (East or West)
stationElev = 0   # enter your station elevation in meters (above sea level)
# here you can specify:
plotWaterfall = True
uploadToS3 = False	# if you want to upload your scans
sendIoTmsg = False  # if you want to send notifications. Please, get in touch with me to get the certificates in order to send mqtt notifications
# do not change the following lines:
awshost = "A101P9EGJE1N9Z.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "mcawsthings-test2"
thingName = "mcawsthings-test2"
caPath = "./aws-iot-rootCA.crt"
certPath = "./cert.pem"
keyPath = "./privkey.pem"
