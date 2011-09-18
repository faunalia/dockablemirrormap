# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Dockable MirrorMap
Description          : Creates a dockable map canvas
Date                 : February 1, 2011 
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def name():
	return "Dockable MirrorMap"

def description():
	return "Creates a dockable map canvas synchronized with the main one"

def version():
	return "0.1.0"

def qgisMinimumVersion():
	return "1.5.0"

def icon():
	return "icons/dockablemirrormap.png"

def authorName():
	return "Giuseppe Sucameli (Faunalia)"

def classFactory(iface):
	from dockableMirrorMapPlugin import DockableMirrorMapPlugin
	return DockableMirrorMapPlugin(iface)

