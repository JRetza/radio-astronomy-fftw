#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program will output the Jupiter-IO radio storm predictions in text format. 
# It's a port to python of an older QBasic program whose original source can be found 
# at http://www.spaceacademy.net.au/spacelab/projects/jovrad/jovrad.htm together with 
# good explanations about the theory and instructions to build a folded dipole antenna.

# please see my project text about the source of the first python porting
# and about the additions I made for geographical specific predictions using SkyField by Brandon Rhodes

from skyfield.api import load, JulianDate, utc
from datetime import datetime, timedelta
from pytz import timezone
from skyfield.api import now
from math import sin, cos, fmod, degrees, radians, floor, trunc, sqrt
import ephem
import radioConfig

#modeset = 1
modeset = 2     # I've found this set to be close to Radio Jupiter Pro results, will check again in the future
#modeset = 3

predictdays = 5 # how many days of predictions
includeonlyiorelated = False
calcinterval = 15

eph = load('jup310.bsp')
planets = load('de421.bsp')
earthobs = planets['earth']

rome = timezone(radioConfig.stationTimezone)
jd = now()
jdutc = jd.utc_datetime()

# let's work from start of current day:
jdutc = jdutc.replace(hour=0,minute=0,second=0,microsecond=0)

jd = JulianDate(utc=jdutc)
dt = jd.astimezone(rome)

ephempos      = ephem.Observer()
ephempos.lon  = float(radioConfig.stationLon[0:-2])		#Note that lon should be in string format
ephempos.lat  = float(radioConfig.stationLat[0:-2])		#Note that lat should be in string format
ephempos.elev = radioConfig.stationElev
#To get U.S. Naval Astronomical Almanac values, use these settings
ephempos.pressure= 0
ephempos.horizon = '-0:34'
myposition = earthobs.topos(radioConfig.stationLat, radioConfig.stationLon)

print('\nUTC:  ' + jdutc.strftime('%Y-%m-%d %H:%M:%S') )
print('Local: ' + dt.strftime('%Y-%m-%d %H:%M:%S'))

# 1) the central meridian longitude of Jupiter that faces us
# 2) the position of the inner-most moon Io in its orbit around Jupiter
# 3) the Jovicentric declination of the Earth

L3 = 0
U1 = 0
th = 0.0

# 1) the central meridian longitude of Jupiter that faces us
# 2) the position of the inner-most moon Io in its orbit around Jupiter

def method2():
	global jd, th, L3, U1

	pi = 3.141593
	kr = pi / 180

	fjd = jd.ut1	# we will use ut1 in input to the algorithm
	d0 = fjd - 2435108

	d = d0 + th / 24.0
	v = (157.0456 + .0011159 * d) % 360.0
	m = (357.2148 + .9856003 * d) % 360.0
	n = (94.3455 + .0830853 * d + .33 * sin(kr * v)) % 360.0
	j = (351.4266 + .9025179 * d - .33 * sin(kr * v)) % 360.0
	a = 1.916 * sin(kr * m) + .02 * sin(kr * 2.0 * m)
	b = 5.552 * sin(kr * n) + .167 * sin(kr * 2.0 * n)
	k = j + a - b
	r = 1.00014 - .01672 * cos(kr * m) - .00014 * cos(kr * 2.0 * m)
	re = 5.20867 - .25192 * cos(kr * n) - .0061 * cos(kr * 2.0 * n)
	dt = sqrt(re * re + r * r - 2 * re * r * cos(kr * k))
	sp = r * sin(kr * k) / dt
	ps = sp / .017452
	dl = d - dt / 173.0
	pb = ps - b
	xi = 150.4529 * int(dl) + 870.4529 * (dl - int(dl))
	L3 = (274.319 + pb + xi + .01016 * 51.0) % 360.0
	U1 = 101.5265 + 203.405863 * dl + pb
	U2 = 67.81114 + 101.291632 * dl + pb
	z = (2.0 * (U1 - U2)) % 360.0
	U1 = U1 + .472 * sin(kr * z)
	U1 = (U1 + 180.0) % 360.0

	L3 = int(L3)
	U1 = int(U1)

