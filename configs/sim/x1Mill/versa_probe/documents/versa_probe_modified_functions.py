#hese were modified to suit the requirements of my built in probe screen with
#the latest .ui button names


# probing - button 1 outside corner measurement X+Y-
# =======================================================================================================
	def pbtn_outside_xpym_released(self):
		btn = self.w.sender().objectName()
		meas = "XpLxYmLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X - xy_clearance Y + edge_lenght
		s="""G91
		G1 X-%f Y-%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0]+0.5* float(self.w.input_probe_diam.text()) )
		self.w.status_xp.setText( "%.4f" % xres)
		self.lenght_x()
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move X + edge_lenght +xy_clearance,  Y + edge_lenght + xy_clearance
		a=float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text())
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
		yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % yres )
		self.probe_result_text(btn,meas,0,0,xres,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
#        self.set_zerro("XY")

# probing - button 2 outside and inside straight in measurement Y-
# =======================================================================================================
	def pbtn_outside_ym_released(self):
		btn = self.w.sender().objectName()
		meas = "YmLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		 # move Y + xy_clearance
		s="""G91
		G1 Y%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start yminus.ngc
		if self.ocode ("O<yminus> call") == -1:
			return
		a=self.probed_position_with_offsets()
		yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,0,0,0,0,yres,0,0,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 Y%f" % yres
		if self.gcode(s) == -1:
			return
		self.set_zerro("Y")

