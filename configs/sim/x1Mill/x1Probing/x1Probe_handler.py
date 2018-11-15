
# x1Probe_handler.py for the associated x1Probe.ui
# Copyright (c) 2018 Johannes P Fassotte
#
# is handler uses a modified version of the verser probing code (v1)
# which has been modified to use the item names of the gui
# for improved clarity and understanding of the code.
#
# This probe screen gui is for use with linuxcnc QTVcp by Chris Morley
#
# This handler program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# layout and design work By Johannes P Fassotte, Fairbanks, Alaska
# with insperation receiced from the gmoccapy gui and especially
# the work by Chris Morley for development of linuxcnc QTvcp.
#
# x1Mill panel size is 1024 x 768 to make it compact which insures
# minimum hand or mouse movement while still providing excellent features
# which is implemented with the use of layering panels that are called up
# when needed and which occupy specific areas within the gui. 
# The gui is in early stages of design work and some panels have not
# been fully completed.
#
# The Define statements for buttons and other items are listed in groups
# by individual front panels that they reside in. These have prefixes as below.
#
# abtn - action buttons
# pbtn - hal pushbutton
# qbtn - qt push button
# led  - hal led
# lab  - qlabel
# slab - hal status label
# scrb - scrowl bar
# pbar - progress bar
# lne  - text line entry
# On going work may have some that are not listed yet
#
# this program requires the below five .ngc files to function
# these files are located in: /x1Probe_macros/
# located in: /macros
# versa_probe_xplus.ngc
# versa_probe_xminus.ngc
# versa_probe_yplus.ngc
# versa_probe_yminus.ngc
# versa_probe_down.ngc
# required renamed icons are located in: /x1Probe_icons/
# these were renamed to agree with buttom sequence numbers for clarity.
#
# Icons have names like: outside_1.png, inside_5.png, down.png
# that agree with the positions below.
#
# Outside     Inside      skew
# -------     -------     ---- 
# 1  2  3     1  2  3     1  2
# 4  5  6     4  5  6     3  4
# 7  8  9     7  8  9
#                         down
#                         ----
#                         down

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFVIEW_WIDGET
from qtvcp.widgets.tool_offsetview import ToolOffsetView as TOOLVIEW_WIDGET
from qtvcp.widgets.dialog_widget import CamViewDialog as CAMVIEW
from qtvcp.widgets.dialog_widget import MacroTabDialog as LATHEMACRO
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.lib.keybindings import Keylookup
from qtvcp.lib.notify import Notify
from qtvcp.core import Status, Action
from qtvcp import logger


import linuxcnc
import sys
import os
import psutil  # used for killing embedded processes
import subprocess
import gtk
import gobject

# set up paths for external programs support
TCLPATH = os.environ['LINUXCNC_TCL_DIR']

# Instantiate libraries section
# -----------------------------
KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()
LOG = logger.getLogger(__name__)
# Set the log level for this module
#LOG.setLevel(logger.INFO) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL

import time;
localtime = time.asctime( time.localtime(time.time()))
print "Local current time :", localtime

class HandlerClass:
    def __init__(self, halcomp,widgets,paths):
        self.hal = halcomp
        self.w = widgets
        self.stat = linuxcnc.stat()
        self.cmnd = linuxcnc.command()
        self.error = linuxcnc.error_channel()
        # connect to GStat to catch linuxcnc events
        STATUS.connect('state-on', self.on_state_on)
        STATUS.connect('state-off', self.on_state_off)
        self.jog_slow_fast=[] # required by jogging

# =================================================================
    def initialized__(self):
        STATUS.forced_update()
#        self.w.tooloffsetdialog._geometry_string='0 0 600 396'
#        self.w.originoffsetdialog._geometry_string='0 0 600 396 onwindow'

       
    def processed_key_event__(self,receiver,event,is_pressed,key,code,shift,cntrl):
        # when typing in MDI, we don't want keybinding to call functions
        # so we catch and process the events directly.
        # We do want ESC, F1 and F2 to call keybinding functions though
        if code not in(QtCore.Qt.Key_Escape,QtCore.Qt.Key_F1 ,QtCore.Qt.Key_F2,
                    QtCore.Qt.Key_F3,QtCore.Qt.Key_F5,QtCore.Qt.Key_F5):
            if isinstance(receiver, OFFVIEW_WIDGET) or \
                isinstance(receiver, MDI_WIDGET):
                if is_pressed:
                    receiver.keyPressEvent(event)
                    event.accept()
                return True
            elif isinstance(receiver, GCODE) and STATUS.is_man_mode() == False:
                if is_pressed:
                    receiver.keyPressEvent(event)
                    event.accept()
                return True
            elif isinstance(receiver,QtWidgets.QDialog):
                print 'dialog'
                return True
        try:
            KEYBIND.call(self,event,is_pressed,shift,cntrl)
            return True
        except Exception as e:
            print 'no function %s in handler file for-%s'%(KEYBIND.convert(event),key)
            return False

    def on_state_on(self,w):
        print 'machine on'

    def on_state_off(self,w):
        print 'machine off'

# x1Probe panel size is 600 x 400 to make it compact
# and provide improved clarity of its functions.

    def _periodic(self):

 
        STATUS.set_jograte(float(3))
# =====================================
        return True
       
