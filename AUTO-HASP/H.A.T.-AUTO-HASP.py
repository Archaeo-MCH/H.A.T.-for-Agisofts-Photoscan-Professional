#__author__ = "Marcel C. Hagner, Alexey Pasumansky, Kolja Hick"
#__copyright__ = "Copyright 2016, LAD@RPS and MCH"
#__credits__ = ["Marcel C. Hagner", "Przemysław P. Sikora"]
#__license__ = "GPL3"
#__version__ = "1.4.0"
#__maintainer__ = "Marcel C. Hagner"
#__email__ = "hagner.archaeo@gmx.de"
#__status__ = "Prototype"
# Compatibility - PhotoScan Professional 1.1.3

# Das HASP-AUTO-Skript V.1.4 MCH  LAD@RPS 2016

# Imports
import os
import time
import random
import PhotoScan
from PySide import QtCore, QtGui




# Dialog class
class AutoScriptDialog(QtGui.QDialog):
	
	# Constants and definitions
	BTN_WIDTH = 130
	BTN_HEIGHT = 40
	LBL_BTN_LOW = "Niedrig"
	LBL_BTN_MEDIUM = "Mittel"
	LBL_BTN_HIGH = "Hoch"
	LBL_BTN_QUIT = "Quit"
	LBL_WIN = "HASP-AUTO-Script"
	LBL_EXPL = "The HASP-AUTO-Script."	
	
	
	# Constructor
	def __init__(self, parent):
	
		QtGui.QDialog.__init__(self, parent)
		
		self.blend_types = {"Average": PhotoScan.BlendingMode.AverageBlending, "Mosaic": PhotoScan.BlendingMode.MosaicBlending, "Min intensity": PhotoScan.BlendingMode.MinBlending, "Max Intensity": PhotoScan.BlendingMode.MaxBlending}

		# Define elements
		self.setWindowTitle(LBL_WIN)
		
		self.resTxt = QtGui.QLabel()
		self.resTxt.setText(LBL_EXPL)
		self.resTxt.setFixedSize(BTN_WIDTH, BTN_HEIGHT)	
		
		self.btnQuit = QtGui.QPushButton(LBL_BTN_QUIT)
		self.btnQuit.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
		self.btnQuit.setStyleSheet('QPushButton {background-color: #A3C1DA; color: #ff0000;}')
		
		self.btnProcessLow = QtGui.QPushButton(LBL_BTN_LOW)
		self.btnProcessLow.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
		
		self.btnProcessMedium = QtGui.QPushButton(LBL_BTN_MEDIUM)
		self.btnProcessMedium.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
		
		self.btnProcessHigh = QtGui.QPushButton(LBL_BTN_HIGH)
		self.btnProcessHigh.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
		
		# Place elements on popup 		
		layout = QtGui.QGridLayout()
		layout.addWidget(self.resTxt, 0, 0)		
		layout.addWidget(self.btnProcessLow, 2, 1)
		layout.addWidget(self.btnProcessMedium, 2, 2)
		layout.addWidget(self.btnProcessHigh, 2, 3)
		layout.addWidget(self.btnQuit, 3, 3)
		self.setLayout(layout)  
	
	
		proc_low = lambda : self.Auto_script_Workflow(PhotoScan.HighAccuracy, PhotoScan.LowQuality, PhotoScan.MediumFaceCount, 4048)
		proc_med = lambda : self.Auto_script_Workflow(PhotoScan.HighAccuracy, PhotoScan.MediumQuality, PhotoScan.MediumFaceCount, 9000)
		proc_hig = lambda : self.Auto_script_Workflow(PhotoScan.HighAccuracy, PhotoScan.HighQuality, PhotoScan.HighFaceCount, 12000)
		
		QtCore.QObject.connect(self.btnProcessLow, QtCore.SIGNAL("clicked()"), proc_low)
		QtCore.QObject.connect(self.btnProcessMedium, QtCore.SIGNAL("clicked()"), proc_med)
		QtCore.QObject.connect(self.btnProcessHigh, QtCore.SIGNAL("clicked()"), proc_hig)
		QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))	

		self.exec	

	# Build workflow
	def Auto_script_Workflow(self, paramAccuracy, paramQuality, paramModelFaceCount, paramTextureSize):
	
			print("-------------------------------------")
			print("Workflow parameter")			
			print("Accuracy: " + str(paramAccuracy))
			print("Quality: " + str(paramQuality))
			print("FaceCount: " + str(paramModelFaceCount))
			print("TextureSize: " + str(paramTextureSize))
						
			
			try:
				path = PhotoScan.app.getExistingDirectory("Bitte wählen Sie den Zielordner mit den gesammelten *.psz Projekten") # Select directory
				chunk = PhotoScan.app.document.chunk # Define chunk
				project_list = os.listdir(path) # Load all files in directory
				print("Selected path: " + str(path))
			except FileNotFoundError:
				print("Error while selecting path. Script will abort.")
				return
			
			doc = PhotoScan.app.document			
			crs = PhotoScan.app.getCoordinateSystem("Please, select a coordinate system.") # Select coordinate system
			print("Selected coordinate system: " + str(crs))
				
			try:
				for project_name in project_list: # Iterate through all files
				
					if ".PSZ" in project_name.upper(): # Check if file extension is PSZ
					
						print("Processing initiated for project: " + str(project_name))
						
						doc.open(path + "/" + project_name) # Open the project
						doc.chunk.crs = crs # Set coordinate system
						
						chunk = doc.chunks[0] 
						chunk.matchPhotos(accuracy=paramAccuracy) # Align photos
						chunk.alignCameras()
						
						chunk.buildDenseCloud(quality=paramQuality) # Build density cloud
						PhotoScan.app.update()
						
						chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation, face_count=paramModelFaceCount) # Build model
						PhotoScan.app.update()
						
						chunk.buildUV(mapping=PhotoScan.GenericMapping)
						chunk.buildTexture(blending=PhotoScan.AverageBlending, color_correction=True, size=paramTextureSize) # Textur average, color correction on size 12000
						PhotoScan.app.update()
						
						chunk.detectMarkers(type=PhotoScan.CircularTarget12bit,tolerance=100) # 12 bit marker will be searched with tolerance 100
						PhotoScan.app.update()
						
						doc.save(absolute_paths = True) # Save project with absolute path
						
						print("Processed project: " + project_name) 

					else:
						continue # Next file
						
			except KeyboardInterrupt:
				print("Process was stopped by user.") 
				return
					
					
			print("Processing was successfull.")
			
			return
	
# Script entry point
def main():
	# Start dialog and pass active window instance
	dlg = AutoScriptDialog(QtGui.QApplication.instance().activeWindow())
	
# Add menu entry in Agisoft PhotoScan
PhotoScan.app.addMenuItem("HagnerArchaeoTools/H.A.T.-Auto HASP", main) # Tab wird eingeladen
