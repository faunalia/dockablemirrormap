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


class MirrorMap(QWidget):

	def __init__(self, parent, iface):
		QWidget.__init__(self, parent)
		self.setAttribute(Qt.WA_DeleteOnClose)

		self.iface = iface
		self.layerId2canvasLayer = {}
		self.canvasLayers = []

		self.setupUi()

	def closeEvent(self, event):
		QObject.disconnect(self.iface.mapCanvas(), SIGNAL( "extentsChanged()" ), self.onExtentsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "destinationSrsChanged()" ), self.onSrsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "mapUnitsChanged()" ), self.onMapUnitsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "hasCrsTransformEnabled(bool)" ), self.onCrsTransformEnabled)
		QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL( "layerWillBeRemoved(QString)" ), self.delLayer)
		QObject.disconnect(self.iface, SIGNAL( "currentLayerChanged(QgsMapLayer *)" ), self.refreshLayerButtons)

		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QWidget.closeEvent(self, event)

	def setupUi(self):
		self.setObjectName( "dockablemirrormap_mirrormap" )

		gridLayout = QGridLayout( self )
		gridLayout.setContentsMargins(0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing())

		self.canvas = QgsMapCanvas( self )
		self.canvas.setCanvasColor( QColor(255,255,255) )
		settings = QSettings()
		self.canvas.enableAntiAliasing( settings.value( "/qgis/enable_anti_aliasing", QVariant(False) ).toBool() )
		self.canvas.useImageToRender( settings.value( "/qgis/use_qimage_to_render", QVariant(False) ).toBool() )
		action = settings.value( "/qgis/wheel_action", QVariant(0) ).toInt()[0]
		zoomFactor = settings.value( "/qgis/zoom_factor", QVariant(2) ).toDouble()[0]
		self.canvas.setWheelAction( QgsMapCanvas.WheelAction(action), zoomFactor )
		gridLayout.addWidget( self.canvas, 0, 0, 1, 3 )

		self.addLayerBtn = QToolButton(self)
		self.addLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
		self.addLayerBtn.setText("Add current layer")
		self.addLayerBtn.setIcon( QIcon(":/dockablemirrormap/plus") )
		QObject.connect(self.addLayerBtn, SIGNAL( "clicked()" ), self.addLayer)
		gridLayout.addWidget( self.addLayerBtn, 1, 0, 1, 1 )

		self.delLayerBtn = QToolButton(self)
		self.delLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
		self.delLayerBtn.setText("Remove current layer")
		self.delLayerBtn.setIcon( QIcon(":/dockablemirrormap/minus") )
		QObject.connect(self.delLayerBtn, SIGNAL( "clicked()" ), self.delLayer)
		gridLayout.addWidget( self.delLayerBtn, 1, 1, 1, 1 )

		self.renderCheck = QCheckBox( "Render", self )
		QObject.connect(self.renderCheck, SIGNAL( "toggled(bool)" ), self.toggleRender)
		self.renderCheck.setChecked(True)
		gridLayout.addWidget( self.renderCheck, 1, 2, 1, 1 )

		# Add a default pan tool
		self.toolPan = QgsMapToolPan( self.canvas )
		self.canvas.setMapTool( self.toolPan )

		QObject.connect(self.iface.mapCanvas(), SIGNAL( "extentsChanged()" ), self.onExtentsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "destinationSrsChanged()" ), self.onSrsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "mapUnitsChanged()" ), self.onSrsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "hasCrsTransformEnabled(bool)" ), self.onCrsTransformEnabled)
		QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL( "layerWillBeRemoved(QString)" ), self.delLayer)
		QObject.connect(self.iface, SIGNAL( "currentLayerChanged(QgsMapLayer *)" ), self.refreshLayerButtons)

		self.refreshLayerButtons()

		self.onExtentsChanged()
		self.onSrsChanged()
		self.onCrsTransformEnabled( self.iface.mapCanvas().hasCrsTransformEnabled() )

	def toggleRender(self, enabled):
		self.canvas.setRenderFlag( enabled )

	def onExtentsChanged(self):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )

		self.canvas.setExtent( self.iface.mapCanvas().extent() )
		self.canvas.zoomScale( self.iface.mapCanvas().scale() )

		self.canvas.setRenderFlag( prevFlag )

	def onSrsChanged(self):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )

		renderer = self.iface.mapCanvas().mapRenderer()
		self.canvas.mapRenderer().setDestinationSrs( renderer.destinationSrs() )
		self.canvas.mapRenderer().setMapUnits( renderer.mapUnits() )

		self.canvas.setRenderFlag( prevFlag )

	def onCrsTransformEnabled(self, enabled):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )

		self.canvas.mapRenderer().setProjectionsEnabled( enabled )

		self.canvas.setRenderFlag( prevFlag )


	def refreshLayerButtons(self):
		layer = self.iface.activeLayer()

		isLayerSelected = layer != None
		hasLayer = False
		for l in self.canvas.layers():
			if l == layer:
				hasLayer = True
				break
		self.addLayerBtn.setEnabled( isLayerSelected and not hasLayer )
		self.delLayerBtn.setEnabled( isLayerSelected and hasLayer )

	def addLayer(self):
		layer = self.iface.activeLayer()
		if layer == None:
			return
		
		# add the layer to the map canvas layer set
		cl = QgsMapCanvasLayer(layer)
		self.layerId2canvasLayer[ layer.getLayerID() ] = cl
		self.canvasLayers.insert(0, cl)

		self.canvas.setLayerSet( self.canvasLayers )

		self.refreshLayerButtons()
		self.onExtentsChanged()

	def delLayer(self, layerId=None):
		if layerId == None:
			layer = self.iface.activeLayer()
			if layer == None:
				return
			layerId = layer.getLayerID()

		# remove the layer from the map canvas layer set
		if not self.layerId2canvasLayer.has_key( layerId ):
			return
		cl = self.layerId2canvasLayer[ layerId ]
		del self.layerId2canvasLayer[ layerId ]
		self.canvasLayers.remove( cl )

		self.canvas.setLayerSet( self.canvasLayers )

		self.refreshLayerButtons()
		self.onExtentsChanged()

