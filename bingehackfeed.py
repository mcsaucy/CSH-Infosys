#!/usr/bin/env python2

#bingehackfeed.py
#Author: Josh McSavaney ( mcsaucy@csh.rit.edu )
#A simple python script designed to scrape the CSH bingehack twitter feed and publish the results


import xmlrpclib
import feedparser
import lastupdated

death = feedparser.parse("http://api.twitter.com/1/statuses/user_timeline.rss?screen_name=BingeHack")
server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")

HEADER_FILE = "50" 
DEATH_FILE = "4"
flash = False
latest_tweet = death.entries[0].title[11:]

if not server.fileExists(HEADER_FILE):
	server.delFile(HEADER_FILE)
	server.addFile(HEADER_FILE)
	server.addText(HEADER_FILE, "ROTATE", "Latest Victim: %"
					+ DEATH_FILE, DEATH_FILE)
	flash = True

if not server.fileExists(DEATH_FILE):
	server.delFile(DEATH_FILE)
	server.addFile(DEATH_FILE)
	flash = True

server.addString(DEATH_FILE, latest_tweet)
#server.addText(VICTIM_FILE, "ROTATE", latest_tweet)

flash = lastupdated.getTime() or flash
if flash:
	server.updateSign()
