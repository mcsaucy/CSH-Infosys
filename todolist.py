#!/usr/bin/env python2

#todolist.py
#Author: Josh McSavaney ( mcsaucy@csh.rit.edu )

import xmlrpclib

server = xmlrpclib.ServerProxy("http://infosys.csh.rit.edu:8080")

todo = open("./todo_list")

TODO_FILE = "90"

server.delFile(TODO_FILE)
server.addFile(TODO_FILE)
server.addText(TODO_FILE, "ROTATE", todo.read())
todo.close()

server.updateSign()
