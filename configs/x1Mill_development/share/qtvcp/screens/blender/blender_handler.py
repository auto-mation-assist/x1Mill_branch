############################
# **** IMPORT SECTION **** #
############################

from PyQt5 import QtCore, QtWidgets
from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFVIEW_WIDGET
from qtvcp.widgets.dialog_widget import CamViewDialog as CAMVIEW
from qtvcp.widgets.dialog_widget import MacroTabDialog as LATHEMACRO
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action

# Set up logging
from qtvcp import logger
log = logger.getLogger(__name__)

import linuxcnc
import sys
import os

###########################################
# **** instantiate libraries section **** #
###########################################

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()
###################################
# **** HANDLER CLASS SECTION **** #
###################################

class HandlerClass:

    ########################
    # **** INITIALIZE **** #
    ########################
    # widgets allows access to  widgets from the qtvcp files
    # at this point the widgets and hal pins are not instantiated
    def __init__(self, halcomp,widgets,paths):
        self.hal = halcomp
        self.w = widgets
        self.stat = linuxcnc.stat()
        self.cmnd = linuxcnc.command()
        self.error = linuxcnc.error_channel()
        self.PATHS = paths
        self.IMAGE_PATH = paths.IMAGEDIR

    ##########################################
    # Special Functions called from QTSCREEN
    ##########################################

    # at this point:
    # the widgets are instantiated.
    # the HAL pins are built but HAL is not set ready
    def initialized__(self):
        STATUS.emit('play-alert','SPEAK This is the blender screen for Qt V C P')

    def processed_key_event__(self,receiver,event,is_pressed,key,code,shift,cntrl):
        # when typing in MDI, we don't want keybinding to call functions
        # so we catch and process the events directly.
        # We do want ESC, F1 and F2 to call keybinding functions though
        if code not in(QtCore.Qt.Key_Escape,QtCore.Qt.Key_F1 ,QtCore.Qt.Key_F2,
                    QtCore.Qt.Key_F3,QtCore.Qt.Key_F5,QtCore.Qt.Key_F5):
            if isinstance(receiver, OFFVIEW_WIDGET) or isinstance(receiver, MDI_WIDGET):
                if is_pressed:
                    receiver.keyPressEvent(event)
                    event.accept()
                return True
            if isinstance(receiver,QtWidgets.QDialog):
                print 'dialog'
                return True
        try:
            KEYBIND.call(self,event,is_pressed,shift,cntrl)
            return True
        except Exception as e:
            #log.debug('Exception loading Macros:', exc_info=e)
            print 'Error in, or no function for: %s in handler file for-%s'%(KEYBIND.convert(event),key)
            if e:
                print e
            #print 'from %s'% receiver
            return False

    ########################
    # callbacks from STATUS #
    ########################

    #######################
    # callbacks from form #
    #######################

    #####################
    # general functions #
    #####################

    def kb_jog(self, state, joint, direction, fast = False, linear = True):
        if linear:
            distance = STATUS.get_jog_increment()
            rate = STATUS.get_jograte()/60
        else:
            distance = STATUS.get_jog_increment_angular()
            rate = STATUS.get_jograte_angular()/60
        if state:
            if fast:
                rate = rate * 2
            ACTION.JOG(joint, direction, rate, distance)
        else:
            ACTION.JOG(joint, 0, 0, 0)

    #####################
    # KEY BINDING CALLS #
    #####################

    # Machine control
    def on_keycall_ESTOP(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_ESTOP_STATE(STATUS.estop_is_clear())
    def on_keycall_POWER(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_MACHINE_STATE(not STATUS.machine_is_on())
    def on_keycall_HOME(self,event,state,shift,cntrl):
        if state:
            if STATUS.is_all_homed():
                ACTION.SET_MACHINE_UNHOMED(-1)
            else:
                ACTION.SET_MACHINE_HOMING(-1)
    def on_keycall_ABORT(self,event,state,shift,cntrl):
        if state:
            if STATUS.stat.interp_state == linuxcnc.INTERP_IDLE:
                self.w.close()
            else:
                self.cmnd.abort()

    # Linear Jogging
    def on_keycall_XPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, 1, shift)

    def on_keycall_XNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, -1, shift)

    def on_keycall_YPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, 1, shift)

    def on_keycall_YNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, -1, shift)

    def on_keycall_ZPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, 1, shift)

    def on_keycall_ZNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, -1, shift)

    def on_keycall_APOS(self,event,state,shift,cntrl):
        pass
        #self.kb_jog(state, 3, 1, shift, False)

    def on_keycall_ANEG(self,event,state,shift,cntrl):
        pass
        #self.kb_jog(state, 3, -1, shift, linear=False)

    ###########################
    # **** closing event **** #
    ###########################

    ##############################
    # required class boiler code #
    ##############################

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)

