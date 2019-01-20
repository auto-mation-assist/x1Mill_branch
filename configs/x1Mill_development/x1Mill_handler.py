# 01-14-2019 22:07 Alaska time
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

# Items withing this gui are identified by a location key
# Refer to the master layout map and then search for Frame_0 or other number to locate desired one.
# In HAL show pins will have reference to Frame number such as fr1, fr8 ect.
#
# Coding will be changing and moved around as needed
#
# You should print out the below info - Do not delete it


# >>>> indents are: Tab 3 <<<< #
# ============================ #

# machine related variables - values are -1 untill updated
# -------------------------------------------------------------------------
# self.machine_info[0] machine units: 1 = inch, 2 = metric - from ini file and verified
# self.machine_info[1] angular units: deg=0, degree=1, rad=2, radian=3, grad=4, gon=5
# self.machine_info[2] units convert: 0 = no conversion 1 = to inch, 2 = to metric
# self.machine_info[3] homing all selected: 0 = False 1 = True
# self.machine_info[4] jogging in progress: 0 = no 1 = Yes

# Jogging control info - values are -1 at start up or have not been updated
# -------------------------------------------------------------------------
# self.jog_control[0] =  jogging enabled: 1 = enabled
# self.jog_control[1] =  jogging mode: 1 = position  2 = linear 3 = angular
# self.jog_control[2] =  jogging type: 1 = continous  2 = incremental
# self.jog_control[3] =  jog rate: 1 = jog slow  2 = jog fast
# self.jog_control[4] =  axis-joint number:  0,1,2,3,4,5,6,7,8
# self.jog_control[5] =  direction: 1 = pos, -1 = neg
# self.jog_control[6] =	increment list in use: 1 = inch, 2 = metric - from ini file and verified
# self.jog_control[7] =  current inch increment index: 0 to 19
# self.jog_control[8] =  curent metric increment index: 0 to 19
# self.jog_control[9] =  current angular increment index: 0 to 19
# self.jog_control[10] = mdi position cmd: 1 = send cmd, -1 = no action or cmd completed

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
import gtk
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFVIEW_WIDGET
from qtvcp.widgets.tool_offsetview import ToolOffsetView as TOOLVIEW_WIDGET
from qtvcp.widgets.dialog_widget import CamViewDialog as CAMVIEW
from qtvcp.widgets.dialog_widget import MacroTabDialog as LATHEMACRO
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
#####from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.lib.keybindings import Keylookup
from qtvcp.lib.notify import Notify
from qtvcp.core import Status, Action
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
STATUS = Status()
ACTION = Action()
LOG = logger.getLogger(__name__)
LOG.setLevel(logger.INFO) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL
#DEBUG = 0x7FFFFFFF
DEBUG = 0

# 	  for reading my own perferences file
cp1 = ConfigParser.RawConfigParser
class x1m_preferences(cp1):
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
			path = '~/.toolch_preferences'  # <<<=====  Will need to change this
		self.fn = os.path.expanduser(path)
		self.read(self.fn)

	def getpref(self, option, default = False, type = bool):
		m = self.types.get(type)
		try:
			o = m(self, 'DEFAULT', option)
		except Exception, detail:
			print detail
			self.set('DEFAULT', option, default)
			self.write(open(self.fn, 'w'))
			if type in(bool, float, int):
				o = type(default)
			else:
				o = default
		return o

	def putpref(self, option, value, type = bool):
		self.set('DEFAULT', option, type(value))
		self.write(open(self.fn, 'w'))

# -------------------------------------------------------------------------
class HandlerClass:
	def __init__(self, halcomp,widgets,paths):
		self.hal = halcomp
		self.w   = widgets
		self.s   = linuxcnc.stat()
		self.c   = linuxcnc.command()
		self.e   = linuxcnc.error_channel()

		# connect to GStat to catch linuxcnc events
		STATUS.connect('state-on', self.on_state_on)
		STATUS.connect('state-off', self.on_state_off)
		STATUS.connect('periodic', self.on_periodic)

		self.e = linuxcnc.error_channel()
		self.s.poll()
		self.e.poll()
		self.init_control_lists()

	def error_poll(self):
		error = self.e.poll()
		return 0

	def init_control_lists(self):
		self.machine_info = range(5)					# machine configuration info
		self.machine_info[0:] = [-1] * 5
		self.jog_control = range(11)				# jogging master control
		self.jog_control[0:] = [0] * 11
		self.jog_rates = range(9)						# jogging rate values
		self.jog_rates[0:] = [0] * 9
		self.inch_increments = range(21)				# jogging increments master
		self.inch_increments[0:] = [0] * 21
		self.metric_increments = range(21)				# jogging increments master
		self.metric_increments[0:] = [0] * 21
		self.active_linear_increments = range(20)		# in use jogging increments
		self.active_linear_increments[0:] = [-1] * 20
		self.angular_increments = range(21)				# jogging increments
		self.angular_increments[0:] = [0] * 21
		self.jog_linear_buttons	= range(21)				# jogging buttons and cmds
		self.jog_linear_buttons[0:]	= [-1] * 21
		self.jog_angular_buttons = range(21)			# jogging buttons and cmds
		self.jog_angular_buttons[0:] = [-1] * 21


# 		make paths to my very own files
	def initialized__(self):
		inipath = os.environ['INI_FILE_NAME']
		print 'Using ini file:',inipath
		self.inifile = ini(inipath)
		if not self.inifile:
			print '===== CANNOT FIND INI FILE INFO ====='
			sys.exit()
		prefname = self.inifile.find('DISPLAY', 'PREFERENCE_FILE_NAME')
		dirname  = os.path.dirname(inipath)
		self.pref_path = dirname + '/' + prefname
		print 'Using our own preference file:', self.pref_path
		self.prefs = x1m_preferences(self.pref_path)

		self.get_machine_info()
		self.make_spindle_pins() # making our own hal pins - halcomp0
		self.setup_jogging()
		self.startup_disables()
#		self.startup_hide()
#		self.get_probing_values()  # from ini file
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
			self.w.plab_f12s5_0_jog_incr_label.setText('INCH INCR')
		if mach_units_linear in ['mm', 'metric']:
			self.machine_info[0] = 2    # machine units are in mm
			self.jog_control[6] = 2 # jogging flag set to metric
			self.w.plab_f12s5_0_jog_incr_label.setText('MM INCR')
		self.machine_info[1]=['deg','degree','rad','radian','grad','gon'].index(mach_units_angular)
		# machine units: 0 = unkown, 1 = inch, 2 = metric
		# angular units: deg=0, degree=1, rad=2, radian=3, grad=4, gon=5
		print 'line 281: ', self.jog_control


