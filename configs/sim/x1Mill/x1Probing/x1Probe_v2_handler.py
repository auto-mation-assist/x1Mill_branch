
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
#
#Notes
# to get a input value,   example:  offset_x= (self.w.input_adj_x.text())
# to set a status label,  example:  self.w.status_xm.setText(offset_x)
# to read a status label, example:  status_1=(self.w.status_xm.text())
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
import psutil  # used for killing embedded processes
import subprocess
import gtk
import gobject

import math
from linuxcnc import ini
import ConfigParser
from datetime import datetime
from subprocess import Popen, PIPE

CONFIGPATH1 = os.environ['CONFIG_DIR']
# set up paths for external programs support
TCLPATH = os.environ['LINUXCNC_TCL_DIR']

cp1 = ConfigParser.RawConfigParser
class ps_preferences(cp1):
    types = {
        bool: cp1.getboolean,
        float: cp1.getfloat,
        int: cp1.getint,
        str: cp1.get,
        repr: lambda self, section, option: eval(cp1.get(self, section, option)),
    }

    def __init__(self, path = None):
        cp1.__init__(self)
        if not path:
            path = "~/.toolch_preferences"
        self.fn = os.path.expanduser(path)
        self.read(self.fn)

    def getpref(self, option, default = False, type = bool):
        m = self.types.get(type)
        try:
            o = m(self, "DEFAULT", option)
        except Exception, detail:
            print detail
            self.set("DEFAULT", option, default)
            self.write(open(self.fn, "w"))
            if type in(bool, float, int):
                o = type(default)
            else:
                o = default
        return o

    def putpref(self, option, value, type = bool):
        self.set("DEFAULT", option, type(value))
        self.write(open(self.fn, "w"))


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
#        STATUS.connect('state-on', self.on_state_on)
#        STATUS.connect('state-off', self.on_state_off)
        self.jog_slow_fast=[] # required by jogging
        self.e = linuxcnc.error_channel()
        self.stat.poll()
        self.e.poll() 
#        self.prefs = ps_preferences( self.get_preference_file_path() )

             
       
# =================================================================
    def initialized__(self):
        STATUS.forced_update()
#        self.w.tooloffsetdialog._geometry_string='0 0 600 396'
#        self.w.originoffsetdialog._geometry_string='0 0 600 396 onwindow'
#        self.w.pbtn_axis4_select_spindle_toggled=True
  
        
# ================================================================
    def get_preference_file_path(self):
        # we get the preference file, if there is none given in the INI
        # we use toolchange2.pref in the config dir
        temp = self.inifile.find("DISPLAY", "PREFERENCE_FILE_PATH")
        if not temp:
            machinename = self.inifile.find("EMC", "MACHINE")
            if not machinename:
                temp = os.path.join(CONFIGPATH1, "probe_screen.pref")
            else:
                machinename = machinename.replace(" ", "_")
                temp = os.path.join(CONFIGPATH1, "%s.pref" % machinename)
        print("****  probe_screen GETINIINFO **** \n Preference file path: %s" % temp)
        return temp

#    def get_display(self):
#        # gmoccapy or axis ?
#        temp = self.inifile.find("DISPLAY", "DISPLAY")
#        if not temp:
#            print("****  probe_screen GETINIINFO **** \n Error recognition of display type : %s" % temp)
#        return temp

    def add_history(self,tool_tip_text,s="",xm=0.,xc=0.,xp=0.,lx=0.,ym=0.,yc=0.,yp=0.,ly=0.,z=0.,d=0.,a=0.):
#        c = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c = datetime.now().strftime('%H:%M:%S  ') + '{0: <10}'.format(tool_tip_text)  
        if "Xm" in s : 
            c += "X-=%.4f "%xm
        if "Xc" in s : 
            c += "Xc=%.4f "%xc
        if "Xp" in s : 
            c += "X+=%.4f "%xp
        if "Lx" in s : 
            c += "Lx=%.4f "%lx
        if "Ym" in s : 
            c += "Y-=%.4f "%ym
        if "Yc" in s : 
            c += "Yc=%.4f "%yc
        if "Yp" in s : 
            c += "Y+=%.4f "%yp
        if "Ly" in s : 
            c += "Ly=%.4f "%ly
        if "Z" in s : 
            c += "Z=%.4f "%z
        if "D" in s : 
            c += "D=%.4f"%d
        if "A" in s : 
            c += "Angle=%.3f"%a
        i=self.buffer.get_end_iter()
        if i.get_line() > 1000 :
            i.backward_line()
            self.buffer.delete(i,self.buffer.get_end_iter())
        i.set_line(0)
        self.buffer.insert(i, "%s \n" % c)

    def error_poll(self):
        error = self.e.poll()
