#!/usr/bin/env python2

#weather.py
#Original author: M. Thomas Schellenberg ( mt86@csh.rit.edu )
#Current maintainer: Josh McSavaney ( mcsaucy@csh.rit.edu )
#A script used to scrape and parse weather information

import urllib, re, xmlrpclib, lastupdated
 
# get the file from the site
file = urllib.urlopen('http://www.weather.gov/data/current_obs/KROC.xml')

# make the file into a string
data = file.read()

WTHR_HEADER = "94"
WTHR_FILE = "12"
TEMP_FILE = "13"
WIND_FILE = "14"

weather = "Not Available"
temp = "Not Available"
windchill = "Not Available"

# search the file for the observation time and store the string
#re1 = re.search(r'<observation_time>(.*?)</observation_time>', data)
#obs = re1.group(1)
#################### BEING CHANGED TO REFLECT WHEN LAST CHANGE WAS MADE TO INFOSYS

# search the file for the weather and store the string
try:
	re2 = re.search(r'<weather>(.*?)</weather>', data)
	weather = re2.group(1)
except (AttributeError):
	pass

# search the file for the temp and store the string
try:
	re3 = re.search(r'<temperature_string>(.*?)</temperature_string>', data)
	temp = re3.group(1)
except (AttributeError):
	pass

# search the file for the windchill and store the string
try:
	re4 = re.search(r'<windchill_string>(.*?)</windchill_string>', data)
	windchill = re4.group(1)
except (AttributeError):
	pass

flash = False
# add the weather to little infosys (see the wiki for more details)
server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")

if not server.fileExists(WTHR_HEADER):
	server.delFile(WTHR_HEADER)
	server.addFile(WTHR_HEADER)
	flash = True

	server.addText(WTHR_HEADER, "ROTATE", "Current Weather Conditions:")
	server.addText(WTHR_HEADER, "HOLD", " %" + WTHR_FILE, WTHR_FILE)
	server.addText(WTHR_HEADER, "ROTATE", "Current Temperature:")
	server.addText(WTHR_HEADER, "HOLD", " %" + TEMP_FILE, TEMP_FILE)
	server.addText(WTHR_HEADER, "ROTATE", "Current Windchill:")
	server.addText(WTHR_HEADER, "HOLD", " %" + WIND_FILE, WIND_FILE)

if not server.fileExists(WTHR_FILE):
	server.delFile(WTHR_FILE)
	server.addFile(WTHR_FILE)
	flash = True
if not server.fileExists(TEMP_FILE):
	server.delFile(TEMP_FILE)
	server.addFile(TEMP_FILE)
	flash = True
if not server.fileExists(WIND_FILE):
	server.delFile(WIND_FILE)
	server.addFile(WIND_FILE)
	flash = True

server.addString(WTHR_FILE, weather)
server.addString(TEMP_FILE, temp)
server.addString(WIND_FILE, windchill)

flash = lastupdated.getTime() or flash
if flash:
	server.updateSign()
