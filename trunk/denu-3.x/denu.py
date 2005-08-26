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

import sys
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import xml.dom.minidom as xml_dom
import string,urllib2,os

home = os.environ['HOME']
denudir = home + '/.denu'
configfile = denudir + '/denu.conf' # FIXME: Use proper config file location

from DenuGUI_config import *

if not os.path.exists(denudir):
	os.makedirs(denudir)
	
if not os.path.exists(denudir + "/pixmaps"):
	os.makedirs(denudir + "/pixmaps")
	
def debugPrint(*args):
	if config.has_option('DEFAULT', 'debug') and config.getboolean('DEFAULT', 'debug'):
		sys.stderr.write("DEBUG: " + ' '.join(args) + "\n")

readConfig(configfile)
#setConfigDefaults()
sys.path.extend(["/usr/share/denu/wms", home + "/.denu/wms", config.get('DEFAULT', 'default'), config.get('DEFAULT', 'default') + "wms", config.get('DEFAULT', 'default') + "includes"])
debugPrint("Importing glade file.")

debugPrint("Loading denu libraries.")
#Denu imports.
import libDenu
from DenuGUI_common import *
import DenuGUI_save
import DenuGUI_open
import DenuGUI_add
import DenuGUI_view
import DenuGUI_edit
from DenuGUI_SharedVars import *
#DenuGUI_view.menuview = menuview
#DenuGUI_view.installedview = installedview

#if config.getboolean('debug'): print "Starting."
debugPrint("Starting.")

## denu.py Functions.
def populate_installed():
	installedstore.clear()
	DenuGUI_common.domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")

###############################
## libDenu.py api functions. ##
###############################
	
def update(widget):
	libDenu.update()
	libDenu.sysupdate()
	installedstore.clear()
	domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")
	return "Successful."
	
def update_installed(widget):
	libDenu.sysupdate()
	installedstore.clear()
	domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")
	return "Successful."
	
def update_db(widget):
	libDenu.update()
	return "Successful."
	
def destroy(widget, signal=""):
	gtk.main_quit()
	
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
	print libDenu.printMenu(libDenu.menu.firstChild)
	
def print_installed(widget):
	print libDenu.printMenu(libDenu.installed.firstChild)

def wm_import(widget, wm):
	libDenu.wm_import(wm)
	libDenu.buildIdChildRelations()
	global menustore
	menustore.clear()
	menustore = domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)

def wm_export(widget, wm):
	libDenu.wm_export(wm)

def deleteEntry(widget):
	iterList = []
	def createList(model, path, iter):
		iterList.append(iter)
	treeselection = menuview.get_selection()
	treeselection.selected_foreach(createList)
	for iter in iterList:
		id = menustore.get_value(iter, 2)
		libDenu.deleteEntry(id)
		menustore.remove(iter)
		
debugPrint("Connecting to gui.")
xml.signal_autoconnect({
	'destroy' : destroy,
	'show_open_denu' : DenuGUI_open.init,
	'show_save_denu' : DenuGUI_save.init,
	'print_menu' : print_menu,
	'show_add_new' : DenuGUI_add.init,
	'delete' : deleteEntry,
	'update' : update,
	'update_db' : update_db,
	'update_installed' : update_installed,
	'print_installed' : print_installed,
	'view_entry' : DenuGUI_view.init,
	'edit_entry' : DenuGUI_edit.init
})
debugPrint("Detecting WM(s).")
libDenu.update_wmConfig()
xml.get_widget("export_button").set_menu(xml.get_widget("export_menu"))
xml.get_widget("import_button").set_menu(xml.get_widget("import_menu"))
wms = libDenu.getInstalledWMs()
debugPrint("Detected WMs: " + ', '.join(wms))
for wm in wms:
	import_button = gtk.MenuItem(libDenu.wmConfig[wm][1])
	xml.get_widget("import_menu").append(import_button)
	import_button.connect("activate", wm_import, wm)
	import_button.show()
	export_button = gtk.MenuItem(libDenu.wmConfig[wm][1])
	xml.get_widget("export_menu").append(export_button)
	export_button.connect("activate", wm_export, wm)
	export_button.show()
running = libDenu.getCurrentWM ()
debugPrint("Opening installed.")
libDenu.d_open(config.get('DEFAULT', 'default') + "installed.xml", "installed")
debugPrint("Opening running menu.")
if len(running) == 1:
        debugPrint("Opening " + running[0] + " menu.")
	libDenu.wm_import(running[0])
	libDenu.buildIdChildRelations()
	menustore = domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)
tvcolumn = gtk.TreeViewColumn('Menu')
cell = gtk.CellRendererPixbuf()
text_render = gtk.CellRendererText()
tvcolumn.pack_start(cell, False)
tvcolumn.pack_start(text_render, True)
tvcolumn.set_attributes(cell, pixbuf=0)
tvcolumn.set_attributes(text_render, text=1)
menuview.append_column(tvcolumn)
menuview.set_model(menustore)
menuview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
menuview.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT)
menuview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
menuview.connect("drag-data-received", drag_data_received_data)
menuview.connect("drag_data_get", drag_data_get_data)

#TreeView
debugPrint("Generating installed tree.")
domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")
tvcolumn2 = gtk.TreeViewColumn('Installed')
cell2 = gtk.CellRendererPixbuf()
text_render2 = gtk.CellRendererText()
tvcolumn2.pack_start(cell2, False)
tvcolumn2.pack_start(text_render2, True)
tvcolumn2.set_attributes(cell2, pixbuf=0)
tvcolumn2.set_attributes(text_render2, text=1)
installedview.append_column(tvcolumn2)
installedview.set_model(installedstore)
installedview.connect("drag_data_get", drag_data_get_data)
installedview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
installedview.show()
xml.get_widget("root").show()
debugPrint("Done.")

def main():
    gtk.main()

if __name__ == "__main__":
    main()
    
debugPrint("Dumping config.")
writeConfig(configfile)
if config.has_option('DEFAULT', 'debug') and config.getboolean('DEFAULT', 'debug'):
	debugPrint("Config is:")
	debugPrint("---BEGIN---")
	config.write(sys.stderr)
	debugPrint("--- END ---")