# probing - button 3 outside corner measurement X-Y-
# =================================================================================================================
	def pbtn_outside_xmym_released(self):
		btn = self.w.sender().objectName()
		meas = "XmLxYmLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X + xy_clearance Y - edge_lenght
		s="""G91
		G1 X%f Y-%f
		G90""" % (float(self.w.input_xy_clearances.text()), float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0]-0.5* float(self.w.input_probe_diam.text()))
		self.w.status_xm.setText( "%.4f" % xres )
		self.lenght_x()
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move X - edge_lenght - xy_clearance,  Y + edge_lenght + xy_clearance
		a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()))
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
		yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText("%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,xres,0,0,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 4 outside and inside straight in measurement X+
# =================================================================================================================
	def pbtn_outside_xp_released(self):
		btn = self.w.sender().objectName()
		meas = "XpLx"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		 # move X - xy_clearance
		s="""G91
		G1 X-%f
		G90""" % float(self.w.input_xy_clearances.text() )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
	   # Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		a=self.probed_position_with_offsets()
		xres=float(a[0]+0.5* float(self.w.input_probe_diam.text()) )
		self.w.status_xp.setText( "%.4f" % xres )
		self.lenght_x()
		self.probe_result_text(btn,meas,0,0,xres,self.lenght_x(),0,0,0,0,0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f" % xres
		if self.gcode(s) == -1:
			return
		self.set_zerro("X")

# probing - button 5 outside center measurement X+ X- Y+ Y-
# =================================================================================================================
	def pbtn_outside_center_released(self):
		btn = self.w.sender().objectName()
		meas = "XmXcXpLxYmYcYpLyD"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X - edge_lenght- xy_clearance
		s="""G91
		G1 X-%f
		G90""" % (float(self.w.input_side_edge_lenght.text()) +float(self.w.input_xy_clearances.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xpres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move X + 2 edge_lenght + 2 xy_clearance
		aa=2*(float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )
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
		xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xmres )
		xcres=0.5*(xpres+xmres)
		self.w.status_xc.setText( "%.4f" % xcres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# distance to the new center of X from current position
		self.stat.poll()
		to_new_xc=self.stat.position[0]-self.stat.g5x_offset[0] - self.stat.g92_offset[0] - self.stat.tool_offset[0] - xcres
		s = "G1 X%f" % xcres
		if self.gcode(s) == -1:
			return

		# move Y - edge_lenght- xy_clearance
		a=(float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )
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
		ypres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % ypres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move Y + 2 edge_lenght + 2 xy_clearance
		aa=2* (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )
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
		ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % ymres )
		self.lenght_y()
		# find, show and move to finded  point
		ycres=0.5*(ypres+ymres)
		self.w.status_yc.setText( "%.4f" % ycres )
		diam=0.5*((xmres-xpres)+(ymres-ypres))
		self.w.status_d.setText( "%.4f" % diam )
		self.probe_result_text(btn,meas,xmres,xcres,xpres,self.lenght_x(),ymres,ycres,ypres,self.lenght_y(),0,diam,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 Y%f" % ycres
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 6 outside and inside straight in measurement X-
# =================================================================================================================
	def pbtn_outside_xm_released(self):
		btn = self.w.sender().objectName()
		meas = "XmLx"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		 # move X + xy_clearance
		s="""G91
		G1 X%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		a=self.probed_position_with_offsets()
		xres=float(a[0]-0.5* float(self.w.input_probe_diam.text()) )
		self.w.status_xm.setText( "%.4f" % xres )
		self.lenght_x()
		self.probe_result_text(btn,meas,xres,0,0,self.lenght_x(),0,0,0,0,0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f" % xres
		if self.gcode(s) == -1:
			return
		self.set_zerro("X")

# probing - button 7 outside corner measurement X+Y+
# =================================================================================================================
	def pbtn_outside_xpyp_released(self):
		btn = self.w.sender().objectName()
		meas = "XpLxYpLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X - xy_clearance Y + edge_lenght
		s="""G91
		G1 X-%f Y%f
		G90""" % (float(self.w.input_xy_clearances.text()), float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres= float(a[0]+0.5* float(self.w.input_probe_diam.text()) )
		self.w.status_xp.setText( "%.4f" % xres )
		self.lenght_x()
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move X + edge_lenght +xy_clearance,  Y - edge_lenght - xy_clearance
		a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,0,0,xres,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 8 outside and inside straight in measurement Y+
# =================================================================================================================
	def pbtn_outside_yp_released(self):
		btn = self.w.sender().objectName()
		meas = "YpLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		 # move Y - xy_clearance
		s="""G91
		G1 Y-%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start yplus.ngc
		if self.ocode ("O<yplus> call") == -1:
			return
		a=self.probed_position_with_offsets()
		yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,0,0,0,0,0,0,yres,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 Y%f" % yres
		if self.gcode(s) == -1:
			return
		self.set_zerro("Y")

# probing - button 9 outside corner measurement X-Y+
# =================================================================================================================
	def pbtn_outside_xmyp_released(self):
		btn = self.w.sender().objectName()
		meas = "XmLxYpLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X + xy_clearance Y + edge_lenght
		s="""G91
		G1 X%f Y%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0]-0.5* float(self.w.input_probe_diam.text()) )
		self.w.status_xm.setText( "%.4f" % xres )
		self.lenght_x()
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return

		# move X - edge_lenght - xy_clearance,  Y - edge_lenght - xy_clearance
		a= (float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,xres,0,0,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")


# ================================================================================================================
# Inside probing shares four buttons with outside probing for
# the movement that moves straight in but opposite direction.
#
# probing - button 1 inside corner measurement X-Y+
# =================================================================================================================
	def pbtn_inside_xmyp_released(self):
		btn = self.w.sender().objectName()
		meas = "XmLxYpLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y - edge_lenght X + xy_clearance
		s="""G91
		G1 X%f Y-%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xres )
		self.lenght_x()

		# move X + edge_lenght Y - xy_clearance
		tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,xres,0,0,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 3 inside corner measurement X+Y+
# =================================================================================================================
	def pbtn_inside_xpyp_released(self):
		btn = self.w.sender().objectName()
		meas = "XpLxYpLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y - edge_lenght X - xy_clearance
		s="""G91
		G1 X-%f Y-%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xres )
		self.lenght_x()

		# move X - edge_lenght Y - xy_clearance
		tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,0,0,xres,self.lenght_x(),0,0,yres,self.lenght_y(),0,0,0)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 5 inside hole center measurement Xin- Xin+ Yin- Yin+
# =================================================================================================================
	def pbtn_inside_xy_hole_released(self):
		btn = self.w.sender().objectName()
		meas = "XmXcXpLxYmYcYpLyD"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		if self.z_clearance_down() == -1:
			return
		# move X - edge_lenght Y + xy_clearance
		tmpx= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xmres )

		# move X +2 edge_lenght - 2 xy_clearance
		tmpx=2* (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xpres )
		self.lenght_x()
		xcres=0.5*(xmres+xpres)
		self.w.status_xc.setText( "%.4f" % xcres )

		# move X to new center
		s="""G1 X%f""" % (xcres)
		if self.gcode(s) == -1:
			return

		# move Y - edge_lenght + xy_clearance
		tmpy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % ymres )

		# move Y +2 edge_lenght - 2 xy_clearance
		tmpy=2* (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		ypres=float(a[1])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % ypres )
		self.lenght_y()
		# find, show and move to finded  point
		ycres=0.5*(ymres+ypres)
		self.w.status_yc.setText( "%.4f" % ycres )
		diam=0.5*((xpres-xmres)+(ypres-ymres))
		self.w.status_d.setText( "%.4f" % diam )
		self.probe_result_text(btn,meas,xmres,xcres,xpres,self.lenght_x(),ymres,ycres,ypres,self.lenght_y(),0,diam,0)
		# move to center
		s = "G1 Y%f" % ycres
		if self.gcode(s) == -1:
			return
		# move Z to start point
		self.z_clearance_up()
		self.set_zerro("XY")

# probing - button 7 inside corner measurement X-Y-
# =================================================================================================================
	def pbtn_inside_xmym_released(self):
		btn = self.w.sender().objectName()
		meas = "XmLxYmLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y + edge_lenght X + xy_clearance
		s="""G91
		G1 X%f Y%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xres )
		self.lenght_x()

		# move X + edge_lenght Y - xy_clearance
		tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,xres,0,0,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 9 inside corner measurement X+Y-
# ================================================================================================
	def pbtn_inside_xpym_released(self):
		btn = self.w.sender().objectName()
		meas = "XpLxYmLy"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y + edge_lenght X - xy_clearance
		s="""G91
		G1 X-%f Y%f
		G90""" % (float(self.w.input_xy_clearances.text()),float(self.w.input_side_edge_lenght.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xres )
		self.lenght_x()

		# move X - edge_lenght Y + xy_clearance
		tmpxy= (float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()) )
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
		yres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % yres )
		self.lenght_y()
		self.probe_result_text(btn,meas,0,0,xres,self.lenght_x(),yres,0,0,self.lenght_y(),0,0,0)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 X%f Y%f" % (xres,yres)
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 1 skew measurement X+X+
# =======================================================================================================
	def pbtn_skew_xp_released(self):
		btn = self.w.sender().objectName()
		meas = "XcXpA"
		self.stat.poll()
		ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
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
		xcres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xc.setText( "%.4f" % xcres )

		# move Y - edge_lenght
		s="""G91
		G1 Y-%f
		G90""" % float(self.w.input_side_edge_lenght.text())
		if self.gcode(s) == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xpres )
		alfa=math.degrees(math.atan2(xcres-xpres,float(self.w.input_side_edge_lenght.text())) )
		self.probe_result_text(btn,meas,0,xcres,xpres,0,0,0,0,0,0,0,alfa)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move XY to adj start point
		s="G1 X%f Y%f" % (xcres,ystart)
		if self.gcode(s) == -1:
			return
		self.rotate_coord_system(alfa)