#        if "axis" in self.display:
#            error_pin= Popen('halcmd getp probe.user.error ', shell=True, stdout=PIPE).stdout.read()
#       else:
#            error_pin= Popen('halcmd getp gmoccapy.error ', shell=True, stdout=PIPE).stdout.read()
#        if error:
#            kind, text = error
#            self.add_history("Error: %s" % text,"",0,0,0,0,0,0,0,0,0,0,0)            
#            if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
#
#                typus = "error"
#                print typus, text
#                return -1
#            else:
#                typus = "info"
#                print typus, text
#                return -1
#        else:
#            if "TRUE" in error_pin:
#                text = "User probe error"
#                self.add_history("Error: %s" % text,"",0,0,0,0,0,0,0,0,0,0,0)            
#                typus = "error"
#                print typus, text
#               return -1
        return 0



    # calculate corner coordinates in rotated coord. system
    def calc_cross_rott(self,x1=0.,y1=0.,x2=0.,y2=0.,a1=0.,a2=90.) :
        coord = [0,0]
        k1=math.tan(math.radians(a1))
        k2=math.tan(math.radians(a2))
        coord[0]=(k1*x1-k2*x2+y2-y1)/(k1-k2)
        coord[1]=k1*(coord[0]-x1)+y1
        return coord

    # rotate point coordinates
    def rott_point(self,x1=0.,y1=0.,a1=0.) :
        coord = [x1,y1]
        if a1 != 0:
            if self.chk_set_zero.get_active() :
                xc=self.spbtn_offs_x.get_value() 
                yc=self.spbtn_offs_y.get_value() 
            else :
                self.stat.poll()
                xc=self.stat.position[0]-self.stat.g5x_offset[0] - self.stat.g92_offset[0] - self.stat.tool_offset[0]
                yc=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
            t = math.radians(a1)
            coord[0] = (x1-xc) * math.cos(t) - (y1-yc) * math.sin(t) + xc
            coord[1] = (x1-xc) * math.sin(t) + (y1-yc) * math.cos(t) + yc
        return coord

    # rotate around 0,0 point coordinates
    def rott00_point(self,x1=0.,y1=0.,a1=0.) :
        coord = [x1,y1]
        if a1 != 0:
            t = math.radians(a1)
            coord[0] = x1 * math.cos(t) - y1 * math.sin(t)
            coord[1] = x1 * math.sin(t) + y1 * math.cos(t)
        return coord

    def probed_position_with_offsets(self) :
        self.stat.poll()
        probed_position=list(self.stat.probed_position)
        coord=list(self.stat.probed_position)
        g5x_offset=list(self.stat.g5x_offset)
        g92_offset=list(self.stat.g92_offset)
        tool_offset=list(self.stat.tool_offset)
#        print "g5x_offset=",g5x_offset
#        print "g92_offset=",g92_offset
#        print "tool_offset=",tool_offset
#        print "actual position=",self.stat.actual_position
#        print "position=",self.stat.position
#        print "joint_actual position=",self.stat.joint_actual_position
#        print "joint_position=",self.stat.joint_position
#        print "probed position=",self.stat.probed_position
        for i in range(0, len(probed_position)-1):
             coord[i] = probed_position[i] - g5x_offset[i] - g92_offset[i] - tool_offset[i]
        angl=self.stat.rotation_xy
        res=self.rott00_point(coord[0],coord[1],-angl)
        coord[0]=res[0]
        coord[1]=res[1]
        return coord


# =================================================================
    def initialized__(self):
        STATUS.forced_update()
        gobject.timeout_add(100, self._periodic)

        # jogging rate set default values
#        self.jograte_slow_position_value=7
#        self.jograte_fast_position_value=10
#        self.jograte_slow_linear_value=5
#        self.jograte_fast_linear_value=8 
#        self.jograte_slow_angular_value=5
#        self.jograte_fast_angular_value=9
      
          

