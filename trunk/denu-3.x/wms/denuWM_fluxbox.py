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

# This is the fluxbox module for denu 3.x
# It is released under the GPLv2
# A module must have these functions:
#	wm_import(file) imports menu and optionally a specific file. Will recieve value of 'default' from libDenu if not set.- Imports menu relavent file(s) to standard denu XML structure.
#	wm_export(file) imports menu and optionally a specific file. Will recieve value of 'default' from libDenu if not set. - Exports denu XML to relavent menu files and check for duplications of files.  ie. use of .desktop files.
#	backup - Backs up the current menu.  For use at first run.  Backs up to the users home/.denu/backup folder inside another folder corresponding to the name of the module after the denuWM_ .
#	restore - Restores backed up menus.
#	refresh - kills and restart entity if necessary.  this refreshes menu, only kills if necessary.
#	getVersion - returns the version number of installed wm.
import os,string,re
import xml.dom.minidom as xml
import sys
home = os.environ['HOME']
sys.path.extend(["/usr/share/denu/wms", home + "/.denu/wms", home + "/denu/svn/trunk/denu-3.x/wms", home + "/denu/svn/trunk/denu-3.x"])
import libDenuShared as denu_shared
config = ['fluxbox', 'Fluxbox']
locale = "en"

def getVersion ():
	global version
	version = os.popen("fluxbox -version", "r").readlines()[0]
	return version
	
def refresh ():
	pass
	
def backup():
	if not os.path.exists(home + "/.denu/backup/fluxbox"):
		os.mkdir(home + "/.denu/backup/fluxbox")
	source = open(home + "/.fluxbox/menu", "r")
	dest = open(home + "/.denu/backup/fluxbox/menu-" + os.date(), "w")
	dest.writelines(source.readlines())
	source.close()
	dest.close()
	
def restore (date="latest"):
	backup()
	if date=="latest":
		if os.path.exists(home + "/.denu/backup/fluxbox"):
			files = os.listdir(home + "/.denu/backup/fluxbox")
			file = open(home + "/.denu/backup/fluxbox/" + files[files.len()-2], "r")
			dest = open(home + "/.fluxbox/menu", "w")
			dest.writelines(file.readlines())
			dest.close()
			file.close()
		else:
			return "No backups."
	else:
		if os.path.exists(home + "/.denu/backup/fluxbox"):
			file = open(home + "/.denu/backup/fluxbox/menu-" + date, "r")
			dest = open(home + "/.fluxbox/menu", "w")
			dest.writelines(file.readlines())
			dest.close()
			file.close()
		else:
			return "No backups."
			
