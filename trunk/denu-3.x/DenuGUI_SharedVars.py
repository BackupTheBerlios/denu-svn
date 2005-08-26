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
import gtk
import gtk.glade
from DenuGUI_config import *
xml = gtk.glade.XML(config.get('DEFAULT', 'default') + 'glade/main.glade')
menuview = xml.get_widget("menu")
installedview = xml.get_widget("installed")
menustore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
installedstore = gtk.TreeStore(gtk.gdk.Pixbuf, str, int)