#		disable these buttons on start up or estop
	def startup_disables(self):
		self.w.pb_f0_estop.setChecked(True)
		self.w.pb_f1_power.setChecked(False)
		startup_data = ['pb_f1_power','pb_f1_manual','pb_f1_mdi','pb_f1_auto','pb_f1_enable_motors',
		                'pb_f1_keyboard','pb_f3_graphic',
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
		            'pb_f7_dro_spare','pb_f10sw3_0_zoom_out','pb_f10sw3_0_zoom_in',
		            'pb_f10sw3_0_graph_dro','pb_f10sw3_0_graph_spare','pb_f10sw3_0_graph_x',
		            'pb_f10sw3_0_graph_y','pb_f10sw3_0_graph_z','pb_f10sw3_0_graph_z2',
		            'pb_f10sw3_0_graph_p','pb_f10sw3_0_graph_clear']
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
		data_false = ['pb_f1_keyboard','pb_f12s5_0_jog_pos_a','pb_f12s5_0_jog_neg_a']
		for num, btn in enumerate(data_true, start=0):
			btn = 'self.w.' + (str(data_true[num])) + '.setChecked(True)'
			exec btn
		for num, btn in enumerate(data_false, start=0):
			btn = 'self.w.' + (str(data_false[num])) + '.setChecked(False)'
			exec btn

#		enable these buttons based on power on or off
		data = ['pb_f1_manual','pb_f1_mdi','pb_f1_auto','pb_f1_enable_motors',
		        'pb_f1_keyboard','pb_f3_graphic',
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
		      'pb_f7_dro_spare','pb_f10sw3_0_zoom_out','pb_f10sw3_0_zoom_in',
		      'pb_f10sw3_0_graph_dro','pb_f10sw3_0_graph_spare','pb_f10sw3_0_graph_x',
		      'pb_f10sw3_0_graph_y','pb_f10sw3_0_graph_z','pb_f10sw3_0_graph_z2',
		      'pb_f10sw3_0_graph_p','pb_f10sw3_0_graph_clear']
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
		        'pb_f6s2_0_spindle_1_quick_set_2','pb_f6s2_0_spindle_1_quick_set_3','scrb_f6s2_0_spindle_1_rpm',
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

	# get machine units from ini file - linear and angular
	# linear units:  self.machine_info[0], in=0, inch=0, imperial=0, mm=1, metric=1
	# angular units: self.machine_info[1], deg=0, degree=1, rad=2, radian=3, grad=4, gon=5
	# units convert: self.machine_info[2], 0=no conversion, 1=convert to inch, 2=convert to metric
	# Homing: 		 self.machine_info[3], homing all selected: 0 = False 1 = True
	# jogging		 self.machine_info[4], jogging in progress: -1 = no 1 = Yes

##### Start loading values from 'ini' file now #####

# 		INI file >>> get and set default values for probing panel user inputs
	def get_probing_values(self):
		print 'setting probing values found in ini file'
		pd = self.inifile.find('PROBING', 'PROBE_DIAM')
		mt = self.inifile.find('PROBING', 'MAX_TRAVEL')
		lr = self.inifile.find('PROBING', 'LATCH_RTRN_DIST')
		sv = self.inifile.find('PROBING', 'SEARCH_VEL')
		pv = self.inifile.find('PROBING', 'PROBE_VEL')
		el = self.inifile.find('PROBING', 'EDGE_LENGHT')
#		wh = self.inifile.find('PROBING', 'WORK_HEIGHT')
#		ts = self.inifile.find('PROBING', 'TOOL_SENSE_HEIGHT')
		xy = self.inifile.find('PROBING', 'XY_CLEARANCES')
		zc = self.inifile.find('PROBING', 'Z_CLEARANCE')

		# set default probing panel user input values
		self.w.input_probe_diam.setText(pd)
		self.w.input_max_travel.setText(mt)
		self.w.input_latch_return_dist.setText(lr)
		self.w.input_search_vel.setText(sv)
		self.w.input_probe_vel.setText(pv)
		self.w.input_side_edge_lenght.setText(el)
#		self.w.input_tool_probe_height.setText(wh)
#		self.w.input_tool_block_height.setText(ts)
		self.w.input_xy_clearances.setText(xy)
		self.w.input_z_clearance.setText(zc)

# 		label jogging position command buttons, also commands and slider values
	def get_jogging_position_cmds(self):
		print 'getting jogging position cmd items'

		jog_pos_cmds = range(8) # generate jogging position command list
		jog_pos_cmds[0] = self.inifile.find('X1GUI', 'POSITION_CMD_0')
		jog_pos_cmds[1] = self.inifile.find('X1GUI', 'POSITION_CMD_1')
		jog_pos_cmds[2] = self.inifile.find('X1GUI', 'POSITION_CMD_2')
		jog_pos_cmds[3] = self.inifile.find('X1GUI', 'POSITION_CMD_3')
		jog_pos_cmds[4] = self.inifile.find('X1GUI', 'POSITION_CMD_4')
		jog_pos_cmds[5] = self.inifile.find('X1GUI', 'POSITION_CMD_5')
		jog_pos_cmds[6] = self.inifile.find('X1GUI', 'POSITION_CMD_6')
		jog_pos_cmds[7] = self.inifile.find('X1GUI', 'POSITION_CMD_7')
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
			pos_max_rate = int(self.inifile.find('X1GUI', 'POSITION_MAX_RATE'))
			lin_max_rate = int(self.inifile.find('X1GUI', 'LINEAR_MAX_RATE'))
			ang_max_rate = int(self.inifile.find('X1GUI', 'ANGULAR_MAX_RATE'))
			self.jog_rates[3] = self.inifile.find('X1GUI', 'POSITION_SLOW')
			self.jog_rates[4] = self.inifile.find('X1GUI', 'POSITION_FAST')
			self.jog_rates[5] = self.inifile.find('X1GUI', 'LINEAR_SLOW')
			self.jog_rates[6] = self.inifile.find('X1GUI', 'LINEAR_FAST')
			self.jog_rates[7] = self.inifile.find('X1GUI', 'ANGULAR_SLOW')
			self.jog_rates[8] = self.inifile.find('X1GUI', 'ANGULAR_FAST')

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