def wm_import(file):
	if file == "default":
		file = home + "/.fluxbox/menu"
	menu_file_obj = open(file, "r")
	menu_file_list = menu_file_obj.readlines()
	menu_file_obj.close()
	domImp = xml.getDOMImplementation()
	dom = domImp.createDocument(None, None, None)
	parent = dom.createElement("data")
	parent.setAttribute("type", "menu")
	dom.appendChild(parent)
	location = [parent]
	x = 0
	for line in menu_file_list:
		if not string.find(line,"[submenu]") == -1: #folder.
			entry = {"folder" : {'name':{}}}
			entry['folder']['name']['en'] = string.strip(re.findall("\({1}[^(^)]+\){1}", line)[0], "()")
			if len(re.findall("\<{1}[^<^>]+\>{1}", line)) > 0:
				entry['folder']['icon'] = {}
				entry['folder']['icon']['file'] = string.strip(re.findall("\<{1}[^<^>]+\>{1}", line)[0], "<>")
			location.append(denu_shared.buildDOM(entry, location[-1], dom))
		elif line[0] == "#": #comment
			name = line[:17] + "..."
		elif not string.find(line, "[exec]") == -1: #program
			name_array = re.findall("\({1}[^(^)]+\){1}", line)
			if not len(name_array)==0:
				entry = {"program" : {'name':{}}}
				entry['program']['name']['en'] = string.strip(name_array[0], "()")
				entry['program']['command'] = string.strip(re.findall("\{{1}[^{^}]+\}{1}", line)[0], "{}")
				if len(re.findall("\<{1}[^<^>]+\>{1}", line)) > 0:
					entry['program']['icon'] = {}
					entry['program']['icon']['file'] = string.strip(re.findall("\<{1}[^<^>]+\>{1}", line)[0], "<>")
				denu_shared.buildDOM(entry, location[-1], dom)
		elif not string.find(line, "[begin]") == -1: #start
			parent.setAttribute("title", string.strip(re.findall("\({1}[^)^(]+\){1}", line)[0], "()"))
		elif not string.find(line, "[end]") == -1: #end
			if not x == len(menu_file_list)-1:
				location.pop()
			else:
				pass
		elif not len(re.findall("\[{1}[a-zA-z]+\]{1}", line)) == 0: #special
			entry = {"special" : {"name" : {}, "content" : {}}}
			name_array = re.findall("\({1}[^(^)]+\){1}", line)
			if not len(name_array)==0:
				entry['special']['name']['en'] = string.strip(name_array[0], "()")
			else:
				entry['special']['name']['en'] = string.strip(line)[:17] + "..."
			entry['special']['content']['fluxbox'] = string.strip(line)
			denu_shared.buildDOM(entry, location[-1], dom)
		x = x + 1
	return dom

def wm_export(menu, file):
	level = 0
	if menu.firstChild.hasAttribute("title"):
		title = menu.firstChild.getAttribute("title")
	else:
		title = "Denu 3.x"
	global menu_file
	menu_file = "[begin] (" + title + ")\n"
	def internal(node, level):
		global menu_file
		for child in node.childNodes:
			if child.nodeName == "program":
				try:
					name = child.getElementsByTagName('name')[0].getElementsByTagName(locale)[0].firstChild.nodeValue
				except:
					name = child.getElementsByTagName('name')[0].getElementsByTagName('en')[0].firstChild.nodeValue
				command = child.getElementsByTagName('command')[0].firstChild.nodeValue
				menu_file += level*"\t" + "[exec] (" + name + ") {" + command + "}"
				if len(child.getElementsByTagName('icon')) > 0:
					if child.getElementsByTagName("icon")[0].parentNode == child:
						icon = child.getElementsByTagName('icon')[0].getElementsByTagName("file")[0].firstChild.nodeValue
						menu_file += " <" + icon + ">\n"
					else:
						menu_file += "\n"
				else:
					menu_file += "\n"
			elif child.nodeName == "special":
				if len(child.getElementsByTagName('content')[0].getElementsByTagName("fluxbox")) > 0:
					menu_file += level*"\t" + child.getElementsByTagName('content')[0].getElementsByTagName("fluxbox")[0].firstChild.nodeValue + "\n"
			elif child.nodeName == "folder":
				try:
					name = child.getElementsByTagName('name')[0].getElementsByTagName(locale)[0].firstChild.nodeValue
				except:
					name = child.getElementsByTagName('name')[0].getElementsByTagName('en')[0].firstChild.nodeValue
				menu_file += level*"\t" + "[submenu] (" + name + ")"
				if len(child.getElementsByTagName('icon')) > 0:
					if child.getElementsByTagName("icon")[0].parentNode == child:
						icon = child.getElementsByTagName('icon')[0].getElementsByTagName("file")[0].firstChild.nodeValue
						menu_file += " <" + icon + ">\n"
					else:
						menu_file += "\n"
				else:
					menu_file += "\n"
				internal (child, level+1)
				menu_file += level*"\t" + "[end]\n"
	internal (menu.firstChild, level)
	menu_file += "[end]"
	if file == "default":
		file = home + "/.fluxbox/menu"
	dest = open(file, "w")
	dest.write(menu_file)
	dest.close()
	return "Successful."
