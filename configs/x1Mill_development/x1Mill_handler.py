    # 01-14-2019 22:07 Alaska time
# x1Mill_handler.py for the associated x1Mill.ui
# Copyright (c) 2018 Johannes P Fassotte x1Mill, x1Lathe, x1gantry
# This gui (x1Mill) is for use with QTvcp a modified version of QTvcp by Chris Morley
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

# Items withing this gui are identified by a location key
# Refer to the master layout map and then search for Frame_0 or other number to locate desired one.
# In HAL show pins will have reference to Frame number such as fr1, fr8 ect.
#
# Coding will be changing and moved around as needed
#
# You should print out the below info - Do not delete it


# >>>> indents are: Tab 3 <<<< #

# ======================================================================== #
# The x1Mill gui uses an expanded .ini file so this
# must be in the display section of the x1mill.ini file.
# 	[DISPLAY]
# 	DISPLAY = qtvcp -d x1Mill
# 	#INCLUDE x1Mill_pref.inc
# It must have '#INCLUDE' and the added parameter file, 'x1Mill_pref.inc')
# ======================================================================== #

# machine related variables
# -------------------------------------------------------------------------
# self.machine_info[0] machine units: 1 = inch, 2 = metric - from ini file and verified
# self.machine_info[1] angular units: deg=0, degree=1, rad=2, radian=3, grad=4, gon=5
# self.machine_info[2] units convert: 0 = no conversion 1 = to inch, 2 = to metric
# self.machine_info[3] jogging in progress: 0 = no, 1 = Yes, 2 = mdi cmd being used
# self.machine_info[4] homing in progress:  0 = no 1 = yes

# self.homing_control[0]   homing panel open = 1,
# self.homing_control[1] 	axis number or axis combination number
# self.homing_control[2]	homing z = 1, z home completed = 2
# self.homing_control[3]	enable homing state check for self.machine_info[4]

# Jogging control info - values are -1 at start up or have not been updated
# -------------------------------------------------------------------------
# self.jog_control[0]  =  jogging allowed: 0 = no, 1 = yes
# self.jog_control[1]  =  jogging mode: 1 = position  2 = linear 3 = angular
# self.jog_control[2]  =  jogging type: 1 = continous  2 = incremental
# self.jog_control[3]  =  jog rate: 1 = jog slow  2 = jog fast
# self.jog_control[4]  =  axis-joint number:  0,1,2,3,4,5,6,7,8
# self.jog_control[5]  =  direction: 1 = pos, -1 = neg
# self.jog_control[6]  =  increment list in use: 1 = inch, 2 = metric - from ini file and verified
# self.jog_control[7]  =  current inch increment index: 0 to 19
# self.jog_control[8]  =  curent metric increment index: 0 to 19
# self.jog_control[9]  =  current angular increment index: 0 to 19
# self.jog_control[10] =  mdi position cmd: 1 = send cmd, -1 = no action or cmd completed

# self.jog_rates[0]	=  inch increment value
# self.jog_rates[1]	=  metric increment value
# self.jog_rates[2]	=  angular increment value
# self.jog_rates[3]	=  position slow rate value
# self.jog_rates[4]	=  position fast rate value
# self.jog_rates[5]	=  linear slow rate value
# self.jog_rates[6]	=  linear fast rate value
# self.jog_rates[7]	=  angular slow rate value
# self.jog_rates[8]	=  angular fast rate value


# inch jogging increment list
# -------------------------------------------------------------------------
# self.inch_increments[0:19]	= inch jogging increment data
# self.inch_increments[20]		= default inch increment
# >>>>> self.inch_incr_list

# inch metric jogging increment list
# -------------------------------------------------------------------------
# self.metric_increments[0:19]	= metric jogging increment data
# self.metric_increments[20]	= default metric increment
# >>>>> self.metric_incr_list

# angular jogging increment list
# -------------------------------------------------------------------------
# self.angular_increments[0:19]	= angular jogging increment data
# self.angular_increments[20]	= default angular increment
# >>>> self.angular_incr_list
# -------------------------------------------------------------------------
# self.spindle0[0]  =  spindle endbale: 0 = disabled 1 = enable
# self.spindle0[1]  =  spindle control: 0 = off, 1 = on, 2 = reverse
# self.spindle0[2]  =  rpm value to spindle
# self.spindle0[3]  =  default rpm value
# self.spindle0[4]  =  slider min rpm
# self.spindle0[5]  =  slider max rpm
# self.spindle0[6]  =  quick  set 0 value
# self.spindle0[7]  =  quick  set 1 value
# self.spindle0[8]  =  quick  set 2 value
# self.spindle0[9]  =  quick  set 3 value


import gtk
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
from qtvcp.core import Status #######, Action
from qtvcp import logger

import linuxcnc
import sys
import os
import psutil  # used for killing embedded processes
import subprocess
import gobject
import math
import time
import hal
import ConfigParser
from linuxcnc import ini
from time import gmtime, strftime
from subprocess import Popen, PIPE
from os.path import abspath, dirname, join

TCLPATH = os.environ['LINUXCNC_TCL_DIR'] # set up paths for external programs support
GSTAT = Status()
#ACTION = Action()
LOG = logger.getLogger(__name__)
LOG.setLevel(logger.INFO) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL
#DEBUG = 0x7FFFFFFF
DEBUG = 0

# 	  for reading my own perferences file
#cp1 = ConfigParser.RawConfigParser
#class x1m_preferences(cp1):
#	types = {
#	   bool: cp1.getboolean,
#	    float: cp1.getfloat,
#	     int: cp1.getint,
#	     str: cp1.get,
#	     repr: lambda self, section, option: eval(cp1.get(self, section, option)),
#	}
#
#	def __init__(self, path = None):
#		cp1.__init__(self)
#		if not path:
#			path = '~/.toolch_preferences'  # <<<=====  Will need to change this
#		self.fn = os.path.expanduser(path)
#		self.read(self.fn)

#	def getpref(self, option, default = False, type = bool):
#		m = self.types.get(type)
#		try:
#			o = m(self, 'DEFAULT', option)
#		except Exception, detail:
#			print detail
#			self.set('DEFAULT', option, default)
#			self.write(open(self.fn, 'w'))
#			if type in(bool, float, int):
#				o = type(default)
#			else:
#				o = default
#		return o
#
#	def putpref(self, option, value, type = bool):
#		self.set('DEFAULT', option, type(value))
#		self.write(open(self.fn, 'w'))

# -------------------------------------------------------------------------
class HandlerClass:
	def __init__(self, halcomp, widgets, paths):
		self.hal  = halcomp
		self.w  = widgets
		self.stat  = linuxcnc.stat()
		self.c  = linuxcnc.command()
		self.e  = linuxcnc.error_channel()

		# GSTAT = QTvcp STATUS to catch linuxcnc events. STATUS is defined in core.py
		GSTAT.connect('state-on',  self.on_state_on)
		GSTAT.connect('state-off', self.on_state_off)
		GSTAT.connect('periodic',  self.on_periodic)


		# TODO see if all self.stat polls can be eliminated by using GSTAT
		self.stat.poll()
		self.e.poll()
		self.init_control_lists()

	def error_poll(self):
		error = self.e.poll()
		return 0

	def init_control_lists(self):
		self.machine_info = range(5)				# machine configuration info
		self.machine_info[0:] = [0] * 5
		self.jog_control = range(11)				# jogging master control
		self.jog_control[0:] = [0] * 11
		self.jog_rates = range(9)					# jogging step and rate values
		self.jog_rates[0:] = [0] * 9
		self.inch_increments = range(21)			# jogging inch increments list
		self.inch_increments[0:] = [0] * 21
		self.metric_increments = range(21)			# jogging metric increments list
		self.metric_increments[0:] = [0] * 21
		self.angular_increments = range(21)			# jogging angular increments list
		self.angular_increments[0:] = [0] * 21
		self.jog_linear_buttons	= range(21)			# jogging linear cmd strings to set button to true at init
		self.jog_linear_buttons[0:]	= [-1] * 21
		self.jog_angular_buttons = range(21)		# jogging angular cmd strings to set button to true at init
		self.jog_angular_buttons[0:] = [-1] * 21
		self.homing_control = range(4)				# safe homing
		self.homing_control[0:] = [0] * 4
		self.spindle0 = range(10)
		self.spindle0[0:] = [-1] * 9
		self.spindle1 = range(10)
		self.spindle1[0:] = [-1] * 9

	def initialized__(self):						# make for sure path to x1mill configuration file
		inipath = os.environ['INI_FILE_NAME']
		print 'Using ini file:',inipath
		self.inifile = ini(inipath)
		if not self.inifile:
			print '===== CANNOT FIND INI FILE INFO ====='
			sys.exit()
		prefname = self.inifile.find('DISPLAY', 'PREFERENCE_FILE_NAME')
		dirname  = os.path.dirname(inipath)
#		self.pref_path = dirname + '/' + prefname
#		print 'Reading x1mill file:', self.pref_path
#		self.prefs = PROBING(self.pref_path)

		self.get_machine_info()
		self.make_spindle_pins() # making our own hal pins - halcomp0
		self.setup_jogging()
		self.startup_disables()
#		self.startup_hide()
		self.get_probing_defaults()  # from ini file
#		self.get_tool_sensor_data()
		self.slider_range_values()
		self.build_jog_increments()
		self.get_jogging_position_cmds()
		self.get_macro_file_locations()
		self.label_linear_jog_btns()
		self.label_angular_jog_btns()
		self.get_spindle_0_settings()
		self.get_spindle_1_settings()
		self.spindle_0(enable=False)
		self.spindle_1(enable=False)
		self.linear_jog_btns(enable=False)