# 		get marco file list of macro buttons
	def get_macro_file_locations(self):
		print 'getting macro_file_locations'
		macro = range(15)
		macro[0:] = [','] * 15
		macro[0] = (self.inifile.find('X1GUI', 'MACRO_FILE_0'))
		macro[1] = self.inifile.find('X1GUI', 'MACRO_FILE_1')
		macro[2] = self.inifile.find('X1GUI', 'MACRO_FILE_2')
		macro[3] = self.inifile.find('X1GUI', 'MACRO_FILE_3')
		macro[4] = self.inifile.find('X1GUI', 'MACRO_FILE_4')
		macro[5] = self.inifile.find('X1GUI', 'MACRO_FILE_5')
		macro[6] = self.inifile.find('X1GUI', 'MACRO_FILE_6')
		macro[7] = self.inifile.find('X1GUI', 'MACRO_FILE_7')
		macro[8] = self.inifile.find('X1GUI', 'MACRO_FILE_8')
		macro[9] = self.inifile.find('X1GUI', 'MACRO_FILE_9')
		macro[10] = self.inifile.find('X1GUI', 'MACRO_FILE_10')
		macro[11] = self.inifile.find('X1GUI', 'MACRO_FILE_11')
		macro[12] = self.inifile.find('X1GUI', 'MACRO_FILE_12')
		macro[13] = self.inifile.find('X1GUI', 'MACRO_FILE_13')
		macro[14] = self.inifile.find('X1GUI', 'MACRO_FILE_14')

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
		# =========
		inch_incr = self.inifile.find('X1GUI', 'LINEAR_INCR_INCH') 	# increments from ini file
		inch_incr = list(inch_incr.split(',')) 						# convert to list
		inch_incr = [float(i) for i in inch_incr]					# convert values to float
		a = 0
		for i in inch_incr:
			self.inch_increments[a]=inch_incr[a]
			if a <= 18: a=a+1
		self.inch_increments[20] = float(self.inifile.find('X1GUI', 'LINEAR_INCR_INCH_DEFAULT'))
		self.jog_control[7] = 0	# needs to be zero at start up

		# =========
		metric_incr = self.inifile.find('X1GUI', 'LINEAR_INCR_MM') 	# increments from ini file
		metric_incr = list(metric_incr.split(',')) 					# convert to list
		metric_incr = [float(i) for i in metric_incr]				# convert values to float
		a = 0
		for i in metric_incr:
			self.metric_increments[a]=metric_incr[a]
			if a <= 18: a=a+1
		self.metric_increments[20] = float(self.inifile.find('X1GUI', 'LINEAR_INCR_MM_DEFAULT'))
		self.jog_control[8] = 0	# needs to be zero at start up

		# =========
		angu_incr = self.inifile.find('X1GUI', 'ANGULAR_INCR') 		# increments from ini file
		angu_incr = list(angu_incr.split(',')) 						# convert to list
		angu_incr = [float(i) for i in angu_incr]					# convert values to float
		a = 0
		for i in angu_incr:
			self.angular_increments[a]=angu_incr[a]
			if a <= 18: a=a+1
		self.angular_increments[20] = float(self.inifile.find('X1GUI', 'ANGULAR_INCR_DEFAULT'))
		self.jog_control[9] = 0	# needs to be zero at start up


	def label_linear_jog_btns(self):
		print 'labeling and adding values to linear jogging buttons'
		if self.jog_control[6] == 1:	# inch
			index = self.jog_control[7]
			for index, value in enumerate(self.inch_increments[0:20]):	# limit to increment values
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.setText(str(self.inch_increments['+str(index)+']))'
				exec btn
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.set_true_string(str(self.inch_increments['+str(index)+']))'
				exec btn
			if self.jog_control[7] == 0: # at init only
				search_value = self.inch_increments[20]
				index = (self.inch_increments.index(search_value))
				self.jog_control[7] = index
			if self.jog_control[7] > 0: # after init
				index = self.jog_control[7]
			exec (self.jog_linear_buttons[index])	# set this button to true at init
			self.jog_rates[0] = self.inch_increments[index]

		if self.jog_control[6] == 2:	# metric
			search_value = self.metric_increments[20]
			for index, value in enumerate(self.metric_increments[0:20]):  # limit to increment values
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.setText(str(self.metric_increments['+str(index)+']))'
				print btn
				print self.metric_increments[0:20]
				exec (btn)
				btn = 'self.w.pb_f12s6_0_jog_linear_'+str(index)+'.set_true_string(str(self.metric_increments['+str(index)+']))'
				exec btn
			if self.jog_control[8] == 0: # at init only
				search_value = self.metric_increments[20]
				index = (self.metric_increments.index(search_value))
				self.jog_control[8] = index
			if self.jog_control[8] > 0: # after init
				index = self.jog_control[8]
			exec (self.jog_linear_buttons[index])	# set this button to true at init
			self.jog_rates[1] = self.metric_increments[index]
		self.label_panel_labels()

	def label_angular_jog_btns(self):
		print 'labeling and adding values to angular jogging buttons'
		index = self.jog_control[9]
		search_value = self.angular_increments[20]
		for index, value in enumerate(self.angular_increments[0:20]):	 # limit to increment values
			btn = 'self.w.pb_f12s6_2_jog_angular_'+str(index)+'.setText(str(self.angular_increments['+str(index)+']))'
			exec btn
			btn = 'self.w.pb_f12s6_2_jog_angular_'+str(index)+'.set_true_string(str(self.angular_increments['+str(index)+']))'
			exec btn
			index = (self.angular_increments.index(search_value))
			if self.jog_control[9] == 0: # at init only
				if index < 20:
					exec (self.jog_angular_buttons[index])	# set this button to true init
					self.jog_control[9] = index
			self.jog_rates[2] = self.angular_increments[index]



#		Preference file get and set prefered probing values
	def get_preferences(self):
		print 'using preference file values for probing'
		pd = '%.5f' %(self.prefs.getpref('pf_probe_diam', 0.0, float) )
		mt = '%.5f' %(self.prefs.getpref('pf_max_travel', 0.0, float) )
		lr = '%.5f' %(self.prefs.getpref('pf_latch_return_dist', 0.0, float) )
		sv = '%.5f' %(self.prefs.getpref('pf_search_vel', 0.0, float) )
		pv = '%.5f' %(self.prefs.getpref('pf_probe_vel', 0.0, float) )
		el = '%.5f' %(self.prefs.getpref('pf_side_edge_lenght', 0.0, float) )
#		wh = '%.5f' %(self.prefs.getpref('pf_work_height', 0.0, float) )
#		ts = '%.5f' %(self.prefs.getpref('pf_tool_sense_height', 0.0, float) )
		xy = '%.5f' %(self.prefs.getpref('pf_xy_clearances', 0.0, float) )
		zc = '%.5f' %(self.prefs.getpref('pf_z_clearance', 0.0, float) )
		adj_x = '%.5f' %(self.prefs.getpref('pf_adj_x', 0.0, float) )
		adj_y = '%.5f' %(self.prefs.getpref('pf_adj_y', 0.0, float) )
		adj_z = '%.5f' %(self.prefs.getpref('pf_adj_z', 0.0, float) )
		pf_adj_angle = '%.5f' %(self.prefs.getpref('pf_adj_angle', 0.0, float) )

		# set default probing panel user input values
		self.w.input_probe_diam.setText(pd)
		self.w.input_max_travel.setText(mt)
		self.w.input_latch_return_dist.setText(lr)
		self.w.input_search_vel.setText(sv)
		self.w.input_probe_vel.setText(pv)
		self.w.input_side_edge_lenght.setText(el)
#		self.w.input_tool_probe_height.setText(wh)
#		self.w.input_tool_block_height.setText(ts)
		self.w.input_xy_clearances.setText(xy)
		self.w.input_z_clearance.setText(zc)