# probing - button 2 skew measurement Y-Y-
# =======================================================================================================
	def pbtn_skew_ym_released(self):
		btn = self.w.sender().objectName()
		meas = "YmYcA"
		self.stat.poll()
		xstart=self.stat.position[0]-self.stat.g5x_offset[0] - self.stat.g92_offset[0] - self.stat.tool_offset[0]
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y + xy_clearance
		s="""G91
		G1 Y%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start yminus.ngc
		if self.ocode ("O<yminus> call") == -1:
			return
		# show Y result
		a=self.probed_position_with_offsets()
		ycres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_yc.setText( "%.4f" % ycres )

		# move X - edge_lenght
		s="""G91
		G1 X-%f
		G90""" % float(self.w.input_side_edge_lenght.text())
		if self.gcode(s) == -1:
			return
		# Start yminus.ngc
		if self.ocode ("O<yminus> call") == -1:
			return
		# show Y result
		a=self.probed_position_with_offsets()
		ymres=float(a[1])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_ym.setText("%.4f" % ymres )
		alfa=math.degrees(math.atan2(ycres-ymres,float(self.w.input_side_edge_lenght.text())) )
		self.probe_result_text(btn,meas,0,0,0,0,ymres,ycres,0,0,0,0,alfa)
		# move Z to start point
		if self.z_clearance_up() == -1:
		   return
		# move XY to adj start point
		s="G1 X%f Y%f" % (xstart,ycres)
		return
		self.rotate_coord_system(alfa)

# probing - button 3 skew measurement X+X+
# =======================================================================================================
	def pbtn_skew_yp_released(self):
		btn = self.w.sender().objectName()
		meas = "XcXpA"
		self.stat.poll()
		ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
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
		xcres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xc.setText( "%.4f" % xcres )

		# move Y - edge_lenght
		s="""G91
		G1 Y-%f
		G90""" % float(self.w.input_side_edge_lenght.text())
		if self.gcode(s) == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText("%.4f" % xpres )
		alfa=math.degrees(math.atan2(xcres-xpres, float(self.w.input_side_edge_lenght.text())) )
		self.probe_result_text(btn,meas,0,xcres,xpres,0,0,0,0,0,0,0,alfa)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move XY to adj start point
		s="G1 X%f Y%f" % (xcres,ystart)
		if self.gcode(s) == -1:
			return
		self.rotate_coord_system(alfa)

# probing - button 4 skew measurement X-X-
# =======================================================================================================
	def pbtn_skew_xm_released(self):
		btn = self.w.sender().objectName()
		meas = "XmXcA"
		self.stat.poll()
		ystart=self.stat.position[1]-self.stat.g5x_offset[1] - self.stat.g92_offset[1] - self.stat.tool_offset[1]
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X + xy_clearance
		s="""G91
		G1 X%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xcres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xc.setText( "%.4f" % xcres )

		# move Y + edge_lenght
		s="""G91
		G1 Y%f
		G90""" % float(self.w.input_side_edge_lenght.text())
		if self.gcode(s) == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText("%.4f" % xmres )
		alfa=math.degrees(math.atan2(xcres-xmres,float(self.w.input_side_edge_lenght.text())) )
		self.probe_result_text(btn,meas,xmres,xcres,0,0,0,0,0,0,0,0,alfa)
		# move Z to start point
		if self.z_clearance_up() == -1:
			return
		# move XY to adj start point
		s="G1 X%f Y%f" % (xcres,ystart)
		if self.gcode(s) == -1:
			return
		self.rotate_coord_system(alfa)

