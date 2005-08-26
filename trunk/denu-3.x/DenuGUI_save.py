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
import libDenu
from DenuGUI_config import config
from DenuGUI_common import *

def init(widget):
	global xml
	xml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/save.glade')
	window = xml.get_widget("save_denu")
	xml.signal_autoconnect({
	#'destroy' : destroy,
	'save_denu' : d_save
	})
	window.show()
	
def d_save(widget):
	global xml
	window = xml.get_widget("save_denu")
	filename = window.get_filename()
	if not filename[-4:] == ".xml":
		filename = filename + ".xml"
	libDenu.d_save(str(filename))
	window.destroy()
