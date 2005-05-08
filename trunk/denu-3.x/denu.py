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
menustore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)

## denu.py Functions.
def populate_installed():
	installedstore.clear()
	domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config['pixbuf_size'], "installed")

def pixbuf_manager(filename, size):
	global pixbuf_index
    	okay = 'yes'
    	if filename.has_key("file"):
    		if os.path.exists(filename["file"]):
    			filename = filename["file"]
    		elif filename.has_key("url"):
    			filename = filename["url"]
    		else:
    			filename = filename["file"]
    	elif filename.has_key("url"):
    		filename = filename["url"]
    		
    	if pixbuf_index.has_key(filename):
    		file_key = "yes"
    		if pixbuf_index[filename].has_key(size):
    			size_key = "yes"
    		else:
    			size_key = "no"
    	else:
    		file_key = "no"
    		size_key = "no"
    		
    	if not filename[0:1]=='/' and not filename[:7]=='http://' and not size_key=="yes":
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
	elif filename[:7]=='http://' and not os.path.exists(home + '/.denu/pixmaps/www/' + string.split(filename, "/")[-1]) and not size_key=="yes":
		full_filename = home + '/.denu/pixmaps/www/' + string.split(filename, "/")[-1]
		try:
			image = urllib2.urlopen(filename)
			okay = 'yes'
		except:
			pixbuf_index[filename] = "Error: no file."
			return "Error: no file."
			okay = 'no'
		if okay=='yes':
			file = open(full_filename, 'w')
			file.write(image.read())
			file.close()
	elif os.path.exists(home + '/.denu/pixmaps/www/' + string.split(filename, "/")[-1]) and not size_key=="yes":
		full_filename = home + '/.denu/pixmaps/www/' + string.split(filename, "/")[-1]
	else:
		full_filename = filename
		
	if okay=='yes' and size_key=="no":
		if file_key == "no":
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
			if len(child.getElementsByTagName("icon")) >= 1 and child.getElementsByTagName("icon")[0].parentNode == child:
				icon = {}
				if len(child.getElementsByTagName("icon")[0].getElementsByTagName("url")) == 1:
					icon['url'] = string.strip(child.getElementsByTagName("icon")[0].getElementsByTagName("url")[0].firstChild.nodeValue)
				if len(child.getElementsByTagName("icon")[0].getElementsByTagName("file")) == 1:
					icon['file'] = string.strip(child.getElementsByTagName("icon")[0].getElementsByTagName("file")[0].firstChild.nodeValue)
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

###############################
## libDenu.py api functions. ##
###############################
def d_open(widget):
	global menustore
	window = xml.get_widget("open_denu")
	filename = window.get_filename()
	libDenu.d_open(filename)
	window.hide()
	libDenu.buildIdChildRelations()
	menustore.clear()
	domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)

def d_save(widget):
	window = xml.get_widget("save_denu")
	filename = window.get_filename()
	if not filename[-4:] == ".xml":
		filename = filename + ".xml"
	libDenu.d_save(str(filename))
	window.hide()
	
def update(widget):
	libDenu.update()
	libDenu.sysupdate()
	installedstore.clear()
	domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config['pixbuf_size'], "installed")
	return "Successful."
	
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
	print libDenu.printMenu(libDenu.menu.firstChild)
	
def show_add_new (widget):
	xml.get_widget("add_window").show()

def wm_import(widget, wm):
	libDenu.wm_import(wm)

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

##################
## DND Functions #
##################
def drag_data_get_data(treeview, context, selection, target_id, etime):
	treeselection = treeview.get_selection()
	model = treeview.get_model()
	iterList = []
	def createList(model, path, iter):
		iterList.append([iter, path])
	treeselection.selected_foreach(createList)
	data = model.get_value(iterList[0][0], 2)
	if treeview == menuview:
		source = "menu"
	elif treeview == installedview:
		source = "installed"
	selection.set(selection.target, 8, "internal>" + source + "|" + str(data))
	global src_iter
	src_iter = iterList[0][0]
	return
   