def calcforjd():
	global jd, th, L3, U1, JupiterRise, JupiterSet, SunRise, SunSet, includeonlyiorelated

	method2()
	s=""

	# ranges from http://www.spaceacademy.net.au/spacelab/projects/jovrad/jovrad.htm
	#~ Source	CML (degrees)	Io Phase (degrees)	Characteristics of emission

	#~ Io Related sources
	#~ Io-A		200-290		195-265			RH polarized, mostly L bursts
	#~ Io-B		90-200		75-105			RH polarized, mostly S bursts
	#~ Io-C		290-10		225-250			LH polarized L and S bursts

	#~ Non-Io Related Sources
	#~ A		200-290
	#~ B		90-200
	#~ C		290-10

	#~ The emission is usually either right (RH) or left hand (LH) circularly
	#~ or elliptically polarized, depending on the source.

	# ORIGINAL QBASIC ranges from http://www.spaceacademy.net.au/spacelab/projects/jovrad/jovrad.htm
	#~if L3 < 255 and L3 > 200 and U1 < 250 and U1 > 220:
		#~s = "io-a"
	#~if L3 < 180 and L3 > 105 and U1 < 100 and U1 > 80:
		#~s = "io-b"
	#~if L3 < 350 and L3 > 300 and U1 < 250 and U1 > 230:
		#~s = "io-c"

	# from which other source?
	#~ if L3>200.0 and L3<290.0:
		#~ s="A"
		#~ if U1>195.0 and U1<265.0:
			#~ s="Io-A"
	#~ if L3>90.0 and L3<200.0:
		#~ s="B"
		#~ if U1>75.0 and U1<105.0:
			#~ s="Io-B"
	#~ if L3>290.0 or L3<10.0:
		#~ s="C"
		#~ if U1>225.0 and U1<250.0:
			#~ s="Io-C"

    # first set of range found in papers:
	if modeset == 1:
		if L3>230.0 and L3<280.0:
			s="A"
		if L3>200.0 and L3<270.0 and U1>205.0 and U1<260.0:
			s="Io-A"
		if L3>105.0 and L3<185.0 and U1>80.0 and U1<110.0:
			s="Io-B"
		if (L3>300.0 or L3<20.0) and U1>225.0 and U1<260.0:
			s="Io-C"
		if (L3>1.0 and L3<200.0) and U1>95.0 and U1<130.0:
			s="Io-D"

    # second set of range found in papers:
	if modeset == 2:
		if L3>200.0 and L3<290.0:
			s="A"
		if L3>200.0 and L3<290.0 and U1>195.0 and U1<265.0:
			s="Io-A"
		if L3>90.0 and L3<200.0:
			s="B"
		if L3>90.0 and L3<200.0 and U1>75.0 and U1<105.0:
			s="Io-B"
		if (L3>290.0 or L3<20.0):
			s="C"
		if (L3>290.0 or L3<20.0) and U1>225.0 and U1<250.0:
			s="Io-C"

    # third set of range found in papers:
	if modeset == 3:
		if L3>200.0 and L3<290.0:
			s="A"
		if L3>200.0 and L3<290.0 and U1>195.0 and U1<265.0:
			s="Io-A"
		if L3>90.0 and L3<200.0:
			s="B"
		if L3>90.0 and L3<200.0 and U1>75.0 and U1<105.0:
			s="Io-B"
		if (L3>290.0 or L3<20.0) and U1>225.0 and U1<250.0:
			s="Io-C"
		if L3>0.0 and L3<200.0 and U1>95.0 and U1<130.0:
			s="Io-D"

	printout=False
	if s != "":
		if includeonlyiorelated == True and s[0:2] == "Io":
			printout=True
		if includeonlyiorelated == False:
			printout=True
		if printout == True:
			print('%s\t%0.3f\t\t%0.3f\t\t%s\t%s-%s\t\t%s-%s' % (jd.utc_strftime('%Y-%m-%d %H:%M:%S'), L3, U1, s, JupiterRise.strftime('%d %H:%M:%S'), JupiterSet.strftime('%d %H:%M:%S'), SunRise.strftime('%H:%M:%S'), SunSet.strftime('%H:%M:%S') ) )

def ephem2julian(inputcdt):
    resdt = datetime.strptime(inputcdt,'%Y/%m/%d %H:%M:%S')
    resdt = resdt.replace(tzinfo=utc)
    return JulianDate(utc=resdt).utc_datetime()

print('UTC\t\t\tCML III\t\tIO phase\tSource\tJupiter Rise-Set\t\tSun Rise-Set')
finaljdutc = jdutc + timedelta(days=predictdays)
#external loop on requested days:
while jdutc < finaljdutc:
	ephempos.date = jdutc.strftime('%Y-%m-%d %H:%M:%S')
	# debug print(ephempos.date)
	JupiterRise = ephem2julian(str(ephempos.previous_rising(ephem.Jupiter())))
	JupiterSet  = ephem2julian(str(ephempos.next_setting   (ephem.Jupiter())))
	JupiterNextRise = ephem2julian(str(ephempos.next_rising(ephem.Jupiter())))
	SunRise = ephem2julian(str(ephempos.next_rising(ephem.Sun())))
	SunSet  = ephem2julian(str(ephempos.next_setting(ephem.Sun())))
	# debug print(JupiterRise,JupiterSet,SunRise,SunSet)

	#internal loop within a single day
	thisdayutc = jdutc
	endofdayutc = jdutc + timedelta(days=1)
	while thisdayutc < endofdayutc:
		#this way i will do the other calcs only when Jupiter is above the local horizon and the Sun is not visible:
		if ((thisdayutc > JupiterRise and thisdayutc < JupiterSet) or thisdayutc > JupiterNextRise ) and (thisdayutc < SunRise or thisdayutc > SunSet):
			calcforjd()
		#calculate again every N minutes:
		thisdayutc = thisdayutc + timedelta(minutes=calcinterval)
		jd = JulianDate(utc=thisdayutc)

	# since we have covered this day, let's go on with the next one:
	jdutc = jdutc + timedelta(days=1)
	jd = JulianDate(utc=jdutc)

print('\nJovicentric Declination of Earth:')
# 3):
jupiter = eph['jupiter']
earth = eph['earth']
geometry = jupiter.at( jd ).observe(earth)
#print(geometry.position.au)
print(geometry.radec())
jcera, jcedec, jcedist = geometry.radec()
