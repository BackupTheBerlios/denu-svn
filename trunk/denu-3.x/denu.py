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
import pygtk
pygtk.require('2.0')
import gtk,libDenu
import gtk.glade
import xml.dom.minidom as xml_dom
import string,urllib2,os
home = os.environ['HOME']
xml = gtk.glade.XML('denu/denu.glade')
config = {}
config['locale'] = 'en'
config['pixbuf_size'] = 32
pixbuf_index = {}
menustore_connects = []
menustore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
def pixbuf_manager(filename, size):
	#print 'file: \"' + filename + '\"'
	global pixbuf_index
    	okay = 'yes'
    	if pixbuf_index.has_key(filename):
    		if not pixbuf_index[filename].has_key(size):
    			if not filename[0:1]=='/':
    				full_filename = home + '/.denu/pixmaps/' + filename
        			if not os.path.exists(full_filename):
       					try:
						image = urllib2.urlopen('http://denu.sourceforge.net/pixmaps/' + filename)
						okay = 'yes'
					except:
						pixbuf_index[filename] = "Error: no file."
						return "Error: no file."
						okay = 'no'
					if okay=='yes':	
						file = open(full_filename, 'w')
						file.write(image.read())
						file.close()
			else:
				full_filename = filename
			if okay=='yes':
				#print filename
            			try:
            				pixbuf_index[filename][size] = gtk.gdk.pixbuf_new_from_file_at_size(full_filename, size, size)
            			except:
            				return "Error: no file."
        else:
        	if not filename[0:1]=='/':
    			full_filename = home + '/.denu/pixmaps/' + filename
        		if not os.path.exists(full_filename):
       				try:
					image = urllib2.urlopen('http://denu.sourceforge.net/pixmaps/' + filename)
					okay = 'yes'
				except:
					pixbuf_index[filename] = "Error: no file."
					return "Error: no file."
					okay = 'no'
				if okay=='yes':	
					file = open(full_filename, 'w')
					file.write(image.read())
					file.close()
		else:
			full_filename = filename
			if okay=='yes':
				pixbuf_index[filename] = {}
            			try:
            				pixbuf_index[filename][size] = gtk.gdk.pixbuf_new_from_file_at_size(full_filename, size, size)
            			except:
            				return "Error: no file."
        if not pixbuf_index[filename] == "Error: no file.":
       		return pixbuf_index[filename][size]
       	else:
       		return pixbuf_index[filename]
       	
def domToTreestore(menu_dom, treestore, parent, location=None, size=config['pixbuf_size'], type="menu"):
	for child in parent.childNodes:
		if child.nodeName == "folder" or child.nodeName == "program" or child.nodeName == "special":
			name = string.strip(child.getElementsByTagName("name")[0].getElementsByTagName(config['locale'])[0].firstChild.nodeValue)
			if len(child.getElementsByTagName("icon")) == 1 and child.getElementsByTagName("icon")[0].parentNode == child:
				icon = string.strip(child.getElementsByTagName("icon")[0].firstChild.nodeValue)
			else:
				icon = None
			id = libDenu.idIndex[type][child]
			if not icon == None and not pixbuf_manager(icon, size) == "Error: no file.":
				iter = treestore.append(location, [pixbuf_manager(icon, size), name, id])
			else:
				iter = treestore.append(location, [None, name, id])
		if child.nodeName == "folder":
			treestore = domToTreestore(menu_dom, treestore, child, iter, size, type)
	return treestore

def domToListstore(liststore, parent, size=config['pixbuf_size'], xml_dom_type="installed"):
	for child in parent.childNodes:
		if child.nodeName == "folder" or child.nodeName == "program" or child.nodeName == "special":
			name = string.strip(child.getElementsByTagName("name")[0].getElementsByTagName(config['locale'])[0].firstChild.nodeValue)
			if len(child.getElementsByTagName("icon")) == 1 and child.getElementsByTagName("icon")[0].parentNode == child:
				icon = string.strip(child.getElementsByTagName("icon")[0].firstChild.nodeValue)
			else:
				icon = None
			id = libDenu.idIndex[xml_dom_type][child]
			if not icon == None and not pixbuf_manager(icon, size) == "Error: no file.":
				liststore.append([pixbuf_manager(icon, size), name, id])
			else:
				liststore.append([None, name, id])
	return liststore
	