def drag_data_received_data(treeview, context, x, y, selection, info, etime):
	model = treeview.get_model()
	data = selection.data
	global src_iter
	temp_dict = {}
	if data[:4]=="http":
		data = string.split(data, "?")
		data[1] = string.split(data[1], "&")
		for row in data[1]:
			key, content = string.split(row, "=")
			content = string.replace(content, "%20", " ")
			if not string.find(key, ".") == -1:
				location = string.split(key, ".")
				dict_key = ""
				tmp = temp_dict
				for place in location:
					if not tmp.has_key(place):
						tmp[place] = {}
					tmp = tmp[place]
					dict_key += "[\"" + place + "\"]"
				exec "temp_dict" + dict_key + " = content"
			else:
				temp_dict[key] = content
		entry = {}
		root = temp_dict["root"]
		del temp_dict["root"]
		entry[root] = temp_dict
		entry[root]["URL"] = data[0]
		drop_info = treeview.get_dest_row_at_pos(x, y)
		if drop_info:
			path, position = drop_info
			iter = model.get_iter(path)
			if position == gtk.TREE_VIEW_DROP_BEFORE:
				if not model.iter_parent(iter) == None:
					parent = model.get_value(model.iter_parent(iter), 2)
				else:
					parent = 0
				sibling = model.get_value(iter, 2)
			elif position == gtk.TREE_VIEW_DROP_AFTER:
				if not model.iter_parent(iter) == None:
					parent = model.get_value(model.iter_parent(iter), 2)
				else:
					parent = 0
				sibling = model.get_value(model.iter_next(iter), 2)
			elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
				parent = model.get_value(iter, 2)
				sibling = None
			id = libDenu.addEntry(entry, parent, sibling)[0]
			if entry[entry.keys()[0]]['name'].has_key(config['locale']):
				name = entry[entry.keys()[0]]['name'][config['locale']]
			else:
				name = entry[entry.keys()[0]]['name']["en"]
			if position == gtk.TREE_VIEW_DROP_BEFORE:
				parent_iter = model.iter_parent(iter)
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
						model.insert_before(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
					else:
						model.insert_before(parent_iter, iter, [None, name, id])
				else:
					model.insert_before(parent_iter, iter, [None, name, id])
			elif position == gtk.TREE_VIEW_DROP_AFTER:
				parent_iter = model.iter_parent(iter)
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
						model.insert_after(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
					else:
						model.insert_after(parent_iter, iter, [None, name, id])
				else:
					model.insert_after(parent_iter, iter, [None, name, id])
			elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
						model.append(iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
					else:
						model.append(iter, [None, name, id])
				else:
					model.append(iter, [None, name, id])
	elif data[:9] == "internal>":
		path, position = treeview.get_dest_row_at_pos(x, y)
		data = string.replace(data, "internal>", "")
		data = string.split(data, "|")
		iter = model.get_iter(path)
		if position == gtk.TREE_VIEW_DROP_BEFORE:
			if not model.iter_parent(iter) == None:
				parent = model.get_value(model.iter_parent(iter), 2)
			else:
				parent = 0
			sibling = model.get_value(iter, 2)
		elif position == gtk.TREE_VIEW_DROP_AFTER:
			if not model.iter_parent(iter) == None:
				parent = model.get_value(model.iter_parent(iter), 2)
			else:
				parent = 0
			sibling = model.get_value(model.iter_next(iter), 2)
		elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
			parent = model.get_value(iter, 2)
			sibling = None
		if model==menustore:
			dest = "menu"
		elif model==installedstore:
			dest = "installed"
		id = libDenu.moveEntry(data[1], parent, sibling, data[0], dest)
		entry = libDenu.viewEntry(id, dest)
		if entry[entry.keys()[0]]['name'].has_key(config['locale']):
			name = entry[entry.keys()[0]]['name'][config['locale']]
		else:
			name = entry[entry.keys()[0]]['name']["en"]
		if position == gtk.TREE_VIEW_DROP_BEFORE:
			parent_iter = model.iter_parent(iter)
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
					new_iter = model.insert_before(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
				else:
					new_iter = model.insert_before(parent_iter, iter, [None, name, id])
			else:
				new_iter = model.insert_before(parent_iter, iter, [None, name, id])
		elif position == gtk.TREE_VIEW_DROP_AFTER:
			parent_iter = model.iter_parent(iter)
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
					new_iter = model.insert_after(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
				else:
					new_iter = model.insert_after(parent_iter, iter, [None, name, id])
			else:
				new_iter = model.insert_after(parent_iter, iter, [None, name, id])
		elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']) == "Error: no file.":
					new_iter = model.append(iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config['pixbuf_size']), name, id])
				else:
					new_iter = model.append(iter, [None, name, id])
			else:
				new_iter = model.append(iter, [None, name, id])
		if data[0] == "menu":
			if menustore.iter_has_child(src_iter):
				copy_rows(new_iter, src_iter, menustore, model)
		elif data[0] == "installed":
			if installedstore.iter_has_child(src_iter):
				copy_rows(new_iter, src_iter, installedstore, model)
		if data[0] == "menu":
			menustore.remove(src_iter)
			
def copy_rows(parent_iter, src_iter, srcmodel, destmodel):
	iter = srcmodel.iter_children(src_iter)
	while iter != None:
		icon, name, id = srcmodel.get(iter, 0, 1, 2)
		parent = destmodel.append(parent_iter, [icon, name, id])
		if srcmodel.iter_has_child(iter):
			copy_rows(parent, iter, srcmodel, destmodel)
		iter = srcmodel.iter_next(iter)
xml.signal_autoconnect({
	'd_open' : d_open,
	'destroy' : destroy,
	'show_open_denu' : show_open_denu,
	'save_denu' : d_save,
	'show_save_denu' : show_save_denu,
	'print_menu' : print_menu,
	'show_add_new' : show_add_new,
	'delete' : deleteEntry,
	'update' : update
})

libDenu.update_wmConfig()
xml.get_widget("export_button").set_menu(xml.get_widget("export_menu"))
xml.get_widget("import_button").set_menu(xml.get_widget("import_menu"))
wms = libDenu.getInstalledWMs()
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
libDenu.d_open("/home/scott/denu/svn/trunk/denu-3.x/installed.xml", "installed")
if len(running) == 1:
	libDenu.wm_import(running[0])
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
menuview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
menuview.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT)
menuview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
menuview.connect("drag-data-received", drag_data_received_data)
menuview.connect("drag_data_get", drag_data_get_data)

#TreeView
installedstore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config['pixbuf_size'], "installed")
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
installedview.connect("drag_data_get", drag_data_get_data)
installedview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
installedview.show()

xml.get_widget("root").show()
gtk.main()
