#!/usr/bin/env python
# Qtvcp versa probe
#
# Copyright (c) 2018  Chris Morley <chrisinnanaimo@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# a probe screen based on Versa probe screen
# this program requires the below five .ngc files to function
# these files are located in: /versa_probe_macros/
# located in: /macros
# versa_probe_xplus.ngc
# versa_probe_xminus.ngc
# versa_probe_yplus.ngc
# versa_probe_yminus.ngc
# versa_probe_down.ngc
# required renamed icons are located in: /versa_probe_icons/
# these were renamed to agree with buttom sequence numbers for clarity.
#
# For easy placement Icons have names like: outside_1.png, inside_5.png, down.png
# that agree with the positions below.
#
# Outside     Inside      skew
# -------     -------     ----
# 1  2  3     1  2  3     1  2
# 4  5  6     4  5  6     3  4
# 7  8  9     7  8  9
#						  inside_xl  ouside_xl
#						  inside_yl  ouside_yl
#
#                         down		 tool_dia

import sys
import os
import math

from PyQt5 import QtGui, QtCore, QtWidgets, uic

from qtvcp.widgets.widget_baseclass import _HalWidgetBase
from qtvcp.core import Status
from qtvcp import logger

# Instiniate the libraries with global reference
# STATUS gives us status messages from linuxcnc
# LOG is for running code logging
STATUS = Status()
LOG = logger.getLogger(__name__)
DATADIR = os.path.abspath( os.path.dirname( __file__ ) )

class VersaProbe(QtWidgets.QWidget, _HalWidgetBase):
    def __init__(self, parent=None):
        super(VersaProbe, self).__init__(parent)
        self.setMinimumSize(600, 400)
        self.filename = os.path.join(DATADIR, 'versa_probe.ui')
        try:
            instance = uic.loadUi(self.filename, self)
        except AttributeError as e:
            log.critical(e)

    def _hal_init(self):
        pass




####################################
# Testing
####################################
if __name__ == "__main__":
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

    app = QtWidgets.QApplication(sys.argv)
    w = VersaProbe()
    w.show()
    sys.exit( app.exec_() )