# 		spindle 0 settings from ini file
	def get_spindle_0_settings(self):
		print 'getting spindle 0 settings'

		# set spindle 0 slider range, min and max values from ini file
		values = self.inifile.find('SPINDLE', 'SPINDLE_0_RPM_MIN_MAX')
		values = list(values.split(','))
		self.w.scrb_f9_spindle_0.setRange(float(values[0])*100,float(values[1])*100)
		self.w.scrb_f9_spindle_0.setValue((float(self.inifile.find('SPINDLE', 'SPINDLE_0_DEFAULT_RPM')))*100)
		self.w.pbar_f9_spindle_0_rpm.setMinimum(0) #(int(values[0]))
		self.w.pbar_f9_spindle_0_rpm.setMaximum(int(values[1]))

		# connect gui items to hal pins
		self.w.pbar_f9_spindle_0_rpm.setValue(self.halcomp0 ['spindle_0_rpm_pbar'])

		# set spindle 0 quick set buttons name and value from ini file
		values_qs0 = self.inifile.find('SPINDLE', 'SPINDLE_0_QUICK_SETS')
		self.values_qs0 = list(values_qs0.split(','))

		# button names
		self.w.pb_f9_spindle_0_quick_set_0.setText(self.values_qs0[0])
		self.w.pb_f9_spindle_0_quick_set_1.setText(self.values_qs0[1])
		self.w.pb_f9_spindle_0_quick_set_2.setText(self.values_qs0[2])
		self.w.pb_f9_spindle_0_quick_set_3.setText(self.values_qs0[3])

		# button true string values
		self.w.pb_f9_spindle_0_quick_set_0.set_true_string(self.values_qs0[0])
		self.w.pb_f9_spindle_0_quick_set_1.set_true_string(self.values_qs0[1])
		self.w.pb_f9_spindle_0_quick_set_2.set_true_string(self.values_qs0[2])
		self.w.pb_f9_spindle_0_quick_set_3.set_true_string(self.values_qs0[3])

# 		spindle 1 settings from ini file
	def get_spindle_1_settings(self):
		print 'getting spindle 1 settings'

		# set spindle 1 slider range, min and max values from ini file
		values = self.inifile.find('SPINDLE', 'SPINDLE_1_RPM_MIN_MAX')
		values = list(values.split(','))
		self.w.scrb_f6s2_0_spindle_1_rpm.setRange(float(values[0])*100,float(values[1])*100)
		self.w.scrb_f6s2_0_spindle_1_rpm.setValue((float(self.inifile.find('SPINDLE', 'SPINDLE_1_DEFAULT_RPM')))*100)
		self.w.pbar_f6s2_0_spindle_1_rpm.setMinimum(0) #(int(values[0]))
		self.w.pbar_f6s2_0_spindle_1_rpm.setMaximum(int(values[1]))

		# start up settings
		self.halcomp0 ['spindle_1_rpm_pbar']=0

		# connect gui items to hal pins
		self.w.pbar_f6s2_0_spindle_1_rpm.setValue(self.halcomp0 ['spindle_1_rpm_pbar'])

		# set spindle 1 quick set buttons name and value from ini file
		values_qs1= self.inifile.find('SPINDLE', 'SPINDLE_1_QUICK_SETS')
		self.values_qs1 = list(values_qs1.split(','))

		# button names
		self.w.pb_f6s2_0_spindle_1_quick_set_0.setText(self.values_qs1[0])
		self.w.pb_f6s2_0_spindle_1_quick_set_1.setText(self.values_qs1[1])
		self.w.pb_f6s2_0_spindle_1_quick_set_2.setText(self.values_qs1[2])
		self.w.pb_f6s2_0_spindle_1_quick_set_3.setText(self.values_qs1[3])

		# button true string values
		self.w.pb_f6s2_0_spindle_1_quick_set_0.set_true_string(self.values_qs1[0])
		self.w.pb_f6s2_0_spindle_1_quick_set_1.set_true_string(self.values_qs1[1])
		self.w.pb_f6s2_0_spindle_1_quick_set_2.set_true_string(self.values_qs1[2])
		self.w.pb_f6s2_0_spindle_1_quick_set_3.set_true_string(self.values_qs1[3])



# 		periodic updates
# ===================================================================
	def on_periodic(self,w):
		self.s.poll()
		self.update_gcodes()
		self.update_mcodes()
#		self.update_spindles()
		self.update_limits_label()
		self.w.lab_f11s4_0_feed_rate.setText('%.2f' %(float(self.s.current_vel * 100)))
		self.w.lab_f12s5_2_gcode_motion_line.setText(str(int(self.s.motion_line)))
		self.w.lab_f12s5_2_gcode_current_line.setText(str(int(self.s.current_line)))
		self.w.lab_f11s4_0_tool_number.setText(str(int(self.s.tool_in_spindle)))
		self.interp_state()
#		self.safe_home_all()
#		self.mdi_to_manual()
		self.jogging_handler()


#		print 'self.jog_control:       ', self.jog_control
#		print 'line 856 jog_control 7: ', self.jog_control[7]
#		print 'line 856 jog_control 8: ', self.jog_control[8]
#		print 'line 856 jog_control 9: ', self.jog_control[9]
#		print 'line 859  jog_rates:    ', self.jog_rates


		feed = self.s.feedrate
		self.w.lab_f12s5_0_jog_rate.setText(str(feed*100))

		self.w.lab_f4_time_date.setText(strftime('%H:%M:%S\n%m/%d/%Y'))
		return True

	def jogging_handler(self):
		if self.machine_info[4] == -1:						# no jogging allowed
			return

		if self.jog_control[2] == 1:						# continous jog  <<<<<<
			jointflag =	1
			axisjoint =	self.jog_control[4]
			if self.machine_info[4] == 2:					# stop jog for selected axis
				self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
				self.machine_info[4] = -1
				return
			rate = 0
			if self.jog_control[3] == 1:
				 rate = (self.jog_rates[5])					# slow linear jog
			if self.jog_control[3] == 2:
				 rate = (self.jog_rates[6])					# fast linear jog
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
				if self.machine_info[4] == 2:				# stop jog for selected axis
					self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
					self.machine_info[4] = -1
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
					if self.jog_control[6] == 1:			# increments are inch
						distance = self.jog_rates[0]
					if self.jog_control[6] == 2:			# mm increments using inch machine
						distance = self.jog_rates[1]/25.4

				if self.machine_info[0] == 2:				# machines units are mm
					if self.jog_control[6] == 2:			# increments are in mm
						distance = self.jog_rates[1]
					if self.jog_control[6] == 1:			# inch increments using mm machine
						distance = self.jog_rates[0]*25.4

				print 'DISTANCE: ',float(distance)
				self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
				self.w.lab_f12s5_0_jog_incr.setText(str(distance))
				self.machine_info[4] = -1

		if self.jog_control[1] == 3:						# angular jogging  <<<<<<
			if self.jog_control[2] == 2:					# incremental jog  <<<<<<
				jointflag =	1
				axisjoint =	self.jog_control[4]
				if self.machine_info[4] == 2:				# stop jog for selected axis
					self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
					self.machine_info[4] = -1
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
				self.w.lab_f12s5_0_jog_incr.setText(str(distance))
				self.machine_info[4] = -1

		# not used yet
		if self.jog_control[1] == 1:						# position jogging - by mdi cmd
			if self.jog_control[2] == 2:					# incremental jogging
				jointflag =	1
				axisjoint =	self.jog_control[4]
				if self.machine_info[4] == 2:				# stop jog for selected axis
					self.c.jog(linuxcnc.JOG_STOP,jointflag,axisjoint)
					self.machine_info[4] = -1
					return
				rate = 0
				if self.jog_control[3] == 1:
					 rate = (self.jog_rates[3])				# slow position jog
				if self.jog_control[3] == 2:
 					rate = (self.jog_rates[4])				# fast position jog
				self.c.feedrate(float(rate)/100)

