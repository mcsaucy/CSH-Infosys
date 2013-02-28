#!/usr/bin/env python2

#clearall.py
#Original author: ???
#A utility script to wipe the contents of the sign

import xmlrpclib

server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")

server.clearAll()
server.updateSign()
