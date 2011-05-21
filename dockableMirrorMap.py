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
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.mainWidget = MirrorMap(self, iface)
		self.setupUi()

	def closeEvent(self, event):
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QDockWidget.closeEvent(self, event)

	def setNumber(self, n=-1):
		title = "%s #%s" % (self.TITLE, n) if n >= 0 else self.TITLE
		self.setWindowTitle( title )

	def setupUi(self):
		self.setObjectName( "dockablemirrormap_dockwidget" )
		self.setNumber()
		self.setWidget(self.mainWidget)