#				dir = (self.jog_control[5])
#				if dir == -1:
#					dir_vel = (float(rate)/100)*-1
#				else:
#					dir_vel = (float(rate)/100)
#				distance = self.jog_rates[5]
#				self.c.jog(linuxcnc.JOG_INCREMENT,jointflag,axisjoint,(float(dir_vel)),(float(distance)))
#				self.w.lab_f12s5_0_jog_incr.setText(str(distance))
#				self.machine_info[4] = -1



# ===================================================================
	def mdi_to_manual(self):
		if self.jog_control[10] == -1:
			return
		if self.jog_control[10] == 1:
			if self.s.inpos == True:
				# task_mode: manual = 1, auto = 2, midi = 3
				if self.s.task_mode == 3:
					self.c.mode(linuxcnc.MODE_MANUAL)
					self.jog_control[10] = -1
					print "mdi position cmd completed"

	def safe_home_all(self):
		if self.s.estop == 1: self.machine_info[3] = -1
		if self.machine_info[3] == -1:
			return
		if self.machine_info[3] == 1:
			data = range(9)
			data[0:] = [','] * 9
			data = self.s.homed
			self.c.home(2)
			self.c.wait_complete()
			self.machine_info[3] = 2
		data = self.s.homed
		if data[2] == 1:
			if self.machine_info[3] == 2:
				print 'z is homed' #, data
				self.c.home(0)
				self.c.home(1)
				self.c.wait_complete()
				self.machine_info[3] = 3
		if self.machine_info[3] == 3:
			if data[0] == 1:
				print 'x is homed' #, data
			if data[1] == 1:
				print 'y is homed' #, data
			self.machine_info[3] = -1


#		update interpreter status display
	def interp_state(self):
		state = self.s.interp_state
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

#		update the in limits label on front panel to indicate which axis is in limits
	def update_limits_label(self):
		if self.s.limit[0] > 0:
			self.w.plab_f2_limits_label.setText('X LIM')
		elif self.s.limit[1] > 0:
			self.w.plab_f2_limits_label.setText('Y LIM')
		elif self.s.limit[2] > 0:
			self.w.plab_f2_limits_label.setText('Z LIM')
		else:
			self.w.plab_f2_limits_label.setText('Limits')
			pass

	def plab_f2_limits_label_setText(self):
		do_nothing =0

#		periodic gcodes update
	def update_gcodes(self):
		gcode_list=''
		gcodes = []
		for i in self.s.gcodes[1:]:
			if i == -1: continue
			if i % 10 == 0:
				gcodes.append('G%d' % (i/10))
			else:
				gcodes.append('G%(ones)d.%(tenths)d' % {'ones': i/10, 'tenths': i%10})
		gcode_list = ' '.join(gcodes)
		self.w.lab_f11s4_0_gcode_list.setText(gcode_list)

# 		periodic mcodes update
	def update_mcodes(self):
		mcode_list=''
		mcodes = []
		for i in self.s.mcodes[1:]:
			if i == -1: continue
			mcodes.append('M%d' % i)
		mcode_list = ' '.join(mcodes)
		self.w.lab_f11s4_0_mcode_list.setText(mcode_list)

#		periodic spindle 0 and 1 update
	def update_spindles(self):
		self.w.pbar_f9_spindle_0_rpm.setFormat(str(int(self.halcomp0 ['spindle_0_rpm_pbar'])))
		self.w.pbar_f9_spindle_0_rpm.setValue(self.halcomp0 ['spindle_0_rpm_pbar'])
		self.w.pbar_f6s2_0_spindle_1_rpm.setFormat(str(int(self.halcomp0 ['spindle_1_rpm_pbar'])))
		self.w.pbar_f6s2_0_spindle_1_rpm.setValue(self.halcomp0 ['spindle_1_rpm_pbar'])

	def on_state_on(self,w):
		print 'machine on'
	def on_state_off(self,w):
		print 'machine off'

#		ensure proper mode
	def ensure_mode(self,m, *p):
		self.s.poll()
		# task_mode: manual = 1, auto = 2, midi = 3
		if self.s.task_mode == m or self.s.task_mode in p: return True
		self.c.mode(m) # task_mode
		self.c.wait_complete()
		self.s.poll()
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

# F0	MainWindow panel buttons
	def pb_f0_estop_toggle(self,pressed):
		if pressed:
			enable = False
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

# F1	MainWindow panel buttons
	def pb_f1_power_toggle(self,pressed):
		if pressed:
			enable = True
			self.power_on_off(enable)
			self.spindle_0(enable)
			self.spindle_1(enable)
			self.linear_jog_btns(enable)
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
			self.w.pb_f1_keyboard.setEnabled(False)
			self.w.pb_f3_graphic.animateClick(True)
			self.w.pb_f2_help.setEnabled(True)
			print 'manual mode'
		else:
			self.w.pb_f2_help.setEnabled(False)

	def pb_f1_mdi_toggle(self,pressed):
		if pressed:
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
			self.w.stackedWidget_5.setCurrentIndex(1)
			self.w.pb_f1_keyboard.setEnabled(True)
			print 'mdi mode'

	def pb_f1_auto_toggle(self,pressed):
		if pressed:
			self.c.mode(linuxcnc.MODE_AUTO)
			self.c.wait_complete()
			self.w.stackedWidget_5.setCurrentIndex(2)
			self.w.pb_f1_keyboard.setEnabled(False)
			file_name = str(self.s.file)
			enable = '.ngc' in file_name
			self.auto_no_file(enable)
			print 'auto mode'

	def pb_f1_keyboard_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_1.setCurrentIndex(1)
			# sends using Hal Xembed: command-string 'matchbox-keyboard --xid'
		else:
			self.w.stackedWidget_1.setCurrentIndex(0)


# F2	MainWindow panel buttons
	def pb_f2_abort_toggle(self,pressed):
		# hal pin: x1mill_p.pb_f1_spare
		if pressed:
			name = self.w.sender().text()
			print name

	def pb_f2_help_toggle(self):
		self.w.stackedWidget_5.setCurrentIndex(4)
		name = self.w.sender().text()
		print name

	def pb_f2_exit_toggle(self):
		self.c.state(linuxcnc.STATE_OFF)
		self.c.wait_complete()

#		the onboard keyboard did not work out so this is not needed
#		as is but saved for potential use
#
#		process = filter(lambda p: p.name() == 'onboard', psutil.process_iter())
#		for i in process:
#			print i.name
#			parent_pid = i.pid
#			parent = psutil.Process(parent_pid)
#			parent.kill()
		sys.exit()

# F3	MainWindow panel buttons
	def pb_f3_graphic_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(0)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_homing_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(1)
			self.w.stackedWidget_4.setCurrentIndex(0)
			self.w.pb_f1_manual.animateClick(True)
			self.c.mode(linuxcnc.MODE_MANUAL)

	def pb_f3_tool_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(2)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_probe_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(3)
#			self.w.pbtn_probe_history.setCheckable(True)
		else:
