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
#Works together with the denu wm module to import the wm menu to denu xml format.
def wm_import(file, wm):
	global menu
	exec 'import ' + "denuWM_" + wm + ' as wm'
	menu = wm.wm_import(file)
	return menu
	
#Works together with the denu wm module to export the denu xml format to the proprietary format of the specified wm.
def wm_export (file, wm):
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
def d_open (file):
	global menu
	menu = xml.parse(file)
	return menu
	
#Duplicates the current file(s) for the specified wm, for restoration from denu using libDenu.restore().  Works in combination with denu wm module.
def backup (wm):
	return "Successful."
	
#Restores the menu to a specific file.  Restores from files created with libDenu.backup().  Works in combination with denu wm module.
def restore (wm):
	print menu
	return "Successful."
	
#Gets current running wm.
def getCurrentWM ():
	print "yup"
	#return wm
	
#Gets installed wms.
def getInstalledWMs ():
	return wms
	
#Updates wm configs in wm_config variable.
def update_wm_modules():
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
def editEntry():
	return "Successful."
	
#Returns information on entries in the xml.  May be a list or object.
def viewEntry():
	return list
	
#Inserts an entry into the denu xml structure.		
def addEntry():
	return "Successful."
	
#Deletes an entry from the denu xml structure.
def deleteEntry():
	return "Successful."
	
#Stores the entry for later use.
def saveEntry():
	return "Successful."
	
#Moves entries within the denu xml structure.
def moveEntry():
	return "Successful."
	
def addSpecial():
	return "Successful."
	
def saveSpecial():
	return "Successful."