#		halcomp0 - x1_spindles - make hal pins for spindle rpm and rpm status
	def make_spindle_pins(self):
		print 'making spindle 0 hal pins'
		self.halcomp0 = hal.component('x1Milla')
		self.halcomp0.newpin('spindle_0_set_rpm',hal.HAL_FLOAT, hal.HAL_IN )
		self.halcomp0.newpin('spindle_0_rpm_lab',hal.HAL_FLOAT, hal.HAL_IN )
		self.halcomp0.newpin('spindle_0_rpm_pbar',hal.HAL_FLOAT, hal.HAL_IN )
		self.halcomp0.newpin('spindle_1_set_rpm',hal.HAL_FLOAT, hal.HAL_IN )
		self.halcomp0.newpin('spindle_1_rpm_lab',hal.HAL_FLOAT, hal.HAL_IN )
		self.halcomp0.newpin('spindle_1_rpm_pbar',hal.HAL_FLOAT, hal.HAL_IN )

		self.halcomp0.newpin('x-pos-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('x-neg-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('y-pos-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('y-neg-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('z-pos-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('z-neg-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('u-pos-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		self.halcomp0.newpin('u-neg-limit-sw',hal.HAL_BIT, hal.HAL_IN )
		
		self.halcomp0.newpin('spindle_0_forward',hal.HAL_BIT, hal.HAL_OUT )
		self.halcomp0.newpin('spindle_0_stop',hal.HAL_BIT, hal.HAL_OUT )
		self.halcomp0.newpin('spindle_0_reverse',hal.HAL_BIT, hal.HAL_OUT )
		self.halcomp0.newpin('spindle_1_forward',hal.HAL_BIT, hal.HAL_OUT )
		self.halcomp0.newpin('spindle_1_stop',hal.HAL_BIT, hal.HAL_OUT )
		self.halcomp0.newpin('spindle_1_reverse',hal.HAL_BIT, hal.HAL_OUT )		
		self.halcomp0.ready()

#       other hal components can be generated by using self.halcomp1,
#		self.halcomp2 ect. Or this one can be renamed and added to
#		for other required pins that may not be generated automatically


	def	setup_jogging(self):
		local_btn_cmds=range(20) # cmd list for setting a button to true by index number
		for index, obj in enumerate(local_btn_cmds):
			self.jog_linear_buttons[index]  = 'self.w.pb_f12s6_0_jog_linear_'+(str(index)+'.setChecked(True)')
			self.jog_angular_buttons[index] = 'self.w.pb_f12s6_2_jog_angular_'+(str(index)+'.setChecked(True)')


	def get_machine_info(self):
		# machine units: 0 = unkown, 1 = inch, 2 = metric
		mach_units_linear = self.inifile.find('TRAJ', 'LINEAR_UNITS')
		mach_units_angular = self.inifile.find('TRAJ', 'ANGULAR_UNITS')
		if mach_units_linear in ['in', 'inch', 'imperial']:
			self.machine_info[0] = 1  # machine units are in inches
			self.jog_control[6] = 1 # jogging flag set to inch
#			self.w.plab_f12s5_0_jog_incr_linear_label.setText('INCH INCR')
		if mach_units_linear in ['mm', 'metric']:
			self.machine_info[0] = 2    # machine units are in mm
			self.jog_control[6] = 2 # jogging flag set to metric
#			self.w.plab_f12s5_0_jog_incr_linear_label.setText('MM INCR')
		self.machine_info[1]=['deg','degree','rad','radian','grad','gon'].index(mach_units_angular)
		# machine units: 0 = unkown, 1 = inch, 2 = metric
		# angular units: deg=0, degree=1, rad=2, radian=3, grad=4, gon=5

#		disable these buttons on start up or estop
	def startup_disables(self):
		self.w.pb_f0_estop.setChecked(True)
		self.w.pb_f1_power.setChecked(False)
		startup_data = ['pb_f1_power','pb_f1_manual','pb_f1_mdi','pb_f1_auto','pb_f1_enable_motors',
		                'pb_f2_keyboard','pb_f2_abort','pb_f3_graphic',
		                'pb_f3_homing','pb_f3_tool','pb_f3_probe','pb_f3_tool_offsets',
		            'pb_f3_origin_offsets','pb_f3_macro','pb_f3_edit_gcode',
		            'pb_f3_camview','pb_f3_file','pb_f4_flood','pb_f4_mist','pb_f4_aux',
		            'pb_f12s5_0_jog_position','pb_f12s5_0_jog_linear','pb_f12s5_0_jog_angular',
		            'pb_f12s5_0_jog_rate_slow','pb_f12s5_0_jog_continous','pb_f12s5_0_jog_increment','pb_f12s5_0_jog_rate_fast',
		            'pb_f12s5_0_jog_pos_x','pb_f12s5_0_jog_neg_x','pb_f12s5_0_jog_pos_y',
		            'pb_f12s5_0_jog_neg_y','pb_f12s5_0_jog_pos_z','pb_f12s5_0_jog_neg_z',
		            'pb_f12s5_0_jog_pos_a','pb_f12s5_0_jog_neg_a','pb_f5_spindle_1',
		            'pb_f5_quick_zero','pb_f5_macro','pb_f5_overrides','pb_f5_dro',
		            'pb_f7_dro_abs','pb_f7_dro_dtg','pb_f7_dro_rel','pb_f7_dro_units',
		            'pb_f7_dro_norm_diam','pb_f10sw3_0_zoom_out','pb_f10sw3_0_zoom_in','pb_f9_spindle_0_default_rpm',
		            'pb_f10sw3_0_graph_dro','pb_f10sw3_0_graph_inch_mm','pb_f10sw3_0_graph_x',
		            'pb_f10sw3_0_graph_y','pb_f10sw3_0_graph_z','pb_f10sw3_0_graph_z2',
		            'pb_f10sw3_0_graph_p','pb_f10sw3_0_graph_clear','scrb_f12s6_0_jog_linear_slow','scrb_f12s6_0_jog_linear_fast',]
		for num, btn in enumerate(startup_data, start=0):
			btn = 'self.w.' + (str(startup_data[num])) + '.setEnabled(False)'
			exec btn

		# at startup these panels will be shown
		self.w.stackedWidget_0.setCurrentIndex(0) # sw0    index 0,1
		self.w.stackedWidget_1.setCurrentIndex(0) # sw1    index 0,1
		self.w.stackedWidget_2.setCurrentIndex(0) # fr6    index 0,1,2,3,4
		self.w.stackedWidget_3.setCurrentIndex(0) # fr10   index 0,1,2,3,4,5,6,7,8,9
		self.w.stackedWidget_4.setCurrentIndex(0) # fr11   index 0,1
		self.w.stackedWidget_5.setCurrentIndex(0) # fr12   index 0,1,2,3,4
		self.w.stackedWidget_6.setCurrentIndex(0) # fr12s6 index 0,1,2,3,4

#		enable buttons on power up
	def power_on_off(self,enable):
		# set these buttons to true at start up
		data_true = ['pb_f1_manual','pb_f3_graphic','pb_f5_spindle_1',
		             'pb_f7_dro_abs','pb_f10sw3_0_graph_p','pb_f12s5_0_jog_linear',
		             'pb_f12s5_0_jog_rate_slow','pb_f12s5_0_jog_continous']
		data_false = ['pb_f2_keyboard','pb_f2_abort','pb_f12s5_0_jog_pos_a','pb_f12s5_0_jog_neg_a']
		for num, btn in enumerate(data_true, start=0):
			btn = 'self.w.' + (str(data_true[num])) + '.setChecked(True)'
			exec btn
		for num, btn in enumerate(data_false, start=0):
			btn = 'self.w.' + (str(data_false[num])) + '.setChecked(False)'
			exec btn

#		enable these buttons based on power on or off
		data = ['pb_f1_manual','pb_f1_mdi','pb_f1_auto','pb_f1_enable_motors',
		        'pb_f2_keyboard','pb_f2_abort','pb_f3_graphic',
		        'pb_f3_homing','pb_f3_tool','pb_f3_probe','pb_f3_tool_offsets',
		      'pb_f3_origin_offsets','pb_f3_macro','pb_f3_edit_gcode',
		      'pb_f3_camview','pb_f3_file','pb_f4_flood','pb_f4_mist','pb_f4_aux',
		      'pb_f12s5_0_jog_position','pb_f12s5_0_jog_linear','pb_f12s5_0_jog_angular',
		      'pb_f12s5_0_jog_rate_slow','pb_f12s5_0_jog_continous','pb_f12s5_0_jog_increment','pb_f12s5_0_jog_rate_fast',
		      'pb_f12s5_0_jog_pos_x','pb_f12s5_0_jog_neg_x','pb_f12s5_0_jog_pos_y',
		      'pb_f12s5_0_jog_neg_y','pb_f12s5_0_jog_pos_z','pb_f12s5_0_jog_neg_z',
		      'pb_f12s5_0_jog_pos_a','pb_f12s5_0_jog_neg_a','pb_f5_spindle_1',
		      'pb_f5_quick_zero','pb_f5_macro','pb_f5_overrides','pb_f5_dro',
		      'pb_f7_dro_abs','pb_f7_dro_dtg','pb_f7_dro_rel','pb_f7_dro_units','pb_f9_spindle_0_default_rpm',
		      'pb_f7_dro_norm_diam','pb_f10sw3_0_zoom_out','pb_f10sw3_0_zoom_in',
		      'pb_f10sw3_0_graph_dro','pb_f10sw3_0_graph_inch_mm','pb_f10sw3_0_graph_x',
		      'pb_f10sw3_0_graph_y','pb_f10sw3_0_graph_z','pb_f10sw3_0_graph_z2',
		      'pb_f10sw3_0_graph_p','pb_f10sw3_0_graph_clear','scrb_f12s6_0_jog_linear_slow','scrb_f12s6_0_jog_linear_fast',]
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn
		if enable == True:
			self.c.state(linuxcnc.STATE_ON)
		if enable == False:
			self.c.state(linuxcnc.STATE_OFF)

#		startup hide these buttons until each is called
#	def startup_hide(self):
#		data = ['pb_f12s7_2_jog_lin_stop_all','pb_f12s7_2_jog_lin_stop_x','pb_f12s7_2_jog_lin_stop_y',
#						'pb_f12s7_2_jog_lin_stop_z','pb_f12s7_2_jog_lin_stop_u','pb_f12s7_2_jog_lin_stop_v',
#						'pb_f12s7_2_jog_lin_stop_w','pb_f12s7_3_jog_ang_stop_all','pb_f12s7_3_jog_ang_stop_a',
#						'pb_f12s7_3_jog_ang_stop_b','pb_f12s7_3_jog_ang_stop_c',]
#		for num, btn in enumerate(data, start=0):
#			btn = 'self.w.' + (str(data[num])) + '.hide()'
#			exec btn

#		spindle 0 btns enable or disable
	def spindle_0(self,enable):
		data = ['pb_f9_spindle_0_quick_set_0','pb_f9_spindle_0_quick_set_1','pb_f9_spindle_0_quick_set_2',
		        'pb_f9_spindle_0_quick_set_3','scrb_f9_spindle_0','pb_f9_spindle_0_reverse',
		        'pb_f9_spindle_0_stop','pb_f9_spindle_0_forward']
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn

#		spindle 1 btns enable or disable
	def spindle_1(self,enable):
		data = ['pb_f6s2_0_spindle_1_enable','pb_f6s2_0_spindle_1_quick_set_0','pb_f6s2_0_spindle_1_quick_set_1',
		        'pb_f6s2_0_spindle_1_quick_set_2','pb_f6s2_0_spindle_1_quick_set_3','scrb_f6s2_0_spindle_1',
		        'pb_f6s2_0_spindle_1_reverse','pb_f6s2_0_spindle_1_stop','pb_f6s2_0_spindle_1_forward']
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn

#		jogging position btns enable or disable
	def position_jog_btns(self,enable):
		data = ['pb_f12s6_1_jog_position_0','pb_f12s6_1_jog_position_1','pb_f12s6_1_jog_position_2',
		        'pb_f12s6_1_jog_position_3','pb_f12s6_1_jog_position_4','pb_f12s6_1_jog_position_5',
		        'pb_f12s6_1_jog_position_6','pb_f12s6_1_jog_position_7']
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn

#		jogging linear btns enable or disable
	def linear_jog_btns(self,enable):
		data = ['pb_f12s6_0_jog_linear_0','pb_f12s6_0_jog_linear_1','pb_f12s6_0_jog_linear_2',
		        'pb_f12s6_0_jog_linear_3','pb_f12s6_0_jog_linear_4','pb_f12s6_0_jog_linear_5',
		        'pb_f12s6_0_jog_linear_6','pb_f12s6_0_jog_linear_7','pb_f12s6_0_jog_linear_8',
		      'pb_f12s6_0_jog_linear_9','pb_f12s6_0_jog_linear_10','pb_f12s6_0_jog_linear_11',
		      'pb_f12s6_0_jog_linear_12','pb_f12s6_0_jog_linear_13','pb_f12s6_0_jog_linear_14',
		      'pb_f12s6_0_jog_linear_15','pb_f12s6_0_jog_linear_16','pb_f12s6_0_jog_linear_17',
		      'pb_f12s6_0_jog_linear_18','pb_f12s6_0_jog_linear_19']
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn

#		jogging angular btns enable or disable
	def angular_jog_btns(self,enable):
		data = ['pb_f12s6_2_jog_angular_0','pb_f12s6_2_jog_angular_1','pb_f12s6_2_jog_angular_2',
		        'pb_f12s6_2_jog_angular_3','pb_f12s6_2_jog_angular_4','pb_f12s6_2_jog_angular_5',
		        'pb_f12s6_2_jog_angular_6','pb_f12s6_2_jog_angular_7','pb_f12s6_2_jog_angular_8',
		      'pb_f12s6_2_jog_angular_9','pb_f12s6_2_jog_angular_10','pb_f12s6_2_jog_angular_11',
		      'pb_f12s6_2_jog_angular_12','pb_f12s6_2_jog_angular_13','pb_f12s6_2_jog_angular_14',
		      'pb_f12s6_2_jog_angular_15','pb_f12s6_2_jog_angular_16','pb_f12s6_2_jog_angular_17',
		      'pb_f12s6_2_jog_angular_18','pb_f12s6_2_jog_angular_19',]
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn

#		auto no file loadedg angular btns enable or disable
	def auto_no_file(self,enable):
		data = ['pb_f12s5_2_gcode_run','pb_f12s5_2_gcode_step','pb_f12s5_2_gcode_pause',
		        'pb_f12s5_2_gcode_abort','pb_f12s5_2_gcode_run_from','pb_f12s5_2_gcode_optn_stop',
		        'pb_f12s5_2_gcode_block_del','pb_f12s5_2_gcode_unload']
		for num, btn in enumerate(data, start=0):
			btn = 'self.w.' + (str(data[num])) + '.setEnabled(' + (str(enable)) + ')'
			exec btn


	def get_jogging_position_cmds(self):
		print 'getting jogging position cmd items'
		jog_pos_cmds = range(8) # generate jogging position command list
		jog_pos_cmds[0] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_0')
		jog_pos_cmds[1] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_1')
		jog_pos_cmds[2] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_2')
		jog_pos_cmds[3] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_3')
		jog_pos_cmds[4] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_4')
		jog_pos_cmds[5] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_5')
		jog_pos_cmds[6] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_6')
		jog_pos_cmds[7] = self.inifile.find('POSITION_CMDS', 'POSITION_CMD_7')
		cmd_list = [(i) for i in jog_pos_cmds]

		jog_pos_cmds = range(8) # seperate name from the command
		jog_pos_cmds[0] = cmd_list[0].split(',')
		jog_pos_cmds[1] = cmd_list[1].split(',')
		jog_pos_cmds[2] = cmd_list[2].split(',')
		jog_pos_cmds[3] = cmd_list[3].split(',')
		jog_pos_cmds[4] = cmd_list[4].split(',')
		jog_pos_cmds[5] = cmd_list[5].split(',')
		jog_pos_cmds[6] = cmd_list[6].split(',')
		jog_pos_cmds[7] = cmd_list[7].split(',')
		self.jogging_position_cmds = jog_pos_cmds

		# label buttons with the names
		self.w.pb_f12s6_1_jog_position_0.setText(jog_pos_cmds[0][0])
		self.w.pb_f12s6_1_jog_position_1.setText(jog_pos_cmds[1][0])
		self.w.pb_f12s6_1_jog_position_2.setText(jog_pos_cmds[2][0])
		self.w.pb_f12s6_1_jog_position_3.setText(jog_pos_cmds[3][0])
		self.w.pb_f12s6_1_jog_position_4.setText(jog_pos_cmds[4][0])
		self.w.pb_f12s6_1_jog_position_5.setText(jog_pos_cmds[5][0])
		self.w.pb_f12s6_1_jog_position_6.setText(jog_pos_cmds[6][0])
		self.w.pb_f12s6_1_jog_position_7.setText(jog_pos_cmds[7][0])

	def slider_range_values(self):
		if self.jog_control[1] == 0:	# initialize
			pos_max_rate = int(self.inifile.find('POSITION_CMDS_RATES','POSITION_MAX_RATE'))
			self.jog_rates[3] = self.inifile.find('POSITION_CMDS_RATES','POSITION_SLOW')
			self.jog_rates[4] = self.inifile.find('POSITION_CMDS_RATES','POSITION_FAST')

			lin_max_rate = int(self.inifile.find('LINEAR_RATES','LINEAR_MAX_RATE'))
			self.jog_rates[5] = self.inifile.find('LINEAR_RATES','LINEAR_SLOW')
			self.jog_rates[6] = self.inifile.find('LINEAR_RATES', 'LINEAR_FAST')

			ang_max_rate = int(self.inifile.find('ANGULAR_RATES','ANGULAR_MAX_RATE'))
			self.jog_rates[7] = self.inifile.find('ANGULAR_RATES','ANGULAR_SLOW')
			self.jog_rates[8] = self.inifile.find('ANGULAR_RATES','ANGULAR_FAST')

			self.w.scrb_f12s6_1_jog_position_slow.setRange(1,pos_max_rate)
			self.w.scrb_f12s6_1_jog_position_fast.setRange(1,pos_max_rate)
			self.w.scrb_f12s6_1_jog_position_slow.setValue(int(self.jog_rates[3]))
			self.w.lab_f12s6_1_jog_position_slow.setText(str(self.jog_rates[3]))
			self.w.scrb_f12s6_1_jog_position_fast.setValue(int(self.jog_rates[4]))
			self.w.lab_f12s6_1_jog_position_fast.setText(str(self.jog_rates[4]))

			self.w.scrb_f12s6_0_jog_linear_slow.setRange(1,lin_max_rate)
			self.w.scrb_f12s6_0_jog_linear_fast.setRange(1,lin_max_rate)
			self.w.scrb_f12s6_0_jog_linear_slow.setValue(int(self.jog_rates[5]))
			self.w.lab_f12s6_0_jog_linear_slow.setText(str(self.jog_rates[5]))
			self.w.scrb_f12s6_0_jog_linear_fast.setValue(int(self.jog_rates[6]))
			self.w.lab_f12s6_0_jog_linear_fast.setText(str(self.jog_rates[6]))

			self.w.scrb_f12s6_2_jog_angular_slow.setRange(1,ang_max_rate)
			self.w.scrb_f12s6_2_jog_angular_fast.setRange(1,ang_max_rate)
			self.w.scrb_f12s6_2_jog_angular_slow.setValue(int(self.jog_rates[7]))
			self.w.lab_f12s6_2_jog_angular_slow.setText(str(self.jog_rates[7]))
			self.w.scrb_f12s6_2_jog_angular_fast.setValue(int(self.jog_rates[8]))
			self.w.lab_f12s6_2_jog_angular_fast.setText(str(self.jog_rates[8]))

	def get_macro_file_locations(self):
		print 'getting macro_file_locations'
		macro = range(15)
		macro[0:] = [','] * 15
		macro[0] = (self.inifile.find('MACROS', 'MACRO_FILE_0'))
		macro[1] = self.inifile.find('MACROS', 'MACRO_FILE_1')
		macro[2] = self.inifile.find('MACROS', 'MACRO_FILE_2')
		macro[3] = self.inifile.find('MACROS', 'MACRO_FILE_3')
		macro[4] = self.inifile.find('MACROS', 'MACRO_FILE_4')
		macro[5] = self.inifile.find('MACROS', 'MACRO_FILE_5')
		macro[6] = self.inifile.find('MACROS', 'MACRO_FILE_6')
		macro[7] = self.inifile.find('MACROS', 'MACRO_FILE_7')
		macro[8] = self.inifile.find('MACROS', 'MACRO_FILE_8')
		macro[9] = self.inifile.find('MACROS', 'MACRO_FILE_9')
		macro[10] = self.inifile.find('MACROS', 'MACRO_FILE_10')
		macro[11] = self.inifile.find('MACROS', 'MACRO_FILE_11')
		macro[12] = self.inifile.find('MACROS', 'MACRO_FILE_12')
		macro[13] = self.inifile.find('MACROS', 'MACRO_FILE_13')
		macro[14] = self.inifile.find('MACROS', 'MACRO_FILE_14')

		#remove items that were blank and have been marked with 'None'
		macro = filter(lambda v: v is not None, macro)

		# Since there may have been items marked with 'None'
		# we need to change the lenght of the list or there
		# will be problems with the split function since
		# it cannot slip something that is not there.

		macro_location = range(len(macro))
		names = range(len(macro))
		i = 0
		a = len(macro)
		while i < len(macro):
			macro_location[i] = macro[i].split(',') # split name and file location
			names[i]  = macro_location[i][0]
			i += 1
		self.macro_file_list = macro_location
		self.labels(names)

#		label macro file buttons
	def labels(self,names):
		for index, obj in enumerate(names):
			exec('self.w.pb_f6s2_2_macro_'+str(index)+'.setText(str(names['+str(index)+']))')

	def build_jog_increments(self):
		inch_incr = self.inifile.find('INCH_INCREMENTS', 'LINEAR_INCR_INCH') 	# increments from ini file
		inch_incr = list(inch_incr.split(',')) 						# convert to list
		inch_incr = [float(i) for i in inch_incr]					# convert values to float
		a = 0
		for i in inch_incr:
			self.inch_increments[a]=inch_incr[a]
			if a <= 18: a=a+1
		self.inch_increments[20] = float(self.inifile.find('INCH_INCREMENTS', 'LINEAR_INCR_INCH_DEFAULT'))
		self.jog_rates[0]	= self.inch_increments[20] 
		
		metric_incr = self.inifile.find('MM_INCREMENTS', 'LINEAR_INCR_MM') 	# increments from ini file
		metric_incr = list(metric_incr.split(',')) 					# convert to list
		metric_incr = [float(i) for i in metric_incr]				# convert values to float
		a = 0
		for i in metric_incr:
			self.metric_increments[a]=metric_incr[a]
			if a <= 18: a=a+1
		self.metric_increments[20] = float(self.inifile.find('MM_INCREMENTS', 'LINEAR_INCR_MM_DEFAULT'))
		self.jog_rates[1] = self.metric_increments[20]
		
		angu_incr = self.inifile.find('ANGULAR_INCREMENTS', 'ANGULAR_INCR') 		# increments from ini file
		angu_incr = list(angu_incr.split(',')) 						# convert to list
		angu_incr = [float(i) for i in angu_incr]					# convert values to float
		a = 0
		for i in angu_incr:
			self.angular_increments[a]=angu_incr[a]
			if a <= 18: a=a+1
		self.angular_increments[20] = float(self.inifile.find('ANGULAR_INCREMENTS', 'ANGULAR_INCR_DEFAULT'))
		self.jog_rates[2]	= self.angular_increments[20]

	def label_linear_jog_btns(self):
		print 'labeling and adding values to linear jogging buttons'
		if self.jog_control[6] == 1:	# inch <<<<
			index = 0
			for index, value in enumerate(self.inch_increments[0:20]):	# limit to increment values
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.setText(str(self.inch_increments['+str(index)+']))'
				exec btn
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.set_true_string(str(self.inch_increments['+str(index)+']))'
				exec btn
#			if self.jog_control[1] == 2:
#				if self.jog_control[2] == 2:
#					self.w.lab_f12s5_0_jog_incr_linear.setText(str(self.jog_rates[0]))	
				
		if self.jog_control[6] == 2:	# metric <<<<
			search_value = self.metric_increments[20]
			for index, value in enumerate(self.metric_increments[0:20]):  # limit to increment values
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.setText(str(self.metric_increments['+str(index)+']))'
				exec (btn)
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.set_true_string(str(self.metric_increments['+str(index)+']))'
				exec btn
#			if self.jog_control[1] == 2:				
#				if self.jog_control[2] == 2:
#					self.w.lab_f12s5_0_jog_incr_linear.setText(str(self.jog_rates[1]))		
#		self.label_panel_labels()

	def label_angular_jog_btns(self):
		print 'labeling and adding values to angular jogging buttons'
		index = self.jog_control[9]
		search_value = self.angular_increments[20]
		for index, value in enumerate(self.angular_increments[0:20]):	 # limit to increment values
			btn = 'self.w.pb_f12s6_2_jog_angular_'+str(index)+'.setText(str(self.angular_increments['+str(index)+']))'
			exec btn
			btn = 'self.w.pb_f12s6_2_jog_angular_'+str(index)+'.set_true_string(str(self.angular_increments['+str(index)+']))'
			exec btn
#		if self.jog_control[1] == 3:	
#			if self.jog_control[2] == 2:
#				self.w.lab_f12s5_0_jog_incr_linear.setText(str(self.jog_rates[2]))	

	def get_probing_defaults(self):
		print 'loading probing default values'

		pd = "%.5f" %(float(self.inifile.find('PROBING', 'PROBE_DIAM')))
		mt = "%.5f" %(float(self.inifile.find('PROBING', 'MAX_TRAVEL')))
		lr = "%.5f" %(float(self.inifile.find('PROBING', 'LATCH_RETURN_DIST')))
		sv = "%.5f" %(float(self.inifile.find('PROBING', 'SEARCH_VEL')))
		pv = "%.5f" %(float(self.inifile.find('PROBING', 'PROBE_VEL')))
		el = "%.5f" %(float(self.inifile.find('PROBING', 'SIDE_EDGE_LENGHT')))
		wh = "%.5f" %(float(self.inifile.find('PROBING', 'TOOL_PROBE_HEIGHT')))
		ts = "%.5f" %(float(self.inifile.find('PROBING', 'TOOL_BLOCK_HEIGHT')))
		xy = "%.5f" %(float(self.inifile.find('PROBING', 'XY_CLEARANCE')))
		zc = "%.5f" %(float(self.inifile.find('PROBING', 'Z_CLEARANCE')))
		adj_x = "%.5f" %(float(self.inifile.find('PROBING', 'ADJ_X')))
		adj_y = "%.5f" %(float(self.inifile.find('PROBING', 'ADJ_Y')))
		adj_z = "%.5f" %(float(self.inifile.find('PROBING', 'ADJ_Z')))
		adj_a = '%.5f' %(float(self.inifile.find('PROBING', 'ADJ_ANGLE')))
		rp = self.inifile.find('PROBING', 'PROBE_RAPID_VEL')
		aaz = str(self.inifile.find('PROBING', 'ALLOW_AUTO_ZERO'))
		aas = str(self.inifile.find('PROBING', 'ALLOW_AUTO_SKEW'))

		######  The below have no destination #######
		tis = int(self.inifile.find('PROBING', 'TOOL_IN_SPINDLE'))
		rt =  bool(self.inifile.find('PROBING', 'RELOAD_TOOL'))
		blh = '%.5f' % (float(self.inifile.find('PROBING', 'BLOCKHEIGHT')))

		# set default probing panel user input values
		self.w.versaprobe.input_probe_diam.setText(pd)
		self.w.versaprobe.input_max_travel.setText(mt)
		self.w.versaprobe.input_latch_return_dist.setText(lr)
		self.w.versaprobe.input_search_vel.setText(sv)
		self.w.versaprobe.input_probe_vel.setText(pv)
		self.w.versaprobe.input_side_edge_length.setText(el)
		self.w.versaprobe.input_xy_clearances.setText(xy)
		self.w.versaprobe.input_z_clearance.setText(zc)
		self.w.versaprobe.data_input_rapid_vel=(rp)
		self.w.versaprobe.input_adj_x.setText = adj_x
		self.w.versaprobe.input_adj_y.setText = adj_y
		self.w.versaprobe.input_adj_z.setText = adj_z
		self.w.versaprobe.input_adj_angle.setText = adj_a
		self.w.versaprobe.input_tool_probe_height.setText(wh)
		self.w.versaprobe.input_tool_block_height.setText(ts)
		if aaz == 'YES':
			self.w.versaprobe.pbtn_allow_auto_zero.setEnabled(True)
		else:
			self.w.versaprobe.pbtn_allow_auto_zero.setEnabled(False)
		if aas == 'YES':
			self.w.versaprobe.pbtn_allow_auto_skew.setEnabled(True)
		else:
			self.w.versaprobe.pbtn_allow_auto_skew.setEnabled(False)

	def get_spindle_0_settings(self):
		print 'getting spindle 0 settings'
		min_max0   = self.inifile.find('SPINDLE_0', 'SPINDLE_0_RPM_MIN_MAX')
		min_max0   = list(min_max0.split(','))
		quick_set0 = self.inifile.find('SPINDLE_0', 'SPINDLE_0_QUICK_SETS')
		quick_set0 = list(quick_set0.split(','))
		self.spindle0[3] = float(self.inifile.find('SPINDLE_0', 'SPINDLE_0_DEFAULT_RPM'))
		self.spindle0[4:5] = min_max0
		self.spindle0[6:9] = quick_set0
		self.spindle0[2] = self.spindle0[3]	 # [2] = actual spindle rpm
		
		# quik set button names
		self.w.pb_f9_spindle_0_quick_set_0.setText(self.spindle0[6])
		self.w.pb_f9_spindle_0_quick_set_1.setText(self.spindle0[7])
		self.w.pb_f9_spindle_0_quick_set_2.setText(self.spindle0[8])
		self.w.pb_f9_spindle_0_quick_set_3.setText(self.spindle0[9])
		
		# quick set button true string values
		self.w.pb_f9_spindle_0_quick_set_0.set_true_string(self.spindle0[6])
		self.w.pb_f9_spindle_0_quick_set_1.set_true_string(self.spindle0[7])
		self.w.pb_f9_spindle_0_quick_set_2.set_true_string(self.spindle0[8])
		self.w.pb_f9_spindle_0_quick_set_3.set_true_string(self.spindle0[9])
				
		# set spindle 0 slider range, min and max values
		self.w.scrb_f9_spindle_0.setRange(float(self.spindle0[4]),float(self.spindle0[5]))
		self.w.scrb_f9_spindle_0.setValue(float(self.spindle0[3]))
		
		# rpm display bar
		self.halcomp0['spindle_0_rpm_pbar']=0
		self.w.pbar_f9_spindle_0_rpm.setValue(self.halcomp0 ['spindle_0_rpm_pbar'])
		self.w.pbar_f9_spindle_0_rpm.setMinimum(0)
		self.w.pbar_f9_spindle_0_rpm.setMaximum(int(self.spindle0[5]))

# 		spindle 1 settings from ini file
	def get_spindle_1_settings(self):
		print 'getting spindle 1 settings'
		min_max1   = self.inifile.find('SPINDLE_1', 'SPINDLE_1_RPM_MIN_MAX')
		min_max1   = list(min_max1.split(','))
		quick_set1 = self.inifile.find('SPINDLE_1', 'SPINDLE_1_QUICK_SETS')
		quick_set1 = list(quick_set1.split(','))
		self.spindle1[3] = float(self.inifile.find('SPINDLE_1', 'SPINDLE_1_DEFAULT_RPM'))
		self.spindle1[4:5] = min_max1
		self.spindle1[6:9] = quick_set1
		self.spindle1[2] = self.spindle1[3]	 # [2] = actual spindle rpm		

		# quik set button names
		self.w.pb_f6s2_0_spindle_1_quick_set_0.setText(self.spindle1[6])
		self.w.pb_f6s2_0_spindle_1_quick_set_1.setText(self.spindle1[7])
		self.w.pb_f6s2_0_spindle_1_quick_set_2.setText(self.spindle1[8])
		self.w.pb_f6s2_0_spindle_1_quick_set_3.setText(self.spindle1[9])

		# quick set button true string values
		self.w.pb_f6s2_0_spindle_1_quick_set_0.set_true_string(self.spindle1[6])
		self.w.pb_f6s2_0_spindle_1_quick_set_1.set_true_string(self.spindle1[7])
		self.w.pb_f6s2_0_spindle_1_quick_set_2.set_true_string(self.spindle1[8])
		self.w.pb_f6s2_0_spindle_1_quick_set_3.set_true_string(self.spindle1[9])
		
		# set spindle 1 slider range, min and max values
		self.w.scrb_f6s2_0_spindle_1.setRange(float(self.spindle1[4]),float(self.spindle1[5]))
		self.w.scrb_f6s2_0_spindle_1.setValue(float(self.spindle1[3]))
		
		# rpm display bar
		self.halcomp0['spindle_1_rpm_pbar'] = 0
		self.w.pbar_f6s2_0_spindle_1_rpm.setValue(self.halcomp0 ['spindle_1_rpm_pbar'])
		self.w.pbar_f6s2_0_spindle_1_rpm.setMinimum(0)
		self.w.pbar_f6s2_0_spindle_1_rpm.setMaximum(int(self.spindle1[5]))
	
# 		periodic updates
# ===================================================================
	def on_periodic(self,w):
		self.stat.poll()

		self.update_gcodes() 	# status area
		self.update_mcodes() 	# status area
		self.check_limits()
		self.w.lab_f11s4_0_feed_rate.setText('%.2f' %(float(self.stat.current_vel * 100)))
		self.w.lab_f12s5_2_gcode_motion_line.setText(str(int(self.stat.motion_line)))
		self.w.lab_f12s5_2_gcode_current_line.setText(str(int(self.stat.current_line)))
		self.w.lab_f11s4_0_tool_number.setText(str(int(self.stat.tool_in_spindle)))
		self.interp_state()
		self.mdi_to_manual()
		self.jogging_handler()
		self.check_z_home()
		self.homing_state()
		self.current_system()
#		self.update_spindles()  # speed bars
		self.update_rates_increments()

#		limit=self.halcomp0 ['z-pos-limit-sw']
#		print 'LIMIT',limit
#		print	self.homing_control
#		print	self.machine_info
#		print 'self.jog_control: ', self.jog_control
#		print 'line 856 jog_control 7: ', self.jog_control[7]
#		print 'line 856 jog_control 8: ', self.jog_control[8]
#		print 'line 856 jog_control 9: ', self.jog_control[9]
#		print 'self.jog_rates  : ', self.jog_rates

		self.w.lab_f4_time_date.setText(strftime('%H:%M:%S\n%m/%d/%Y'))
		return True

	def current_system(self):
		n=(self.stat.g5x_index) # get current
		ref=['0','G54','G55','G56','G57','G58','G59','G59.1','G59.2','G59.3']
		ref=ref[n]
		self.w.lab_f7_dro_system.setText(str(ref))
		
	def jogging_handler(self):
		if self.jog_control[0] == 0:						# no jogging allowed
			return
			
		if self.machine_info[3] == 1 or  self.machine_info[3] == 2:  # allow jogging only if value is 1 or 2
			if self.jog_control[2] == 1:						# continous jog  <<<<<<
				jointflag =	1
				axisjoint =	self.jog_control[4]
				if self.machine_info[3] == 2:					# stop jog for selected axis
					self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
					self.machine_info[3] = 0
					return
				rate = 0
				if self.jog_control[3] == 1:
					 rate = (self.jog_rates[5])				# slow linear jog
				if self.jog_control[3] == 2:
					 rate = (self.jog_rates[6])				# fast linear jog
				self.c.feedrate(float(rate)/100)
				dir = (self.jog_control[5])
				if dir == -1:
					dir_vel = (float(rate)/100)*-1
				else:
					dir_vel = (float(rate)/100)
				self.c.jog(linuxcnc.JOG_CONTINUOUS,1,axisjoint,(float(dir_vel)))

			if self.jog_control[1] == 2:						# linear jogging   <<<<<<
				if self.jog_control[2] == 2:					# incremental jog  <<<<<<
					jointflag =	1
					axisjoint =	self.jog_control[4]
					if self.machine_info[3] == 2:				# stop jog for selected axis
						self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
						self.machine_info[3] = 0
						return
					rate = 0
					if self.jog_control[3] == 1:
						rate = (self.jog_rates[5])				# slow linear jog
					if self.jog_control[3] == 2:
						rate = (self.jog_rates[6])				# fast linear jog
					self.c.feedrate(float(rate)/100)
					dir = (self.jog_control[5])
					if dir == -1:
						dir_vel = (float(rate)/100)*-1
					else:
						dir_vel = (float(rate)/100)

					if self.machine_info[0] == 1:				# machines units are inch
						if self.jog_control[6] == 1:			# jog increments are inch
							distance = self.jog_rates[0]
						if self.jog_control[6] == 2:			# jog mm increments using inch machine
							distance = self.jog_rates[1]/25.4

					if self.machine_info[0] == 2:				# machines units are mm
						if self.jog_control[6] == 2:			# jog increments are in mm
							distance = self.jog_rates[1]
						if self.jog_control[6] == 1:			# jog inch increments using mm machine
							distance = self.jog_rates[0]*25.4
					print 'DISTANCE: ',float(distance)
					self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
					self.machine_info[3] = 0

			if self.jog_control[1] == 3:						# angular jogging  <<<<<<
				if self.jog_control[2] == 2:					# incremental jog  <<<<<<
					jointflag =	1
					axisjoint =	self.jog_control[4]
					if self.machine_info[3] == 2:				# stop jog for selected axis
						self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
						self.machine_info[3] = 0
						return
					rate = 0
					if self.jog_control[3] == 1:
						rate = (self.jog_rates[7])				# slow angular jog
					if self.jog_control[3] == 2:
						rate = (self.jog_rates[8])				# fast angular jog

					self.c.feedrate(float(rate)/100)
					dir = (self.jog_control[5])
					if dir == -1:
						dir_vel = (float(rate)/100)*-1
					else:
						dir_vel = (float(rate)/100)
					distance = self.jog_rates[2]
					print 'DISTANCE: ',float(distance)
					self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
					self.machine_info[3] = 0

			# not used yet
			if self.jog_control[1] == 1:						# position jogging - by mdi cmd
				if self.jog_control[2] == 2:					# incremental jogging
					jointflag =	1
					axisjoint =	self.jog_control[4]
					if self.machine_info[3] == 2:				# stop jog for selected axis
						self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
						self.machine_info[3] = 0
						return
					rate = 0
					if self.jog_control[3] == 1:
						 rate = (self.jog_rates[3])			# slow position jog
					if self.jog_control[3] == 2:
						rate = (self.jog_rates[4])				# fast position jog
					self.c.feedrate(float(rate)/100)
					
		# update the display jog rates and increments	
	def update_rates_increments(self):
		if self.jog_control[0] != 1: # Jogging disabled
			self.w.lab_f12s5_0_jog_rate.setText('NO JOG')
			self.w.lab_f12s5_0_jog_incr.setText('NO JOG')
			return
		if self.jog_control[1] == 1: # position
			self.w.lab_f12s5_0_jog_incr.setText(str(0))
			if self.jog_control[3] == 1: # slow rate
				self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[3]))
			if self.jog_control[3] == 2: # fast rate
				self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[4]))
		
		if self.jog_control[2] == 1: # continous jog
			if self.jog_control[1] == 2: # linear
				self.w.lab_f12s5_0_jog_incr.setText(str(0))
				if self.jog_control[3] == 1: # slow rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[5]))
				if self.jog_control[3] == 2: # fast rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[6]))
			if self.jog_control[1] == 3: # angular
				self.w.lab_f12s5_0_jog_incr.setText(str(0))
				if self.jog_control[3] == 1: # slow rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[7]))
				if self.jog_control[3] == 2: # fast rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[8]))		

		if self.jog_control[2] == 2: # increment
			if self.jog_control[1] == 2: # linear
				if self.jog_control[6] == 1: # inch
					self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[0]))
				if self.jog_control[6] == 2: # metric
					self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[1]))
				if self.jog_control[3] == 1: # slow rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[5]))	
				if self.jog_control[3] == 2: # fast rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[6]))

			if self.jog_control[1] == 3: # angular
				if self.jog_control[3] == 1: # slow rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[7]))	
				if self.jog_control[3] == 2: # fast rate
					self.w.lab_f12s5_0_jog_rate.setText(str(self.jog_rates[8]))
				self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[2]))						

