#!/usr/bin/env python2

#xmlrpcserver.py
#Original author: Possibly Scott Dougan ( orange@csh.rit.edu )
#Current maintainer: Josh McSavaney ( mcsaucy@csh.rit.edu )
#XML-RPC server to manage the state of the BetaBrite sign and ensure persistence
#	across updates

import os
import sys
import SimpleXMLRPCServer
from twisted.web import server, xmlrpc
from BetaBrite import WRITE_MODES, startPacket, endPacket, setPriority, removePriority
from xml.dom import minidom
from sayxml import parsexml, handleFile
from time import sleep
import signal

def gracefullyDepart(SIG, FRM): #ensure graceful departure if this is killed by systemd
	sys.exit(0)

signal.signal(signal.SIGHUP, gracefullyDepart)

NAMESPACE = 'http://infosys.csh.rit.edu/'
CURR_XML_LOC = '/tmp'
PORT=8080

FILE = CURR_XML_LOC + "/infosys_current.xml"
#FILE = "%s/infosys_current.xml" % os.path.expanduser('~')

def getDom():
  dom = minidom.parse(FILE)
  dom.normalize()
  return dom

def saveDom(dom):
  file = open(FILE, 'w')
  file.write(dom.toxml())
  file.close()

class Methods:
  def addFile(self, filelabel):
    if int(filelabel) < 0 or int(filelabel) > 95:
      return "BAD_FILELABEL"
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    # verify the file does not exist
    for file in files:
      if int(file.getAttribute('label')) == int(filelabel):
        return "FILE_EXISTS"
    # done with assertions now add the file
    file_element = dom.createElement('file')
    file_label = file_element.setAttribute('label', str(filelabel))
    lilinfosys.appendChild(file_element)
    saveDom(dom)
    return 'ok'

  def addText(self, filelabel, effect, text, embed = "0"):
    if int(filelabel) <= 0 or int(filelabel) > 95:
      return "BAD_FILELABEL"
    if not WRITE_MODES.has_key(effect.upper()):
      return "BAD_EFFECT"
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    found = False
    for file in files:
      if int(file.getAttribute('label')) == int(filelabel):
        assert not found
        found = True
        text_element = dom.createElement('text')
        text_effect = text_element.setAttribute('effect', effect.upper())
        embed = int(embed)
        if embed <= 94 and embed > 0 and embed != 63:
			text_embed = text_element.setAttribute('embed', str(embed))
        text_text = dom.createTextNode(text)
        text_element.appendChild(text_text)
        file.appendChild(text_element)
    if not found:
      return "FILE_DOES_NOT_EXIST"
    saveDom(dom)
    return 'ok'
 
  def addString(self, filelabel, string):
    if int(filelabel) <= 0 or int(filelabel) > 95 or int(filelabel) == 63:
      return "BAD_FILELABEL"
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    found = False
    foundFile = None
	
    flash = False #do we need to flash a memory config (and thus the display) for this?
    for file in files:
      if int(file.getAttribute('label')) == int(filelabel):
        assert not found
        found = True
        foundFile = file
    
    if not found:
      return "FILE_DOES_NOT_EXIST"

    if len(string) > 120: #play it safe, I guess
      string = string[:120]
      print "** WARNING ** truncating string to 120 characters"
		
    if foundFile.getElementsByTagName('text').length != 0:
	  print "CANNOT HAVE STRING AND TEXT IN SAME FILE"
	  return "CANNOT_HAVE_STRING_AND_TEXT_IN_SAME_FILE"
	  #Yo, you can't have a string and text item together.
		
    strings = foundFile.getElementsByTagName(u'string')
    if strings.length != 1 or not strings.item(0).hasAttribute(u'size') and strings.item(0).getAttribute(u'size') < len(string):
      print "Well, this won't be as seemless as we would've liked..."
      flash = True
		
    file_element = dom.createElement('file')
    file_label = file_element.setAttribute('label', str(filelabel))

    string_element = dom.createElement('string')
    string_size = string_element.setAttribute('size', str(len(string)))
    string_element.appendChild( dom.createTextNode( string ) )
	
    file_element.appendChild(string_element)
    lilinfosys.replaceChild(file_element, foundFile) #we'll just perform a switcheroo here...
    	
	#and NOW we should actually process that update...
    saveDom(dom)
    if flash:
      dom = getDom()
      parsexml(dom.toxml())
    else:
      startPacket()
      handleFile(file_element)
      endPacket()

    return 'ok'

  def delFile(self, filelabel):
    if int(filelabel) <= 0 or int(filelabel) > 95:
      return "BAD_FILELABEL"
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    # not caring if it finds more than one...
    # that should never happen (tm)
    # or doesn't find one
    for file in files:
      if file.getAttribute('label') == str(filelabel):
        lilinfosys.removeChild(file)
    saveDom(dom)
    return 'ok'

  def fileListing(self):
    list = [];
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    for file in files:
      list.append(int(file.getAttribute('label')))
    return list

  def fileExists(self, filelabel):
    if int(filelabel) < 0 or int(filelabel) > 95:
      return "BAD_FILELABEL"
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    for file in files:
      if int(file.getAttribute('label')) == int(filelabel):
        return True
    return False

  def fileContent(self, filelabel):
    if int(filelabel) <= 0 or int(filelabel) > 95:
      return "BAD_FILELABEL"
    list = []
    dom = getDom()
    lilinfosys = dom.documentElement
    files = lilinfosys.getElementsByTagName('file')
    for file in files:
      if int(file.getAttribute('label')) == int(filelabel):
        return file.toxml()
    return "FILE_NOT_FOUND"

  def updateSign(self):
    dom = getDom()
    parsexml(dom.toxml())
    return 'ok'

  def clearAll(self):
    dom = minidom.Document()
    infosys = dom.createElement('lilinfosys')
    dom.appendChild(infosys)
    saveDom(dom)
    return 'ok'

class InfosysXmlRpc(xmlrpc.XMLRPC):
  def xmlrpc_clearAll(self):
    return Methods.clearAll()

if __name__ == "__main__":
  from twisted.internet import reactor
  import xml.dom.minidom
  print "xmlrpcserver starting"
  if not os.path.exists( FILE ):
    print "Creating file " + FILE
    file = open (FILE, 'w')
    dom = xml.dom.minidom.Document()
    infosys_element = dom.createElementNS('http://infosys.csh.rit.edu/', 'lilinfosys')
    dom.appendChild(infosys_element)
    file.write(dom.toxml())
    file.close()
  methods_object = Methods()
  server = SimpleXMLRPCServer.SimpleXMLRPCServer(("0.0.0.0", PORT))
  server.register_instance(methods_object)
  server.serve_forever()
