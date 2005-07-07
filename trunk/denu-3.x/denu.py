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

from ConfigParser import SafeConfigParser
import sys
import pygtk
pygtk.require('2.0')
import gtk,libDenu
import gtk.glade
import xml.dom.minidom as xml_dom
import string,urllib2,os

home = os.environ['HOME']
denudir = home + '/.denu'
configfile = denudir + '/denu.conf' # FIXME: Use proper config file location
config = SafeConfigParser()

if not os.path.exists(denudir):
	os.makedirs(denudir)
	
if not os.path.exists(denudir + "/pixmaps"):
	os.makedirs(denudir + "/pixmaps")
	
def debugPrint(*args):
	if config.has_option('DEFAULT', 'debug') and config.getboolean('DEFAULT', 'debug'):
		sys.stderr.write("DEBUG: " + ' '.join(args) + "\n")

def readConfig():
	try:
		config.read(configfile)
		debugPrint("Read config file successfully")
	except:
		debugPrint("Unable to read config file!")

def setConfigDefaults(): # Put default configuration options here.
	if not config.has_option('DEFAULT', 'debug'):       config.set('DEFAULT', 'debug', 'true')
	#if not config.has_option('DEFAULT', 'default'):     config.set('DEFAULT', 'default', home + "/denu/svn/trunk/denu-3.x/")
	if not config.has_option('DEFAULT', 'default'):     config.set('DEFAULT', 'default', os.getcwd() + "/")
	if not config.has_option('DEFAULT', 'locale'):      config.set('DEFAULT', 'locale', 'en')
	if not config.has_option('DEFAULT', 'pixbuf_size'): config.set('DEFAULT', 'pixbuf_size', '32')

def writeConfig():
	try:
		cfp = open(configfile, "w")
		config.write(cfp)
		cfp.close()
		debugPrint("Wrote config file successfully.")
	except:
		debugPrint("Unable to write config file!")
		
def updateConfig():
	pass

def showConfig():
	pass
	
readConfig()
setConfigDefaults()
#if config.getboolean('debug'): print "Starting."
debugPrint("Starting.")
debugPrint("Loading libraries.")
debugPrint("Importing glade file.")
xml = gtk.glade.XML(config.get('DEFAULT', 'default') + '/denu/denu.glade')
pixbuf_index = {}
menustore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)

## denu.py Functions.
def populate_installed():
	installedstore.clear()
	domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")

def pixbuf_manager(filename, size=config.getint('DEFAULT', 'pixbuf_size')):
	global pixbuf_index
    	okay = True
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
    		file_key = True
    		if pixbuf_index[filename].has_key(size):
    			size_key = True
    		else:
    			size_key = False
    	else:
    		file_key = False
    		size_key = False
    		
    	if not filename[0:1]=='/' and not filename[:7]=='http://' and not size_key:
    		full_filename = denudir + '/pixmaps/' + filename
        	if not os.path.exists(full_filename):
       			try:
				image = urllib2.urlopen('http://denu.sourceforge.net/pixmaps/' + filename)
				okay = True
			except:
				pixbuf_index[filename] = "Error: no file."
				return "Error: no file."
				okay = False
			if okay:
				file = open(full_filename, 'w')
				file.write(image.read())
				file.close()
	elif filename[:7]=='http://' and not os.path.exists(denudir + '/pixmaps/www/' + string.split(filename, "/")[-1]) and not size_key:
		full_filename = denudir + '/pixmaps/www/' + string.split(filename, "/")[-1]
		try:
			image = urllib2.urlopen(filename)
			okay = True
		except:
			pixbuf_index[filename] = "Error: no file."
			return "Error: no file."
			okay = False
		if okay:
			file = open(full_filename, 'w')
			file.write(image.read())
			file.close()
	elif os.path.exists(denudir + '/pixmaps/www/' + string.split(filename, "/")[-1]) and not size_key:
		full_filename = denudir + '/pixmaps/www/' + string.split(filename, "/")[-1]
	else:
		full_filename = filename
		
	if okay and not size_key:
		if file_key == False:
			pixbuf_index[filename] = {}
        	try:
        		pixbuf_index[filename][size] = gtk.gdk.pixbuf_new_from_file_at_size(full_filename, size, size)
        	except:
        		return "Error: no file."
        		
        if not pixbuf_index[filename] == "Error: no file.":
       		return pixbuf_index[filename][size]
       	else:
       		return pixbuf_index[filename]
       	
def domToTreestore(menu_dom, treestore, parent, location=None, size=config.getint('DEFAULT', 'pixbuf_size'), type="menu"):
	for child in parent.childNodes:
		if child.nodeName == "folder" or child.nodeName == "program" or child.nodeName == "special":
			name = string.strip(child.getElementsByTagName("name")[0].getElementsByTagName(config.get('DEFAULT', 'locale'))[0].firstChild.nodeValue)
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
	
def dictToTreestore(dict, model, parent=None):
	type = ""
	for key in dict.keys():
		try:
			dict[key].keys()
		except:
			type = "string"
		if type=="string":
			model.append(parent, [key, dict[key]])
		else:
			tmp = model.append(parent, [key, ""])
			dictToTreestore(dict[key], model, tmp)
		type = ''

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
	
def print_installed(widget):
	print libDenu.printMenu(libDenu.installed.firstChild)
	
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
		