# end init self
# =================================================================

    def gcode(self,s, data = None): 
        for l in s.split("\n"):
            if "G1" in l :
                l+= " F#<_ini[TOOLSENSOR]RAPID_SPEED>"
            self.cmnd.mdi( l )
            self.cmnd.wait_complete()
            if self.error_poll() == -1:
                return -1
        return 0

    def ocode(self,s, data = None):	
        self.cmnd.mdi(s)
        self.stat.poll()
        while self.stat.exec_state == 7 or self.stat.exec_state == 3 :
            if self.error_poll() == -1:
                return -1
            self.cmnd.wait_complete()
            self.stat.poll()
        self.cmnd.wait_complete()
        if self.error_poll() == -1:
            return -1
        return 0

    def z_clearance_down(self, data = None):
        # move Z - z_clearance
        s="""G91
        G1 Z-%f
        G90""" % float(self.w.input_xy_clearances.text())       
        if self.gcode(s) == -1:
            return -1
        return 0

    def z_clearance_up(self, data = None):
        # move Z + z_clearance
        s="""G91
        G1 Z%f
        G90""" % float(self.w.input_xy_clearances.text())        
        if self.gcode(s) == -1:
            return -1
        return 0

    def rotate_coord_system(self,a=0.):
        if  self.w.pbtn_allow_auto_skew.isChecked():
             print "Yes"
             self.w.input_adj_angle.setText("%.3f" %  a)             ### <<<<<<<<<<<<<<<<<<<<<<<<
             self.w.status_a.setText( "%.3f" % a)          ### <<<<<<<<<<<<<<<<<<<<<<<<
             s="G10 L2 P0"
             if self.w.pbtn_allow_auto_zero.isChecked():
                s +=  " X%s"% float(self.w.input_adj_x.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<    
                s +=  " Y%s"% float(self.w.input_adj_y.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<    
        else :
                print "Not yes"
                self.stat.poll()
                x=self.stat.position[0]
                y=self.stat.position[1]
                s +=  " X%s"%x      
                s +=  " Y%s"%y      
        s +=  " R%s"%a                      
        self.gcode(s)
        print s
        time.sleep(1)

#        STATUS.connect('periodic', self._periodic)
        gobject.timeout_add(100, self._periodic)


# start periodic
# =================================================================
#        STATUS.connect('periodic', self._periodic)
    def _periodic(self):

#        self.w.lab_jog_jog_rate.setText(str(self.jog_rate_selected_out))
#        self.w.lab_jog_jog_step.setText(str(self.jogStep))
#        distance = STATUS.get_jog_rate()
#        print "jog increment", distance 

#        self.w.abtn_jog_pos_a.setEnabled(False) # sim only has 3 axis so keep these disabled
#        self.w.abtn_jog_neg_a.setEnabled(False) # sim only has 3 axis so keep these disabled

#        STATUS.set_jograte(float(3))

        return True

# end periodic
# =====================================


       
# This is ready for verser code insertion
# and modification to except new names for improved clarity
# Further work or moifications may be required for the
# status labels and the inputs for value entries.
# The input for value entries are giving error messages.
# ===============================================================

# Outside measurements
# ===============================================================

# button 1 outside corner measurement X+Y-
# ===============================================================
    def pbtn_outside_xpym_released(self):
        print  "1 xpym_released "
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()           ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X - xy_clearance Y + edge_lenght
        s="""G91
        G1 X-%f Y-%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0]+0.5* float(self.w.input_probe_diam.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xres) ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + edge_lenght +xy_clearance,  Y + edge_lenght + xy_clearance
        a=float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f Y%f
        G90""" % (a,a)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])-0.5* float(self.w.input_probe_diam.text()) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % yres ) ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"XpLxYmLy",0,0,xres,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")


# button 2 outside and inside straight in measurement Y-
# =============================================================== 
    def pbtn_outside_ym_released(self):
        print  "2 outside_ym_released - also inside_ym_released"
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
         # move Y + xy_clearance
        s="""G91
        G1 Y%f
        G90""" % float(self.w.input_xy_clearances.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        a=self.probed_position_with_offsets()
        yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % yres )   ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"YmLy",0,0,0,0,yres,0,0,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 Y%f" % yres
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("Y")