# probing - button 1 Lx IN inside lenght x
# =======================================================================================================
	def pbtn_inside_lenght_x_released(self):
		btn = self.w.sender().objectName()
		meas = "XmXcXpLx"
		print "pbtn_inside_lenght_x_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		if self.z_clearance_down() == -1:
			return
		# move X - edge_lenght Y + xy_clearance
		tmpx= float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text())
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
		xmres=float(a[0])-0.5* float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xmres )

		# move X +2 edge_lenght - 2 xy_clearance
		tmpx=2* float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text())
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
		xpres=float(a[0])+0.5* float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xpres )
		self.lenght_x()
		xcres=0.5*(xmres+xpres)
		self.w.status_xc.setText( "%.4f" % xcres )
		self.probe_result_text(btn,meas,xmres,xcres,xpres,self.lenght_x(),0,0,0,0,0,0,0)
		# move X to new center
		s="""G1 X%f""" % (xcres)
		if self.gcode(s) == -1:
			return
		# move Z to start point
		self.z_clearance_up()
		self.set_zerro("XY")

# probing - button 2 Lx outside lenght x
# =======================================================================================================
	def pbtn_outside_lenght_x_released(self):
		btn = self.w.sender().objectName()
		meas = "XmXcXpLx"
		print "pbtn_outside_lenght_x_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move X - edge_lenght- xy_clearance
		s="""G91
		G1 X-%f
		G90""" % (float(self.w.input_side_edge_lenght.text()) + float(self.w.input_xy_clearances.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xpres=float(a[0])+0.5*float(self.w.input_probe_diam.text())
		self.w.status_xp.setText( "%.4f" % xpres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point X
		s = "G1 X%f" % xpres
		if self.gcode(s) == -1:
			return

		# move X + 2 edge_lenght +  xy_clearance
		aa=2*float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text())
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
		xmres=float(a[0])-0.5*float(self.w.input_probe_diam.text())
		self.w.status_xm.setText( "%.4f" % xmres )
		self.lenght_x()
		xcres=0.5*(xpres+xmres)
		self.w.status_xc.setText( "%.4f" % xcres )
		self.probe_result_text(btn,meas,xmres,xcres,xpres,self.lenght_x(),0,0,0,0,0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# go to the new center of X
		s = "G1 X%f" % xcres
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 3 Ly IN inside lenght y
# =======================================================================================================
	def pbtn_inside_lenght_y_released(self):
		btn = self.w.sender().objectName()
		meas = "YmYcYpLy"
		print "pbtn_inside_lenght_y_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		if self.z_clearance_down() == -1:
			return
		# move Y - edge_lenght + xy_clearance
		tmpy=float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text())
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
		ymres=float(a[1])-0.5*float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % ymres )

		# move Y +2 edge_lenght - 2 xy_clearance
		tmpy=2*(float(self.w.input_side_edge_lenght.text())-float(self.w.input_xy_clearances.text()))
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
		ypres=float(a[1])+0.5*float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % ypres )
		self.lenght_y()
		# find, show and move to finded  point
		ycres=0.5*(ymres+ypres)
		self.w.status_yc.setText( "%.4f" % ycres )
		self.probe_result_text(btn,meas,0,0,0,0,ymres,ycres,ypres,self.lenght_y(),0,0,0)
		# move to center
		s = "G1 Y%f" % ycres
		if self.gcode(s) == -1:
			return
		# move Z to start point
		self.z_clearance_up()
		self.set_zerro("XY")