################################
# required handler boiler code #
################################

def get_handlers(halcomp,widgets,paths):
     return [HandlerClass(halcomp,widgets,paths)]

#####################################################################
# Styles - put them here to keep things tidy
#####################################################################
class Styles:
    def __init__(self, widgets, paths):
        self.w = widgets
        self.PATH = paths.CONFIGPATH
        self.IMAGE_PATH = paths.IMAGEDIR

    def bright_style(self):
        self.w.setStyleSheet('''#MainWindow {background: black; }
QLineEdit {
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #888);
padding: 1px;
border-style: solid;
border: 2px solid gray;
border-radius: 8px;
}

QPushButton {
color: #333;
border: 2px solid #555;
border-radius: 11px;
padding: 5px;
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #888);
min-width: 40px;
}

 QPushButton:hover {
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
}

QPushButton:pressed {
background: qradialgradient(cx: 0.4, cy: -0.1,
fx: 0.4, fy: -0.1,
radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}
QPushButton:checked {
background: qradialgradient(cx: 0.4, cy: -0.1,
fx: 0.4, fy: -0.1,
radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}

QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 5px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
    stop: 0 #66e, stop: 1 #bbf);
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
    stop: 0 #bbf, stop: 1 #55f);
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 1px solid #777;
width: 20px;
margin-top: -7px;
margin-bottom: -75px;
border-radius: 4px;

}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border: 1px solid #444;
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
min-height: 30px;
}
#frame_man { border: 3px solid gray;border-radius: 15px;
background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0000ff, stop: 1 #141529);
 }

''')

        style ='''#frame { border: 3px solid gray;border-radius: 15px;
background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0000ff, stop: 1 #141529);
 } '''
        try:
            self.w.frame.setStyleSheet(style)
        except:
            pass
        try:
            style ='''QFrame { border: 3px solid gray;border-radius: 15px;
background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0000ff, stop: 1 #141529);
 } '''
            self.w.frame_mdi.setStyleSheet(style)
            self.w.frame_auto.setStyleSheet(style)
            self.w.frame_auto_2.setStyleSheet(style)
            self.w.frame_auto_3.setStyleSheet(style)
            self.w.frame_auto_4.setStyleSheet(style)
            self.w.frame_auto_5.setStyleSheet(style)
            self.w.frame_auto_6.setStyleSheet(style)
            self.w.frame_auto_7.setStyleSheet(style)
            self.w.frame_auto_8.setStyleSheet(style)
            self.w.frame_auto_9.setStyleSheet(style)
            self.w.frame_auto_10.setStyleSheet(style)
        except:
            pass

    def dark_style(self):
        self.w.setStyleSheet('''#MainWindow {background: black; }
QLineEdit {
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #888);
padding: 1px;
border-style: solid;
border: 2px solid gray;
border-radius: 8px;
}

QPushButton {
color: #333;
border: 2px solid #555;
border-radius: 11px;
padding: 5px;
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #888);
min-width: 40px;
}

 QPushButton:hover {
background: qradialgradient(cx: 0.3, cy: -0.4,
fx: 0.3, fy: -0.4,
radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
}

QPushButton:pressed {
background: qradialgradient(cx: 0.4, cy: -0.1,
fx: 0.4, fy: -0.1,
radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}
QPushButton:checked {
background: qradialgradient(cx: 0.4, cy: -0.1,
fx: 0.4, fy: -0.1,
radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}

QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 5px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
    stop: 0 #66e, stop: 1 #bbf);
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
    stop: 0 #bbf, stop: 1 #55f);
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 1px solid #777;
width: 20px;
margin-top: -7px;
margin-bottom: -75px;
border-radius: 4px;

}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border: 1px solid #444;
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
min-height: 30px;
}
#frame_man { border: 3px solid gray;border-radius: 15px;
background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #38395a, stop: 1 #141529);
 }

''')

        style ='''QFrame { border: 3px solid gray;border-radius: 15px;
background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #38395a, stop: 1 #141529);
 } '''
        try:

            self.w.frame.setStyleSheet(style)
        except:
            pass
        try:
            self.w.frame_mdi.setStyleSheet(style)
            self.w.frame_auto.setStyleSheet(style)
            self.w.frame_auto_2.setStyleSheet(style)
            self.w.frame_auto_3.setStyleSheet(style)
            self.w.frame_auto_4.setStyleSheet(style)
            self.w.frame_auto_5.setStyleSheet(style)
            self.w.frame_auto_6.setStyleSheet(style)
            self.w.frame_auto_7.setStyleSheet(style)
            self.w.frame_auto_8.setStyleSheet(style)
            self.w.frame_auto_9.setStyleSheet(style)
            self.w.frame_auto_10.setStyleSheet(style)
        except:
            pass