#			self.w.pbtn_probe_history.setCheckable(False)
			print 'Probing panel closed'

	def pb_f3_tool_offsets_toggle(self, pressed):
		if pressed:
			self.w.stackedWidget_3.setCurrentIndex(4)
			self.w.stackedWidget_4.setCurrentIndex(0)

	def pb_f3_origin_offsets_toggle(self, pressed):
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

# F4 	MainWindow panel buttons
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

# F5  	selects stacked widget 2
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

# F6 	Index 0 stackedWidget_2
	def pb_f6s2_0_spindle_1_enable_toggle(self,pressed):
		if pressed:
			print 'Spindle_1_enabled'
	def scrb_f6s2_0_spindle_1_rpm_setRange(self):
		print ''
	def pbar_f6s2_0_spindle_1_rpm_setMinimum(self):
		name = self.w.sender().text()
	def pbar_f6s2_0_spindle_1_rpm_setMaximum(self):
		name = self.w.sender().text()
	def pbar_f6s2_0_spindle_1_rpm_setValue(self):
		name = self.w.sender().text()
	def lab_f6s2_0_spindle_1_rpm_setText(self):
		self=''
	def pb_f6s2_0_spindle_1_quick_set_0_clicked(self):
		self.w.scrb_f6s2_0_spindle_1_rpm.setValue(float(self.values_qs1[0])*100)
	def pb_f6s2_0_spindle_1_quick_set_1_clicked(self):
		self.w.scrb_f6s2_0_spindle_1_rpm.setValue(float(self.values_qs1[1])*100)
	def pb_f6s2_0_spindle_1_quick_set_2_clicked(self):
		self.w.scrb_f6s2_0_spindle_1_rpm.setValue(float(self.values_qs1[2])*100)
	def pb_f6s2_0_spindle_1_quick_set_3_clicked(self):
		self.w.scrb_f6s2_0_spindle_1_rpm.setValue(float(self.values_qs1[3])*100)
	def scrb_f6s2_0_spindle_1_rpm_setValue(self,value):
		spin_1_rps = float(value)/10000
		self.c.spindleoverride(spin_1_rps,1)
		self.w.lab_f6s2_0_spindle_1_rpm.setText(str(self.w.scrb_f6s2_0_spindle_1_rpm.value()/100))
	def scrb_f6s2_0_spindle_1_rpm_valueChanged(self):
		value1 = self.w.sender().value()
		print 'valueChanged',value1
#		   # the below to see progress bar move - will come from spindle encoder later
#		   self.w.pbar_f6s2_0_spindle_1_rpm_setValue(value1)
	def pb_f6s2_0_spindle_1_forward_toggle(self,pressed):
		if pressed:
			self.c.spindle(1,400,1) # dir/speed/spindle
	def pb_f6s2_0_spindle_1_stop_toggle(self,pressed):
		if pressed:
			self.c.spindle(0,1)
	def pb_f6s2_0_spindle_1_reverse_toggle(self,pressed):
		if pressed:
			self.c.spindle(-1,400,1) # dir/speed/spindle

# F6 	Index 1 stackedWidget_2
	def pb_f6s2_1_zero_current_toggle(self):
		cmd = 'G10 L2 P0 X0 Y0 Z0 A0'
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
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_y_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_z_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_a_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_b_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_c_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_u_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_v_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def pb_f6s2_1_joint_zero_w_click(self):
		cmd = ''
		self.fast_zero(cmd)

	def fast_zero(self,cmd):
		self.c.mode(linuxcnc.MODE_MDI)
		self.c.mdi(str(cmd))
		print 'COMMAND >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>:',cmd
		self.jog_control[10] = 1 # position mdi cmd mode change


# F6 	Index 2 stackedWidget_2 - uses [MDI_COMMAND_LIST] in INI file
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

# F6 	Index 3 stackedWidget_2
	def scrb_f6s2_3_override_spindle_0_setRange(self):
		print ''
	def lab_f6s2_3_override_spindle_0_setText(self):
		print ''
	def scrb_f6s2_3_override_spindle_0_setValue(self,value):
		self.w.lab_f6s2_3_override_spindle_0.setText(str(value))
	def pb_f6s2_3_override_spindle_0_click(self):
		name = self.w.sender().text()
		print name
	def scrb_f6s2_3_override_feed_setRange(self):
		print ''
	def  lab_f6s2_3_override_feed_setText(self):
		print ''
	def scrb_f6s2_3_override_feed_setValue(self,value):
		self.w.lab_f6s2_3_override_feed.setText(str(value))
	def pb_f6s2_3_override_feed_click(self):
		name = self.w.sender().text()
		print name
	def scrb_f6s2_3_override_rapid_setRange(self):
		print ''
	def lab_f6s2_3_override_rapid_setText(self):
		print ''
	def scrb_f6s2_3_override_rapid_setValue(self,value):
		self.w.lab_f6s2_3_override_rapid.setText(str(value))
	def pb_f6s2_3_override_rapid_click(self):
		name = self.w.sender().text()
		print name
	def scrb_f6s2_3_override_jog_linear_setRange(self):
		print ''
	def lab_f6s2_3_override_jog_linear_setText(self):
		print ''
	def scrb_f6s2_3_override_jog_linear_setValue(self,value):
		self.w.lab_f6s2_3_override_jog_linear.setText(str(value))
	def pb_f6s2_3_override_jog_linear_click(self):
		name = self.w.sender().text()
		print name
	def scrb_f6s2_3_override_jog_angular_setRange(self):
		print ''
	def lab_f6s2_3_override_jog_angular_setText(self):
		print ''
	def scrb_f6s2_3_override_jog_angular_setValue(self,value):
		self.w.lab_f6s2_3_override_jog_angular.setText(str(value))
	def pb_f6s2_3_override_jog_angular_click(self):
		name = self.w.sender().text()
		print name

# F6 	Index 4 stackedWidget_2
	def dro_f6s2_4_display_b_setText(self):
		self=0
	def dro_f6s2_4_display_c_setText(self):
		self=0
	def dro_f6s2_4_display_u_setText(self):
		self=0
	def dro_f6s2_4_display_v_setText(self):
		self=0
	def dro_f6s2_4_display_w_setText(self):
		self=0

