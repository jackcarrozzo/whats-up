#!/usr/bin/python

from time import gmtime, strftime, sleep
from optparse import OptionParser
from optparse import OptionGroup
from ConfigParser import SafeConfigParser
import ephem
import math
import sys
import os

defaultconfig="base.conf"
defaulttle   ="tle/visual.txt"

usage= "Usage: %prog [arguments]\n"
usage+="With no arguments, visible objects are printed using the default TLE and config files."
parser=OptionParser(usage=usage)

parser.add_option("-c", dest="configfile",  default=defaultconfig,
  help="Config file (default is %s)" % defaultconfig)
parser.add_option("-e", dest="tlefile",     default=defaulttle,
  help="TLE file from which to load objects (default is %s)" % defaulttle)
parser.add_option("-v", dest="verbose", action="store_true", default=False,
  help="Print debugging info")
parser.add_option("-f", dest="follow", action="store_true", default=False,
  help="Used in conjunction with any action to repeatedly run")

group=OptionGroup(parser,"Actions")
group.add_option("-l", "--list",    action="store_true",dest="action",default=True,
  help="List objects currently above the horizon (default)")
group.add_option("-t",  dest="object",
  help="Point to a specified object")
group.add_option("-p",  dest="azel",
  help="Point to a given Az-El vector (ie, \"280.4,71.0\")")
group.add_option("-a",  dest="abspos",
  help="Point to a given absolute coord")
group.add_option("-T", "--test",    action="store_true",dest="action",
  help="Test the platform (spin both axis)")
parser.add_option_group(group)

(options,args)=parser.parse_args()

p=SafeConfigParser()
try:
  p.read(options.configfile)
except Exception, e:
  print "Error opening config %s: %s" % (options.configfile,str(e))
  print "You can pass the config path with -c, or -h for help."
  sys.exit(1)

if options.verbose: print "Using %s and %s." % (options.tlefile,options.configfile)

me=ephem.Observer()

try:
  me.lat=p.get("location","latitude")
  me.lon=p.get("location","longitude")
except Exception, e:
  print "Conf parse error, exiting: %s" % e
  sys.exit(1)

# read a file of TLEs and return a list of TLE objects
def readTLEs(fname):
  try:
    f=open(options.tlefile,'r')
  except IOError:
    print "Can't open TLE file %s (try -h for help)" % (options.tlefile)
    sys.exit(1)

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

  if options.verbose: print "Read in %d TLEs from file." % len(sats)

  return sats

# take a list of object and return only the ones above the horizon
def satsAboveHorizon(s):
  satsAbove=list()
  me.date=strftime("%Y/%m/%d %H:%M:%S",gmtime())
  for somesat in s:
  	somesat.compute(me)

  	if (somesat.alt>0): 
  		satsAbove.append(somesat)

  return satsAbove

def printSats(s):
  # find longest name length
  maxlen=0
  for somesat in s:
  	if (len(somesat.name)>maxlen):
  		maxlen=len(somesat.name)

  # sort by name
  s=sorted(s,key=lambda somesat: somesat.name)

  namestr='NAME'
  numspaces=maxlen-len("NAME")
  for i in range(4,numspaces):
  	namestr=namestr+" "
  print "%s \t AZIMUTH(deg) \t ALTITUDE(deg) \t RANGE(km)" % namestr

  for somesat in s:
  	numspaces=maxlen-len(somesat.name)
  	namestr=somesat.name
  	i=0
  	for i in range(0,numspaces):
  		namestr=namestr+" "

  	print "%s\t% 3.2f\t\t% 3.2f\t\t% .0f" % (
  		namestr,math.degrees(somesat.az),math.degrees(somesat.alt),
  		somesat.range/1000)
	
def actionList():
  sats=readTLEs(options.tlefile)

  runflag=True  
  while runflag:
    if options.follow: os.system("clear")
    showsats=satsAboveHorizon(sats)
    printSats(showsats)
    
    if options.follow : sleep(0.05)
    else              : runflag=False

actionList()