# ===================================================================
	def on_state_on(self,w):
		print 'machine on'
	def on_state_off(self,w):
		print 'machine off'

	def search_kill_process(self,name):
		# name = onboard
		process = filter(lambda p: p.name() == 'name', psutil.process_iter())
		for i in process:
			print i.name
			parent_pid = i.pid
			parent = psutil.Process(parent_pid)
			parent.kill()
		sys.exit()

	def mdi_to_manual(self):
		if self.jog_control[10] == -1:
			return
		if self.jog_control[10] == 1:
			if self.stat.inpos == True:
				# task_mode: manual = 1, auto = 2, midi = 3
				if self.stat.task_mode == 3:
					self.c.mode(linuxcnc.MODE_MANUAL)
					self.jog_control[10] = -1
					print "mdi position cmd completed"

	def interp_state(self):
		state = self.stat.interp_state
		interp = 'x1Gui v1.0.1'
		if state == 1:
			interp = 'IDLE'
		if state == 2:
			interp = 'READING'
		if state == 3:
			interp = 'PAUSED'
		if state == 4:
			interp = 'WAITING'
		self.w.plab_f11s4_0_interp.setText(interp)

	def check_limits(self):
		limits=self.stat.limit	
		for i in range(len(limits)):
			if 0<limits[i]:
				msg=['X LIM', 'Y LIM','Z LIM', 'A LIM', 'B LIM', 'C LIM','U LIM', 'V LIM', 'W LIM']
				self.w.plab_f2_limits_label.setText(msg[i])
				if  self.stat.estop == 1:
					self.w.pb_f2_out_of_limits.setEnabled(False)
				else:	
					self.w.pb_f2_out_of_limits.setEnabled(True)

	def plab_f2_limits_label_setText(self):
		do_nothing = 0

	def update_gcodes(self):
		gcode_list=''
		gcodes = []
		for i in self.stat.gcodes[1:]:
			if i == -1: continue
			if i % 10 == 0:
				gcodes.append('G%d' % (i/10))
			else:
				gcodes.append('G%(ones)d.%(tenths)d' % {'ones': i/10, 'tenths': i%10})
		gcode_list = ' '.join(gcodes)
		self.w.lab_f11s4_0_gcode_list.setText(gcode_list)

	def update_mcodes(self):
		mcode_list=''
		mcodes = []
		for i in self.stat.mcodes[1:]:
			if i == -1: continue
			mcodes.append('M%d' % i)
		mcode_list = ' '.join(mcodes)
		self.w.lab_f11s4_0_mcode_list.setText(mcode_list)

	def update_spindles(self):
		val0 = (self.halcomp0 ['spindle_0_rpm_pbar'])
		if val0 <0:
			val0 = val0*-1
		self.w.pbar_f9_spindle_0_rpm.setFormat(str(int(val0)))
		self.w.pbar_f9_spindle_0_rpm.setValue(val0)	
	
		val1 = self.halcomp0['spindle_1_rpm_pbar']
		if val1 <0:
			val1 = val1*-1
		self.w.pbar_f6s2_0_spindle_1_rpm.setFormat(str(int(val1)))
		self.w.pbar_f6s2_0_spindle_1_rpm.setValue(val1)

	def ensure_mode(self,m, *p):
		self.stat.poll()
		# task_mode: manual = 1, auto = 2, midi = 3
		if self.stat.task_mode == m or self.stat.task_mode in p: return True
		self.c.mode(m) # task_mode
		self.c.wait_complete()
		self.stat.poll()
		return True

