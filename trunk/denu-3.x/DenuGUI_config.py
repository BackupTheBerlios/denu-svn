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
from ConfigParser import SafeConfigParser
import sys,os

home = os.environ['HOME']

global config
config = SafeConfigParser()

def debugPrint(*args):
	if config.has_option('DEFAULT', 'debug') and config.getboolean('DEFAULT', 'debug'):
		sys.stderr.write("DEBUG: " + ' '.join(args) + "\n")
		
def readConfig(configfile):
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

def writeConfig(configfile):
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
