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
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
from DenuGUI_config import config,home
sys.path.extend(["/usr/share/denu/wms", home + "/.denu/wms", config.get('DEFAULT', 'default'), config.get('DEFAULT', 'default') + "wms", config.get('DEFAULT', 'default') + "includes"])
from DenuGUI_common import *
import libDenu
from DenuGUI_SharedVars import xml,menuview,installedview
	
def init(widget):
	global xml
	xml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/edit.glade')
	menu_iterList = []
	def createMenuList(model, path, iter):
		menu_iterList.append(iter)
	treeselection = menuview.get_selection()
	treeselection.selected_foreach(createMenuList)
	installed_iterList = []
	def createInstalledList(model, path, iter):
		installed_iterList.append(iter)
	treeselection2 = installedview.get_selection()
	treeselection2.selected_foreach(createInstalledList)
	global id
	if len(menu_iterList) > 0:
		model = menustore
		iter = menu_iterList[0]
		id = menustore.get_value(iter, 2)
		entry = libDenu.viewEntry(id, "menu")
	elif len(installed_iterList) > 0:
		model = installedstore
		iter = installed_iterList[0]
		id = installedstore.get_value(iter, 2)
		entry = libDenu.viewEntry(id, "installed")
	text_render = gtk.CellRendererText()
	text_render2 = gtk.CellRendererText()
	
	#Individual fields.
	#Type
	type = entry.keys()[0]
	xml.get_widget("type").set_text(type)
	#Name
	if entry[type]['name'].has_key(config.get('DEFAULT', 'locale')):
		xml.get_widget("name").set_text(entry[type]['name'][config.get('DEFAULT', 'locale')])
	else: # Default to english
		xml.get_widget("name").set_text(entry[type]['name']['en'])
	#Command
	if not type == 'folder':
		xml.get_widget("command").set_text(entry[type]['command'])
	#Icon
	#debugPrint(xml.get_widget("image").get_title())
	if entry[type].has_key('icon'):
		#if entry[type]['icon'].has_key('file'):
		#	xml.get_widget("image").set_label(entry[type]['icon']['file'])
		#elif entry[type]['icon'].has_key('url'):
		#	xml.get_widget("image").set_label(entry[type]['icon']['url'])
		if pixbuf_manager(entry[type]['icon']) != "Error: no file.":
			icon = gtk.Image()
			icon.set_from_pixbuf(pixbuf_manager(entry[type]['icon']))
			icon.show()
			xml.get_widget("image").add(icon)
	else:
		xml.get_widget("image").set_label('None.')
	xml.signal_autoconnect({'destroy' : destroy, 'edit' : edit})
	xml.get_widget("edit_window").show()
	
def edit (widget):
	global id
	global xml
	name = xml.get_widget("name").get_text()
	type = xml.get_widget("type").get_text()
	command = xml.get_widget("command").get_text()
	entry = {type : {'name' : {config.get('DEFAULT', 'locale') : name}, 'command' : command}}
	debugPrint("Edit " + type)
	libDenu.editEntry(entry,id)
