# Jaay
# x1Mill_handler.py for the associated x1Mill.ui
# Copyright (c) 2018 Johannes P Fassotte
# This gui is for use with linuxcnc QTVcp by Chris Morley
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
# On going work may have some that are not listed yet
#

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
        self.w.stackedWidget_0.setCurrentIndex(0)
        self.w.stackedWidget_1.setCurrentIndex(0)
        self.w.stackedWidget_2.setCurrentIndex(0)
        self.w.stackedWidget_3.setCurrentIndex(0)  
        self.w.stackedWidget_4.setCurrentIndex(0) 
        self.w.stackedWidget_5.setCurrentIndex(0)
        self.w.pbtn_axis4_select_spindle_toggled=True
        self.w.scrb_spindle_main_rpm.setRange(200,3000)
        self.w.pbar_spindle_main_rpm_ind_bar.setMinimum(0)
        self.w.pbar_spindle_main_rpm_ind_bar.setMaximum(3000)
        self.w.scrb_spindle_main_rpm.setValue(1250)
        self.w.scrb_axis4_spindle_rpm.setRange(0,500)
        self.w.pbar_axis4_spindle_rpm_ind_bar.setMinimum(0)
        self.w.pbar_axis4_spindle_rpm_ind_bar.setMaximum(500)
        self.w.scrb_axis4_spindle_rpm.setValue(182)
        self.w.pbtn_mainv_misc_keyboard.setEnabled(False)

        # jogging scrowl bar range setting
        self.w.scrb_jog_linear_slow.setRange(0,100)
        self.w.scrb_jog_linear_fast.setRange(0,100)
        self.w.scrb_jog_position_slow.setRange(0,100)
        self.w.scrb_jog_position_fast.setRange(0,100)
#        self.w.scrb_jog_angular_slow.setRange(0,100) - not installed yet
#        self.w.scrb_jog_angular_fast.setRange(0,100) - not installed yet

        # jogging rate set default values
        self.jograte_slow_position_value=7
        self.jograte_fast_position_value=10
        self.jograte_slow_linear_value=5
        self.jograte_fast_linear_value=8 
        self.jograte_slow_angular_value=5
        self.jograte_fast_angular_value=9

        # jogging scrowl bar position setting  - to be set to same values as the above                  
        self.w.scrb_jog_position_slow.setValue(7)
        self.w.scrb_jog_position_fast.setValue(10)
        self.w.scrb_jog_linear_slow.setValue(5) 
        self.w.scrb_jog_linear_fast.setValue(8)
#        self.w.scrb_jog_angular_slow.setValue(5) - not installed yet
#        self.w.scrb_jog_angular_fast.setValue(9) - not installed yet

        # at startup set these buttons to true
        self.w.pbtn_jog_mode_linear.animateClick(True)
        self.w.pbtn_jog_rate_slow.animateClick(True)
        self.w.pbtn_axis4_select_spindle.animateClick(True)
        self.w.abtn_dro_abs.animateClick(True)

        self.w.scrb_override_rate_spindle.setRange(0,125)
        self.w.scrb_override_rate_spindle.setValue(85)
        self.w.scrb_override_rate_feed.setRange(0,125)
        self.w.scrb_override_rate_feed.setValue(95)
        self.w.scrb_override_rate_rapid.setRange(0,125)
        self.w.scrb_override_rate_rapid.setValue(100)
        self.w.scrb_override_rate_jog.setRange(0,125)
        self.w.scrb_override_rate_jog.setValue(45)
        self.w.scrb_override_rate_angular.setRange(0,125)
        self.w.scrb_override_rate_angular.setValue(25)

        self.jog_mode=0               # 0=none 1=position 2=linear 3=angular   
        self.jog_slow_fast=0          # slow = 0 fast = 1
        self.jog_rate_selected_out=0  # *** jog rate value to be sent to linuxcnc ***
        self.jogStep = 0.0000         # step value from buttons

        self.w.abtn_jog_pos_a.setEnabled(False)
        self.w.abtn_jog_neg_a.setEnabled(False)

