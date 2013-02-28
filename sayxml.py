#!/usr/bin/python2

#sayxml.py
#Original author: Scott Dougan ( orange@csh.rit.edu )
#Current maintainer: Josh McSavaney ( mcsaucy@csh.rit.edu )
#A script used for bridging the gap between XML and the BetaBrite sign

from xml.dom import minidom
from BetaBrite import *
from time import sleep
from os import system
import re

def parsexml(xml):
  dom = minidom.parseString(xml)
  dom.normalize()
  handleLilinfosys(dom.documentElement)

def getText(nodelist):
  rc = ""
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc = rc + node.data
  return rc

def handleLilinfosys(lilinfosys):
  #handle any future infosys attribute extensions here
  device = u'/dev/ttyUSB0'
  if lilinfosys.hasAttribute(u'device'):
    device = lilinfosys.getAttribute(u'device')
  type = u'ALL SIGNS'
  if lilinfosys.hasAttribute(u'type'):
    type = lilinfosys.getAttribute(u'type')
  address = u'00'
  if lilinfosys.hasAttribute(u'address'):
    address = lilinfosys.getAttribute(u'address')
  startPacket(port=device.encode('ASCII'), type=type.encode('ASCII'), address=address.encode('ASCII'))
  files = lilinfosys.getElementsByTagName(u'file')
  #send memory config
  handleConfiguration(files)
  endPacket()
  # this is where we would sleep time.sleep(10)
  # we may want to consider temporarily displaying a blank priority file to prevent the annoying flickering
  for file in files:
    sleep(.1)
    startPacket(port=device.encode('ASCII'), type=type.encode('ASCII'), address=address.encode('ASCII'))
    handleFile(file)
    endPacket()

def handleConfiguration(files):	#should find a way to handle STRING files
  startSpecialFunction()
  startMemoryConfig()
  for file in files:
    print "label", file.getAttribute(u'label')
    if file.getElementsByTagName(u'string').length > 0:
        addStringConfig(file.getAttribute(u'label').encode('ASCII'), getFileLength(file))
    else:
        addTextConfig(file.getAttribute(u'label').encode('ASCII'), getFileLength(file), 'ALL TIMES', 'NO TIMES' )
  endMemoryConfig()
  endSpecialFunction()

def getFileLength(file):
  texts = file.getElementsByTagName(u'text')
  strings = file.getElementsByTagName(u'string');

  #we NEED to check to see if there are STRINGs in here. If there are, that may ruin things quickly
  #my current way to handle this is to ignore all text when working with strings
  length = 1 # one off... probably due to file label

  if len(strings) > 0:
  	for string in strings:
		length += len(getText(string.childNodes)) + 1 #more waste, why not...
	print "string length", length
	return length
  for text in texts:
    # length includes the length of the write mode
    # adding an extra byte for good luck, and because i love waste
    length += len(WRITE_MODES[text.getAttribute(u'effect')]) + len(getText(text.childNodes)) + 1

  print 'length',  length
  return length

def handleFile(file):	#this should also be modified to handle STRINGs
  textLines = file.getElementsByTagName(u'text')
  stringLines = file.getElementsByTagName(u'string')

  #I'm pretty sure you can't mix string and text statements.
  #Under the off chance that you can, I'm pretty sure this isn't ready for it.
  if len(stringLines) > 0:
    print "STRING"
    startFile(file.getAttribute(u'label'), "WRITE STRING")
    handleStringLines(stringLines)
  else:
    print "TEXT"
    startFile(file.getAttribute(u'label'))
    handleTextLines(textLines)
  
  endFile()

def handleTextLines(lines):
  for line in lines:
    handleTextLine(line)

def handleStringLines(lines):
  text = ""
  for line in lines:
    if line.hasAttribute(u'effect'):
      print "I'm not sure what you were thinking. Strings don't really have effects..."
    text += getText(line.childNodes)
    print "Handling a line of string-age"
    
  addString(text = text.encode('ASCII'))

def embedStringInText(match):
  #This function will change %<FILE LABEL> into an appropriate STRING call for TEXT entries
  fileLabel = int(match.group(0)[1:3])
  print fileLabel

  if fileLabel > 0 and fileLabel <= 94 and fileLabel is not 31:
  	return "\x10" + FILE_LABELS[str(fileLabel)]
  else:
  	return match.group(0)

def handleTextLine(line):
  style = u'ROTATE'
  if line.hasAttribute(u'effect'):
    style = line.getAttribute(u'effect')
  	
  text = getText(line.childNodes)
  if line.hasAttribute(u'embed'):
  	text = re.sub( "%[0-9]{1,2}", embedStringInText, text )
  addText(text = text.encode('ASCII'), mode = style.encode('ASCII'))