def d_open(widget):
	global menustore, menustore_connects
	window = xml.get_widget("open_denu")
	filename = window.get_filename()
	libDenu.d_open(filename)
	window.hide()
	libDenu.buildIdChildRelations()
	for handler in menustore_connects:
		menustore.handler_block(handler)
	menustore.clear()
	domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)
	for handler in menustore_connects:
		menustore.handler_unblock(handler)

def d_save(widget):
	window = xml.get_widget("save_denu")
	filename = window.get_filename()
	if not filename[-4:] == ".xml":
		filename = filename + ".xml"
	libDenu.d_save(str(filename))
	window.hide()
	
def show_save_denu(widget):
	window = xml.get_widget("save_denu")
	window.show()
	
def destroy(widget, signal=""):
	gtk.main_quit()
	
def show_open_denu(widget):
	xml.get_widget("open_denu").show()
	
def reorder (treemodel, path, iter):
	childId = treemodel.get_value(iter, 2)
	if not treemodel.iter_parent(iter) == None:
		parent = treemodel.get_value(treemodel.iter_parent(iter), 2)
	else:
		parent = 0
	if not treemodel.iter_next(iter) == None:
		sibling = treemodel.get_value(treemodel.iter_next(iter), 2)
	else:
		sibling = None
	libDenu.moveEntry(childId, parent, sibling)

def print_menu(widget):
	print libDenu.menu.toprettyxml()
	
xml.signal_autoconnect({
	'd_open' : d_open,
	'destroy' : destroy,
	'show_open_denu' : show_open_denu,
	'save_denu' : d_save,
	'show_save_denu' : show_save_denu,
	'print_menu' : print_menu
})
xml.get_widget("export_button").set_menu(xml.get_widget("export_menu"))
xml.get_widget("import_button").set_menu(xml.get_widget("import_menu"))
libDenu.update_wmConfig()
wms = libDenu.getInstalledWMs()
for wm in wms:
	import_button = gtk.MenuItem(libDenu.wmConfig[wm][1])
	xml.get_widget("import_menu").append(import_button)
	import_button.connect("activate", libDenu.wm_import, wm)
	import_button.show()
	export_button = gtk.MenuItem(libDenu.wmConfig[wm][1])
	xml.get_widget("export_menu").append(export_button)
	export_button.connect("activate", libDenu.wm_export, wm)
	export_button.show()
running = libDenu.getCurrentWM ()
libDenu.d_open("/home/scott/denu/svn/trunk/denu-3.x/installed.xml", "installed")
if len(running) == 1:
	libDenu.wm_import("", running[0])
	#libDenu.d_open("/home/scott/denu/svn/trunk/denu-3.x/test.xml")
	libDenu.buildIdChildRelations()
	menustore = domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)
menuview = xml.get_widget("menu")
tvcolumn = gtk.TreeViewColumn('Menu')
cell = gtk.CellRendererPixbuf()
text_render = gtk.CellRendererText()
tvcolumn.pack_start(cell, False)
tvcolumn.pack_start(text_render, True)
tvcolumn.set_attributes(cell, pixbuf=0)
tvcolumn.set_attributes(text_render, text=1)
menuview.append_column(tvcolumn)
menuview.set_model(menustore)

# Installed.
# Iconic view.
installed_icon_store = gtk.ListStore(gtk.gdk.Pixbuf, str, int)
installed_icon_store = domToListstore(installed_icon_store, libDenu.installed.firstChild, 48)
iconview = xml.get_widget("icon_installed")
iconview.set_model(installed_icon_store)
iconview.set_pixbuf_column(0)
iconview.set_text_column(1)

#TreeView
installedstore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
installedstore = domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config['pixbuf_size'], "installed")
installedview = xml.get_widget("installed")
tvcolumn2 = gtk.TreeViewColumn('Installed')
cell2 = gtk.CellRendererPixbuf()
text_render2 = gtk.CellRendererText()
tvcolumn2.pack_start(cell2, False)
tvcolumn2.pack_start(text_render2, True)
tvcolumn2.set_attributes(cell2, pixbuf=0)
tvcolumn2.set_attributes(text_render2, text=1)
installedview.append_column(tvcolumn2)
installedview.set_model(installedstore)
installedview.show()

# Non-glade connects.
menustore_connects.append(menustore.connect("row-changed", reorder))
#menustore.connect(
xml.get_widget("root").show()
gtk.main()