#        STATUS.connect('periodic', self._periodic)
        gobject.timeout_add(100, self._periodic)

       
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

# x1Mill panel size is 1024 x 768 to make it compact which insures minimum hand or mouse movement
# while still providing excellent features that is provided by layering. 
# The x1MillGui is in early stages of design work and some panels have not been completed.
# Define statements are listed by individual front panels.

    def _periodic(self):

        self.w.lab_jog_jog_rate.setText(str(self.jog_rate_selected_out))
        self.w.lab_jog_jog_step.setText(str(self.jogStep))
#        distance = STATUS.get_jog_rate()
#        print "jog increment", distance 

        self.w.abtn_jog_pos_a.setEnabled(False) # sim only has 3 axis so keep these disabled
        self.w.abtn_jog_neg_a.setEnabled(False) # sim only has 3 axis so keep these disabled

        STATUS.set_jograte(float(3))
# =====================================
        return True
       
# MainWindow panel -- seven vertical main control buttons lower right
# ===============================================================
    def abtn_main_estop_toggled(self,pressed):
        if pressed:
            print "Estop On"
        else:
            print "Estop off"
 
    def abtn_mainv_power_on_toggled(self,pressed):
        print "power on"
        if pressed:
           # self.cmnd.state(linuxcnc.STATE_ON)
           print "power on"
        else:
           # self.cmnd.state(linuxcnc.STATE_OFF)
           print "power off"  
 
    def abtn_mainv_mode_manual_toggled(self,pressed):
        print 'machine manual click',pressed
        self.cmnd.mode(linuxcnc.MODE_MANUAL)
        self.w.stackedWidget_4.setCurrentIndex(0)
        self.w.pbtn_mainv_misc_keyboard.setEnabled(False) 
        self.w.pbtn_mainh_panel_graphic.animateClick(True)

    def abtn_mainv_mode_mdi_toggled(self,pressed):
        print 'machine mdi click',pressed
        self.cmnd.mode(linuxcnc.MODE_MDI)
        self.w.stackedWidget_2.setCurrentIndex(0)
        self.w.stackedWidget_4.setCurrentIndex(1)
        self.w.pbtn_mainv_misc_keyboard.setEnabled(True)

    def abtn_mainv_mode_auto_toggled(self,pressed):
        print 'machine mdi click',pressed
        self.cmnd.mode(linuxcnc.MODE_AUTO)
        self.w.stackedWidget_4.setCurrentIndex(2)
        self.w.pbtn_mainv_misc_keyboard.setEnabled(False)

    def pbtn_mainv_spare_2_toggled(self):
        name = self.w.sender().text()
        print name

    def pbtn_mainv_spare_1_toggled(self):
        name = self.w.sender().text()
        print name
   
# MainWindow panel -- four buttons vertical upper right
# ===============================================================
    def  pbtn_mainv_misc_keyboard_toggled(self,pressed):
         if pressed:
            self.w.stackedWidget_2.setCurrentIndex(1)
#            self.w.stackedWidget_2.(onboard --xid)
#            self.onboard.stdout.readline()
#         else:
#            self.w.stackedWidget_2.setCurrentIndex(0)
#            self.onboard_vkeyboard.kill()
#            self.onboard_vkeyboard.terminate()

#  onboard --xid
    def pbtn_mainv_misc_spare_toggled(self):
        name = self.w.sender().text()
        print name

    def pbtn_mainv_misc_help_toggled(self):
        self.w.stackedWidget_4.setCurrentIndex(4)
        name = self.w.sender().text()
        print name


    def pbtn_mainv_misc_exit_clicked(self):
        name = self.w.sender().text()
        print name

