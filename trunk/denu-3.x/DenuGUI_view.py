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
	viewxml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/view.glade')
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
	viewstore = gtk.TreeStore(str, str)
	dictToTreestore(entry, viewstore)
	viewview = viewxml.get_widget("viewview")
	viewcolumn = gtk.TreeViewColumn('Entry')
	text_render = gtk.CellRendererText()
	text_render2 = gtk.CellRendererText()
	viewcolumn.pack_start(text_render, True)
	viewcolumn.pack_start(text_render2, True)
	viewcolumn.set_attributes(text_render, text=0)
	viewcolumn.set_attributes(text_render2, text=1)
	viewview.append_column(viewcolumn)
	viewview.set_model(viewstore)
	
	#Individual fields.
	#Type
	type = entry.keys()[0]
	viewxml.get_widget("view_type").set_text(type)
	#Name
	if entry[type]['name'].has_key(config.get('DEFAULT', 'locale')):
		viewxml.get_widget("view_name").set_text(entry[type]['name'][config.get('DEFAULT', 'locale')])
	else: # Default to english
		viewxml.get_widget("view_name").set_text(entry[type]['name']['en'])
	#Command
	if not type == 'folder':
		viewxml.get_widget("view_command").set_text(entry[type]['command'])
	#Icon
	if entry[type].has_key('icon'):
		if pixbuf_manager(entry[type]['icon']) != "Error: no file.":
			viewxml.get_widget("view_image").set_from_pixbuf(pixbuf_manager(entry[type]['icon']))
		if entry[type]['icon'].has_key('file'):
			viewxml.get_widget("view_icon").set_text(entry[type]['icon']['file'])
		elif entry[type]['icon'].has_key('url'):
			viewxml.get_widget("view_icon").set_text(entry[type]['icon']['url'])
	else:
		viewxml.get_widget("view_icon").set_text('None.')
	#viewxml.signal_autoconnect({'destroy' : destroy})
	viewxml.get_widget("view_window").show()
