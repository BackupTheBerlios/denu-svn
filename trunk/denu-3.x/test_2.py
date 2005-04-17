#!/usr/bin/env python
#Denu test 2
#Test generating a dict object which corresponds numeric ids to nodes of the xml menu.
import libDenu
libDenu.d_open("mockup.xml")
libDenu.buildIdChildRelations()
libDenu.printIdIndex()
print libDenu.idIndex[3].firstChild.nodeValue
