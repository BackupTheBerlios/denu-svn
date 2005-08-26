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
import DenuGUI_common
import libDenu
from DenuGUI_SharedVars import *
from DenuGUI_common import *

def init(widget):
	global xml
	xml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/open.glade')
	xml.signal_autoconnect({
	#'destroy' : destroy,
	'd_open' : d_open
	})
	xml.get_widget("open_denu").show()
	
def d_open(widget):
	global menustore
	global xml
	window = xml.get_widget("open_denu")
	filename = window.get_filename()
	libDenu.d_open(filename)
	window.hide()
	libDenu.buildIdChildRelations()
	menustore.clear()
	DenuGUI_common.domToTreestore(libDenu.menu, menustore, libDenu.menu.firstChild)