def addEntry (widget):
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
			if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
				menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
			else:
				menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [None, name, id])
		else:
			menustore.insert_before(menustore.iter_parent(iterList[0]), iterList[0], [None, name, id])
	else:
		parent = 0
		id = libDenu.addEntry(entry, parent)[0]
		if entry[entry.keys()[0]].has_key('icon'):
			if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
				menustore.append(None, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
			else:
				menustore.append(None, [None, name, id])
		else:
			menustore.append(None, [None, name, id])
	xml.get_widget("add_window").hide()
	
def cancel_add(widget):
	xml.get_widget("add_window").hide()
	
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
	
def view_entry(widget):
	viewxml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'denu/denu.glade', 'view_window')
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
	viewxml.get_widget("view_window").show()
	
def edit_entry_start (widget):
	window = xml.get_widget("save_denu")

def edit_entry_end (widget):
	pass
	
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
	
def last_visible (parent, model, treeview):
	last_iter = model.iter_nth_child(parent, model.iter_n_children(parent)-1)
	path = model.get_path(last_iter)
	if model.iter_has_child(last_iter):
		if treeview.row_expanded(path):
			path = last_visible(last_iter, model, treeview)
	return path
   
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
			if entry[entry.keys()[0]]['name'].has_key(config.get('DEFAULT', 'locale')):
				name = entry[entry.keys()[0]]['name'][config.get('DEFAULT', 'locale')]
			else:
				name = entry[entry.keys()[0]]['name']["en"]
			if position == gtk.TREE_VIEW_DROP_BEFORE:
				parent_iter = model.iter_parent(iter)
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
						model.insert_before(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
					else:
						model.insert_before(parent_iter, iter, [None, name, id])
				else:
					model.insert_before(parent_iter, iter, [None, name, id])
			elif position == gtk.TREE_VIEW_DROP_AFTER:
				parent_iter = model.iter_parent(iter)
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
						model.insert_after(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
					else:
						model.insert_after(parent_iter, iter, [None, name, id])
				else:
					model.insert_after(parent_iter, iter, [None, name, id])
			elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
				if entry[entry.keys()[0]].has_key('icon'):
					if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
						model.append(iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
					else:
						model.append(iter, [None, name, id])
				else:
					model.append(iter, [None, name, id])
	elif data[:9] == "internal>":
		if not treeview.get_dest_row_at_pos(x, y)==None:
			path, position = treeview.get_dest_row_at_pos(x, y)
		else:
			path = last_visible(None, model, treeview)
			position = gtk.TREE_VIEW_DROP_AFTER				
		data = string.replace(data, "internal>", "")
		data = string.split(data, "|")
		iter = model.get_iter(path)
		if src_iter==iter:
			pass
		elif position == gtk.TREE_VIEW_DROP_BEFORE:
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
			if not model.iter_next(iter) == None:
				sibling = model.get_value(model.iter_next(iter), 2)
			else:
				sibling = None
		elif position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE:
			parent = model.get_value(iter, 2)
			sibling = None
		if model==menustore:
			dest = "menu"
		elif model==installedstore:
			dest = "installed"
		if not int(data[1]) == sibling and int(data[1]) != parent:
			id = libDenu.moveEntry(data[1], parent, sibling, data[0], dest)
			entry = libDenu.viewEntry(id, dest)
			if entry[entry.keys()[0]]['name'].has_key(config.get('DEFAULT', 'locale')):
				name = entry[entry.keys()[0]]['name'][config.get('DEFAULT', 'locale')]
			else:
				name = entry[entry.keys()[0]]['name']["en"]
		if position == gtk.TREE_VIEW_DROP_BEFORE and int(data[1]) != parent and int(data[1]) != sibling:
			parent_iter = model.iter_parent(iter)
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
					new_iter = model.insert_before(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
				else:
					new_iter = model.insert_before(parent_iter, iter, [None, name, id])
			else:
				new_iter = model.insert_before(parent_iter, iter, [None, name, id])
		elif position == gtk.TREE_VIEW_DROP_AFTER and int(data[1]) != parent and int(data[1]) != sibling:
			parent_iter = model.iter_parent(iter)
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
					new_iter = model.insert_after(parent_iter, iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
				else:
					new_iter = model.insert_after(parent_iter, iter, [None, name, id])
			else:
				new_iter = model.insert_after(parent_iter, iter, [None, name, id])
		elif (position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) and int(data[1]) != parent and int(data[1]) != sibling:
			if entry[entry.keys()[0]].has_key('icon'):
				if not pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
					new_iter = model.append(iter, [pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
				else:
					new_iter = model.append(iter, [None, name, id])
			else:
				new_iter = model.append(iter, [None, name, id])
		if int(data[1]) != sibling and int(data[1]) != parent:
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
		
debugPrint("Connecting to gui.")
xml.signal_autoconnect({
	'd_open' : d_open,
	'destroy' : destroy,
	'show_open_denu' : show_open_denu,
	'save_denu' : d_save,
	'show_save_denu' : show_save_denu,
	'print_menu' : print_menu,
	'show_add_new' : show_add_new,
	'delete' : deleteEntry,
	'update' : update,
	'update_db' : update_db,
	'update_installed' : update_installed,
	'print_installed' : print_installed,
	'add_entry' : addEntry,
	'cancel_add' : cancel_add,
	'change_add_state' : change_add_state,
	'view_entry' : view_entry
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
debugPrint("Generating installed tree.")
installedstore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
domToTreestore(libDenu.installed, installedstore, libDenu.installed.firstChild, None, config.getint('DEFAULT', 'pixbuf_size'), "installed")
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
debugPrint("Done.")
gtk.main()
debugPrint("Dumping config.")
writeConfig()
if config.has_option('DEFAULT', 'debug') and config.getboolean('DEFAULT', 'debug'):
	debugPrint("Config is:")
	debugPrint("---BEGIN---")
	config.write(sys.stderr)
	debugPrint("--- END ---")
