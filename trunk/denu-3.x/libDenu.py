#!/usr/bin/env python
#Copyright (C) 2005  Scott Shawcroft
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# This is the start of libDenu 3.x
# It is released under the GPLv2

##################
# Module Imports #
##################
import xml.dom.minidom as xml
import sys,os,string
from xml.sax import saxlib, saxexts
import libDenuShared as denu_shared

#################
# Variable Init #
#################
home = os.environ['HOME']
sys.path.extend(["/usr/share/denu/wms", home + "/.denu/wms", home + "/denu/svn/trunk/denu-3.x/wms"])
config = {}
config['static'] = '/usr/share/denu/'
config['dynamic'] = '/var/cache/denu/'
config['testdir'] = '/home/scott/denu/svn/trunk/denu-3.x/'

#######################
# WM module wrappers. #
#######################

#Works together with the denu wm module to import the wm menu to denu xml format.
def wm_import(wm, file="default"):
	global menu
	exec 'import ' + "denuWM_" + wm + ' as wm'
	menu = wm.wm_import(file)
	return menu
	
#Works together with the denu wm module to export the denu xml format to the proprietary format of the specified wm.
def wm_export (wm, file="default"):
	global menu
	exec 'import ' + "denuWM_" + wm + ' as wm'
	wm.wm_export(menu)
	return "Successful."
	
#Duplicates the current file(s) for the specified wm, for restoration from denu using libDenu.restore().  Works in combination with denu wm module.
def backup (wm):
	exec 'import ' + "denuWM_" + wm + ' as wm'
	wm.backup()
	return "Successful."
	
#Restores the menu to a specific file.  Restores from files created with libDenu.backup().  Works in combination with denu wm module.
def restore (wm):
	global menu
	exec 'import ' + "denuWM_" + wm + ' as wm'
	wm.restore()
	return "Successful."
	
###########################
# File Oriented Functions #
###########################

#Saves the denu xml format to a .xml file.
def d_save (file):
	global menu
	file = open(file, 'w')
	menu.writexml(file)
	return "Successful."

#Opens a denu xml file into the program.
def d_open (file, var='menu'):
	if os.path.exists(file):
		if var == 'menu':
			global menu
			menu = xml.parse(file)
			return menu
		elif var == 'installed':
			installed = xml.parse(file)
			return installed
	else:
		return "Failed: Does not exist."

############################	
# Window Manager Functions #
############################

#Gets current running wm.
def getCurrentWM ():
	keys = wmConfig.keys()
	running = []
	for key in keys:
		if len(os.popen("ps -C " + wmConfig[key][0], "r").readlines()) > 1:
			running.append(key)
	return running
	
#Gets installed wms.
def getInstalledWMs ():
	path = os.environ['PATH']
	path = string.split(path,':')
	bins = []
	wms = {}
	wm = []
	keys = wmConfig.keys()
	for key in keys:
		wms[wmConfig[key][0]] = key
	for spath in path:
		if os.path.exists(spath):
			tmp = os.listdir(spath)
			for entry in tmp:
				bins.append(entry)
			for bin in bins:
				if wms.has_key(bin):
					wm.append(wms[bin])
			bins = []
	return wm
	
#Updates wm configs in wmConfig variable.
def update_wmConfig():
	global wmConfig
	if os.path.exists("/home/scott/denu/svn/trunk/denu-3.x/wms"):
		default_files = os.listdir("/home/scott/denu/svn/trunk/denu-3.x/wms")
	else:
		default_files = []
	if os.path.exists(home + "/.denu/wms"):
		user_files = os.listdir(home + "/.denu/wms")
	else:
		user_files = []
	wmConfig = {}
	for fn in default_files:
		if not fn.find("denuWM_") == -1 and user_files.count(fn)==0:
			name = fn.replace(".py", "")
			exec "import " + name + " as wm"
			name = name.replace("denuWM_", "")
			wmConfig[name] = wm.config
	return "Successful."
	
############################
# Initialization Functions #
############################