# button 3 outside corner measurement X-Y-
# =========================================================================
    def pbtn_outside_xmym_released(self):
    	print  "3 outside_xmym_released "
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X + xy_clearance Y - edge_lenght
        s="""G91
        G1 X%f Y-%f
        G90""" % (float(self.w.input_xy_clearances.text()), float(self.w.input_side_edge_lenght.text()) )   ### <<<<<<<<<<<<<<<<<<<<<<<<     
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0]-0.5* float(self.w.input_probe_diam.text())) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<     
#        self.lenght_x()
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X - edge_lenght - xy_clearance,  Y + edge_lenght + xy_clearance
        a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()))  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X-%f Y%f
        G90""" % (a,a)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])-0.5* float(self.w.input_probe_diam.text()) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText("%.4f" % yres )
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XmLxYmLy",xres,0,0,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")


# button 4 outside and inside straight in measurement X+
# ========================================================================= 
    def pbtn_outside_xp_released(self):
    	print  "4 outside_xp_released - also on inside_xp_released"
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
         # move X - xy_clearance
        s="""G91
        G1 X-%f
        G90""" % float(self.w.input_xy_clearances.text() )    ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
       # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        a=self.probed_position_with_offsets()
        xres=float(a[0]+0.5* float(self.w.input_probe_diam.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()
#        self.add_history(gtkbutton.get_tooltip_text(),"XpLx",0,0,xres,self.lenght_x(),0,0,0,0,0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f" % xres
        if self.gcode(s) == -1:
            return
#        self.set_zerro("X")
        print s


    def pbtn_outside_center_released(self):
          print  "5 outside_center_released "
# button 5 outside center measurement X+ X- Y+ Y-       
# =========================================================================
    def pbtn_outside_center_released(self):
    	print  "5 outside_center_released "
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete() ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X - edge_lenght- xy_clearance
        s="""G91
        G1 X-%f
        G90""" % (float(self.w.input_side_edge_lenght.text()) +float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text()) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xpres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + 2 edge_lenght + 2 xy_clearance
        aa=2*(float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f
        G90""" % (aa)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc

        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xmres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        xcres=0.5*(xpres+xmres)
        self.w.status_xc.setText( "%.4f" % xcres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # distance to the new center of X from current position
#        self.stat.poll()
#        to_new_xc=self.stat.position[0]-self.stat.g5x_offset[0] - self.stat.g92_offset[0] - self.stat.tool_offset[0] - xcres
        s = "G1 X%f" % xcres
        if self.gcode(s) == -1:
            return


        # move Y - edge_lenght- xy_clearance 
        a=(float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 Y-%f
        G90""" % a
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ypres=float(a[1])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % ypres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move Y + 2 edge_lenght + 2 xy_clearance
        aa=2* (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 Y%f
        G90""" % (aa)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % ymres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
        # find, show and move to finded  point
        ycres=0.5*(ypres+ymres)
        self.w.status_yc.setText( "%.4f" % ycres ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        diam=0.5*((xmres-xpres)+(ymres-ypres))
        self.w.status_d.setText( "%.4f" % diam )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"XmXcXpLxYmYcYpLyD",xmres,xcres,xpres,self.lenght_x(),ymres,ycres,ypres,self.lenght_y(),0,diam,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 Y%f" % ycres
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

# button 6 outside and inside straight in measurement X-
# ========================================================================= 
    def pbtn_outside_xm_released(self):
    	print  "6 outside_xm_released - also on inside_xm_released"
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
         # move X + xy_clearance
        s="""G91
        G1 X%f
        G90""" % float(self.w.input_xy_clearances.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        a=self.probed_position_with_offsets()
        xres=float(a[0]-0.5* float(self.w.input_probe_diam.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xres ) ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()
#        self.add_history(gtkbutton.get_tooltip_text(),"XmLx",xres,0,0,self.lenght_x(),0,0,0,0,0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f" % xres
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("X")

# button 7 outside corner measurement X+Y+
# ========================================================================= 
    def pbtn_outside_xpyp_released(self):
    	print  "7 outside_xpyp_released "
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X - xy_clearance Y + edge_lenght
        s="""G91
        G1 X-%f Y%f
        G90""" % (float(self.w.input_xy_clearances.text()), float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres= float(a[0]+0.5* float(self.w.input_probe_diam.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xres )
#        self.lenght_x()
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + edge_lenght +xy_clearance,  Y - edge_lenght - xy_clearance
        a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f Y-%f
        G90""" % (a,a)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())   ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XpLxYpLy",0,0,xres,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

# button 8 outside and inside straight in measurement Y+
# ========================================================================= 
    def pbtn_outside_yp_released(self):
    	print  "8 outside_yp_released - also on inside_yp_released"
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
         # move Y - xy_clearance
        s="""G91
        G1 Y-%f
        G90""" % float(self.w.input_xy_clearances.text())   ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        a=self.probed_position_with_offsets()
        yres=float(a[1])+0.5* float(self.w.input_probe_diam.text()) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"YpLy",0,0,0,0,0,0,yres,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 Y%f" % yres
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("Y")

# button 9 outside corner measurement X-Y+
# =========================================================================
    def pbtn_outside_xmyp_released(self):
    	print  "9 outside_xmyp_released "
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X + xy_clearance Y + edge_lenght
        s="""G91
        G1 X%f Y%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0]-0.5* float(self.w.input_probe_diam.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X - edge_lenght - xy_clearance,  Y - edge_lenght - xy_clearance
        a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X-%f Y-%f
        G90""" % (a,a)        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XmLxYpLy",xres,0,0,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

# button 1 inside corner measurement X-Y+
# =========================================================================       
    def pbtn_inside_xmyp_released(self):
    	print  "1 inside_xmyp_released "
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Y - edge_lenght X + xy_clearance
        s="""G91
        G1 X%f Y-%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()

        # move X + edge_lenght Y - xy_clearance
        tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f Y%f
        G90""" % (tmpxy,tmpxy)        
        if self.gcode(s) == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return

        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XmLxYpLy",xres,0,0,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s 
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

# button 3 inside corner measurement X+Y+        
# =========================================================================        
    def pbtn_inside_xpyp_released(self):
    	print  "3 inside_xpyp_released"
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Y - edge_lenght X - xy_clearance
        s="""G91
        G1 X-%f Y-%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()

        # move X - edge_lenght Y - xy_clearance
        tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X-%f Y%f
        G90""" % (tmpxy,tmpxy)        
        if self.gcode(s) == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XpLxYpLy",0,0,xres,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

# button 5 inside hole center measurement Xin- Xin+ Yin- Yin+
# =========================================================================
    def pbtn_inside_xy_hole_released(self):
    	print  "5 inside_xy_hole_released"
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        if self.z_clearance_down() == -1:
            return
        # move X - edge_lenght Y + xy_clearance
        tmpx= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X-%f
        G90""" % (tmpx)        
        if self.gcode(s) == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xmres )  ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move X +2 edge_lenght - 2 xy_clearance
        tmpx=2* (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f
        G90""" % (tmpx)        
        if self.gcode(s) == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xpres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()
        xcres=0.5*(xmres+xpres)
        self.w.status_xc.setText( "%.4f" % xcres )  ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move X to new center
        s="""G1 X%f""" % (xcres)        
        if self.gcode(s) == -1:
            return

        # move Y - edge_lenght + xy_clearance
        tmpy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 Y-%f
        G90""" % (tmpy)        
        if self.gcode(s) == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % ymres )  ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move Y +2 edge_lenght - 2 xy_clearance
        tmpy=2* (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 Y%f
        G90""" % (tmpy)        
        if self.gcode(s) == -1:
            return
        # Start yplus.ngc
        if self.ocode ("O<yplus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ypres=float(a[1])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yp.setText( "%.4f" % ypres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
        # find, show and move to finded  point
        ycres=0.5*(ymres+ypres)
        self.w.status_yc.setText( "%.4f" % ycres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        diam=0.5*((xpres-xmres)+(ypres-ymres))
        self.w.status_d.setText( "%.4f" % diam )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"XmXcXpLxYmYcYpLyD",xmres,xcres,xpres,self.lenght_x(),ymres,ycres,ypres,self.lenght_y(),0,diam,0)  
        # move to center
        s = "G1 Y%f" % ycres
        print s
        if self.gcode(s) == -1:
            return
        # move Z to start point
        self.z_clearance_up()
 #       self.set_zerro("XY")

# button 7 inside corner measurement X-Y-        
# =========================================================================          
    def pbtn_inside_xmym_released(self):
    	print  "7 inside_xmym_released"
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Y + edge_lenght X + xy_clearance
        s="""G91
        G1 X%f Y%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )   ### <<<<<<<<<<<<<<<<<<<<<<<<     
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xm.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()

        # move X + edge_lenght Y - xy_clearance
        tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X%f Y-%f
        G90""" % (tmpxy,tmpxy)        
        if self.gcode(s) == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XmLxYmLy",xres,0,0,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)  ### <<<<<<<<<<<<<<<<<<<<<<<<
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")

    def pbtn_inside_xpym_released(self):
          print  "9 inside_xpym_released "
# button 9 inside corner measurement X+Y-
# ========================================================          
    def pbtn_inside_xpym_released(self):
    	print  "9 inside_xpym_released "
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Y + edge_lenght X - xy_clearance
        s="""G91
        G1 X-%f Y%f
        G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_x()

        # move X - edge_lenght Y + xy_clearance
        tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        s="""G91
        G1 X-%f Y-%f
        G90""" % (tmpxy,tmpxy)        
        if self.gcode(s) == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % yres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.lenght_y()
#        self.add_history(gtkbutton.get_tooltip_text(),"XpLxYmLy",0,0,xres,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move to finded  point
        s = "G1 X%f Y%f" % (xres,yres)
        print s
        if self.gcode(s) == -1:
            return
#        self.set_zerro("XY")
 
# button 1 skew measurement X+X+
# ===============================================================
    def pbtn_skew_xp_released(self):
    	print "1 skew_xp_released"
        self.stat.poll()
        ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X - xy_clearance
        s="""G91
        G1 X-%f
        G90""" % float(self.w.input_xy_clearances.text())        
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xcres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xc.setText( "%.4f" % xcres )  ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move Y - edge_lenght
        s="""G91
        G1 Y-%f
        G90""" % float(self.w.input_side_edge_lenght.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        if self.gcode(s) == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xpres ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        alfa=math.degrees(math.atan2(xcres-xpres,float(self.w.input_side_edge_lenght.text())) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"XcXpA",0,xcres,xpres,0,0,0,0,0,0,0,alfa)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move XY to adj start point
        s="G1 X%f Y%f" % (xcres,ystart)
        print s
        if self.gcode(s) == -1:
            return
        self.rotate_coord_system(alfa)
 

# button 2 skew measurement Y-Y-
# ===============================================================
    def pbtn_skew_ym_released(self):
    	print "2 skew_ym_released"
        self.stat.poll()
        xstart=self.stat.position[0]-self.stat.g5x_offset[0] - self.stat.g92_offset[0] - self.stat.tool_offset[0]
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()     ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move Y + xy_clearance
        s="""G91
        G1 Y%f
        G90""" % float(self.w.input_xy_clearances.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<     
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ycres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_yc.setText( "%.4f" % ycres )  ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move X - edge_lenght
        s="""G91
        G1 X-%f
        G90""" % float(self.w.input_side_edge_lenght.text())   ### <<<<<<<<<<<<<<<<<<<<<<<<      
        if self.gcode(s) == -1:
            return
        # Start yminus.ngc
        if self.ocode ("O<yminus> call") == -1:
            return
        # show Y result
        a=self.probed_position_with_offsets()
        ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_ym.setText( "%.4f" % ymres )
#        alfa=math.degrees(math.atan2(ycres-ymres,float(self.w.input_side_edge_lenght.text()) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"YmYcA",0,0,0,0,ymres,ycres,0,0,0,0,alfa)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move XY to adj start point
        s="G1 X%f Y%f" % (xstart,ycres)
        print s
        return
#        self.rotate_coord_system(alfa)

# button 3 skew measurement X+X+
# ===============================================================
    def pbtn_skew_yp_released(self):
    	print "3 skew_yp_released"
        self.stat.poll()
        ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # move X - xy_clearance
        s="""G91
        G1 X-%f
        G90""" % float(self.w.input_xy_clearances.text())   ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xcres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xc.setText( "%.4f" % xcres )   ### <<<<<<<<<<<<<<<<<<<<<<<<

        # move Y - edge_lenght
        s="""G91
        G1 Y-%f
        G90""" % float(self.w.input_side_edge_lenght.text())   ### <<<<<<<<<<<<<<<<<<<<<<<<     
        if self.gcode(s) == -1:
            return
        # Start xplus.ngc
        if self.ocode ("O<xplus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.w.status_xp.setText( "%.4f" % xpres )  ### <<<<<<<<<<<<<<<<<<<<<<<<
        alfa=math.degrees(math.atan2(xcres-xpres, float(self.w.input_side_edge_lenght.text())) )
#        self.add_history(gtkbutton.get_tooltip_text(),"XcXpA",0,xcres,xpres,0,0,0,0,0,0,0,alfa)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move XY to adj start point
        s="G1 X%f Y%f" % (xcres,ystart)
        print s
        if self.gcode(s) == -1:
            return
#        self.rotate_coord_system(alfa)

# button 4 skew measurement X-X-       
# ===============================================================
    def pbtn_skew_xm_released(self):
    	print "4 skew_xm_released"
        self.stat.poll()
        ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
        self.cmnd.mode( linuxcnc.MODE_MDI )  ### <<<<<<<<<<<<<<<<<<<<<<<< 
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<< 
        # move X + xy_clearance
        s="""G91
        G1 X%f
        G90""" % float(self.w.input_xy_clearances.text())    ### <<<<<<<<<<<<<<<<<<<<<<<<       
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xcres=float(a[0])-0.5* float(self.w.input_probe_diam.text())   ### <<<<<<<<<<<<<<<<<<<<<<<< 
        self.w.status_xc.setText( "%.4f" % xcres )

        # move Y + edge_lenght
        s="""G91
        G1 Y%f
        G90""" % float(self.w.input_side_edge_lenght.text())        ### <<<<<<<<<<<<<<<<<<<<<<<< 
        if self.gcode(s) == -1:
            return
        # Start xminus.ngc
        if self.ocode ("O<xminus> call") == -1:
            return
        # show X result
        a=self.probed_position_with_offsets()
        xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())  ### <<<<<<<<<<<<<<<<<<<<<<<< 
        self.w.status_xm.setText( "%.4f" % xmres )   ### <<<<<<<<<<<<<<<<<<<<<<<< 
        alfa=math.degrees(math.atan2(xcres-xmres,float(self.w.input_side_edge_lenght.text())) )  ### <<<<<<<<<<<<<<<<<<<<<<<< 
#        self.add_history(gtkbutton.get_tooltip_text(),"XmXcA",xmres,xcres,0,0,0,0,0,0,0,0,alfa)
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        # move XY to adj start point
        s="G1 X%f Y%f" % (xcres,ystart)
        print s 
        if self.gcode(s) == -1:
            return
#        self.rotate_coord_system(alfa)

# Straight down measurement down
# ===============================================================
    def pbtn_down_released(self):
    	print "down_released"
        self.cmnd.mode( linuxcnc.MODE_MDI ) ### <<<<<<<<<<<<<<<<<<<<<<<<
        self.cmnd.wait_complete()  ### <<<<<<<<<<<<<<<<<<<<<<<<
        # Start down.ngc
        if self.ocode ("O<down> call") == -1:
            return
        a=self.probed_position_with_offsets()
        self.w.status_z.setText( "%.4f" % float(a[2]) )  ### <<<<<<<<<<<<<<<<<<<<<<<<
#        self.add_history(gtkbutton.get_tooltip_text(),"Z",0,0,0,0,0,0,0,0,a[2],0,0)
#        self.set_zerro("Z",0,0,a[2])          

# Additions for version 2 - two more in input section
# ===============================================================
    def pbtn_inside_lenght_x_released(self):
        print "pbtn_inside_lenght_x_released"
    def pbtn_outside_lenght_x_released(self):
        print "pbtn_outside_lenght_x_released"
    def pbtn_inside_lenght_y_released(self):
        print "pbtn_inside_lenght_y_released"
    def pbtn_outside_lenght_y_released(self):
        print "pbtn_outside_lenght_y_released"
    def pbtn_measure_diam_released(self):
        print "pbtn_measure_diam_released"

# Auto zero and auto skew allow or not to allow
# This has two associated warming LED's
# ===============================================================
    def pbtn_allow_auto_zero_toggle(self,pressed):
        if pressed:
#             self.w.led_auto_zero_warning=True
             print "allow_auto_zero"
        else:
            print "dont allow_auto_zero"
    def pbtn_allow_auto_skew_toggle(self,pressed):
        if pressed:
#            self.w.led_auto_skew_warning=True
            print "allow_auto_skew"
        else:
            print "dont allow_auto_skew"

# Set offsets for values entered by inputs
# ===============================================================
    def pbtn_set_x_released(self):
        print "set_x_released"
#        self.prefs.putpref( "ps_offs_x", float(self.w.input_adj_x.text()) )
        self.cmnd.mode( linuxcnc.MODE_MDI )
        self.cmnd.wait_complete() 
        self.cmnd.mdi( "G10 L20 P0 X%f" % float(self.w.input_adj_x.text()) )
        time.sleep(1)
 
    def pbtn_set_y_released(self):
        print "set_y_released"
#        self.prefs.putpref( "ps_offs_y", float(self.w.input_adj_y.text()) )
        self.cmnd.mode( linuxcnc.MODE_MDI )
        self.cmnd.wait_complete()
        self.cmnd.mdi( "G10 L20 P0 Y%f" % float(self.w.input_adj_y.text()) )
        time.sleep(1)

    def pbtn_set_z_released(self): # old = on_btn1_set_z_released
        print "set_z_released"
#        self.prefs.putpref( "ps_offs_z", float(self.w.input_adj_z.text()) )
        self.cmnd.mode( linuxcnc.MODE_MDI )
        self.cmnd.wait_complete()
        self.cmnd.mdi( "G10 L20 P0 Z%f" % float(self.w.input_adj_z.text()) )
        time.sleep(1)

    def pbtn_set_angle_released(self): # old = on_btn1_set_angle
        print "set_angle_released"
#        self.prefs.putpref( "ps_offs_angle", float(self.w.input_adj_angle.text()) )
        self.w.status_a.setText( "%.3f" % float(self.w.input_adj_angle.text()) )
        self.cmnd.mode( linuxcnc.MODE_MDI )
        self.cmnd.wait_complete()
        s="G10 L2 P0"
        if self.w.pbtn_allow_auto_zero.isChecked():         ###<<<<<<<<<<<<<<<<<<<<
            s +=  " X%.4f"% float(self.w.input_adj_x.text())      
            s +=  " Y%.4f"% float(self.w.input_adj_y.text())    
        else :
            self.stat.poll()
            x=self.stat.position[0]
            y=self.stat.position[1]
            s +=  " X%.4f"%x      
            s +=  " Y%.4f"%y      
        s +=  " R%.4f"% float(self.w.input_adj_angle.text())
        print "s=",s                     
        self.gcode(s)
        time.sleep(1)

# Inputs for the offest values above
# ===============================================================
    def input_adj_x_enter(self):
        offset_x= (self.w.input_adj_x.text())
        print "offset_x ",offset_x
# to set a status label 
        self.w.status_xm.setText(offset_x)
# to read a status label
        status_1=(self.w.status_xm.text())
        print "Status_1 ",status_1

    def input_adj_y_enter(self):
        offset_y= (self.w.input_adj_y.text())
        print "offset_y ",offset_y 
# to set a status label 
        self.w.status_xp.setText(offset_y)
# to read a status label
        status_2=(self.w.status_xp.text())
        print "Status_2 ",status_2

    def input_adj_z_enter(self):
        offset_z= (self.w.input_adj_z.text())
        print "offset_z ",offset_z 
# to set a status label 
        self.w.status_ym.setText(offset_z)
# to read a status label
        status_3=(self.w.status_ym.text())
        print "Status_3 ",status_3 

    def input_adj_angle_enter(self):
        offset_angle= (self.w.input_adj_angle.text())
        print "offset_angle ",offset_angle  
# to set a status label 
        self.w.status_yp.setText(offset_angle)
# to read a status label
        status_4=(self.w.status_yp.text())
        print "Status_4 ",status_4

# Inputs - for primary values
# ===============================================================
    def input_probe_diam_enter(self):
        probe_diam= (self.w.input_probe_diam.text())
        print "input Probe_diam ",probe_diam
    def input_max_travel_enter(self):
        max_travel= (self.w.input_max_travel.text())
        print "input max_travel ",max_travel
    def input_latch_return_dist_enter(self):
        latch_return_dist= (self.w.input_latch_return_dist.text())
        print "input latch_return_dist ",latch_return_dist
    def input_search_vel_enter(self):
        search_vel= (self.w.input_search_vel.text())
        print "input search_vel ",search_vel
    def input_probe_vel_enter(self):
        probe_vel= (self.w.input_probe_vel.text())
        print "input probe_vel ",probe_vel
    def input_side_edge_lenght_enter(self):
        side_edge_lenght= (self.w.input_side_edge_lenght.text())
        print "input side_edge_lenght ",side_edge_lenght
    def input_xy_clearances_enter(self):
        xy_clearances= (self.w.input_xy_clearances.text())
        print "input xy_clearances ",xy_clearances
    def input_z_clearance_enter(self):
        z_clearance= (self.w.input_z_clearance.text())
        print "input z_clearance ",z_clearance

    def input_tool_sensor_height_enter(self):
        tool_sensor_height= (self.w.input_tool_sensor_height.text())
        print "input_tool_sensor_height", tool_sensor_height

    def input_work_probe_height_enter(self):
        work_probe_height= (self.w.input_work_probe_height.text())
        print "input_work_probe_height", work_probe_height

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