# Start of gui buttons and other items
# ==============================================================================================
#
# 	>>>> estop button and reset logic in postgui hal <<<<
#	-----------------------------------------------------
#	setp oneshot.1.width .150
#	net estop-set x1Mill.pb_f0_estop halui.estop.activate  not.4.in
#	net estop-notset  not.4.out  oneshot.1.in
#	net estop-clear oneshot.1.out halui.estop.reset
#	-----------------------------------------------------

# F0

	def pb_f0_estop_toggle(self,pressed):
		if pressed:
			enable = False
			self.spindle0[0] = 0
			self.spindle1[0] = 0
			self.startup_disables()
			self.spindle_0(enable)
			self.spindle_1(enable)
			self.linear_jog_btns(enable)
			print 'estop active'
		else:
			# estop reset is handled in postgui with oneshot component
			self.w.pb_f1_power.setEnabled(True)
			units = self.inifile.find('TRAJ', 'LINEAR_UNITS')
			ang_units = self.inifile.find('TRAJ', 'ANGULAR_UNITS')
			self.jog_control[0] = 0 # jogging disable
			self.jog_control[1] = 0 # jogging mode set to none
			print 'estop cleared'

# F1

	def pb_f1_power_toggle(self,pressed):
		if pressed:
			enable = True
			self.power_on_off(enable)
			self.spindle_0(enable)
			self.spindle_1(enable)
			self.linear_jog_btns(enable)
			self.w.lab_f9_spindle_0_rpm.setText(str(int(self.spindle0[2]))) 
			self.w.lab_f6s2_0_spindle_1_rpm.setText(str(int(self.spindle1[2])))
		else:
			enable = False
			self.power_on_off(enable)
			self.spindle_0(enable)
			self.spindle_1(enable)
			self.linear_jog_btns(enable)

	def pb_f1_enable_motors_toggle(self,pressed):
		# hal pin: x1mill_p.pb_f1_enable_motors
		if pressed:
			name = self.w.sender().text()
			print name

	def pb_f1_manual_toggle(self,pressed):
		if pressed:
			self.c.mode(linuxcnc.MODE_MANUAL)
			self.c.wait_complete()
			self.w.stackedWidget_5.setCurrentIndex(0)
			self.w.pb_f2_keyboard.setEnabled(False)
			self.w.pb_f3_graphic.animateClick(True)
			self.w.pb_f2_help.setEnabled(True)
			self.jog_control[0] = 1 # allow jogging
			self.spindle0[0] = 1
			self.spindle1[0] = 1
			print 'manual mode'
		else:
			self.w.pb_f2_help.setEnabled(False)

	def pb_f1_mdi_toggle(self,pressed):
		if pressed:
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
			self.w.stackedWidget_5.setCurrentIndex(1)
			self.w.pb_f2_keyboard.setEnabled(True)
			self.jog_control[0] = 0 # disable jogging
			print 'mdi mode'

	def pb_f1_auto_toggle(self,pressed):
		if pressed:
			self.c.mode(linuxcnc.MODE_AUTO)
			self.c.wait_complete()
			self.w.stackedWidget_5.setCurrentIndex(2)
			self.w.pb_f2_keyboard.setEnabled(False)
			file_name = str(self.stat.file)
			enable = '.ngc' in file_name
			self.auto_no_file(enable)
			self.jog_control[0] = 0 # disable jogging
			print 'auto mode'

	def pb_f2_keyboard_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_1.setCurrentIndex(1)
			# sends using Hal Xembed: command-string 'matchbox-keyboard --xid'
		else:
			self.w.stackedWidget_1.setCurrentIndex(0)