# This is ready for verser code insertion
# and modification to except new names for improved clarity
# Further work or moifications may be required for the
# status labels and the inputs for value entries.
# The input for value entries are giving error messages.
# ===============================================================

# Outside measurements
# ===============================================================
    def pbtn_outside_xpym_released(self):
        print  "1 xpym_released "
    def pbtn_outside_ym_released(self):   # also for pbtn_inside_ym_released
        print  "2 outside_ym_released - also inside_ym_released"
    def pbtn_outside_xmym_released(self):
          print  "3 outside_xmym_released "
    def pbtn_outside_xp_released(self):   # also for pbtn_inside_xp_released
          print  "4 outside_xp_released - also inside_xp_released"
    def pbtn_outside_center_released(self):
          print  "5 outside_center_released "
    def pbtn_outside_xm_released(self):   # also for pbtn_inside_xm_released
          print  "6 outside_xm_released - also inside_xm_released"
    def pbtn_outside_xpyp_released(self):
          print  "7 outside_xpyp_released "
    def pbtn_outside_yp_released(self):   # also for pbtn_inside_yp_released
          print  "8 outside_yp_released - also inside_yp_released"
    def pbtn_outside_xmyp_released(self):
          print  "9 outside_xmyp_released "

# Inside measurements
# ===============================================================
    def pbtn_inside_xmyp_released(self):
          print  "1 inside_xmyp_released "
    def pbtn_inside_xpyp_released(self):
          print  "3 inside_xpyp_released"
    def pbtn_inside_xy_hole_released(self):
          print  "5 inside_xy_hole_released"
    def pbtn_inside_xmym_released(self):
          print  "7 inside_xmym_released"
    def pbtn_inside_xpym_released(self):
          print  "9 inside_xpym_released "

# Skew measurements - formally "rotation"
# ===============================================================
    def pbtn_skew_xp_released(self):
          print "skew_xp_released"  
    def pbtn_skew_ym_released(self):
          print "skew_ym_released"  
    def pbtn_skew_yp_released(self):
          print "skew_yp_released"
    def pbtn_skew_xm_released(self):
          print "skew_xm_released"

# Straight down measurement
# ===============================================================
    def pbtn_down_released(self):
          print "down_released"

# Auto zero and auto skew allow or not to allow
# This has two associated warming LED's
# ===============================================================
    def pbtn_allow_auto_zero_toggle(self,pressed):
        if pressed:
             print "allow_auto_zero"
        else:
            print "dont allow_auto_zero"
    def pbtn_allow_auto_skew_toggle(self,pressed):
        if pressed:
            print "allow_auto_skew"
        else:
            print "dont allow_auto_skew"

# Set offsets for values entered by inputs
# ===============================================================
    def pbtn_set_x_released(self):
          print "set_x_released"
    def pbtn_set_y_released(self):
          print "set_y_released"
    def pbtn_set_z_released(self):
          print "set_z_released"
    def pbtn_set_angle_released(self):
          print "set_angle_released"

# Inputs for the offest values above
# ===============================================================
    def input_adj_x_enter(self):
        print "adjust_x"
    def input_adj_y_enter(self):
        print "adjust_y"
    def input_adj_z_enter(self):
        print "adjust_z"
    def input_adj_angle_enter(self):
        print "adjust_angle"

# Inputs for the offest values above
# ===============================================================
    def input_probe_diam_enter(self):
        print "input Probe_diam"
    def input_max_travel_enter(self):
        print "input max_travel"
    def input_latch_return_dist_enter(self):
        print "input latch_return_dist"
    def input_search_vel_enter(self):
        print "input search_vel"
    def input_probe_vel_enter(self):
        print "input probe_vel"
    def input_side_edge_lenght_enter(self):
        print "input side_edge_lenght"
    def input_xy_clearances_enter(self):
        print "input xy_clearances"
    def input_z_clearance_enter(self):
        print "input z_clearance"

# Staus display labels which are used to display and store values
# ===============================================================
    def status_z_setText(self):
        print "status_z"
    def status_not_used_setText(self):
        print "status_not_used"
    def status_yc_setText(self):
        print "status_z"
    def status_a_setText(self):
        print "status_a"
    def status_yp_setText(self):
        print "status_yp"
    def status_xm_setText(self):
        print "status_xm"
    def status_xc_setText(self):
        print "status_xc"
    def status_lx_setText(self):
        print "status_lx"
    def status_ly_setText(self):
        print "status_ly"
    def status_d_setText(self):
        print "status_d"
    def status_ym_setText(self):
        print "status_ym"
    def status_xp_setText(self):
        print "status_xp"

# end of gui specific items
# ===============================================================

# The below are standard required items
# ===============================================================

    def continous_jog(self, axis, direction):
        STATUS.continuous_jog(axis, direction)

    def on_keycall_ESTOP(self,event,state,shift,cntrl):
        if state:
            self.w.button_estop.click()
    def on_keycall_POWER(self,event,state,shift,cntrl):
        if state:
            self.w.button_machineon.click()
    def on_keycall_HOME(self,event,state,shift,cntrl):
        if state:
            self.w.button_home.click()

    def closeEvent(self, event):
        event.accept()

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)

def get_handlers(halcomp,widgets,paths):
    localtime = time.asctime( time.localtime(time.time()) )
    print "Local current time :", localtime
    return [HandlerClass(halcomp,widgets,paths)]

#END
