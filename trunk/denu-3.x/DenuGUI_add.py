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
from DenuGUI_config import config
from DenuGUI_SharedVars import *
from DenuGUI_common import *

def init(widget):
	global xml
	xml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/add.glade')
	xml.signal_autoconnect({
	'cancel_add' : destroy,
	'add_entry' : add_entry
	})
	xml.get_widget("add_window").show()
	
def add_entry (widget):
	global xml
	type_array = ['folder', 'program', 'special']
	type = xml.get_widget("add_type").get_active()
	entry = {type_array[type] : {'name' : {}}}
	
	#Name
	name = xml.get_widget("add_name").get_text()
	if config.get('DEFAULT', 'locale'):
		entry[type_array[type]]['name'][config.get('DEFAULT', 'locale')] = name
	else: # Default to english
		entry[type_array[type]]['name']['en'] = name
		
	#Command
	command = xml.get_widget("add_command").get_text()
	if not command == "" and not type == 0:
		entry[type_array[type]]['command'] = command
	elif not type == 0:
		pass #Stop, required.
	
	#Portage ID
	pid = xml.get_widget("add_pid").get_text()
	if not pid == "":
		entry[type_array[type]]['portage-id'] = pid
	
	#Folder
	folder = xml.get_widget("add_folder").get_text()
	if not folder == "":
		if type == 0:
			entry[type_array[type]]['key'] = pid
		else:
			entry[type_array[type]]['location'] = pid
	
	#Icon
	icon = xml.get_widget("add_icon").get_filename()
	if not icon == None:
		entry[type_array[type]]['icon'] = {}
		entry[type_array[type]]['icon']['file'] = icon
		
	
	iterList = []
	def createList(model, path, iter):
		iterList.append(iter)
	treeselection = menuview.get_selection()
	treeselection.selected_foreach(createList)
	if len(iterList) > 0:
		if menustore.iter_parent(iterList[0]) == None:
			parent = 0
		else:
			parent = menustore.get_value(menustore.iter_parent(iterList[0]), 2)
		id = libDenu.addEntry(entry, parent, menustore.get_value(iterList[0], 2))[0]
		if entry[entry.keys()[0]].has_key('icon'):
			if not DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
				menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
			else:
				menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [None, name, id])
		else:
			menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [None, name, id])
	else:
		parent = 0
		id = libDenu.addEntry(entry, parent)[0]
		if entry[entry.keys()[0]].has_key('icon'):
			if not DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
				menustore.append(None, [DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
			else:
				menustore.append(None, [None, name, id])
		else:
			menustore.append(None, [None, name, id])
	xml.get_widget("add_window").destroy()
	
def change_add_state(widget):
	new_type = widget.get_active()
	if new_type == 0:
		if xml.get_widget("add_command_cont").get_property('visible'):
			xml.get_widget("add_command_cont").hide()
	elif new_type == 1:
		if not xml.get_widget("add_command_cont").get_property('visible'):
			xml.get_widget("add_command_cont").show()
	elif new_type == 2:
		if not xml.get_widget("add_command_cont").get_property('visible'):
			xml.get_widget("add_command_cont").show()