# F2

	def pb_f2_abort_toggle(self,pressed):
		self.c.abort()

	def pb_f2_help_toggle(self):
		self.w.stackedWidget_5.setCurrentIndex(4)
		name = self.w.sender().text()
		print name

	def pb_f2_out_of_limits_toggle(self):
		enable = True
		jointflag = 1
		axisjoint = -1
		distance  = 0.3750
		self.power_on_off(enable)
		self.c.override_limits()
		if self.halcomp0['x-pos-limit-sw'] == True:
			dir_vel = -5
			axisjoint = 0
		if self.halcomp0['x-neg-limit-sw'] == True:
			dir_vel = .5
			axisjoint = 0
		if self.halcomp0['y-pos-limit-sw'] == True:
			dir_vel = -.5
			axisjoint = 1
		if self.halcomp0['y-neg-limit-sw'] == True:
			dir_vel = .5
			axisjoint = 1
		if self.halcomp0['z-pos-limit-sw'] == True:
			dir_vel = -.5
			axisjoint = 2
		if self.halcomp0['z-neg-limit-sw'] == True:
			dir_vel = .5
			axisjoint = 2
		if axisjoint != -1:
			self.power_on_off(enable)
			self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
#		if self.w.plab_f2_limits_label.getText() != Limits:
#			self.w.plab_f2_limits_label.setText('Limits')

	def pb_f2_keyboard_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_1.setCurrentIndex(1)
			# sends using Hal Xembed: command-string 'matchbox-keyboard --xid'
		else:
			self.w.stackedWidget_1.setCurrentIndex(0)

	def pb_f2_exit_toggle(self):
		self.c.state(linuxcnc.STATE_OFF)
		self.c.wait_complete()
#		# name = onboard
#		process = filter(lambda p: p.name() == 'name', psutil.process_iter())
#		for i in process:
#			print i.name
#			parent_pid = i.pid
#			parent = psutil.Process(parent_pid)
#			parent.kill()
		sys.exit()

# F3

	def pb_f3_graphic_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(0)
			self.w.stackedWidget_4.setCurrentIndex(0)
			self.w.gcodegraphics.set_view('p')

	def pb_f3_homing_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(1)
			self.w.stackedWidget_4.setCurrentIndex(0)
			self.w.pb_f1_manual.animateClick(True)
			self.c.mode(linuxcnc.MODE_MANUAL)
			self.w.gcodegraphics_2.set_view('p')
			self.homing_control[0] = 1 			# enable homing specific polling step 1

	def pb_f3_probe_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(2)
#			self.w.pbtn_probe_history.setCheckable(True)
		else:
#			self.w.pbtn_probe_history.setCheckable(False)
			print 'Probing panel closed'
			
	def pb_f3_origin_offsets_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(3)
			self.w.stackedWidget_4.setCurrentIndex(0)
						
	def pb_f3_tool_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(4)
			self.w.stackedWidget_4.setCurrentIndex(0)	

	def pb_f3_tool_offsets_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(5)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_macro_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(6)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_edit_gcode_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(7)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_camview_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(8)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_file_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(9)
			self.w.stackedWidget_4.setCurrentIndex(0)

# F4

	def pb_f4_flood_toggle(self,pressed):
		# hal pin: x1mill_p.pb_f4_flood
		if pressed:
			self.c.flood(1)
		else:
			self.c.flood(0)

	def pb_f4_mist_toggle(self,pressed):
		# hal pin: x1mill_p.pb_f4_mist
		if pressed:
			self.c.mist(1)
		else:
			self.c.mist(0)

	def pb_f4_aux_toggle(self,pressed):
		# hal pin: x1mill_p.pb_f4_aux
		name = self.w.sender().text()
		print name

	def lab_f4_time_date_setText(self):
		name = self.w.sender().text()
		print name

# F5

	def pb_f5_spindle_1_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_2.setCurrentIndex(0) # axis4_panel
	def pb_f5_quick_zero_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_2.setCurrentIndex(1) # quick_zero_panel
	def pb_f5_macro_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_2.setCurrentIndex(2) # macro_btns_panel
	def pb_f5_overrides_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_2.setCurrentIndex(3) # override_panel
	def pb_f5_dro_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_2.setCurrentIndex(4) # dro_5_to_9_panel