# F7 	dro buttons
	def pb_f7_dro_abs_toggle(self,pressed):
		if pressed:
			STATUS.emit('dro-reference-change-request', 0)
			name = self.w.sender().text()
			print 'Dro changed to:',name

	def pb_f7_dro_rel_toggle(self,pressed):
		if pressed:
			STATUS.emit('dro-reference-change-request', 1)
			name = self.w.sender().text()
			print 'Dro changed to:',name

	def pb_f7_dro_dtg_toggle(self,pressed):
		if pressed:
			STATUS.emit('dro-reference-change-request', 2)
			name = self.w.sender().text()
			print 'Dro changed to:',name

	def pb_f7_dro_units_toggle(self,pressed):  # dro units change requested <<<<
		if pressed:
			if self.machine_info[0]  == 1:		# machine units are in inches dro btn calls for metric increments
				self.jog_control[6] = 2			# metric increments in use now
				self.machine_info[2]  = 2		# values to be converted to metric
				self.label_linear_jog_btns()	# change button and panel labels

			if self.machine_info[0]  == 2:		# machine units are metric but dro btn calls for inch increments
				self.jog_control[6] = 1			# inch increments in use now
				self.machine_info[2]  = 1		# values to be converted to inch
				self.label_linear_jog_btns()	# change button and panel labels

		else: 	 # back to machines ini units <<<<
			if self.machine_info[0]  == 2:		# machine units are metric and dro btn calls for metric increments
				self.jog_control[6] = 2			# metric increments in use now
				self.machine_info[2]  = 2  		# values to be converted to metric
				self.label_linear_jog_btns()	# change button and panel labels

			if self.machine_info[0]  == 1:		# machine units are inch and dro btn calls for inch increments
				self.jog_control[6] = 1			# inch increments in use now
				self.machine_info[2]  = 1		# values to be converted to inch
				self.label_linear_jog_btns()	# change button and panel labels


	def pb_f7_dro_spare_toggle(self,pressed):
		if pressed:
			name = self.w.sender().text()
			print name

# F8	dro displays
	def dro_f8_display_x_setText(self):
		self=0
	def dro_f8_display_y_setText(self):
		self=0
	def dro_f8_display_z_setText(self):
		self=0
	def dro_f8_display_a_setText(self):
		self=0

# F12

	def pb_f12s5_0_jog_pos_x_pressed(self):
		self.jog_control[4]	= 0			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[4] = 1    	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_x_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 0		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()


	def pb_f12s5_0_jog_neg_x_pressed(self):
		self.jog_control[4]	= 0 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[4] = 1     	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_x_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 0		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()


	def pb_f12s5_0_jog_pos_y_pressed(self):
		self.jog_control[4]	= 1			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[4] = 1   		# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_y_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 1		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

		# jog Y neg
	def pb_f12s5_0_jog_neg_y_pressed(self):
		self.jog_control[4]	= 1 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[4] = 1    	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_y_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 1		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

		# jog Z pos
	def pb_f12s5_0_jog_pos_z_pressed(self):
		self.jog_control[4]	= 2			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[4] = 1   	 	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_z_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 2		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_z_pressed(self):
		self.jog_control[4]	= 2 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[4] = 1    	# allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_z_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 2		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_pos_a_pressed(self):
		self.jog_control[4]	= 3			# axis number
		self.jog_control[5] = 1			# direction
		self.machine_info[4] = 1     	# start jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_pos_a_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 3		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

	def pb_f12s5_0_jog_neg_a_pressed(self):
		self.jog_control[4]	= 3 		# axis number
		self.jog_control[5] = -1		# direction
		self.machine_info[4] = 1    	 # allow jogging
		self.jogging_handler()

	def pb_f12s5_0_jog_neg_a_released(self):
		if self.jog_control[2] == 1:	# continous jog
			self.jog_control[4]	= 3		# axis number
			self.jog_control[5] = 0		# direction
			self.machine_info[4] = 2    # stop jogging
			self.jogging_handler()

	def label_panel_labels(self):
		if self.jog_control[6] == 1:	# Inch units
			self.w.plab_f12s6_0_jog_mode_linear.setText('INCH - LINEAR JOG MODE')
			self.w.plab_f12s5_0_jog_incr_label.setText('INCH INCR')
		if self.jog_control[6] == 2:	# metric units
			self.w.plab_f12s6_0_jog_mode_linear.setText('MM - LINEAR JOG MODE')
			self.w.plab_f12s5_0_jog_incr_label.setText('MM INCR')
		if self.jog_control[1] == 3:	# angular
			self.w.plab_f12s5_0_jog_incr_label.setText('DEGREE INCR')

#		jogging position mode - position jog mode is only for use
#		with preset commands read from .ini file
	def pb_f12s5_0_jog_position_toggle(self,pressed):
		self.w.pb_f12s5_0_jog_pos_x.setEnabled(False)
		self.w.pb_f12s5_0_jog_neg_x.setEnabled(False)
		self.w.pb_f12s5_0_jog_pos_y.setEnabled(False)
		self.w.pb_f12s5_0_jog_neg_y.setEnabled(False)
		self.w.pb_f12s5_0_jog_pos_z.setEnabled(False)
		self.w.pb_f12s5_0_jog_neg_z.setEnabled(False)
		self.w.pb_f12s5_0_jog_pos_a.setEnabled(False)
		self.w.pb_f12s5_0_jog_neg_a.setEnabled(False)

		if pressed:
#			STATUS.set_jog_increments(0,0)
			self.w.pb_f12s5_0_jog_continous.setChecked(False)
			self.w.pb_f12s5_0_jog_continous.setEnabled(False)
			self.w.pb_f12s5_0_jog_increment.setChecked(False)
			self.w.pb_f12s5_0_jog_increment.setEnabled(False)
			self.jog_control[1] = 1
			self.w.stackedWidget_6.setCurrentIndex(1)
#			self.w.lab_f12s5_0_jog_incr.setText(str(STATUS.get_jog_increment()))
			self.label_panel_labels()


	def pb_f12s5_0_jog_linear_toggle(self,pressed):
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
			self.w.lab_f12s5_0_jog_incr.setText(str(STATUS.get_jog_increment()))
			self.w.lab_f12s5_0_jog_rate.setText(str(STATUS.get_jograte()))
			self.label_panel_labels()



	def pb_f12s5_0_jog_angular_toggle(self,pressed):
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
			self.w.lab_f12s5_0_jog_incr.setText(str(STATUS.get_jog_increment_angular()))
			self.w.lab_f12s5_0_jog_rate.setText(str(STATUS.get_jograte_angular()))
			self.label_panel_labels()

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
				self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[0]))
			if self.jog_control[6] == 2: 		# metric
				self.jog_control[8] = index
				self.jog_rates[1] = self.metric_increments[index]
				self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[1]))


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
			self.w.lab_f12s5_0_jog_incr.setText(str(self.jog_rates[2]))


	def scrb_f12s6_1_jog_position_slow_setRange(self):
		place_holder=0
	def scrb_f12s6_1_jog_position_fast_setRange(self):
		place_holder=0
	def lab_f12s6_1_jog_position_slow_setText(self):
		place_holder=0
	def lab_f12s6_1_jog_position_fast_setText(self):
		place_holder=0
	def scrb_f12s6_0_jog_linear_slow_setRange(self):
		place_holder=0
	def scrb_f12s6_0_jog_linear_fast_setRange(self):
		place_holder=0
	def lab_f12s6_0_jog_linear_slow_setText(self):
		place_holder=0
	def lab_f12s6_0_jog_linear_fast_setText(self):
		place_holder=0
	def scrb_f12s6_2_jog_angular_slow_setRange(self):
		place_holder=0
	def scrb_f12s6_2_jog_angular_fast_setRange(self):
		place_holder=0
	def lab_f12s6_2_jog_angular_slow_setText(self):
		place_holder=0
	def lab_f12s6_2_jog_angular_fast_setText(self):
		place_holder=0

		# displayed
	def lab_f12s5_0_jog_rate_setText(self):
		place_holder=0
	def lab_f12s5_0_jog_incr_setText(self):
		place_holder=0