#Updates denu database of programs.Variable:data.
def update ():
	import urllib2
	try:
		newestDB = urllib2.urlopen('http://denu.sourceforge.net/files/newestDB').readline()
	except:
		return 'Could not find denu server.'
	newestDB = string.strip(newestDB)
	installedDB = open (config['testdir'] + 'installedDB')
	installDB = installedDB.readline()
	installedDB.close()
	#Compare newest and installed so that the same version isn't downloaded again.
	if installDB != newestDB:
		file = urllib2.urlopen('http://denu.sourceforge.net/files/prgmDB.xml')
		tmp = open(config['testdir'] + 'prgmDB.xml', 'w')
		tmp.writelines(file.readlines())
		tmp.close()
		file.close()
	return "Successful."

#Class for handling the raw xml database to installed xml records.
#Modeled after tutorial here: http://www.rexx.com/~dkuhlman/pyxmlfaq.html#howsaxhandler
class installedHandler (saxlib.HandlerBase):
	def __init__ (self):
		self.level = 0
		self.entry = {}
		self.keep = 1
		self.location = []
		path = os.environ['PATH']
		path = string.split(path,':')
		self.bins = []
		for spath in path:
			if os.path.exists(spath):
				tmp = os.listdir(spath)
				for entry in tmp:
					self.bins.append(entry)
					
	def startDocument(self):
		self.domImp = xml.getDOMImplementation()
		self.dom = self.domImp.createDocument(None, None, None)
		self.parent = self.dom.createElement("data")
		self.parent.setAttribute("type", "installed")
		self.dom.appendChild(self.parent)
		
	def startElement(self, name, attributes):
		if not name == "data":
			self.location.append(name)
		if name == "program":
			commands = attributes.get("command")
			commands = commands.split(":")
			exists = "no"
			for command in commands:
				if self.bins.count(command)>0:
					exists = "yes"
			if exists == "yes":
				self.entry = {"program" : {"portage-id": attributes.get("portage-id")}}
				self.keep = 1
			else:
				self.keep = 0
		
	def endElement(self, name):
		if not name == "data":
			self.location.pop()
		if name == "program" and self.keep == 1:
			denu_shared.buildDOM(self.entry, self.parent, self.dom)
		
	def endDocument(self):
		file = open("/home/scott/denu/svn/trunk/denu-3.x/installed.xml", 'w')
		strng = self.dom.toprettyxml()
		file.write(strng)
		file.close()
		
	def characters(self, chars, offset, length):
		if self.keep == 1:
			if not chars.strip() == "":
				variable = "self.entry"
				for place in self.location:
					exec "result = " + variable + ".has_key(place)"
					if not result:
						exec variable + "[place] = {}"
					variable += "['" + place + "']"
				exec variable + " = chars"
		
#Updates denu database of installed programs. Variable:installed.
def sysupdate():
	handler = installedHandler()
	parser = saxexts.make_parser()
	parser.setDocumentHandler(handler)
	prgmDB = open("/home/scott/denu/svn/trunk/denu-3.x/prgmDB.xml", 'r')
	parser.parseFile(prgmDB)
	prgmDB.close()
	return "Successful."
	
#Returns a denu xml structure with all installed programs in them.
def autoGen ():
	installed = xml.parse("/home/scott/denu/svn/trunk/denu-3.x/installed.xml")
	for child in installed.firstChild.childNodes:
		location = child.getElementsByTagName("location")[0].nodeValue
		split_location = location.split("|")
		split_location.pop(0)
		domImp = xml.getDOMImplementation()
		dom = domImp.createDocument(None, None, None)
		parent = dom.createElement("data")
		parent.setAttribute("type", "menu")
		dom.appendChild(parent)
	return menu
	
#Modifies an entry in the xml.
def editEntry(entry, entryId):
	global menu
	element = idIndex[entryId]
	for tag in element.childNodes:
		element.removeChild(tag)
	denu_shared.buildDOM(entry['program'], element, menu)
	return "Successful."
				
