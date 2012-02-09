from time import gmtime, strftime, sleep
import ephem
import math
import sys
import os

if (len(sys.argv)!=2):
	print "Usage: %s <tle_file>"
	sys.exit(1)

try:
	f=open(sys.argv[1],'r')
except IOError:
	print "Can't open the file."
	sys.exit(1)

me=ephem.Observer()
me.lat,me.lon='40.77','-73.90'

name=''
tle1=''
tle2=''
sats=list()
for line in f:
	if (line[0]=='1'):
		tle1=line.rstrip()
	elif (line[0]=='2'):
		tle2=line.rstrip()
	else:
		name=line.rstrip()

	if (name!='') and (tle1!='') and (tle2!=''):
		sats.append(ephem.readtle(name,tle1,tle2))
		
		name=''
		tle1=''
		tle2=''

print "Read in %d TLEs from file." % len(sats)

while (1):
	showsats=list()
	me.date=strftime("%Y/%m/%d %H:%M:%S",gmtime())
	for somesat in sats:
		somesat.compute(me)

		if (somesat.alt>0): 
			showsats.append(somesat)

	maxlen=0
	for somesat in showsats:
		if (len(somesat.name)>maxlen):
			maxlen=len(somesat.name)

	showsats=sorted(showsats,key=lambda somesat: somesat.name)

	namestr='NAME'
	numspaces=maxlen-len("NAME")
	for i in range(4,numspaces):
		namestr=namestr+" "
	print "%s \t AZIMUTH(deg) \t ALTITUDE(deg) \t RANGE(m)" % namestr

	for somesat in showsats:
		numspaces=maxlen-len(somesat.name)
		namestr=somesat.name
		i=0
		for i in range(0,numspaces):
			namestr=namestr+" "

		print "%s\t% 3.2f\t\t% 3.2f\t\t% .0f" % (
			namestr,math.degrees(somesat.az),math.degrees(somesat.alt),
			somesat.range)
	
	sleep(1)
	os.system("clear")