# probing - button 4 Ly OUT outside lenght y
# =======================================================================================================
	def pbtn_outside_lenght_y_released(self):
		btn = self.w.sender().objectName()
		meas = "YmYcYpLy"
		print "pbtn_outside_lenght_y_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move Y - edge_lenght- xy_clearance
		a=float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text())
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
		ypres=float(a[1])+0.5*float(self.w.input_probe_diam.text())
		self.w.status_yp.setText( "%.4f" % ypres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point Y
		s = "G1 Y%f" % ypres
		if self.gcode(s) == -1:
			return

		# move Y + 2 edge_lenght +  xy_clearance
		aa=2*float(self.w.input_side_edge_lenght.text())+float(self.w.input_xy_clearances.text())
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
		ymres=float(a[1])-0.5*float(self.w.input_probe_diam.text())
		self.w.status_ym.setText( "%.4f" % ymres )
		self.lenght_y()
		# find, show and move to finded  point
		ycres=0.5*(ypres+ymres)
		self.w.status_yc.setText( "%.4f" % ycres )
		self.probe_result_text(btn,meas,0,0,0,0,ymres,ycres,ypres,self.lenght_y(),0,0,0)
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point
		s = "G1 Y%f" % ycres
		if self.gcode(s) == -1:
			return
		self.set_zerro("XY")

# probing - button 5 straight down
# =======================================================================================================
	def pbtn_down_released(self):
		btn = ("5 ") + self.w.sender().objectName()
		meas = "Z"
		print "down_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# Start down.ngc
		if self.ocode ("O<down> call") == -1:
			return
		a=self.probed_position_with_offsets()
		self.w.status_z.setText("%.4f" % float(a[2]) )
		self.probe_result_text(btn,meas,0,0,0,0,0,0,0,0,a[2],0,0)
 #       self.set_zerro("Z",0,0,a[2]

# probing - button 6 tool diameter -
# =======================================================================================================
	def pbtn_measure_diam_released(self):
		btn = self.w.sender().objectName()
		meas = "XcYcZD"
		print "pbtn_measure_diam_released"
		self.cmnd.mode( linuxcnc.MODE_MDI )
		self.cmnd.wait_complete()
		# move XY to Tool Setter point
		# Start gotots.ngc
		if self.ocode ("O<gotots> call") == -1:
			return
		# move X - edge_lenght- xy_clearance
		s="""G91
		G1 X-%f
		G90""" % (.5*float(self.tsdiam)+float(self.w.input_xy_clearances.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xplus.ngc
		if self.ocode ("O<xplus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xpres=float(a[0])+0.5*float(self.w.input_probe_diam.text())
#        self.w.status_xp.setText( "%.4f" % xpres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point X
		s = "G1 X%f" % xpres
		if self.gcode(s) == -1:
			return

		# move X + tsdiam +  xy_clearance
		s="""G91
		G1 X%f
		G90""" % (float(self.tsdiam)+float(self.w.input_xy_clearances.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc

		if self.ocode ("O<xminus> call") == -1:
			return
		# show X result
		a=self.probed_position_with_offsets()
		xmres=float(a[0])-0.5*float(self.w.input_probe_diam.text())
#        self.w.status_xm.setText( "%.4f" % xmres )
		self.lenght_x()
		xcres=0.5*(xpres+xmres)
		self.w.status_xc.setText( "%.4f" % xcres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# go to the new center of X
		s = "G1 X%f" % xcres
		if self.gcode(s) == -1:
			return


		# move Y - tsdiam/2 - xy_clearance
		a=0.5*float(self.tsdiam)+float(self.w.input_xy_clearances.text())
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
		ypres=float(a[1])+0.5*float(self.w.input_probe_diam.text())
#        self.w.status_yp.setText( "%.4f" % ypres )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		# move to finded  point Y
		s = "G1 Y%f" % ypres
		if self.gcode(s) == -1:
			return

		# move Y + tsdiam +  xy_clearance
		s="""G91
		G1 Y%f
		G90""" % (float(self.tsdiam)+float(self.w.input_xy_clearances.text()) )
		if self.gcode(s) == -1:
			return
		if self.z_clearance_down() == -1:
			return
		# Start xminus.ngc
		if self.ocode ("O<yminus> call") == -1:
			return
		# show Y result
		a=self.probed_position_with_offsets()
		ymres=float(a[1])-0.5*float(self.w.input_probe_diam.text())
#        self.w.status_ym.setText( "%.4f" % ymres )
		self.lenght_y()
		# find, show and move to finded  point
		ycres=0.5*(ypres+ymres)
		self.w.status_yc.setText( "%.4f" % ycres )
		diam=float(self.w.input_probe_diam.text())+(ymres-ypres-float(self.tsdiam))
		self.w.status_d.setText( "%.4f" % diam )
		# move Z to start point up
		if self.z_clearance_up() == -1:
			return
		self.stat.poll()
		tmpz=self.stat.position[2] - 4
		self.probe_result_text(btn,meas,0,xcres,0,0,0,ycres,0,0,tmpz,diam,0)
		# move to finded  point
		s = "G1 Y%f" % ycres
		if self.gcode(s) == -1:
			return

# probing - auto zero and auto skew allow select
# =======================================================================================================
	def pbtn_allow_auto_zero_toggle(self,pressed):
		if pressed:
#             self.w.led_auto_zero_warning=True
			 print "PBTN Allow Auto Zero"
		else:
			print "PBTN Dont Allow Auto Zero"
	def pbtn_allow_auto_skew_toggle(self,pressed):
		if pressed:
#            self.w.led_auto_skew_warning=True
			print "PBTN Allow Auto Skew"
		else:
			print "PBTN Dont Allow Auto Skew"

# probing - set offsets for values entered by inputs
# =======================================================================================================
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

# probing - inputs for the offest values above
# =======================================================================================================
	def input_adj_x_enter(self):
		self.halcomp["ps_adj_x"] = self.w.input_adj_x.text()
		offset_x= (self.w.input_adj_x.text())
		print "offset_x ",offset_x
		# to set a status label
		self.w.status_xm.setText(offset_x)
		# to read a status label
		status_1=(self.w.status_xm.text())
		print "Status_1 ",status_1

	def input_adj_y_enter(self):
		self.halcomp["ps_adj_y"] = self.w.input_adj_y.text()
		offset_y= (self.w.input_adj_y.text())
		print "offset_y ",offset_y
		# to set a status label
		self.w.status_xp.setText(offset_y)
		# to read a status label
		status_2=(self.w.status_xp.text())
		print "Status_2 ",status_2

	def input_adj_z_enter(self):
		self.halcomp["ps_adj_z"] = self.w.input_adj_z.text()
		offset_z= (self.w.input_adj_z.text())
		print "offset_z ",offset_z
		# to set a status label
		self.w.status_ym.setText(offset_z)
		# to read a status label
		status_3=(self.w.status_ym.text())
		print "Status_3 ",status_3

	def input_adj_angle_enter(self):
		self.halcomp["ps_adj_angle"] = self.w.input_adj_angle.text()
		offset_angle= (self.w.input_adj_angle.text())
		print "offset_angle ",offset_angle
		# to set a status label
		self.w.status_yp.setText(offset_angle)
		# to read a status label
		status_4=(self.w.status_yp.text())
		print "Status_4 ",status_4

# probing - inputs - for primary values
# =======================================================================================================
	def input_probe_diam_enter(self):
		self.halcomp["ps_probe_diam"] = self.w.input_probe_diam.text()
		probe_diam= (self.w.input_probe_diam.text())
		print "input Probe_diam ",probe_diam

	def input_max_travel_enter(self):
		self.halcomp["ps_max_travel"] = self.w.input_max_travel.text()
		print "input max_travel ",max_travel

	def input_latch_return_dist_enter(self):
		self.halcomp["ps_latch_return_dist"] = self.w.input_latch_return_dist.text()
		latch_return_dist= (self.w.input_latch_return_dist.text())
		print "input latch_return_dist ",latch_return_dist

	def input_search_vel_enter(self):
		self.halcomp["ps_search_vel"] = self.w.input_search_vel.text()
		search_vel= (self.w.input_search_vel.text())
		print "input search_vel ",search_vel

	def input_probe_vel_enter(self):
		self.halcomp["ps_probe_vel"] = self.w.input_probe_vel.text()
		probe_vel= (self.w.input_probe_vel.text())
		print "input probe_vel ",probe_vel

	def input_side_edge_lenght_enter(self):
		self.halcomp["ps_side_edge_lenght"] = self.w.input_side_edge_lenght.text()
		side_edge_lenght= (self.w.input_side_edge_lenght.text())
		print "input side_edge_lenght ",side_edge_lenght

	def input_xy_clearances_enter(self):
		self.halcomp["ps_xy_clearances"] = self.w.input_xy_clearances.text()
		xy_clearances= (self.w.input_xy_clearances.text())
		print "input xy_clearances ",xy_clearances

	def input_z_clearance_enter(self):
		self.halcomp["ps_z_clearance"] = self.w.input_z_clearance.text()
		z_clearance= (self.w.input_z_clearance.text())
		print "input z_clearance ",z_clearance

	def input_tool_probe_height_enter(self):
		tool_probe_height= (self.w.input_tool_probe_height.text())
		print "input_tool_probe_height", tool_probe_height

	def input_tool_block_height_enter(self):
		tool_block_height= (self.w.input_tool_block_height.text())
		print "input_tool_probe_height", tool_block_height

	def pbtn_use_tool_measurement_toggle(self):
		print "use_tool_measurement - enabling remap m6"

	def pbtn_probe_history_toggle(self,pressed):
		if pressed:
			self.w.stackedWidget_6.setCurrentIndex(1)
			print "pbtn_probe_history_toggle pushed"
		else :
			self.w.stackedWidget_6.setCurrentIndex(0)
			print "pbtn_probe_history_toggle released"

# probing - status display labels which are used to display and store values
# =======================================================================================================
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

# Probing history values to text box and console
# ===============================================================================================================================
	def probe_result_text(link,name,meas="",xm=0.,xc=0.,xp=0.,lx=0.,ym=0.,yc=0.,yp=0.,ly=0.,z=0.,d=0.,a=0.):
		time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		probed_data=("")
		global probed_data
		if "Xm" in meas :
			probed_data += "X-=%.4f "%xm
		if "Xc" in meas :
			probed_data += "Xc=%.4f "%xc
		if "Xp" in meas :
			probed_data += "X+=%.4f "%xp
		if "Lx" in meas :
			probed_data += "Lx=%.4f "%lx
		if "Ym" in meas :
			probed_data += "Y-=%.4f "%ym
		if "Yc" in meas :
			probed_data += "Yc=%.4f "%yc
		if "Yp" in meas :
			probed_data += "Y+=%.4f "%yp
		if "Ly" in meas :
			probed_data += "Ly=%.4f "%ly
		if "Z" in meas :
			probed_data += "Z=%.4f  "%z
		if "D" in meas :
			probed_data += "D=%.4f  "%d
		if "A" in meas :
			probed_data += "Angle=%.3f "%a

		# to lab_probe_text display
		probed_data=name + ":  " + probed_data
		# print to console
		print time,":",name,":",probed_data
		return probed_data



# probing calculate corner coordinates in rotated coord. system
# =========================================
	def calc_cross_rott(self,x1=0.,y1=0.,x2=0.,y2=0.,a1=0.,a2=90.) :
		coord = [0,0]
		k1=math.tan(math.radians(a1))
		k2=math.tan(math.radians(a2))
		coord[0]=(k1*x1-k2*x2+y2-y1)/(k1-k2)
		coord[1]=k1*(coord[0]-x1)+y1
		return coord

# probing rotate point coordinates
# =========================================
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

# probing rotate around 0,0 point coordinates
# =========================================
	def rott00_point(self,x1=0.,y1=0.,a1=0.) :
		coord = [x1,y1]
		if a1 != 0:
			t = math.radians(a1)
			coord[0] = x1 * math.cos(t) - y1 * math.sin(t)
			coord[1] = x1 * math.sin(t) + y1 * math.cos(t)
		return coord

# probing position with offsets
# =========================================
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

# probing gcode
# =========================================
	def gcode(self,s, data = None):
		for l in s.split("\n"):
			if "G1" in l :
				l+= " F#<_ini[TOOLSENSOR]RAPID_SPEED>"
			self.cmnd.mdi( l )
			self.cmnd.wait_complete()
			if self.error_poll() == -1:
				return -1
		return 0

# probing subroutine calls
# =========================================
	def ocode(self,s, data = None):
		print "Sub Routine Call",s
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

# probing z  clearance
# =========================================
	def z_clearance_down(self, data = None):
		# move Z - z_clearance
		s="""G91
		G1 Z-%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return -1
		return 0

# probing z up
# =========================================
	def z_clearance_up(self, data = None):
		# move Z + z_clearance
		s="""G91
		G1 Z%f
		G90""" % float(self.w.input_xy_clearances.text())
		if self.gcode(s) == -1:
			return -1
		return 0

# probing lenght x
# =========================================
	def lenght_x(self, data = None):
		res=0
		if self.w.status_xm.text() == "" or self.w.status_xp.text() == "" :
			return res
		xm = float(self.w.status_xm.text())
		xp = float(self.w.status_xp.text())
		if xm < xp :
			res=xp-xm
		else:
			res=xm-xp
		self.w.status_lx.setText("%.4f" % res)
		return res

# probing lenght y
# =========================================
	def lenght_y(self, data = None):
		res=0
		if self.w.status_ym.text() == "" or self.w.status_yp.text() == "" :
			return res
		ym = float(self.w.status_ym.text())
		yp = float(self.w.status_yp.text())
		if ym < yp :
			res=yp-ym
		else:
			res=ym-yp
		self.w.status_ly.setText("%.4f" % res)
		return res

# probing set zero
# =========================================
	def set_zerro(self,s="XYZ",x=0.,y=0.,z=0.):
		if  self.w.pbtn_allow_auto_skew.isChecked():
			print "Allow Auto Zero Routine"
			#  Z current position
			self.stat.poll()
			tmpz=self.stat.position[2]-self.stat.g5x_offset[2] - self.stat.g92_offset[2] - self.stat.tool_offset[2]
			c = "G10 L20 P0"
			s=s.upper()
			if "X" in s :
				x+= float(self.w.input_adj_x.text())
				c += " X%s"%x
			if "Y" in s :
				y+= float(self.w.input_adj_y.text())
				c += " Y%s"%y
			if "Z" in s :
				tmpz=tmpz-z+ float(self.w.input_adj_z.text())
				c += " Z%s"%tmpz
			self.gcode(c)
			time.sleep(1)
		else:
			print  "Dont Allow Auto Zero Routine"

# skew adjust
# =========================================
	def rotate_coord_system(self,a=0.):
		s="G10 L2 P0"
		self.w.input_adj_angle.setText("%.3f" %  a)
		self.w.status_a.setText( "%.3f" % a)
		if  self.w.pbtn_allow_auto_skew.isChecked():
			 print "Allow Auto Skew Routine"
			 if self.w.pbtn_allow_auto_zero.isChecked():
				s +=  " X%s"% float(self.w.input_adj_x.text())
				s +=  " Y%s"% float(self.w.input_adj_y.text())
		else:
				print "Dont Allow Auto Skew Routine"
				self.stat.poll()
				x=self.stat.position[0]
				y=self.stat.position[1]
				s +=  " X%s"%x
				s +=  " Y%s"%y
		s +=  " R%s"%a
		self.gcode(s)
		print s
		time.sleep(1)

# end
# ========================================================================================================