#Returns information on entries in the xml.  May be a list or object.
def viewEntry(entryId):
	global idIndex
	entry = idIndex[entryId]
	dict = {}
	dict[entry.nodeName] = {}
	location = []
	denu_shared.DOMtoDict (dict[entry.nodeName], entry, location)
	return dict
			
#Inserts an entry into the denu xml structure.		
def addEntry(entry, parent, sibling=None):
	global idIndex
	global menu
	newId = []
	for key in entry.keys():
		tmp = menu.createElement(key)
		denu_shared.buildDOM(entry[key], tmp, menu)
		if sibling == None:
			idIndex[parent].appendChild(tmp)
		else:
			idIndex[parent].insertBefore(tmp, idIndex[sibling])
		tmpId = len(idIndex)/2
		newId.append(tmpId)
		idIndex[tmpId] = tmp
		idIndex[tmp] = tmpId
	return newId
	
#Deletes an entry from the denu xml structure.
def deleteEntry(entryId):
	idIndex[entryId].parentNode.removeChild(idIndex[entryId])
	return "Successful."
	
#Stores the entry for later use.
def saveEntry(entryId, overwrite=0):
	global idIndex
	import random
	type = idIndex[entryId].nodeName
	filename = idIndex[entryId].getElementsByTagName("command")
	filename = filename + ".xml"
	if os.path.exists(config['testdir'] + type + "/" + filename) and overwrite == 0:
		filename = filename.replace(".xml", random.random(0,500,1) + ".xml")
	file = open(config['testdir'] + type + "/" + filename, 'w')
	strng = idIndex[entryId].toprettyxml()
	file.write(strng)
	file.close()
	return "Successful."
	
def loadEntry(file, parent, sibling=None):
	global idIndex
	tmp = = xml.parse(file)
	newId = []
	if sibling == None:
		idIndex[parent].appendChild(tmp)
	else:
		idIndex[parent].insertBefore(tmp, idIndex[sibling])
	tmpId = len(idIndex)/2
	newId.append(tmpId)
	idIndex[tmpId] = tmp
	idIndex[tmp] = tmpId
	return newId
	
#Moves entries within the denu xml structure.
def moveEntry(entryId, parent, sibling=None):
	child = idIndex[entryId].parentNode.removeChild(idIndex[entryId])
	if sibling == None:
		idIndex[parent].appendChild(child)
	else:
		idIndex[parent].insertBefore(child, idIndex[sibling])
	return "Successful."
	
#############################	
# Troubleshooting Functions #
#############################

def printMenu(root, locale="en", level=0):
	tab="   "
	for node in root.childNodes:
		if node.nodeName == "program":
			name = node.getElementsByTagName("name")
			local_name = name[0].getElementsByTagName(locale)
			if not local_name == []:
				print tab*level + local_name[0].firstChild.nodeValue
			else:
				local_name = name[0].getElementsByTagName("en")
				print tab*level + local_name[0].firstChild.nodeValue
		elif node.nodeName == "folder":
			name = node.getElementsByTagName("name")
			local_name = name[0].getElementsByTagName(locale)
			if not local_name == []:
				print tab*level + local_name[0].firstChild.nodeValue
			else:
				local_name = name[0].getElementsByTagName("en")
				print tab*level + local_name[0].firstChild.nodeValue
			printMenu(node, locale, level + 1)

def buildIdChildRelations ():
	global menu,idIndex
	idIndex = {}
	def internal(node, idIndex, x=0):
		for child in node.childNodes:
			if child.nodeName == "data" or child.nodeName == "folder" or child.nodeName == "program" or child.nodeName == "special":
				idIndex[child] = x
				idIndex[x] = child
				x = x + 1
			if child.nodeName == "data" or child.nodeName == "folder":
				x, idIndex = internal(child, idIndex, x)
			
		return x, idIndex
	x, idIndex = internal(menu, idIndex)
			
def printIdIndex():
	global idIndex
	for key in idIndex.keys():
		print "id: " + str(key) + " value: "
		print idIndex[key]