# F6_0

	def pb_f6s2_0_spindle_1_enable_toggle(self,pressed):
		if pressed:
			print 'Spindle_1_enabled'
	def scrb_f6s2_0_spindle_1_setRange(self):
		pass
	def pbar_f6s2_0_spindle_1_rpm_setMinimum(self):
		pass
	def pbar_f6s2_0_spindle_1_rpm_setMaximum(self):
		pass
	def pbar_f6s2_0_spindle_1_rpm_setValue(self):
		pass
	def lab_f6s2_0_spindle_1_rpm_setText(self):
		pass
		
		# spindle 1 quick rpm set buttons
	def pb_f6s2_0_spindle_1_quick_set_0_clicked(self):
		self.scrb_f6s2_0_spindle_1_setValue(value = self.spindle1[6])
	def pb_f6s2_0_spindle_1_quick_set_1_clicked(self):
		self.scrb_f6s2_0_spindle_1_setValue(value = self.spindle1[7])
	def pb_f6s2_0_spindle_1_quick_set_2_clicked(self):
		self.scrb_f6s2_0_spindle_1_setValue(value = self.spindle1[8])
	def pb_f6s2_0_spindle_1_quick_set_3_clicked(self):
		self.scrb_f6s2_0_spindle_1_setValue(value = self.spindle1[9])
		
	def pb_f6s2_0_spindle_1_default_rpm_toggle(self):
		self.w.scrb_f6s2_0_spindle_1.setValue(float(self.spindle1[3]))
		self.scrb_f6s2_0_spindle_1_setValue(value=(self.spindle1[3]))
		self.spindle1[2] = self.spindle1[3]
		
		# spindle 1 speed update via slider or quick set buttons
	def scrb_f6s2_0_spindle_1_setValue(self,value):
		self.w.lab_f6s2_0_spindle_1_rpm.setText(str(int(value)))
		self.w.scrb_f6s2_0_spindle_1.setValue(float(value))
		if self.spindle1[0] == 0:
			return
		if self.spindle1[0] == 1:	
			self.spindle1[2] = float(value)
			if self.spindle1[1] == 1: # spindle running forward
				self.c.spindle(linuxcnc.SPINDLE_FORWARD,float(self.spindle1[2]),0)
			if self.spindle1[1] == 2: # spindle running reverse
				self.c.spindle(linuxcnc.SPINDLE_REVERSE,float(self.spindle1[2]),0)	

	def pb_f6s2_0_spindle_1_stop_toggle(self,pressed):
		if pressed:
			self.spindle1[1] = 0 # spindle stop
			self.c.spindle(linuxcnc.SPINDLE_OFF,0)

	def pb_f6s2_0_spindle_1_forward_toggle(self,pressed):
		if pressed:
			if self.spindle1[0] == 1:	# spindle enable
				self.spindle1[1] = 1 	# spindle running forward
				self.c.spindle(linuxcnc.SPINDLE_FORWARD,float(self.spindle1[2]),0) 
			
	def pb_f6s2_0_spindle_1_reverse_toggle(self,pressed):
		if pressed:
			if self.spindle1[0] == 1:  	# spindle enable
				self.spindle1[1] = 2			# spindle running reverse
				self.c.spindle(linuxcnc.SPINDLE_REVERSE,float(self.spindle1[2]),0)

# F6_1

	def pb_f6s2_1_zero_current_toggle(self):
		cmd = 'G10 L2 P0 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g52_toggle(self):
		cmd = 'G52 X0.0 Y0.0 Z0.0 A0.0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g54_toggle(self):
		cmd = 'G10 L2 P1 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g55_toggle(self):
		cmd = 'G10 L2 P2 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g56_toggle(self):
		cmd = 'G10 L2 P3 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g57_toggle(self):
		cmd = 'G10 L2 P4 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g58_toggle(self):
		cmd = 'G10 L2 P5 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g59_toggle(self):
		cmd = 'G10 L2 P6 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g591_toggle(self):
		cmd = 'G10 L2 P7 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g592_toggle(self):
		cmd = 'G10 L2 P8 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_zero_g593_toggle(self):
		cmd = 'G10 L2 P9 X0 Y0 Z0 A0'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_x_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' X0.000000'
		print 'cmd',cmd
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_y_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' Y0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_z_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' Z0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_a_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' A0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_b_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' B0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_c_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' C0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_u_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' U0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_v_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' V0.000000'
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_w_click(self):
		n=str(self.stat.g5x_index)
		cmd = 'G10 L20 P'+n+' W0.000000'
		self.fast_zero(cmd)

	def fast_zero(self,cmd):
		self.c.mode(linuxcnc.MODE_MDI)
		self.c.mdi(str(cmd))
		print 'zero command ',cmd
		self.jog_control[10] = 1 # position mdi cmd mode change

