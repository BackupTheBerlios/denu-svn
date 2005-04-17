#!/usr/bin/env python
#Denu test 1
#Test generating a nested view of the menu.

import libDenu
print "You are running:"
for wm in libDenu.getCurrentWM():
	print "\t\t" + wm
menu = libDenu.d_open("mockup.xml")
tab = "  "
root = menu.firstChild
libDenu.printMenu(root)
