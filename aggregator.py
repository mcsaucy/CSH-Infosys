#!/usr/bin/env python2

#aggregator.py
#Original author: Scott Dougan ( orange@csh.rit.edu )
#Current maintainer: Josh McSavaney ( mcsaucy@csh.rit.edu )
#A news aggregator script

"""
RUN ME ON A CRON
"""
import feedparser, lastupdated
from pysqlite2 import dbapi2 as sqlite
import xmlrpclib
SQLITEDB = "/home/orange/lilinfosys.db"
INFOSYS_FILE = "91"
server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")
server.delFile(INFOSYS_FILE)
server.addFile(INFOSYS_FILE)
server.addText(INFOSYS_FILE, "SPRAY", "Feed Parser")
con = sqlite.connect(SQLITEDB)
cur = con.cursor()
cur.execute('SELECT * FROM feeds ORDER BY id')
feeds = cur.fetchall()
for feed in feeds:
  d = feedparser.parse(feed[1].encode('ASCII'))
  server.addText(INFOSYS_FILE, "FLASH", d.feed.title.encode("ASCII") + ": ")
  numdisplayed = 0
  for entry in d.entries:
    if numdisplayed >= feed[3]:
      break
    server.addText(INFOSYS_FILE, "ROTATE", entry.title.encode("ASCII").replace("&amp;", "&").replace("&quot;", "\""))
    numdisplayed += 1

lastupdated.getTime()
server.updateSign()
