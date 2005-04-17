#!/usr/bin/env python
#Denu test 2
#Test adding, moving and deleting an element.

#Initial
import libDenu,xml.dom.minidom
menu = libDenu.d_open("mockup.xml")
libDenu.buildIdChildRelations()
#libDenu.printIdIndex()

#Add entry.
entry = {"program" : {"name": {"en" : "Denu"}, "command" : "denu-ng", "icon" : "denu.png"}}
addedId = libDenu.addEntry(entry, 0, 2)
print libDenu.menu.toxml()

#Move entry
libDenu.moveEntry(addedId[0], 0)
print libDenu.menu.toxml()

#Delete entry
libDenu.deleteEntry(addedId[0])
print libDenu.menu.toxml()
