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

from ui.dlgAbout_ui import Ui_DlgAbout

import resources_rc

class DlgAbout(QDialog, Ui_DlgAbout):

	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		
		self.setupUi(self)
		self.logo.setPixmap( QPixmap( ":/dockablemirrormap/icons/faunalia_logo.png" ) )
