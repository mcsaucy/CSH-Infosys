#!/usr/bin/python2

#lastupdated.py
#Author: Josh McSavaney ( mcsaucy@csh.rit.edu )
#A script for documenting when the last update to the sign was made

import xmlrpclib, time

server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")
def getTime():	
	HEADER_FILE = "24"
	TIME_FILE = "1"
	flash = False
	
	time_string = time.strftime("%b %d at %H:%M", time.localtime())
	
	if not server.fileExists(HEADER_FILE):
		server.delFile(HEADER_FILE)
		server.addFile(HEADER_FILE)
		server.addText(HEADER_FILE, "COMPRESSED ROTATE",
						"Last updated on %" + TIME_FILE,
						TIME_FILE)
		flash = True
	if not server.fileExists(TIME_FILE):
		server.delFile(TIME_FILE)
		server.addFile(TIME_FILE)
		flash = True

	server.addString(TIME_FILE, time_string)

	return flash

def update():
	server.updateSign()

if(__name__ == "__main__"):
	if getTime():
		update()
