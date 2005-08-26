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

from DenuGUI_config import config
import string
import libDenu
import os
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
from DenuGUI_SharedVars import *
home = os.environ['HOME']
denudir = home + '/.denu'

pixbuf_index = {}

def destroy(widget):
	widget.get_parent_window().destroy()
	
def copy_rows(parent_iter, src_iter, srcmodel, destmodel):
	iter = srcmodel.iter_children(src_iter)
	while iter != None:
		icon, name, id = srcmodel.get(iter, 0, 1, 2)
		parent = destmodel.append(parent_iter, [icon, name, id])
		if srcmodel.iter_has_child(iter):
			copy_rows(parent, iter, srcmodel, destmodel)
		iter = srcmodel.iter_next(iter)
	
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
		if not treeview.get_dest_row_at_pos(x, y)==None:
			path, position = treeview.get_dest_row_at_pos(x, y)
		else:
			path = last_visible(None, model, treeview)
			position = gtk.TREE_VIEW_DROP_AFTER	
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
			if not model.iter_next(iter) == None:
				sibling = model.get_value(model.iter_next(iter), 2)
			else:
				sibling = None
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
				if not DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')) == "Error: no file.":
					model.insert_before(parent_iter, iter, [DenuGUI_common.pixbuf_manager(entry[entry.keys()[0]]['icon'], config.getint('DEFAULT', 'pixbuf_size')), name, id])
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
		if not int(data[1]) == sibling and not int(data[1]) == parent:
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
