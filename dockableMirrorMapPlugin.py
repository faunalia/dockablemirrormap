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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import resources_rc

class DockableMirrorMapPlugin:

	def __init__(self, iface):
		# Save a reference to the QGIS iface
		self.iface = iface
		
	def initGui(self):
		self.dockableMirrors = []
		self.lastDockableMirror = 0
		self.dockableAction = QAction(QIcon(":/icons/dockablemirrormap.png"), "Dockable MirrorMap", self.iface.mainWindow())
		QObject.connect(self.dockableAction, SIGNAL("triggered()"), self.runDockableMirror)

		self.aboutAction = QAction("About", self.iface.mainWindow())
		QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)


		# Add to the plugin menu and toolbar
		self.iface.addPluginToMenu("Dockable MirrorMap", self.dockableAction)
		self.iface.addPluginToMenu("Dockable MirrorMap", self.aboutAction)
		self.iface.addToolBarIcon(self.dockableAction)

	def unload(self):
		self.removeDockableMirrors()

		# Remove the plugin
		self.iface.removePluginMenu("Dockable MirrorMap",self.dockableAction)
		self.iface.removePluginMenu("Dockable MirrorMap",self.aboutAction)
		self.iface.removeToolBarIcon(self.dockableAction)

	def about(self):
		from DlgAbout import DlgAbout
		DlgAbout(self.iface.mainWindow()).exec_()


	def removeDockableMirrors(self):
		for d in list(self.dockableMirrors):
			d.close()

	def runDockableMirror(self):
		from dockableMirrorMap import DockableMirrorMap
		wdg = DockableMirrorMap(self.iface.mainWindow(), self.iface)

		othersize = QGridLayout().verticalSpacing()
		minsize = wdg.minimumSize()
		maxsize = wdg.maximumSize()

		if len(self.dockableMirrors) <= 0:
			width = self.iface.mapCanvas().size().width()/2 - othersize
			position = Qt.RightDockWidgetArea
			wdg.setMinimumWidth( width )
			wdg.setMaximumWidth( width )

		elif len(self.dockableMirrors) == 1:
			height = self.dockableMirrors[0].size().height()/2 - othersize/2
			position = Qt.RightDockWidgetArea
			wdg.setMinimumHeight( height )
			wdg.setMaximumHeight( height )

		elif len(self.dockableMirrors) == 2:
			height = self.iface.mapCanvas().size().height()/2 - othersize/2
			position = Qt.BottomDockWidgetArea
			wdg.setMinimumHeight( height )
			wdg.setMaximumHeight( height )

		else:
			position = Qt.BottomDockWidgetArea
			wdg.setFloating( True )

		self.addDockWidget(position, wdg)
		wdg.setMinimumSize(minsize)
		wdg.setMaximumSize(maxsize)

		if wdg.isFloating():
			wdg.move(50, 50)	# move the widget to the center


	def addDockWidget(self, position, wdg):
		mapCanvas = self.iface.mapCanvas()
		oldSize = mapCanvas.size()

		self.iface.mapCanvas().setRenderFlag(False)
		self.iface.addDockWidget(position, wdg)

		wdg.setNumber( self.lastDockableMirror )
		self.lastDockableMirror = self.lastDockableMirror+1
		self.dockableMirrors.append( wdg )

		QObject.connect(wdg, SIGNAL( "closed(PyQt_PyObject)" ), self.onCloseDockableMirror)

		newSize = mapCanvas.size()
		if newSize != oldSize:
			# trick: update the canvas size
			mapCanvas.resize(newSize.width() - 1, newSize.height())
			mapCanvas.setRenderFlag(True)
			mapCanvas.resize(newSize)
		else:
			mapCanvas.setRenderFlag(True)


	def onCloseDockableMirror(self, wdg):
		if self.dockableMirrors.count( wdg ) > 0:
			self.dockableMirrors.remove( wdg )

