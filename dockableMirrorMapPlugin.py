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
		self.dockableAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/dockablemirrormap.png"), "Dockable MirrorMap", self.iface.mainWindow())
		QObject.connect(self.dockableAction, SIGNAL("triggered()"), self.runDockableMirror)

		self.aboutAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/about.png"), "About", self.iface.mainWindow())
		QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)


		# Add to the plugin menu and toolbar
		self.iface.addPluginToMenu("Dockable MirrorMap", self.dockableAction)
		self.iface.addPluginToMenu("Dockable MirrorMap", self.aboutAction)
		self.iface.addToolBarIcon(self.dockableAction)

		QObject.connect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
		QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)
	
	def unload(self):
		QObject.disconnect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
		QObject.disconnect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)

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
			self.iface.removeDockWidget(d)
		self.dockableMirrors = []
		self.lastDockableMirror = 0

	def runDockableMirror(self):
		from dockableMirrorMap import DockableMirrorMap
		wdg = DockableMirrorMap(self.iface.mainWindow(), self.iface)

		minsize = wdg.minimumSize()
		maxsize = wdg.maximumSize()

		self.setupDockWidget(wdg)		
		self.addDockWidget(wdg)

		wdg.setMinimumSize(minsize)
		wdg.setMaximumSize(maxsize)

		if wdg.isFloating():
			wdg.move(50, 50)	# move the widget to the center

	def setupDockWidget(self, wdg):
		othersize = QGridLayout().verticalSpacing()

		if len(self.dockableMirrors) <= 0:
			width = self.iface.mapCanvas().size().width()/2 - othersize
			wdg.setLocation( Qt.RightDockWidgetArea )
			wdg.setMinimumWidth( width )
			wdg.setMaximumWidth( width )

		elif len(self.dockableMirrors) == 1:
			height = self.dockableMirrors[0].size().height()/2 - othersize/2
			wdg.setLocation( Qt.RightDockWidgetArea )
			wdg.setMinimumHeight( height )
			wdg.setMaximumHeight( height )

		elif len(self.dockableMirrors) == 2:
			height = self.iface.mapCanvas().size().height()/2 - othersize/2
			wdg.setLocation( Qt.BottomDockWidgetArea )
			wdg.setMinimumHeight( height )
			wdg.setMaximumHeight( height )

		else:
			wdg.setLocation( Qt.BottomDockWidgetArea )
			wdg.setFloating( True )


	def addDockWidget(self, wdg, position=None):
		if position == None:
			position = wdg.getLocation()
		else:
			wdg.setLocation( position )

		mapCanvas = self.iface.mapCanvas()
		oldSize = mapCanvas.size()

		prevFlag = mapCanvas.renderFlag()
		mapCanvas.setRenderFlag(False)
		self.iface.addDockWidget(position, wdg)

		wdg.setNumber( self.lastDockableMirror )
		self.lastDockableMirror = self.lastDockableMirror+1
		self.dockableMirrors.append( wdg )

		QObject.connect(wdg, SIGNAL( "closed(PyQt_PyObject)" ), self.onCloseDockableMirror)

		newSize = mapCanvas.size()
		if newSize != oldSize:
			# trick: update the canvas size
			mapCanvas.resize(newSize.width() - 1, newSize.height())
			mapCanvas.setRenderFlag(prevFlag)
			mapCanvas.resize(newSize)
		else:
			mapCanvas.setRenderFlag(prevFlag)


	def onCloseDockableMirror(self, wdg):
		if self.dockableMirrors.count( wdg ) > 0:
			self.dockableMirrors.remove( wdg )

		if len(self.dockableMirrors) <= 0:
			self.lastDockableMirror = 0

		
	def onWriteProject(self, domproject):
		if len(self.dockableMirrors) <= 0:
			return

		QgsProject.instance().writeEntry( "DockableMirrorMap", "/numMirrors", len(self.dockableMirrors) )
		for i, dockwidget in enumerate(self.dockableMirrors):
			# save position and geometry
			floating = dockwidget.isFloating()
			QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/floating" % i, floating )
			if floating:
				position = "%s %s" % (dockwidget.pos().x(), dockwidget.pos().y())
			else:
				position = u"%s" % dockwidget.getLocation()
			QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/position" % i, str(position) )

			size = "%s %s" % (dockwidget.size().width(), dockwidget.size().height())
			QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/size" % i, str(size) )

			QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/label" % i, dockwidget.getMirror().label )

			# save the layer list
			layerIds = dockwidget.getMirror().getLayerSet()
			QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/layers" % i, layerIds )

			scaleFactor = dockwidget.getMirror().scaleFactor.value()
			QgsProject.instance().writeEntryDouble("DockableMirrorMap", "/mirror%s/scaleFactor" % i, scaleFactor)

			# layer style overrides
			if QGis.QGIS_VERSION_INT >= 21100:
				keys = []
				values = []
				for k,v in dockwidget.getMirror().overrides.iteritems():
					keys.append(k)
					values.append(v)
				QgsProject.instance().writeEntry("DockableMirrorMap", "/mirror%s/layerStylesKeys" % i, keys)
				QgsProject.instance().writeEntry("DockableMirrorMap", "/mirror%s/layerStylesValues" % i, values)

	def onProjectLoaded(self):
		# restore mirrors?
		num, ok = QgsProject.instance().readNumEntry("DockableMirrorMap", "/numMirrors")
		if not ok or num <= 0:
			return

		# remove all mirrors
		self.removeDockableMirrors()

		mirror2lids = {}
		# load mirrors
		for i in range(num):
			if num >= 2:
				if i == 0: 
					prevFlag = self.iface.mapCanvas().renderFlag()
					self.iface.mapCanvas().setRenderFlag(False)
				elif i == num-1:
					self.iface.mapCanvas().setRenderFlag(True)

			from dockableMirrorMap import DockableMirrorMap
			dockwidget = DockableMirrorMap(self.iface.mainWindow(), self.iface)

			minsize = dockwidget.minimumSize()
			maxsize = dockwidget.maximumSize()

			# restore position
			floating, ok = QgsProject.instance().readBoolEntry("DockableMirrorMap", "/mirror%s/floating" % i)
			if ok: 
				dockwidget.setFloating( floating )
				position, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/position" % i)
				if ok: 
					try:
						if floating:
							parts = position.split(" ")
							if len(parts) >= 2:
								dockwidget.move( int(parts[0]), int(parts[1]) )
						else:
							dockwidget.setLocation( int(position) )
					except ValueError:
						pass

			# restore geometry
			dockwidget.setFixedSize( dockwidget.geometry().width(), dockwidget.geometry().height() )
			size, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/size" % i)
			if ok:
				try:
					parts = size.split(" ")
					dockwidget.setFixedSize( int(parts[0]), int(parts[1]) )
				except ValueError:
					pass				

			label, ok = QgsProject.instance().readEntry( "DockableMirrorMap", "/mirror%s/label" % i )
			if ok:
				dockwidget.getMirror().label = label

			scaleFactor, ok = QgsProject.instance().readDoubleEntry("DockableMirrorMap", "/mirror%s/scaleFactor" % i, 1.0)
			if ok: dockwidget.getMirror().scaleFactor.setValue( scaleFactor )

			# get layer list
			layerIds, ok = QgsProject.instance().readListEntry("DockableMirrorMap", "/mirror%s/layers" % i)
			if ok: dockwidget.getMirror().setLayerSet( layerIds )

			# layer style overrides
			if QGis.QGIS_VERSION_INT >= 21100:
				keys, ok = QgsProject.instance().readListEntry("DockableMirrorMap", "/mirror%s/layerStylesKeys" % i)
				values, ok = QgsProject.instance().readListEntry("DockableMirrorMap", "/mirror%s/layerStylesValues" % i)
				if ok and len(keys) == len(values):
					dockwidget.getMirror().overrides = dict(zip(keys, values))
					dockwidget.getMirror().updateStyleOverrides()

			self.addDockWidget( dockwidget )
			dockwidget.setMinimumSize(minsize)
			dockwidget.setMaximumSize(maxsize)

