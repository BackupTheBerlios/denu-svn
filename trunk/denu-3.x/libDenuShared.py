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

# This is the start of libDenu 3.x
# It is released under the GPLv2

def DOMtoDict (dict, entry, location):
	for child in entry.childNodes:
		print child.nodeName
		if not child.nodeName == "#text":
			location.append(child.nodeName)
			DOMtoDict (dict, child, location)
			location.pop()
		elif not child.nodeValue.strip() == "":
			variable = "dict"
			for place in location:
				exec "result = " + variable + ".has_key(place)"
				if not result:
					exec variable + "[place] = {}"
				variable += "['" + place + "']"
			exec variable + " = child.nodeValue"
			
def buildDOM(dict, element, root):
	type = ""
	for key in dict.keys():
		tmp = root.createElement(key)
		element.appendChild(tmp)
		try:
			dict[key].keys()
		except:
			type = "string"
		if type=="string":
			strng = root.createTextNode(dict[key])
			tmp.appendChild(strng)
		else:
			buildDOM(dict[key], tmp, root)
		type = ''
	return tmp