# F6_2

	def pb_f6s2_2_macro_0_click(self,name):
		cmd = self.macro_file_list[0][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_1_click(self):
		cmd = self.macro_file_list[1][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_2_click(self):
		cmd = self.macro_file_list[2][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_3_click(self):
		cmd = self.macro_file_list[3][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_4_click(self):
		cmd = self.macro_file_list[4][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_5_click(self):
		cmd = self.macro_file_list[5][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_6_click(self):
		cmd = self.macro_file_list[6][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_7_click(self):
		cmd = self.macro_file_list[7][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_8_click(self):
		cmd = self.macro_file_list[8][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_9_click(self):
		cmd = self.macro_file_list[9][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_10_click(self):
		cmd = self.macro_file_list[10][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_11_click(self):
		cmd = self.macro_file_list[11][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_12_click(self):
		cmd = self.macro_file_list[12][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_13_click(self):
		cmd = self.macro_file_list[13][1]
		print 'macro file cmd:' ,cmd

	def pb_f6s2_2_macro_14_click(self):
		cmd = self.macro_file_list[14][1]
		print 'macro file cmd:' ,cmd

# F6_3

	def scrb_f6s2_3_override_spindle_0_setRange(self):
		pass
	def lab_f6s2_3_override_spindle_0_setText(self):
		pass
		
	def scrb_f6s2_3_override_spindle_0_setValue(self,value):
		self.w.lab_f6s2_3_override_spindle_0.setText(str(value))
		
	def pb_f6s2_3_override_spindle_0_click(self):
		pass
	def scrb_f6s2_3_override_feed_setRange(self):
		pass
	def  lab_f6s2_3_override_feed_setText(self):
		pass
		
	def scrb_f6s2_3_override_feed_setValue(self,value):
		self.w.lab_f6s2_3_override_feed.setText(str(value))
		
	def pb_f6s2_3_override_feed_click(self):
		pass
	def scrb_f6s2_3_override_rapid_setRange(self):
		pass
	def lab_f6s2_3_override_rapid_setText(self):
		pass
		
	def scrb_f6s2_3_override_rapid_setValue(self,value):
		self.w.lab_f6s2_3_override_rapid.setText(str(value))
		
	def pb_f6s2_3_override_rapid_click(self):
		pass
	def scrb_f6s2_3_override_jog_linear_setRange(self):
		pass
	def lab_f6s2_3_override_jog_linear_setText(self):
		pass
		
	def scrb_f6s2_3_override_jog_linear_setValue(self,value):
		self.w.lab_f6s2_3_override_jog_linear.setText(str(value))
		
	def pb_f6s2_3_override_jog_linear_click(self):
		pass
	def scrb_f6s2_3_override_jog_angular_setRange(self):
		pass
	def lab_f6s2_3_override_jog_angular_setText(self):
		pass
		
	def scrb_f6s2_3_override_jog_angular_setValue(self,value):
		self.w.lab_f6s2_3_override_jog_angular.setText(str(value))
		
	def pb_f6s2_3_override_jog_angular_click(self):
		pass

# F6

	def dro_f6s2_4_display_b_setText(self):
		pass
	def dro_f6s2_4_display_c_setText(self):
		pass
	def dro_f6s2_4_display_u_setText(self):
		pass
	def dro_f6s2_4_display_v_setText(self):
		pass
	def dro_f6s2_4_display_w_setText(self):
		pass

# F7

	def pb_f7_dro_abs_toggle(self,pressed):
		if pressed:
			GSTAT.emit('dro-reference-change-request', 0) # passed to STATUS dro_widget.py

	def pb_f7_dro_rel_toggle(self,pressed):
		if pressed:

			GSTAT.emit('dro-reference-change-request', 1) # passed to STATUS dro_widget.py


	def current_system(self):
		n=(self.stat.g5x_index) # get current
		ref=['0','G54','G55','G56','G57','G58','G59','G59.1','G59.2','G59.3']
		ref=ref[n]
		self.w.lab_f7_dro_system.setText(str(ref))

	def pb_f7_dro_dtg_toggle(self,pressed):
		if pressed:
			GSTAT.emit('dro-reference-change-request', 2) # passed to STATUS dro_widget.py

	def pb_f7_dro_units_toggle(self,pressed):  # dro units change requested <<<<
		print 'LINE 1584 jog_rates: ',self.jog_rates
		if pressed:
			if self.machine_info[0]  == 1:	# machine units are in inches dro btn calls for metric increments
				self.jog_control[6] = 2			# metric increments in use now
				self.machine_info[2]  = 2		# values to be converted to metric
				self.label_linear_jog_btns()	# change button and panel labels
				GSTAT.emit('metric-mode-changed', 1)	# passed to STATUS dro_widget.py

			if self.machine_info[0]  == 2:	# machine units are metric but dro btn calls for inch increments
				self.jog_control[6] = 1			# inch increments in use now
				self.machine_info[2]  = 1		# values to be converted to inch
				self.label_linear_jog_btns()	# change button and panel labels
				GSTAT.emit('metric-mode-changed', 0)	# passed to STATUS dro_widget.py

		else: 	 # back to machines ini units <<<<
			if self.machine_info[0]  == 2:	# machine units are metric and dro btn calls for metric increments
				self.jog_control[6] = 2			# metric increments in use now
				self.machine_info[2]  = 2  	# values to be converted to metric
				self.label_linear_jog_btns()	# change button and panel labels
				GSTAT.emit('metric-mode-changed', 1)	# passed to STATUS dro_widget.py

			if self.machine_info[0]  == 1:	# machine units are inch and dro btn calls for inch increments
				self.jog_control[6] = 1			# inch increments in use now
				self.machine_info[2]  = 1		# values to be converted to inch
				self.label_linear_jog_btns()	# change button and panel labels
				GSTAT.emit('metric-mode-changed', 0)	# passed to STATUS dro_widget.py

	def pb_f7_dro_norm_diam_toggle(self,pressed):
		if pressed:
			GSTAT.emit('diameter-mode', 1)	# passed to STATUS dro_widget.py
			self.w.plab_f8_x.setText('DIA')
		else:
			GSTAT.emit('diameter-mode', 0)	# passed to STATUS dro_widget.py
			self.w.plab_f8_x.setText('X')

	def lab_f7_dro_system_setText(self):
		pass

# F8

	def dro_f8_display_x_setText(self):
		pass
	def dro_f8_display_y_setText(self):
		pass
	def dro_f8_display_z_setText(self):
		pass
	def dro_f8_display_a_setText(self):
		pass

# F12_0

	def pb_f12s5_0_jog_pos_x_pressed(self):
		self.jog_control[4]	= 0		# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[3] = 1    	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_x_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4] = 0		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2   # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_x_pressed(self):
		self.jog_control[4]	= 0 		# axis number
		self.jog_control[5]	= -1		# direction
		self.machine_info[3] = 1     	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_x_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4] = 0		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2   # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_pos_y_pressed(self):
		self.jog_control[4]	= 1		# axis number
		self.jog_control[5]  = 1		# direction
		self.machine_info[3] = 1   	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_y_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 1	# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2   # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_y_pressed(self):
		self.jog_control[4]	= 1 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[3] = 1    	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_y_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 1		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_pos_z_pressed(self):
		self.jog_control[4]	= 2			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[3] = 1   	 	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_z_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 2		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_z_pressed(self):
		self.jog_control[4]	= 2 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[3] = 1    	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_z_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 2		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_pos_a_pressed(self):
		self.jog_control[4]	= 3			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[3] = 1     	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_a_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 3		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_a_pressed(self):
		self.jog_control[4]	= 3 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[3] = 1    	 # allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_a_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 3		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[3] = 2    # stop jogging
			self.jogging_handler()

	def label_panel_labels(self):
		if self.jog_control[6] == 1:	# Inch units
			self.w.plab_f12s6_0_jog_mode_linear.setText('INCH - LINEAR JOG MODE')
#			self.w.plab_f12s5_0_jog_incr_linear_label.setText('INCH INCR')
		if self.jog_control[6] == 2:	# metric units
			self.w.plab_f12s6_0_jog_mode_linear.setText('MM - LINEAR JOG MODE')
#			self.w.plab_f12s5_0_jog_incr_linear_label.setText('MM INCR')
#		if self.jog_control[1] == 3:	# angular
#			self.w.plab_f12s5_0_jog_incr_linear_label.setText('DEGREE INCR')

	def pb_f12s5_0_jog_position_toggle(self,pressed):
		if self.jog_control[0] == 1:
			self.w.pb_f12s5_0_jog_pos_x.setEnabled(False)
			self.w.pb_f12s5_0_jog_neg_x.setEnabled(False)
			self.w.pb_f12s5_0_jog_pos_y.setEnabled(False)
			self.w.pb_f12s5_0_jog_neg_y.setEnabled(False)
			self.w.pb_f12s5_0_jog_pos_z.setEnabled(False)
			self.w.pb_f12s5_0_jog_neg_z.setEnabled(False)
			self.w.pb_f12s5_0_jog_pos_a.setEnabled(False)
			self.w.pb_f12s5_0_jog_neg_a.setEnabled(False)

			if pressed:
				self.w.pb_f12s5_0_jog_continous.setChecked(False)
				self.w.pb_f12s5_0_jog_continous.setEnabled(False)
				self.w.pb_f12s5_0_jog_increment.setChecked(False)
				self.w.pb_f12s5_0_jog_increment.setEnabled(False)
				self.jog_control[1] = 1
				self.w.stackedWidget_6.setCurrentIndex(1)

	def pb_f12s5_0_jog_linear_toggle(self,pressed):
			if self.jog_control[0] == 1:
				self.w.pb_f12s5_0_jog_continous.setEnabled(True)
				self.w.pb_f12s5_0_jog_increment.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_x.setEnabled(True)
				self.w.pb_f12s5_0_jog_neg_x.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_y.setEnabled(True)
				self.w.pb_f12s5_0_jog_neg_y.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_z.setEnabled(True)
				self.w.pb_f12s5_0_jog_neg_z.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_a.setEnabled(False)
				self.w.pb_f12s5_0_jog_neg_a.setEnabled(False)
				if pressed:
					self.jog_control[1] = 2 # linear mode
					self.w.stackedWidget_6.setCurrentIndex(0)

	def pb_f12s5_0_jog_angular_toggle(self,pressed):
			if self.jog_control[0] == 1:
				self.w.pb_f12s5_0_jog_continous.setEnabled(True)
				self.w.pb_f12s5_0_jog_increment.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_a.setEnabled(True)
				self.w.pb_f12s5_0_jog_neg_a.setEnabled(True)
				self.w.pb_f12s5_0_jog_pos_x.setEnabled(False)
				self.w.pb_f12s5_0_jog_neg_x.setEnabled(False)
				self.w.pb_f12s5_0_jog_pos_y.setEnabled(False)
				self.w.pb_f12s5_0_jog_neg_y.setEnabled(False)
				self.w.pb_f12s5_0_jog_pos_z.setEnabled(False)
				self.w.pb_f12s5_0_jog_neg_z.setEnabled(False)
				if pressed:
					self.jog_control[1] = 3 # angular mode
					self.w.stackedWidget_6.setCurrentIndex(2)

	def pb_f12s5_0_jog_rate_slow_toggle(self,pressed):
		self.jog_control[3]=1

	def pb_f12s5_0_jog_rate_fast_toggle(self,pressed):
		self.jog_control[3]=2

	def pb_f12s5_0_jog_continous_toggle(self,pressed):
		if pressed:
			self.jog_control[2] = 1 # set to continuous jogging mode
			
	def pb_f12s5_0_jog_increment_toggle(self,pressed):
		if pressed:
			self.jog_control[2] = 2 # set to increment jogging mode		
							
# F12_1

	def scrb_f12s6_1_jog_position_slow_setValue(self,value):
		self.w.lab_f12s6_1_jog_position_slow.setText(str(value))
		if self.jog_control[1] == 1: # position jog
			self.jog_rates[3] = value

	def scrb_f12s6_1_jog_position_fast_setValue(self,value):
		self.w.lab_f12s6_1_jog_position_fast.setText(str(value))
		if self.jog_control[1] == 1: # position jog
			self.jog_rates[4] = value

	def scrb_f12s6_0_jog_linear_slow_setValue(self,value):
		self.w.lab_f12s6_0_jog_linear_slow.setText(str(value))
		if self.jog_control[1] == 2: # linear jog
			self.jog_rates[5] = value

	def scrb_f12s6_0_jog_linear_fast_setValue(self,value):
		self.w.lab_f12s6_0_jog_linear_fast.setText(str(value))
		if self.jog_control[1] == 2: # linear jog
			self.jog_rates[6] = value

	def scrb_f12s6_2_jog_angular_slow_setValue(self,value):
		self.w.lab_f12s6_2_jog_angular_slow.setText(str(value))
		if self.jog_control[1] == 3: # angular jog
			self.jog_rates[7] = value

	def scrb_f12s6_2_jog_angular_fast_setValue(self,value):
		self.w.lab_f12s6_2_jog_angular_fast.setText(str(value))
		if self.jog_control[1] == 3:
			self.jog_rates[8] = value

	def pb_f12s6_1_jog_position_0_pressed(self):
		self.position_cmds(btn=0)
	def pb_f12s6_1_jog_position_1_pressed(self):
		self.position_cmds(btn=1)
	def pb_f12s6_1_jog_position_2_pressed(self):
		self.position_cmds(btn=2)
	def pb_f12s6_1_jog_position_3_pressed(self):
		self.position_cmds(btn=3)
	def pb_f12s6_1_jog_position_4_pressed(self):
		self.position_cmds(btn=4)
	def pb_f12s6_1_jog_position_5_pressed(self):
		self.position_cmds(btn=5)
	def pb_f12s6_1_jog_position_6_pressed(self):
		self.position_cmds(btn=6)
	def pb_f12s6_1_jog_position_7_pressed(self):
		self.position_cmds(btn=7)

	def position_cmds(self,btn):
		self.c.mode(linuxcnc.MODE_MDI)
		self.c.mdi(str(self.jogging_position_cmds[btn][1]))
		self.jog_control[10] = 1 # position mdi cmd mode change

	def pb_f12s6_0_jog_linear_0_pressed(self):
		self.new_linear_incr(index = 0)
	def pb_f12s6_0_jog_linear_1_pressed(self):
		self.new_linear_incr(index = 1)
	def pb_f12s6_0_jog_linear_2_pressed(self):
		self.new_linear_incr(index = 2)
	def pb_f12s6_0_jog_linear_3_pressed(self):
		self.new_linear_incr(index = 3)
	def pb_f12s6_0_jog_linear_4_pressed(self):
		self.new_linear_incr(index = 4)
	def pb_f12s6_0_jog_linear_5_pressed(self):
		self.new_linear_incr(index = 5)
	def pb_f12s6_0_jog_linear_6_pressed(self):
		self.new_linear_incr(index = 6)
	def pb_f12s6_0_jog_linear_7_pressed(self):
		self.new_linear_incr(index = 7)
	def pb_f12s6_0_jog_linear_8_pressed(self):
		self.new_linear_incr(index = 8)
	def pb_f12s6_0_jog_linear_9_pressed(self):
		self.new_linear_incr(index = 9)
	def pb_f12s6_0_jog_linear_10_pressed(self):
		self.new_linear_incr(index = 10)
	def pb_f12s6_0_jog_linear_11_pressed(self):
		self.new_linear_incr(index = 11)
	def pb_f12s6_0_jog_linear_12_pressed(self):
		self.new_linear_incr(index = 12)
	def pb_f12s6_0_jog_linear_13_pressed(self):
		self.new_linear_incr(index = 13)
	def pb_f12s6_0_jog_linear_14_pressed(self):
		self.new_linear_incr(index = 14)
	def pb_f12s6_0_jog_linear_15_pressed(self):
		self.new_linear_incr(index = 15)
	def pb_f12s6_0_jog_linear_16_pressed(self):
		self.new_linear_incr(index = 16)
	def pb_f12s6_0_jog_linear_17_pressed(self):
		self.new_linear_incr(index = 17)
	def pb_f12s6_0_jog_linear_18_pressed(self):
		self.new_linear_incr(index = 18)
	def pb_f12s6_0_jog_linear_19_pressed(self):
		self.new_linear_incr(index = 19)

	def new_linear_incr(self,index):
		if self.jog_control[1] == 2:	 		# linear jogging mode
			if self.jog_control[6] == 1: 		# inch
				self.jog_control[7] = index
				self.jog_rates[0] =  self.inch_increments[index]
			if self.jog_control[6] == 2: 		# metric
				self.jog_control[8] = index
				self.jog_rates[1] = self.metric_increments[index]

	def pb_f12s6_2_jog_angular_0_pressed(self):
		self.new_angular_incr(index = 0)
	def pb_f12s6_2_jog_angular_1_pressed(self):
		self.new_angular_incr(index = 1)
	def pb_f12s6_2_jog_angular_2_pressed(self):
		self.new_angular_incr(index = 2)
	def pb_f12s6_2_jog_angular_3_pressed(self):
		self.new_angular_incr(index = 3)
	def pb_f12s6_2_jog_angular_4_pressed(self):
		self.new_angular_incr(index = 4)
	def pb_f12s6_2_jog_angular_5_pressed(self):
		self.new_angular_incr(index = 5)
	def pb_f12s6_2_jog_angular_6_pressed(self):
		self.new_angular_incr(index = 6)
	def pb_f12s6_2_jog_angular_7_pressed(self):
		self.new_angular_incr(index = 7)
	def pb_f12s6_2_jog_angular_8_pressed(self):
		self.new_angular_incr(index = 8)
	def pb_f12s6_2_jog_angular_9_pressed(self):
		self.new_angular_incr(index = 9)
	def pb_f12s6_2_jog_angular_10_pressed(self):
		self.new_angular_incr(index = 10)
	def pb_f12s6_2_jog_angular_11_pressed(self):
		self.new_angular_incr(index = 11)
	def pb_f12s6_2_jog_angular_12_pressed(self):
		self.new_angular_incr(index = 12)
	def pb_f12s6_2_jog_angular_13_pressed(self):
		self.new_angular_incr(index = 13)
	def pb_f12s6_2_jog_angular_14_pressed(self):
		self.new_angular_incr(index = 14)
	def pb_f12s6_2_jog_angular_15_pressed(self):
		self.new_angular_incr(index = 15)
	def pb_f12s6_2_jog_angular_16_pressed(self):
		self.new_angular_incr(index = 16)
	def pb_f12s6_2_jog_angular_17_pressed(self):
		self.new_angular_incr(index = 17)
	def pb_f12s6_2_jog_angular_18_pressed(self):
		self.new_angular_incr(index = 18)
	def pb_f12s6_2_jog_angular_19_pressed(self):
		self.new_angular_incr(index = 19)

	def new_angular_incr(self,index):
		if self.jog_control[1] == 3:	# angular jogging mode
			self.jog_control[9] = index
			self.jog_rates[2] = self.angular_increments[index]

	def scrb_f12s6_1_jog_position_slow_setRange(self):
		pass
	def scrb_f12s6_1_jog_position_fast_setRange(self):
		pass
	def lab_f12s6_1_jog_position_slow_setText(self):
		pass
	def lab_f12s6_1_jog_position_fast_setText(self):
		pass
	def scrb_f12s6_0_jog_linear_slow_setRange(self):
		pass
	def scrb_f12s6_0_jog_linear_fast_setRange(self):
		pass
	def lab_f12s6_0_jog_linear_slow_setText(self):
		pass
	def lab_f12s6_0_jog_linear_fast_setText(self):
		pass
	def scrb_f12s6_2_jog_angular_slow_setRange(self):
		pass
	def scrb_f12s6_2_jog_angular_fast_setRange(self):
		pass
	def lab_f12s6_2_jog_angular_slow_setText(self):
		pass
	def lab_f12s6_2_jog_angular_fast_setText(self):
		pass
	def lab_f12s5_0_jog_rate_setText(self):
		pass
	def lab_f12s5_0_jog_incr_setText(self):
		pass
		
# F9	
		# spindle 0 quick rpm set buttons
	def pb_f9_spindle_0_quick_set_0_clicked(self): 
		self.scrb_f9_spindle_0_setValue(value = self.spindle0[6])
	def pb_f9_spindle_0_quick_set_1_clicked(self):
		self.scrb_f9_spindle_0_setValue(value = self.spindle0[7])
	def pb_f9_spindle_0_quick_set_2_clicked(self):
		self.scrb_f9_spindle_0_setValue(value = self.spindle0[8])
	def pb_f9_spindle_0_quick_set_3_clicked(self):
		self.scrb_f9_spindle_0_setValue(value = self.spindle0[9])
		
	def pb_f9_spindle_0_default_rpm_toggle(self):	# button - recall and use last rpm value
		self.w.scrb_f9_spindle_0.setValue(float(self.spindle0[3]))  # set 
		self.scrb_f9_spindle_0_setValue(value=(self.spindle0[3]))
		self.spindle0[2] = self.spindle0[3]
		
	def scrb_f9_spindle_0_setRange(self):
		pass

		# spindle 0 speed update via slider or quick set buttons
	def scrb_f9_spindle_0_setValue(self,value):
		self.w.lab_f9_spindle_0_rpm.setText(str(int(value)))
		self.w.scrb_f9_spindle_0.setValue(float(value))
		if self.spindle0[0] == 0:
			return
		if self.spindle0[0] == 1:	
			self.spindle0[2] = float(value)
			if self.spindle0[1] == 1: # spindle running forward
				self.c.spindle(linuxcnc.SPINDLE_FORWARD,float(self.spindle0[2]),0)
			if self.spindle0[1] == 2: # spindle running reverse
				self.c.spindle(linuxcnc.SPINDLE_REVERSE,float(self.spindle0[2]),0)	

	def pb_f9_spindle_0_stop_toggle(self,pressed):
		if pressed:
			self.spindle0[1] = 0 # spindle stop
			self.c.spindle(linuxcnc.SPINDLE_OFF,0)
		
	def pb_f9_spindle_0_forward_toggle(self,pressed):
		if pressed:
			if self.spindle0[0] == 1:	# spindle enable
				self.spindle0[1] = 1 	# spindle running forward
				self.c.spindle(linuxcnc.SPINDLE_FORWARD,float(self.spindle0[2]),0) 

	def pb_f9_spindle_0_reverse_toggle(self,pressed):
		if pressed:
			if self.spindle0[0] == 1:  	# spindle enable
				self.spindle0[1] = 2			# spindle running reverse
				self.c.spindle(linuxcnc.SPINDLE_REVERSE,float(self.spindle0[2]),0)

	def lab_f9_spindle_0_rpm_setText(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setMinimum(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setMaximum(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setValue(self):
		name = self.w.sender().text()


# F9	sw3_1
#		Hal Xembed: command-string 'matchbox-keyboard --xid' - location and size 0x0x954x228

# F10_0	Gcode graphics display panel
	def pb_f10sw3_0_graph_inch_mm_toggle(self,pressed):
		if pressed:
			self.w.gcodegraphics.set_metric_units(0,1)
		else:
			self.w.gcodegraphics.set_metric_units(1,0)
	def pb_f10sw3_0_graph_dro_toggle(self):
		self.w.gcodegraphics.show_dtg
	def pb_f10sw3_0_zoom_out_pressed(self):
		self.w.gcodegraphics.zoomout()
	def pb_f10sw3_0_zoom_in_pressed(self):
		self.w.gcodegraphics.zoomin()
	def pb_f10sw3_0_graph_x_toggle(self):
		self.w.gcodegraphics.set_view('x')
	def pb_f10sw3_0_graph_y_toggle(self):
		self.w.gcodegraphics.set_view('y')
	def pb_f10sw3_0_graph_z_toggle(self):
		self.w.gcodegraphics.set_view('z')
	def pb_f10sw3_0_graph_z2_toggle(self):
		self.w.gcodegraphics.set_view('z2')
	def pb_f10sw3_0_graph_p_toggle(self):
		self.w.gcodegraphics.set_view('p')
	def pb_f10sw3_0_graph_clear_clicked(self):
		self.w.gcodegraphics.clear_live_plotter()


# F10_1

	def pb_f10sw3_1_home_all_toggle(self):
		self.safe_homing(btn=10)
	def pb_f10sw3_1_home_xyz_toggle(self):
		self.safe_homing(btn=11)
	def pb_f10sw3_1_home_x_toggle(self):
		self.safe_homing(btn=0)
	def pb_f10sw3_1_home_y_toggle(self):
		self.safe_homing(btn=1)
	def pb_f10sw3_1_home_z_toggle(self):
		self.safe_homing(btn=2)
	def pb_f10sw3_1_home_a_toggle(self):
		self.safe_homing(btn=3)
	def pb_f10sw3_1_home_all_toggle(self):
		self.safe_homing(btn=10)
	def pb_f10sw3_1_home_xyz_toggle(self):
		self.safe_homing(btn=11)
	def pb_f10sw3_1_unhome_all_toggle(self):
		self.safe_homing(btn=12)


	def safe_homing(self,btn):					# No resets are done of homing_control - retains last status info
		if self.stat.estop == 1:
			self.machine_info[4] = 0			# info for not actively homing
			return
		self.homing_control[3] = 1				# homing active start polling state
		self.homing_control[1] = btn			# store axis number
		if self.homing_control[2] != 2:		# z home not completed
			self.c.home(2)							# home z before any other axis
			self.homing_control[2] = 1			# flag to run recheck z homed function
			self.check_z_home()					# run it now
		if self.homing_control[2] == 2:		# it returned 2 - z home completed
			data = self.stat.homed				# get current z homed or not status
			if data[2] == 1:						# send individual axis commands
				dataz = self.stat.position[2] # see if Z needs to be raised and how far to raise it
				distance = (float(dataz))*-1  # invert the distance
				dir_vel = 100 						# raise it at max 100% speed
				jointflag = 1
				axisjoint = 2 						# axis Z
				self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
				if btn == 0:  self.c.home(0)
				if btn == 1:  self.c.home(1)
				if btn == 2:  self.c.home(2)
				if btn == 3:  self.c.home(3)
				if btn == 4:  self.c.home(4)
				if btn == 5:  self.c.home(5)
				if btn == 6:  self.c.home(6)
				if btn == 7:  self.c.home(7)
				if btn == 8:  self.c.home(8)
				if btn == 10: self.c.home(0),self.c.home(1),self.c.home(3)
				if btn == 11: self.c.home(0),self.c.home(1)
		if btn == 12:
			self.c.unhome(-1)

	def check_z_home(self):
		if self.homing_control[2] != 1:			# if 1 - z is being homed - do not return
			return
		data = self.stat.homed
		if data[2] == 1: # z homing is in progress
			btn = self.homing_control[1]
			self.homing_control[2] = 2			# z homing has been completed
			self.safe_homing(btn)

	def homing_state(self):
		if self.homing_control[0] != 1:			# update homing status if homing panel is open
			return
		if self.homing_control[0] == 1:
			if self.homing_control[3] == 1:
				if self.stat.state == 2: 		# state is rcs_exec
					self.machine_info[4] = 1
				if self.stat.state == 1:
					self.machine_info[4] = 0	# state = rcs_done

# F11   status panel
	def lab_f11s4_0_mcode_list_setText(self):
		pass
	def lab_f11s4_0_gcode_list_setText(self):
		pass
	def lab_f11s4_0_tool_comment_setText(self):
		pass
	def lab_f11s4_0_tool_number_setText(self):
		pass
	def lab_f11s4_0_tool_diameter_setText(self):
		pass
	def lab_f11s4_0_feed_rate_setText(self):
		pass
	def lab_f11s4_0_feed_per_rev_setText(self):
		pass

# F11   text display
	def lab_f11s4_1_text_display_setText(self):
		self.w.lab_f11s4_1_text_display_setText('')

# F12   auto mode gcode
	def pb_f12s5_2_gcode_load_pressed(self):
		if self.stat.task_mode == 2:
			file_name = str(self.stat.file)
			enable = '.ngc' in file_name
			self.auto_no_file(enable)
		# doing this for now
		self.w.pb_f3_file.animateClick()

	def pb_f12s5_2_gcode_run_pressed(self):
		self.ensure_mode(linuxcnc.MODE_AUTO)
		self.c.auto(linuxcnc.AUTO_RUN,0)

	def pb_f12s5_2_gcode_step_toggle(self):
#		if self.stat.task_mode != linuxcnc.MODE_AUTO or self.stat.interp_state != linuxcnc.INTERP_IDLE:
#			return
		self.ensure_mode(linuxcnc.MODE_AUTO)
		self.c.auto(linuxcnc.AUTO_STEP)

		# pause
	def pb_f12s5_2_gcode_pause_toggle(self,pressed):
#		if self.stat.task_mode != linuxcnc.MODE_AUTO or self.stat.interp_state not in (linuxcnc.INTERP_READING, linuxcnc.INTERP_WAITING):
#			return
		if pressed:
			self.c.auto(linuxcnc.AUTO_PAUSE)
		else:
			self.c.auto(linuxcnc.AUTO_RESUME)

#		self.ensure_mode(linuxcnc.MODE_AUTO)
#		if not self.stat.paused:
#			print 'Line 2230 we are paused'
#			self.c.auto(linuxcnc.AUTO_RESUME)
#		else:
#			print 'Line 2233 we are not paused'
#			self.c.auto(linuxcnc.AUTO_PAUSE)

		# abort
	def pb_f12s5_2_gcode_abort_toggle(self):
		self.c.abort()

		# run from a specific line
	def pb_f12s5_2_gcode_run_from_pressed(self):
		self.c.auto(linuxcnc.AUTO_RUN,0)

	def pb_f12s5_2_gcode_optn_stop_toggle(self,pressed):
		if pressed:
			self.c.set_optional_stop(True)
		else:
			self.c.set_optional_stop(False)

	def pb_f12s5_2_gcode_block_del_toggle(self,pressed):
		if pressed:
			self.c.set_block_delete(True)
		else:
			self.c.set_block_delete(False)

	def pb_f12s5_2_gcode_unload_toggle(self):
		# load do nothing program
		self.c.program_open('/home/cnc/qtvcp-dev/configs/x1Mill/unload.ngc')

	def lab_f12s5_2_gcode_motion_line_setText(self):
		name = self.w.sender().text()
		print name

	def lab_f12s5_2_gcode_current_line_setText(self):
		name = self.w.sender().text()
		print name

# F12   s5_3
#		is not in use yet

# F12   help panel - for hal tools and g/m code tables
	def pb_f12s5_4_help_calibration_clicked(self):
		os.popen('tclsh {0}/bin/emccalib.tcl -- -ini {1} > /dev/null &'.format(TCLPATH, sys.argv[2]), 'w')
		name = self.w.sender().text()
		print name
	def pb_f12s5_4_help_classicladder_clicked(self):
		os.popen('classicladder  &', 'w')
		name = self.w.sender().text()
		print name
	def pb_f12s5_4_help_status_clicked(self):
		os.popen('linuxcnctop  > /dev/null &', 'w')
		name = self.w.sender().text()
		print name
	def pb_f12s5_4_help_hal_meter_clicked(self):
		os.popen('halmeter &')
		name = self.w.sender().text()
		print name
	def pb_f12s5_4_help_hal_scope_clicked(self):
		os.popen('halscope  > /dev/null &', 'w')
		name = self.w.sender().text()
		print name
	def pb_f12s5_4_help_hal_show_clicked(self):
		os.popen('tclsh {0}/bin/halshow.tcl &'.format(TCLPATH))
		name = self.w.sender().text()
		print name

#   switchedWidget status info
	def stackedWidget_0_currentChanged(self,index):
		print 'SW_0_index changed',index

	# sw1 index0 = contains area f5,f6,f7,f8,f9 - index1 = virtual keyboard
	def stackedWidget_1_currentChanged(self,index):
		print 'SW_1_index changed',index

	# sw2 handles f6 panel swamps
	def stackedWidget_2_currentChanged(self,index):
		print 'SW_2_index changed',index

	# sw3 handldes f10 panel swamps
	def stackedWidget_3_currentChanged(self,index):
		print 'SW_3_index changed',index

	# sw4 handles f11 panel swamps
	def stackedWidget_4_currentChanged(self,index):
		print 'SW_4_index changed',index

	# sw5 handles f12 panel swamps - also contains sw6 and sw7
	def stackedWidget_5_currentChanged(self,index):
		print 'SW_5_index changed',index

	# sw6 inside f12 - handles jogging items swamps
	def stackedWidget_6_currentChanged(self,index):
		print 'SW_6_index changed',index


# 		end of gui specific items
# -------------------------------------------------------------

# 		The below are standard items
	def continuous_jog(self, axis, direction):
		GSTAT.continuous_jog(axis, direction)

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
	print 'Local current time :', localtime
	return [HandlerClass(halcomp,widgets,paths)]


#END