# MainWindow panel -- ten buttons horizontal bottom left
# these are meant to bring up dialogs or control panels in the
# gcode graphics display area. Max size of these is w600xh400
# the cmds listed are entered with qt designer not here
# ===============================================================
        
    def pbtn_mainh_panel_graphic_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(0)
        
    def pbtn_mainh_panel_homing_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(1)
        
    def pbtn_mainh_panel_tool_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(2)

    def pbtn_mainh_panel_probe_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(3)
        
    def pbtn_mainh_panel_tool_offsets_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(4)

    def pbtn_mainh_panel_origin_offsets_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(5)

    def pbtn_mainh_panel_macro_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(6)
 
    def pbtn_mainh_panel_spare_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(7)
 
    def pbtn_mainh_panel_camview_toggled(self):
        self.w.stackedWidget_1.setCurrentIndex(8)

    def pbtn_mainh_panel_file_toggled(self):
       self.w.stackedWidget_1.setCurrentIndex(9)

# MainWindow panel -- three buttons horizontal bottom right and Time/date label
# ===============================================================
    def abtn_mainh_aux_flood_toggled(self):
        name = self.w.sender().text()
        print name 
 
    def abtn_mainh_aux_mist_toggled(self):
        name = self.w.sender().text()
        print name 

    def btn_mainh_aux_aux_toggled(self):
        name = self.w.sender().text()
        print name 
 
    def lab_mainh_aux_time_date_setText(self):
        name = self.w.sender().text()
        print name

# Note: under the primany spindle and dro panel area listed below is a panel for a
# virtual keyboard. It its maximum size is 954x228, stackedWidget_3 index(1)

# primany spindle and dro panel -- stackedWidget_3 index(0)
# ===============================================================
    def pbtn_spindle_main_quick_set_25_clicked(self):
        self.w.scrb_spindle_main_rpm.setValue(750)
  
    def pbtn_spindle_main_quick_set_50_clicked(self):
        self.w.scrb_spindle_main_rpm.setValue(1500)
 
    def pbtn_spindle_main_quick_set_100_clicked(self):
        self.w.scrb_spindle_main_rpm.setValue(2250) 
   
    def scrb_spindle_main_rpm_setRange(self):
        print ""

    def scrb_spindle_main_rpm_setValue(self,value):
            value0 = self.w.sender().value()
            print "set value",value0
            # the below to see progress bar move - will come from spindle encoder later
            self.w.pbar_spindle_main_rpm_ind_bar.setValue(value0)

    def scrb_spindle_main_rpm_valueChanged(self,value):
            value0 = self.w.sender().value()
            print "valueChanged",value0
            # the below to see progress bar move - will come from spindle encoder later
            self.w.pbar_spindle_main_rpm_ind_bar.setValue(value0)

    def abtn_spindle_main_rpm_decrease_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_spindle_main_rpm_increase_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_spindle_main_forward_toggled(self):
        name = self.w.sender().text()
        print name

    def abtn_spindle_main_stop_toggled(self):
        name = self.w.sender().text()
        print name
 
    def abtn_spindle_main_reverse_toggled(self):
        name = self.w.sender().text()
        print name 
 
    def lab_spindle_main_rpm_setText(self):
        name = self.w.sender().text()
        print name 

    def pbar_spindle_main_rpm_valueChanged(self):
        name = self.w.sender().text()
        print name
 
    def pbar_spindle_main_rpm_ind_bar_setMinimum(self):
        name = self.w.sender().text()
        print name

    def pbar_spindle_main_rpm_ind_bar_setMaximum(self):
        name = self.w.sender().text()
        print name

    def pbar_spindle_main_rpm_ind_bar_setValue(self):
        name = self.w.sender().text()
        print name

# dro panel for axis x,y,z,a 
# ===============================================================
    def abtn_dro_abs_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def abtn_dro_dtg_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name
 
    def abtn_dro_rel_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def pbtn_dro_inch_mm_toggled(self,pressed):
        if pressed:
            print "MM"
        else: print "INCH"

    def pbtn_dro_spare_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

