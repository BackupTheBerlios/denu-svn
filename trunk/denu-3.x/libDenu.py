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

import xml.dom.minidom as xml
import sys,os
home = os.environ['HOME']
sys.path.append("/usr/share/denu/wms", home + "/.denu/wms")
#wmConfig = {"fluxbox" : ["fluxbox", "Fluxbox"], "gnome" : ["gnome-panel", "Gnome"]}

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
	
#Saves the denu xml format to a .xml file.
def d_save (file):
	global menu
	file = open(file, 'w')
	menu.writexml(file)
	return "Successful."

#Opens a denu xml file into the program.
def d_open (file, var='menu'):
	if var == 'menu':
		global menu
		menu = xml.parse(file)
		return menu
	elif var == 'installed':
		installed = xml.parse(file)
		return installed
	
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
	import string
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
					print spath
					wm.append(wms[bin])
			bins = []
	return wm
	
#Updates wm configs in wmConfig variable.
def update_wmConfig():
	global wmConfig
	import string
	default_files = os.listdir("/usr/share/denu/wms")
	user_files = os.listdir(home + "/.denu/wms")
	wmConfig = {}
	for fn in default_files:
		if not fn.find("denuWM_") == "-1":
			name = fn.replace(".py", "")
			exec "import " + name + " as wm"
			name = name.replace("denuWM_", "")
			wmConfig[name] = wm.config
	return "Successful."
	
#Updates denu database of programs.Variable:data.
def update ():
	return "Successful."
	
#Updates denu database of installed programs. Variable:installed.
def sysupdate ():
	return "Successful."
	
#Returns a denu xml structure with all installed programs in them.
def autoGen ():
	return menu
	
#Adds a folder entry into the denu xml structure.
def addFolder():
	return menu
	
#Modifies an entry in the xml.
def editEntry(entry, entryId):
	return "Successful."
	
#Returns information on entries in the xml.  May be a list or object.
def viewEntry(entryId):
	
	return list
	
#Inserts an entry into the denu xml structure.		
def addEntry(entry, parent, sibling=None):
	def fill(dict, element, menu):
		for key in dict.keys():
			tmp = menu.createElement(key)
			element.appendChild(tmp)
			try:
				dict[key].keys()
			except:
				type = "string"
			if type=="string":
				strng = menu.createTextNode(dict[key])
				tmp.appendChild(strng)
			else:
				fill(dict[key], tmp, menu)
			type = ""
	global idIndex
	newId = []
	for key in entry.keys():
		tmp = menu.createElement(key)
		fill(entry[key], tmp, menu)
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
def saveEntry(entryId):
	return "Successful."
	
#Moves entries within the denu xml structure.
def moveEntry(entryId, parent, sibling=None):
	child = idIndex[entryId].parentNode.removeChild(idIndex[entryId])
	if sibling == None:
		idIndex[parent].appendChild(child)
	else:
		idIndex[parent].insertBefore(child, idIndex[sibling])
	return "Successful."
	
def addSpecial():
	return "Successful."
	
def saveSpecial():
	return "Successful."
	
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
