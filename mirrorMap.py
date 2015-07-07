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
		self.layers = {}

		self.setupUi()

	def closeEvent(self, event):
		self.scaleFactor.valueChanged.disconnect(self.onExtentsChanged)
		QObject.disconnect(self.iface.mapCanvas(), SIGNAL( "extentsChanged()" ), self.onExtentsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "destinationCrsChanged()" ), self.onCrsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "mapUnitsChanged()" ), self.onMapUnitsChanged)
		QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "hasCrsTransformEnabled(bool)" ), self.onCrsTransformEnabled)
		QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL( "layerWillBeRemoved(QString)" ), self.delLayer)

		if QGis.QGIS_VERSION_INT >= 20400:
			self.iface.layerTreeView().selectionModel().selectionChanged.disconnect(self.refreshLayerButtons)
		else:
			self.iface.currentLayerChanged.disconnect(self.refreshLayerButtons)

		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QWidget.closeEvent(self, event)

	def setupUi(self):
		self.setObjectName( "dockablemirrormap_mirrormap" )

		gridLayout = QGridLayout( self )
		gridLayout.setContentsMargins(0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing())

		self.canvas = QgsMapCanvas( self )
		self.canvas.setCanvasColor( QColor(255,255,255) )
		settings = QSettings()
		self.canvas.enableAntiAliasing( settings.value( "/qgis/enable_anti_aliasing", False, type=bool ))
		self.canvas.useImageToRender( settings.value( "/qgis/use_qimage_to_render", False, type=bool ))
		action = settings.value( "/qgis/wheel_action", 0, type=int)
		zoomFactor = settings.value( "/qgis/zoom_factor", 2.0, type=float )
		self.canvas.setWheelAction( QgsMapCanvas.WheelAction(action), zoomFactor )
		gridLayout.addWidget( self.canvas, 0, 0, 1, 6 )

		self.addLayerBtn = QToolButton(self)
		#self.addLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
		#self.addLayerBtn.setText("Add current layer")
		self.addLayerBtn.setIcon( QIcon(":/plugins/DockableMirrorMap/icons/plus.png") )
		QObject.connect(self.addLayerBtn, SIGNAL( "clicked()" ), self.addLayer)
		gridLayout.addWidget( self.addLayerBtn, 1, 0, 1, 1 )
		self.addLayerBtn.setAutoRaise(True)

		self.delLayerBtn = QToolButton(self)
		#self.delLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
		#self.delLayerBtn.setText("Remove current layer")
		self.delLayerBtn.setIcon( QIcon(":/plugins/DockableMirrorMap/icons/minus.png") )
		QObject.connect(self.delLayerBtn, SIGNAL( "clicked()" ), self.delLayer)
		gridLayout.addWidget( self.delLayerBtn, 1, 1, 1, 1 )
		self.delLayerBtn.setAutoRaise(True)

		self.styleMenu = QMenu(self)
		self.styleBtn = QPushButton("Layer Style", self)
		self.styleBtn.setMenu(self.styleMenu)
		self.styleBtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		gridLayout.addWidget(self.styleBtn, 1, 2, 1, 1)
		if QGis.QGIS_VERSION_INT < 21100:
			self.styleBtn.hide()

		self.renderCheck = QCheckBox( "Render", self )
		QObject.connect(self.renderCheck, SIGNAL( "toggled(bool)" ), self.toggleRender)
		self.renderCheck.setChecked(True)
		gridLayout.addWidget( self.renderCheck, 1, 3, 1, 1 )

		self.scaleFactorLabel = QLabel(self)
		self.scaleFactorLabel.setText("Scale factor:")
		self.scaleFactorLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		gridLayout.addWidget(self.scaleFactorLabel, 1, 4, 1, 1)
		self.scaleFactor = QDoubleSpinBox(self)
		self.scaleFactor.setMinimum(0.0)
		self.scaleFactor.setMaximum(1000.0)
		self.scaleFactor.setDecimals(3)
		self.scaleFactor.setValue(1)
		self.scaleFactor.setObjectName("scaleFactor")
		self.scaleFactor.setSingleStep(.05)
		gridLayout.addWidget(self.scaleFactor, 1, 5, 1, 1)
		self.scaleFactor.valueChanged.connect(self.onExtentsChanged)

		# Add a default pan tool
		self.toolPan = QgsMapToolPan( self.canvas )
		self.canvas.setMapTool( self.toolPan )

		QObject.connect(self.iface.mapCanvas(), SIGNAL( "extentsChanged()" ), self.onExtentsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "destinationCrsChanged()" ), self.onCrsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "mapUnitsChanged()" ), self.onCrsChanged)
		QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL( "hasCrsTransformEnabled(bool)" ), self.onCrsTransformEnabled)
		QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL( "layerWillBeRemoved(QString)" ), self.delLayer)
		if QGis.QGIS_VERSION_INT >= 20400:
			self.iface.layerTreeView().selectionModel().selectionChanged.connect(self.refreshLayerButtons)
		else:
			self.iface.currentLayerChanged.connect(self.refreshLayerButtons)

		self.refreshLayerButtons()

		self.onExtentsChanged()
		self.onCrsChanged()
		self.onCrsTransformEnabled( self.iface.mapCanvas().hasCrsTransformEnabled() )

	def toggleRender(self, enabled):
		self.canvas.setRenderFlag( enabled )

	def onExtentsChanged(self):
		self.canvas.setExtent( self.iface.mapCanvas().extent() )
		self.canvas.zoomByFactor( self.scaleFactor.value() )

	def onCrsChanged(self):
		renderer = self.iface.mapCanvas().mapRenderer()
		self.canvas.mapRenderer().setDestinationCrs( renderer.destinationCrs() )
		self.canvas.mapRenderer().setMapUnits( renderer.mapUnits() )

	def onCrsTransformEnabled(self, enabled):
		self.canvas.mapRenderer().setProjectionsEnabled( enabled )


	def refreshLayerButtons(self):
		has_layers_to_add = False
		has_layers_to_remove = False
		sel_layers = self._selectedLayers()
		for layerId in sel_layers:
			if layerId in self.layers:
				has_layers_to_remove = True
			else:
				has_layers_to_add = True

		self.addLayerBtn.setEnabled(has_layers_to_add)
		self.delLayerBtn.setEnabled(has_layers_to_remove)

		if QGis.QGIS_VERSION_INT >= 21100:
			if len(sel_layers) == 1 and sel_layers[0] in self.layers:
				layer = QgsMapLayerRegistry.instance().mapLayer(sel_layers[0])
				self._populateLayerStylesMenu(layer)
			else:
				self._populateLayerStylesMenu(None)

	def setLayerStyle(self):
		sel_layers = self._selectedLayers()
		if len(sel_layers) != 1:
			return
		layer = QgsMapLayerRegistry.instance().mapLayer(sel_layers[0])

		styleName = self.sender().text()
		if styleName == "(default)":
			styleName = ""
		overrides = self.canvas.layerStyleOverrides()
		if styleName == "(use current)":
			if layer.id() in overrides:
				del overrides[layer.id()]
		else:
			overrides[layer.id()] = layer.styleManager().style(styleName).xmlData()
		self.canvas.setLayerStyleOverrides(overrides)
		self.canvas.refresh()
		self.refreshLayerButtons()

	def getLayerSet(self):
		return self.layers.keys()

	def setLayerSet(self, layerIds=None):
		self.layers = {}
		if layerIds is not None:
			for lid in layerIds:
				self.layers[lid] = 1

		self._updateCanvasLayers()


	def addLayer(self):
		for layerId in self._selectedLayers():
			self.layers[layerId] = 1
		self._updateCanvasLayers()

	def delLayer(self, layerId=None):
		if layerId is None:
			layers = self._selectedLayers()
		else:
			layers = [layerId]

		for layerId in layers:
			if layerId in self.layers:
				del self.layers[layerId]
		self._updateCanvasLayers()

	def _updateCanvasLayers(self):

		canvas_layers = []
		for l in self.iface.legendInterface().layers():
			if l.id() in self.layers:
				canvas_layers.append(QgsMapCanvasLayer(l))

		self.canvas.setLayerSet(canvas_layers)

		self.refreshLayerButtons()
		self.onExtentsChanged()

	def _selectedLayers(self):
		if QGis.QGIS_VERSION_INT >= 20400:
			return self._selectedLayers_new()
		else:
			return self._selectedLayers_old()

	def _selectedLayers_new(self):
		lst = []
		for n in self.iface.layerTreeView().selectedNodes():
			if isinstance(n, QgsLayerTreeLayer) and n.layer():
				lst.append(n.layer().id())
			elif isinstance(n, QgsLayerTreeGroup):
				lst += n.findLayerIds()

		return lst

	def _selectedLayers_old(self):
		layer = self.iface.activeLayer()
		return [layer.id()] if layer else []

	def _currentStyleName(self, layer):
		overrides = self.canvas.layerStyleOverrides()
		if layer.id() not in overrides:
			return "__current__"  # special value if not overridden

		for style_name in layer.styleManager().styles():
			if layer.styleManager().style(style_name).xmlData() == overrides[layer.id()]:
				return style_name

	def _populateLayerStylesMenu(self, layer):
		if layer is None or len(layer.styleManager().styles()) <= 1:
			self.styleBtn.setEnabled(False)
			return

		self.styleBtn.setEnabled(True)
		cur_style_name = self._currentStyleName(layer)
		self.styleMenu.clear()

		a = self.styleMenu.addAction("(use current)", self.setLayerStyle)
		a.setCheckable(True)
		a.setChecked(cur_style_name == "__current__")
		self.styleMenu.addSeparator()

		for style_name in layer.styleManager().styles():
			is_current = style_name == cur_style_name
			if len(style_name) == 0: style_name = "(default)"
			a = self.styleMenu.addAction(style_name, self.setLayerStyle)
			a.setCheckable(True)
			a.setChecked(is_current)