# 		end of jogging section


# F9	spindle and dro panel -- stackedWidget_3 index(0)
		# values are adjusted to give 1 rpm change per click - linuxcnc uses revs per second
	def pb_f9_spindle_0_quick_set_0_clicked(self):
		self.w.scrb_f9_spindle_0.setValue(float(self.values_qs0[0])*100)
	def pb_f9_spindle_0_quick_set_1_clicked(self):
		self.w.scrb_f9_spindle_0.setValue(float(self.values_qs0[1])*100)
	def pb_f9_spindle_0_quick_set_2_clicked(self):
		self.w.scrb_f9_spindle_0.setValue(float(self.values_qs0[2])*100)
	def pb_f9_spindle_0_quick_set_3_clicked(self):
		self.w.scrb_f9_spindle_0.setValue(float(self.values_qs0[3])*100)

	def scrb_f9_spindle_0_setRange(self):
		print ''

		# set spindle 0 speed
	def scrb_f9_spindle_0_setValue(self,value):
		spin_0_rps = float(value)/10000
		self.c.spindleoverride(spin_0_rps)
		self.w.lab_f9_spindle_0_rpm.setText(str(self.w.scrb_f9_spindle_0.value()/100))

	def pb_f9_spindle_0_forward_toggle(self):
		ACTION.SET_SPINDLE_ROTATION(linuxcnc.SPINDLE_FORWARD)

	def pb_f9_spindle_0_stop_toggle(self):
		ACTION.SET_SPINDLE_STOP()

	def pb_f9_spindle_0_reverse_toggle(self):
		ACTION.SET_SPINDLE_ROTATION(linuxcnc.SPINDLE_REVERSE)

	def lab_f9_spindle_0_rpm_setText(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setMinimum(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setMaximum(self):
		name = self.w.sender().text()

	def pbar_f9_spindle_0_rpm_setValue(self):
		name = self.w.sender().text()

		# for periodic updates
	def spindle_updates(self):
		self.w.pbar_f9_spindle_0_rpm.setFormat(str(int(self.halcomp0 ['spindle_0_rpm_pbar'])))
		self.w.pbar_f9_spindle_0_rpm.setValue(self.halcomp0 ['spindle_0_rpm_pbar'])
		self.w.pbar_f6s2_0_spindle_1_rpm.setFormat(str(int(self.halcomp0 ['spindle_1_rpm_pbar'])))
		self.w.pbar_f6s2_0_spindle_1_rpm.setValue(self.halcomp0 ['spindle_1_rpm_pbar'])

# F9	sw3_1
#		Hal Xembed: command-string 'matchbox-keyboard --xid' - location and size 0x0x954x228

# F10_0	Gcode graphics display panel
	def pb_f10sw3_0_graph_spare_toggle(self):
		print 'graph_spare_2'
	def pb_f10sw3_0_graph_dro_toggle(self):
		print 'graph_dro'
	def pb_f10sw3_0_zoom_out_pressed(self):
		print 'graph_zoom out'
#		self.w.GRAPHICS_NAME.zoom_out()
	def pb_f10sw3_0_zoom_in_pressed(self):
		print 'graph_zoom in'
#		self.w.GRAPHICS_NAME.zoom_in()
	def pb_f10sw3_0_graph_x_toggle(self):
		STATUS.emit('view-changed', '%s' % 'x')
	def pb_f10sw3_0_graph_y_toggle(self):
		STATUS.emit('view-changed', '%s' % 'y')
	def pb_f10sw3_0_graph_z_toggle(self):
		STATUS.emit('view-changed', '%s' % 'z')
	def pb_f10sw3_0_graph_z2_toggle(self):
		STATUS.emit('view-changed', '%s' % 'z2')
	def pb_f10sw3_0_graph_p_toggle(self):
		STATUS.emit('view-changed', '%s' % 'p')
	def pb_f10sw3_0_graph_clear_clicked(self):
		STATUS.emit('view-changed', '%s' % 'clear')

# F10_1	Homing panel
	def pb_f10sw3_1_home_xyz_toggle(self):
		self.machine_info[3] = 1

	def pb_f10sw3_1_home_x_toggle(self):
		self.c.home(0)
		self.c.wait_complete()

	def pb_f10sw3_1_home_y_toggle(self):
		self.c.home(1)
		self.c.wait_complete()

	def pb_f10sw3_1_home_z_toggle(self):
		self.c.home(2)
		self.c.wait_complete()

	def pb_f10sw3_1_home_a_toggle(self):
		self.c.home(3)
		self.c.wait_complete()

	def pb_f10sw3_1_unhome_all_toggle(self):
		self.c.unhome(-1)

# F11   status panel
	def lab_f11s4_0_mcode_list_setText(self):
		print ''
	def lab_f11s4_0_gcode_list_setText(self):
		print ''
	def lab_f11s4_0_tool_comment_setText(self):
		print ''
	def lab_f11s4_0_tool_number_setText(self):
		print ''
	def lab_f11s4_0_tool_diameter_setText(self):
		print ''
	def lab_f11s4_0_feed_rate_setText(self):
		print ''
	def lab_f11s4_0_feed_per_rev_setText(self):
		print ''

# F11   text display
	def lab_f11s4_1_text_display_setText(self):
		self.w.lab_f11s4_1_text_display_setText('')

# F12   auto mode gcode
	def pb_f12s5_2_gcode_load_pressed(self):
		if self.s.task_mode == 2:
			file_name = str(self.s.file)
			enable = '.ngc' in file_name
			self.auto_no_file(enable)
		# doing this for now
		self.w.pb_f3_file.animateClick()

#		flt = INFO.get_filter_program(str(fname))
#		if not flt:
#			self.c.program_open(str(fname))
#		else:
#			self.open_filter_program(str(fname), flt)
#		STATUS.emit('reload-display')

		# run gcode
	def pb_f12s5_2_gcode_run_pressed(self):
		self.ensure_mode(linuxcnc.MODE_AUTO)
		self.c.auto(linuxcnc.AUTO_RUN,0)

	def pb_f12s5_2_gcode_step_toggle(self):
#		if self.s.task_mode != linuxcnc.MODE_AUTO or self.s.interp_state != linuxcnc.INTERP_IDLE:
#			return
		self.ensure_mode(linuxcnc.MODE_AUTO)
		self.c.auto(linuxcnc.AUTO_STEP)

		# pause
	def pb_f12s5_2_gcode_pause_toggle(self,pressed):
#		if self.s.task_mode != linuxcnc.MODE_AUTO or self.s.interp_state not in (linuxcnc.INTERP_READING, linuxcnc.INTERP_WAITING):
#			return
		if pressed:
			self.c.auto(linuxcnc.AUTO_PAUSE)
		else:
			self.c.auto(linuxcnc.AUTO_RESUME)

#		self.ensure_mode(linuxcnc.MODE_AUTO)
#		if not self.s.paused:
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
	print 'Local current time :', localtime
	return [HandlerClass(halcomp,widgets,paths)]


#END

