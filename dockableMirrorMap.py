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

from mirrorMap import MirrorMap

class DockableMirrorMap(QDockWidget):

	TITLE = "MirrorMap"

	def __init__(self, parent, iface):
		QDockWidget.__init__(self, parent)

		self.mainWidget = MirrorMap(self, iface)
		self.location = Qt.RightDockWidgetArea
		self.number = -1

		self.setupUi()
		self.connect(self, SIGNAL("dockLocationChanged(Qt::DockWidgetArea)"), self.setLocation)

	def closeEvent(self, event):
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QDockWidget.closeEvent(self, event)

	def setNumber(self, n=-1):
		self.number = n
		self.updateLabel()

	def getMirror(self):
		return self.mainWidget

	def getLocation(self):
		return self.location

	def setLocation(self, location):
		self.location = location

	def setupUi(self):
		self.setObjectName( "dockablemirrormap_dockwidget" )
		self.updateLabel()
		self.setWidget(self.mainWidget)

	def updateLabel(self):
		title = "%s #%s" % (self.TITLE, self.number) if self.number >= 0 else self.TITLE
		if len(self.mainWidget.label) != 0:
			title += ": " + self.mainWidget.label
		self.setWindowTitle( title )