# options panel left side of the primary dro's contains the below items:
# ===============================================================
# index 0: axis4_panel
# index 1: quick_zero_panel
# index 2: macro_btns_panel
# index 3: override_panel
# index 4: dro_5_to_9_panel
# lists of these follows:

# left side buttons for selection of the five panels listed above
# ===============================================================
    def pbtn_axis4_select_spindle_toggled(self):
        self.w.stackedWidget_3.setCurrentIndex(0)
 
    def pbtn_axis4_select_quick_zero_toggled(self):
        self.w.stackedWidget_3.setCurrentIndex(1)
 
    def pbtn_axis4_select_macro_toggled(self):
        self.w.stackedWidget_3.setCurrentIndex(2)

    def pbtn_axis4_select_overrides_toggled(self):
        self.w.stackedWidget_3.setCurrentIndex(3)

    def pbtn_axis4_select_dro_toggled(self):
        self.w.stackedWidget_3.setCurrentIndex(4)

# axis4_panel
# ===============================================================
    def pbtn_axis4_spindle_quick_set_25_clicked(self):
        self.w.scrb_axis4_spindle_rpm.setValue(125)
  
    def pbtn_axis4_spindle_quick_set_50_clicked(self):
        self.w.scrb_axis4_spindle_rpm.setValue(250)

    def pbtn_axis4_spindle_quick_set_100_clicked(self):
        self.w.scrb_axis4_spindle_rpm.setValue(500)

    def abtn_axis4_spindle_reverse_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def abtn_axis4_spindle_forward_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def abtn_axis4_spindle_stop_toggled(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def abtn_axis4_spindle_rpm_decrease_clicked(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name
    
    def abtn_axis4_spindle_rpm_increase_clicked(self,pressed):
        if pressed:
            name = self.w.sender().text()
            print name

    def scrb_axis4_spindle_rpm_setRange(self):
             value1 = self.w.sender().value()
             print "setRange",value1

    def scrb_axis4_spindle_rpm_setValue(self):
             value1 = self.w.sender().value()
             print "setValue",value1

    def scrb_axis4_spindle_rpm_valueChanged(self):
           value1 = self.w.sender().value()
           print "valueChanged",value1
           # the below to see progress bar move - will come from spindle encoder later
           self.w.pbar_axis4_spindle_rpm_ind_bar.setValue(value1)
        
    def pbtn_axis4_spindle_mode_enable_toggled(self):
          print "SPIN MODE"

    def pbar_axis4_spindle_rpm_ind_bar_setMinimum(self):
          print ""

    def pbar_axis4_spindle_rpm_ind_bar_setMaximum(self):
          print ""

    def pbar_axis4_spindle_rpm_ind_bar_setValue(self):
          print ""

    def lab_axis4_spindle_rpm_setText(self):
          print ""

# quick zero panel
# ===============================================================
    def abtn_select_joint_zero_x_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_y_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_z_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_a_clicked(self):
        name = self.w.sender().text()
        print name
    def abtn_select_joint_zero_b_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_c_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_u_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_v_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_select_joint_zero_w_clicked(self):
        name = self.w.sender().text()
        print name

# macro buttons panel - uses [MDI_COMMAND_LIST] in INI file
# ===============================================================
    def abtn_macro_1_clicked(self):
        name = self.w.sender().text()
        print name
    def abtn_macro_2_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_3_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_4_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_5_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_6_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_7_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_8_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_9_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_10_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_11_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_12_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_13_clicked(self):
        name = self.w.sender().text()
        print name


    def abtn_macro_14_clicked(self):
        name = self.w.sender().text()
        print name

    def abtn_macro_15_clicked(self):
        name = self.w.sender().text()
        print name

# override panel
# ===============================================================
    def abtn_override_spindle_rate_clicked(self):
        name = self.w.sender().text()
        print name

    def scrb_override_rate_spindle_setRange(self):
        print ""
        
    def scrb_override_rate_spindle_setValue(self,value):
        self.w.lab_override_rate_spindle.setText(str(value))

    def lab_override_rate_spindle_setText(self):
        print ""
#------
    def abtn_override_feed_rate_clicked(self):
        name = self.w.sender().text()
        print name
    
    def scrb_override_rate_feed_setRange(self):
        print ""

    def scrb_override_rate_feed_setValue(self,value):
        self.w.lab_override_rate_feed.setText(str(value))

    def lab_override_rate_feed_setText(self):
        print ""
#------
    def abtn_override_rapid_rate_clicked(self):
        name = self.w.sender().text()
        print name

    def scrb_override_rate_rapid_setRange(self):
        print ""
        
    def scrb_override_rate_rapid_setValue(self,value):
        self.w.lab_override_rate_rapid.setText(str(value))

    def lab_override_rate_rapid_setText(self):
        print ""
#------
    def abtn_override_jog_rate_clicked(self):
        name = self.w.sender().text()
        print name

    def scrb_override_rate_jog_setRange(self):
        print ""

    def scrb_override_rate_jog_setValue(self,value):
        self.w.lab_override_rate_jog.setText(str(value))

    def lab_override_rate_jog_setText(self):
        print ""
#------
    def abtn_override_angular_rate_clicked(self):
        name = self.w.sender().text()
        print name

    def scrb_override_rate_angular_setRange(self):
        print ""

    def scrb_override_rate_angular_setValue(self,value):
        self.w.lab_override_rate_angular.setText(str(value))

    def lab_override_rate_angular_setText(self):
        print ""

# dro_5_to_9 panel
# ===============================================================
# the panel has no buttons. dro's link automatically via status
  
# Gcode graphics display panel
# ===============================================================
    def abtn_graphics_view_z2_toggled(self):
        name = self.w.sender().text()
        print name

    def abtn_graphics_view_y2_toggled(self):
        name = self.w.sender().text()
        print name 

    def abtn_graphics_view_p_toggled(self):
        name = self.w.sender().text()
        print name
 
    def abtn_graphics_view_x_toggled(self):
        name = self.w.sender().text()
        print name 
 
    def abtn_graphics_view_y_toggled(self):
        name = self.w.sender().text()
        print name 
 
    def abtn_graphics_view_z_toggled(self):
        name = self.w.sender().text()
        print name 

    def abtn_graphics_clear_clicked(self):
        name = self.w.sender().text()
        print name

# status panel
# ===============================================================
    def lab_mcode_list_setText(self):
        name = self.w.sender().text()
        print name

    def lab_gcode_list_setText(self):
        name = self.w.sender().text()
        print name 

    def lab_tool_comment_setText(self):
        name = self.w.sender().text()
        print name

    def lab_feed_per_rev_setText(self):
        name = self.w.sender().text()
        print name

    def lab_tool_numb_setText(self):
        name = self.w.sender().text()
        print name

    def lab_tool_diam_setText(self):
        name = self.w.sender().text()
        print name

    def lab_feed_rate_setText(self):
        name = self.w.sender().text()
        print name

# jogging buttons with jog mode selection
# ===============================================================
    def abtn_jog_pos_x_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_neg_x_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_y_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_neg_y_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_z_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_neg_z_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_a_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_neg_a_clicked(self):
        name = self.w.sender().text()
        print name 

    def pbtn_jog_mode_position_toggled(self,pressed):
        if pressed:
            self.jog_mode=1 #position
            self.w.stackedWidget_5.setCurrentIndex(1)
            if self.jog_slow_fast==0: # slow jog
               self.jog_rate_selected_out=self.jograte_slow_position_value
            if self.jog_slow_fast==1: # fast jog
               self.jog_rate_selected_out=self.jograte_fast_position_value

    def pbtn_jog_mode_linear_toggled(self,pressed):
        if pressed:
            self.jog_mode=2 #linear
            self.w.stackedWidget_5.setCurrentIndex(0)
            if self.jog_slow_fast==0: # slow jog
               self.jog_rate_selected_out=self.jograte_slow_linear_value
            if self.jog_slow_fast==1: # fast jog
               self.jog_rate_selected_out=self.jograte_fast_linear_value
        
    def pbtn_jog_mode_angular_toggled(self,pressed):
        if pressed:
            self.jog_mode=3 #angular
            self.w.stackedWidget_5.setCurrentIndex(2)
            if self.jog_slow_fast==0: # slow jog
               self.jog_rate_selected_out=self.jograte_slow_angular_value
            if self.jog_slow_fast==1: # fast jog  
               self.jog_rate_selected_out=self.jograte_fast_angular_value

    def pbtn_jog_rate_slow_toggled(self,pressed):
        self.jog_slow_fast=0
        if pressed:
          if self.jog_mode==1:
               self.jog_rate_selected_out=self.jograte_slow_position_value
          elif self.jog_mode==2:
               self.jog_rate_selected_out=self.jograte_slow_linear_value
          elif self.jog_mode==3:
               self.jog_rate_selected_out=self.jograte_slow_angular_value

    def pbtn_jog_rate_fast_toggled(self,pressed):
        self.jog_slow_fast=1
        if pressed:
          if self.jog_mode==1:
               self.jog_rate_selected_out=self.jograte_fast_position_value
          elif self.jog_mode==2:
               self.jog_rate_selected_out=self.jograte_fast_linear_value
          elif self.jog_mode==3:
               self.jog_rate_selected_out=self.jograte_fast_angular_value

    def pbtn_jog_method_toggled(self,pressed):  # continuous or step mode select
        if pressed:
            self.w.jog_rate_action(False) # no such item - cont jog
            self.w.jog_incr_action(True)  # no such item - step jog link to linuxcnc
        else:
            self.w.jog_incr_action(False) # no such item - step jog
            self.w.jog_rate_action(True)  # no such item - cont jog link to linuxcnc
  
        name = self.w.sender().text()
        print name 
      
    def lab_jog_jog_rate_setText(self):
        name = self.w.sender().text()
        print name 

    def lab_jog_jog_step_setText(self):
        name = self.w.sender().text()
        print name
   
# position commands jogging panel
# ===============================================================
    def abtn_jog_pos_cmd_1_clicked(self,value):
        print value
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_2_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_3_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_4_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_5_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_6_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_7_clicked(self):
        name = self.w.sender().text()
        print name 

    def abtn_jog_pos_cmd_8_clicked(self):
        name = self.w.sender().text()
        print name 

    def scrb_jog_position_slow_setValue(self,value):
        self.w.lab_jog_position_slow.setText(str(value))
        if self.jog_slow_fast==0:
           self.jograte_slow_position_value=value
           self.jog_rate_selected_out=value
        if self.jog_slow_fast==1: # fast jog - slow slider moved update slow jog value   
           self.jograte_slow_position_value=value            

    def scrb_jog_position_fast_setValue(self,value):
        self.w.lab_jog_position_fast.setText(str(value))
        if self.jog_slow_fast==1:
           self.jograte_fast_position_value=value
           self.jog_rate_selected_out=value
        if self.jog_slow_fast==0:  # slow jog - fast slider moved update fast jog value  
           self.jograte_fast_position_value=value
 
    def scrb_jog_position_slow_setRange(self):
        print ""

    def scrb_jog_position_fast_setRange(self):
        print ""

    def lab_jog_position_slow_setText(self):
        print ""

    def lab_jog_position_fast_setText(self):
        print ""

# linear jogging panel and step sizes
# ===============================================================
    def pbtn_jog_linear_0_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_0.true_state_string
    
    def pbtn_jog_linear_1_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_1.true_state_string
 
    def pbtn_jog_linear_2_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_2.true_state_string

    def pbtn_jog_linear_3_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_3.true_state_string

    def pbtn_jog_linear_4_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_4.true_state_string

    def pbtn_jog_linear_5_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_5.true_state_string

    def pbtn_jog_linear_6_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_6.true_state_string

    def pbtn_jog_linear_7_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_7.true_state_string

    def pbtn_jog_linear_8_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_8.true_state_string

    def pbtn_jog_linear_9_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_9.true_state_string

    def pbtn_jog_linear_10_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_10.true_state_string

    def pbtn_jog_linear_11_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_11.true_state_string

    def pbtn_jog_linear_12_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_12.true_state_string

    def pbtn_jog_linear_13_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_13.true_state_string

    def pbtn_jog_linear_14_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_14.true_state_string

    def pbtn_jog_linear_15_toggled(self):
        self.jogStep=self.w.pbtn_jog_linear_15.true_state_string
        
    def scrb_jog_linear_slow_setValue(self,value):
        self.w.lab_jog_linear_slow.setText(str(value))
        if self.jog_slow_fast==0: #slow jog
           self.jograte_slow_linear_value=value
           self.jog_rate_selected_out=value
        if self.jog_slow_fast==1: # fast jog - slow slider moved - update slow jog value    
           self.jograte_slow_linear_value=value

    def scrb_jog_linear_fast_setValue(self,value):
        self.w.lab_jog_linear_fast.setText(str(value))
        if self.jog_slow_fast==1: #fast jog
           self.jograte_fast_linear_value=value
           self.jog_rate_selected_out=value
        if self.jog_slow_fast==0: # slow jog - fast slider moved - update fast jog value   
           self.jograte_fast_linear_value=value 
   
    def scrb_jog_linear_slow_setRange(self):
        print ""
        
    def scrb_jog_linear_fast_setRange(self):
        print "" 

    def lab_jog_linear_slow_setText(self):
        print ""

    def lab_jog_linear_fast_setText(self):
        print ""

# future angular jogging panel
#===============================================================
# just has lab_jog_mode_angular message for now
# could be used for common bolt hole circles from 2 to 10.
# it has space enough for 30 buttons

# help panel - for hal tools and other helfull such as g/m code tables main panel index 1
# ===============================================================
    def pbtn_help_calibration_clicked(self):
        os.popen("tclsh {0}/bin/emccalib.tcl -- -ini {1} > /dev/null &".format(TCLPATH, sys.argv[2]), "w")
        name = self.w.sender().text()
        print name 

    def pbtn_help_classicladder_clicked(self):
        os.popen("classicladder  &", "w")
        name = self.w.sender().text()
        print name 

    def pbtn_help_status_clicked(self):
        os.popen("linuxcnctop  > /dev/null &", "w")
        name = self.w.sender().text()
        print name 

    def pbtn_help_hal_meter_clicked(self):
        os.popen("halmeter &")
        name = self.w.sender().text()
        print name 

    def pbtn_help_hal_scope_clicked(self):
        os.popen("halscope  > /dev/null &", "w")
        name = self.w.sender().text()
        print name 

    def pbtn_help_hal_show_clicked(self):
        os.popen("tclsh {0}/bin/halshow.tcl &".format(TCLPATH))
        name = self.w.sender().text()
        print name  

# these provide the stacked panels that are called up by index number
# ===============================================================
    def stackedWidget_0_currentChanged(self):
        print "stackedWidget_0_index changed"

    def stackedWidget_1_currentChanged(self):
        print "stackedWidget_1_index changed"

    def stackedWidget_2_currentChanged(self):
        print "stackedWidget_2_index changed"

    def stackedWidget_3_currentChanged(self):
        print "stackedWidget_3_index changed"

    def stackedWidget_4_currentChanged(self,index):
        print "stackedWidget_4_index changed",index

    def stackedWidget_5_currentChanged(self):
        print "stackedWidget_5_index changed"


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
