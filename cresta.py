# Main file for CrESTA

#kivy needed for app
import kivy
kivy.require('2.1.0')

#python packages
import os, subprocess
from threading import Thread, Lock
import re
from collections import defaultdict
import shutil
import time
import pandas as pd
import numpy as np
import starfile
import mrcfile
import matplotlib.pyplot as plt
import weakref
from datetime import timedelta, datetime
import random
import mrcfile
import starfile
from scipy.spatial.transform import Rotation as R
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

#import tom.py
import tom

#disabling multi-touch kivy emulation
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
#importing necessary kivy features
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
Window.size = (900,900)

#importing kivy file
Builder.load_file(os.getcwd() + '/gui.kv')

class Cresta(App):

	def build(self):
		self.icon = 'bin/crestalogo.png'
		self.title = 'CrESTA'
		return Tabs()

# classes used to save filechooser selections
class StarFinder(FloatLayout):
	stardsave = ObjectProperty(None)
	text_input = ObjectProperty(None)
	cancel = ObjectProperty(None)

class StarFiltFinder(FloatLayout):
	stardfiltsave = ObjectProperty(None)
	text_input = ObjectProperty(None)
	cancel = ObjectProperty(None)
    
class SubtomoFinder(FloatLayout):
    subtomodsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class CMMFinder(FloatLayout):
    cmmdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class WedgeFinder(FloatLayout):
    wedgedsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class MrcFinder(FloatLayout):
    mrcdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class TomoFinder(FloatLayout):
    tomodsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class TomoCoordsFinder(FloatLayout):
    tomocoordsdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class StartVecFinder(FloatLayout):
    startvecdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class EndVecFinder(FloatLayout):
    endvecdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class MaskFinder(FloatLayout):
    maskdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class RefPathFinder(FloatLayout):
    refpathdsave = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class Tabs(TabbedPanel):
	
	# create gaussian row
	label = Label(text="Sigma")
	label2 = Label(text=" ", size_hint_y=.8)
	sigma = TextInput(text="5", multiline=False, size_hint_x=.12, size_hint_y=1.9, pos_hint={'center_x': .5, 'center_y': .5}, cursor_color=(0,0,0,1), halign='center')

	# close filechooser popups
	def dismiss_popup(self):
		self._popup.dismiss()
		
	# star file unfiltered save
	def show_star(self):
		content = StarFinder(stardsave=self.starsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Unfiltered Star File", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def starsave(self, path, filename):
		starfpath = filename.strip()
		if len(starfpath) != 0:
			if starfpath.endswith('.star') == False:
				self.ids.mainstar.hint_text = 'Not a ".star" file — Enter/Choose Unfiltered Star File Path'
			else:
				self.ids.mainstar.text = starfpath
				self.ids.mainsubtomo.text = "/".join(self.ids.mainstar.text.split("/")[:-1]) + '/'
				starfilted = starfpath.replace('.star', '_filtered.star')
				if os.path.isfile(starfilted) == True:
					self.ids.mainstarfilt.text = starfilted
				else:
					self.ids.mainstarfilt.hint_text = 'Enter/Choose Filtered Star File Path'
		elif len(starfpath) == 0:
			self.ids.mainstar.hint_text = 'Enter/Choose Unfiltered Star File Path'
		self.dismiss_popup()

	# star file filtered save
	def show_starfilt(self):
		content = StarFiltFinder(stardfiltsave=self.starfiltsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Filtered Star File", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def starfiltsave(self, path, filename):
		starfiltpath = filename.strip()
		if len(starfiltpath) != 0:
			if starfiltpath.endswith('.star') == False:
				self.ids.mainstarfilt.hint_text = 'Not a ".star" file — Enter/Choose Unfiltered Star File Path'
			else:
				self.ids.mainstarfilt.text = starfiltpath
				self.ids.mainsubtomo.text = "/".join(self.ids.mainstarfilt.text.split("/")[:-1]) + '/'
		elif len(starfiltpath) == 0:
			self.ids.mainstarfilt.hint_text = 'Enter/Choose Filtered Star File Path'
		self.dismiss_popup()

	# subtomogram directory save
	def show_subtomo(self):
		content = SubtomoFinder(subtomodsave=self.subtomosave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Subtomogram Directory", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def subtomosave(self, path, filename):
		subtomopath = path.strip()
		if len(subtomopath) != 0:
			self.ids.mainsubtomo.text = subtomopath + '/'
		elif len(subtomopath) == 0:
			self.ids.mainsubtomo.hint_text = 'Enter/Choose Subtomogram Directory'
		self.dismiss_popup()

	# cmm file directory save
	def show_cmm(self):
		content = CMMFinder(cmmdsave=self.cmmsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save CMM Files Directory", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def cmmsave(self, path, filename):
		cmmpath = path.strip()
		if len(cmmpath) != 0:
			self.ids.maincmm.text = cmmpath + '/'
		elif len(cmmpath) == 0:
			self.ids.maincmm.hint_text = 'Enter/Choose CMM Files Directory'
		self.dismiss_popup()

	# wedge file save
	def show_wedge(self):
		content = WedgeFinder(wedgedsave=self.wedgesave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Wedge File", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def wedgesave(self, path, filename):
		wedgepath = filename.strip()
		if len(wedgepath) != 0:
			self.ids.mainwedge.text = wedgepath
		elif len(wedgepath) == 0:
			self.ids.mainwedge.hint_text = 'Enter/Choose Wedge File'
		self.dismiss_popup()

	# mrc file save
	def show_mrc(self):
		content = MrcFinder(mrcdsave=self.mrcsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Mrc Directory", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def mrcsave(self, path, filename):
		mrcpath = path.strip()
		if len(mrcpath) != 0:
			self.ids.mainmrc.text = mrcpath + '/'
		elif len(mrcpath) == 0:
			self.ids.mainmrc.text = 'Choose Mrc Directory'
		self.dismiss_popup()

	# change extraction appearance if the user selected automated extraction
	# ATB: included definitions for vectorStart and vectorEnd text boxes and buttons, Jan. 24, 2024
	def updateExtract(self):
		if self.ids.tomoFolder.active == True:
			self.ids.tomo.text = ''
			self.ids.tomo.hint_text = 'Choose Directory with Tomogram Folders (or Data Collection Folders with Tomogram Folders).\nEach Tomogram Folder should contain a tomogram (.mrc) and corresponding coordinate file (.coords)\n(and optionally .coordsM, .coordsC files)'
			self.ids.tomocoords.hint_text = 'Disabled'
			self.ids.tomocoords.text = ''
			self.ids.tomocoords.readonly = True
			self.ids.tomocoordbutton.background_color = (1, 1, 1, .5)
			self.ids.tomocoordbutton.disabled = True
			self.ids.vectorStart.hint_text = 'Disabled'
			self.ids.vectorStart.text = ''
			self.ids.vectorStart.readonly = True
			self.ids.vectorStartButton.background_color = (1, 1, 1, .5)
			self.ids.vectorStartButton.disabled = True
			self.ids.vectorEnd.hint_text = 'Disabled'
			self.ids.vectorEnd.text = ''
			self.ids.vectorEnd.readonly = True
			self.ids.vectorEndButton.background_color = (1, 1, 1, .5)
			self.ids.vectorEndButton.disabled = True
		else:
			self.ids.tomo.text = ''
			self.ids.tomo.hint_text = 'Enter/Choose Tomogram Path'
			self.ids.tomocoords.hint_text = 'Enter/Choose Coords Path .coords'
			self.ids.tomocoords.readonly = False
			self.ids.tomocoordbutton.background_color = (1, 1, 1, 1)
			self.ids.tomocoordbutton.disabled = False
			self.ids.vectorStart.hint_text = 'Enter/Choose Vector Start Coords .coordsM (leave blank if not available)'
			self.ids.vectorStart.readonly = False
			self.ids.vectorStartButton.background_color = (1, 1, 1, 1)
			self.ids.vectorStartButton.disabled = False
			self.ids.vectorEnd.hint_text = 'Enter/Choose Vector End Coords .coordsC (leave blank if not available)'
			self.ids.vectorEnd.readonly = False
			self.ids.vectorEndButton.background_color = (1, 1, 1, 1)
			self.ids.vectorEndButton.disabled = False

	def updateFilterDirectory(self):
		if self.ids.mrcfilter.active == True:
			self.ids.mainmrc.hint_text = 'Enter/Choose Mrc Directory'
			self.ids.mainmrc.text = ''
			self.ids.mainmrc.readonly = False
			self.ids.mainmrc.cursor_blink = True
			self.ids.mrcfilter.background_color = (1, 1, 1, 1)
			# self.ids.mrcfilter.disabled = False
		elif self.ids.starfilter.active == True:
			self.ids.mainmrc.hint_text = 'Disabled'
			self.ids.mainmrc.text = ''
			self.ids.mainmrc.readonly = True
			self.ids.mainmrc.cursor_blink = False
			self.ids.mrcfilter.background_color = (1, 1, 1, .5)
			# self.ids.mrcfilter.disabled = True
		else:
			self.ids.mainmrc.hint_text = 'Pick Either Star File or Subtomogram Directory Filtering'
			self.ids.mainmrc.text = ''
			self.ids.mainmrc.readonly = True
			self.ids.mainmrc.cursor_blink = False
			self.ids.mrcfilter.background_color = (1, 1, 1, .5)
			# self.ids.mrcfilter.disabled = True

	# tomogram path save
	def show_tomo(self):
		content = TomoFinder(tomodsave=self.tomosave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Tomogram Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def tomosave(self, path, filename):
		if self.ids.tomoFolder.active == False:
			tomopath = filename.strip()
		else: 
			tomopath = path.strip() + '/'
		if len(tomopath) != 0:
			if tomopath.endswith('.mrc') == False and self.ids.tomoFolder.active == False:
				self.ids.tomo.hint_text = 'Not a ".mrc" file — Enter/Choose Tomogram Path'
			else:
				self.ids.tomo.text = tomopath
		elif len(tomopath) == 0:
			self.ids.tomo.hint_text = 'Enter/Choose Tomogram Path'
		self.dismiss_popup()

	# tomogram coords path save
	def show_tomocoords(self):
		content = TomoCoordsFinder(tomocoordsdsave=self.tomocoordssave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Tomogram Coords Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def tomocoordssave(self, path, filename):
		tomocoordspath = filename.strip()
		if len(tomocoordspath) != 0:
			self.ids.tomocoords.text = tomocoordspath
		elif len(tomocoordspath) == 0:
			self.ids.tomocoords.hint_text = 'Enter/Choose Coords Path .coords'
		self.dismiss_popup()

	# start vector path save
	def show_startvec(self):
		content = StartVecFinder(startvecdsave=self.startvecsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Start Vector Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def startvecsave(self, path, filename):
		startvecpath = filename.strip()
		if len(startvecpath) != 0:
			self.ids.vectorStart.text = startvecpath
		elif len(startvecpath) == 0:
			self.ids.vectorStart.hint_text = 'Enter/Choose Vector Start Coords .coordsM (leave blank if not available)'
		self.dismiss_popup()

	# end vector path save
	def show_endvec(self):
		content = EndVecFinder(endvecdsave=self.endvecsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save End Vector Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def endvecsave(self, path, filename):
		endvecpath = filename.strip()
		if len(endvecpath) != 0:
			self.ids.vectorEnd.text = endvecpath
		elif len(endvecpath) == 0:
			self.ids.vectorEnd.hint_text = 'Enter/Choose Vector End Coords .coordsC (leave blank if not available)'
		self.dismiss_popup()

	# mask path save
	def show_mask(self):
		content = MaskFinder(maskdsave=self.masksave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Mask Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def masksave(self, path, filename):
		maskpath = filename.strip()
		if len(maskpath) != 0:
			if maskpath.endswith('.mrc') == False:
				self.ids.maskpath.hint_text = 'Not a ".mrc" file — Enter/Choose Mask Path'
			else:
				self.ids.maskpath.text = maskpath
		elif len(maskpath) == 0:
			self.ids.maskpath.hint_text = 'Enter/Choose Mask Path (mask.mrc)'
		self.dismiss_popup()

	# ref path save
	def show_refpath(self):
		content = RefPathFinder(refpathdsave=self.refpathsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Ref Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def refpathsave(self, path, filename):
		refpath = path.strip()
		if len(refpath) != 0:
			self.ids.refPath.text = refpath + '/'
		elif len(refpath) == 0:
			self.ids.refPath.hint_text = 'Enter/Choose Ref Path'
		self.dismiss_popup()

	# function to add a slash to the end of a path
	def addslash(self, path):
		if path != '':
			if path[-1] != '/':
				path = path + '/'
		return path

	# save project info
	def savedata(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			# add slash to the end of the save path
			self.ids.save.text = self.addslash(self.ids.save.text)
			# create text file with saved project data and text inputs
			save = self.ids.save.text + self.ids.savename.text + '.txt'
			file_opt = open(save, 'w')
			file_opt.writelines('Project ' + self.ids.savename.text + '\n')
			file_opt.writelines('StarFileUnfilt:' + '\t' + self.ids.mainstar.text + '\n')
			file_opt.writelines('StarFileFilt:' + '\t' + self.ids.mainstarfilt.text + '\n')
			file_opt.writelines('SubtomoPath:' + '\t' + self.ids.mainsubtomo.text + '\n')
			file_opt.writelines('CMMPath:' + '\t' + self.ids.maincmm.text + '\n')
			file_opt.writelines('WedgePath:' + '\t' + self.ids.mainwedge.text + '\n')
			file_opt.writelines('MrcPath:' + '\t' + self.ids.mainmrc.text + '\n')
			file_opt.writelines('BoxSize:' + '\t' + self.ids.px1.text + '\n')
			file_opt.writelines('PxSize:' + '\t' + self.ids.A1.text + '\n')
			file_opt.writelines('Threads:' + '\t' + self.ids.CPU.text + '\n')
			file_opt.writelines('ChimeraX:' + '\t' + self.ids.chimera_path.text + '\n')
			file_opt.writelines('Tomogram:' + '\t' + self.ids.tomo.text + '\n')
			file_opt.writelines('TomoCoord:' + '\t' + self.ids.tomocoords.text + '\n')
			file_opt.writelines('StartVect:' + '\t' + self.ids.vectorStart.text + '\n')
			file_opt.writelines('EndVect:' + '\t' + self.ids.vectorEnd.text + '\n')
			file_opt.writelines('Index:' + '\t' + self.ids.index.text + '\n')
			file_opt.writelines('Indall:' + '\t' + self.ids.index2.text + '\n')
			file_opt.writelines('Defocus:' + '\t' + self.ids.defoc.text + '\n')
			file_opt.writelines('SnrFall:' + '\t' + self.ids.snrval.text + '\n')
			file_opt.writelines('Highpass:' + '\t' + self.ids.highpass.text + '\n')
			file_opt.writelines('Voltage:' + '\t' + self.ids.voltage.text + '\n')
			file_opt.writelines('CS:' + '\t' + self.ids.cs.text + '\n')
			file_opt.writelines('Envelope:' + '\t' + self.ids.envelope.text + '\n')
			file_opt.writelines('BFactor:' + '\t' + self.ids.bfactor.text + '\n')
			file_opt.writelines('Sigma:' + '\t' + self.ids.sigma.text + '\n')
			file_opt.writelines('Filename:' + '\t' + self.ids.filenameget.text + '\n')
			file_opt.writelines('MaskPath:' + '\t' + self.ids.maskpath.text + '\n')
			file_opt.writelines('SDThresh:' + '\t' + self.ids.sdrange.text + '\n')
			file_opt.writelines('SDShift:' + '\t' + self.ids.sdshift.text + '\n')
			file_opt.writelines('MaskBlur:' + '\t' + self.ids.blurrate.text + '\n')
			file_opt.writelines('Volvol:' + '\t' + self.ids.volvol.text + '\n')
			file_opt.writelines('RefPath:' + '\t' + self.ids.refPath.text + '\n')
			file_opt.writelines('RefBasename:' + '\t' + self.ids.refBasename.text + '\n')
			file_opt.writelines('NewSubname:' + '\t' + self.ids.newSubtomoName.text + '\n')
			file_opt.writelines('SubCsvFile:' + '\t' + self.ids.subCsvFile.text + '\n')
			file_opt.writelines('RefSubPath:' + '\t' + self.ids.subRefPath.text + '\n')
			file_opt.writelines('RefSubBasename:' + '\t' + self.ids.subRefBasename.text + '\n')
			file_opt.close()
			self.ids.pullpath.text = save
		except IndexError:
			print('Enter a project directory and name')

	# load existing project information from a project file
	def pulldata(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			load = self.ids.pullpath.text
			with open(load) as pull:
				direct, proj = os.path.split(load)
				self.ids.save.text = direct
				self.ids.savename.text = proj.replace('.txt', '')
				for line in pull:
					pinfo = line.split()
					try:
						# get all elements from pinfo after the first element
						yank = ' '.join(pinfo[1:])
					except IndexError:
						yank = ''
					if re.search('StarFileUnfilt', line):
						self.ids.mainstar.text = yank
					if re.search('StarFileFilt', line):
						self.ids.mainstarfilt.text = yank
					if re.search('SubtomoPath', line):
						self.ids.mainsubtomo.text = yank
					if re.search('CMMPath', line):
						self.ids.maincmm.text = yank
					if re.search('WedgePath', line):
						self.ids.mainwedge.text = yank
					if re.search('MrcPath', line):
						self.ids.mainmrc.text = yank
					if re.search('BoxSize', line):
						self.ids.px1.text = yank
					if re.search('PxSize', line):
						self.ids.A1.text = yank
					if re.search('Threads', line):
						self.ids.CPU.text = yank
					if re.search('ChimeraX', line):
						self.ids.chimera_path.text = yank
					if re.search('Tomogram', line):
						self.ids.tomo.text = yank
					if re.search('TomoCoord', line):
						self.ids.tomocoords.text = yank
					if re.search('StartVect', line):
						self.ids.vectorStart.text = yank
					if re.search('EndVect', line):
						self.ids.vectorEnd.text = yank
					if re.search('Index', line):
						self.ids.index.text = yank
					if re.search('Indall', line):
						self.ids.index2.text = yank
					if re.search('Defocus', line):
						self.ids.defoc.text = yank
					if re.search('SnrFall', line):
						self.ids.snrval.text = yank
					if re.search('Highpass', line):
						self.ids.highpass.text = yank
					if re.search('Voltage', line):
						self.ids.voltage.text = yank
					if re.search('CS', line):
						self.ids.cs.text = yank
					if re.search('Envelope', line):
						self.ids.envelope.text = yank
					if re.search('BFactor', line):
						self.ids.bfactor.text = yank
					if re.search('Sigma', line):
						self.ids.sigma.text = yank
					if re.search('Filename', line):
						self.ids.filenameget.text = yank
					if re.search('MaskPath', line):
						self.ids.maskpath.text = yank	
					if re.search('SDThresh', line):
						self.ids.sdrange.text = yank
					if re.search('SDShift', line):
						self.ids.sdshift.text = yank	
					if re.search('MaskBlur', line):
						self.ids.blurrate.text = yank	
					if re.search('Volvol', line):
						self.ids.volvol.text = yank
					if re.search('RefPath', line):
						self.ids.refPath.text = yank
					if re.search('RefBasename', line):
						self.ids.refBasename.text = yank
					if re.search('NewSubname', line):
						self.ids.newSubtomoName.text = yank
					if re.search('SubCsvFile', line):
						self.ids.subCsvFile.text = yank
					if re.search('RefSubPath', line):
						self.ids.subRefPath.text = yank
					if re.search('RefSubBasename', line):
						self.ids.subRefBasename.text = yank
		except FileNotFoundError:
			print('Enter a file path')
		except IsADirectoryError:
			print('Enter a text file')

	# transition between wiener and gaussian filters
	def show_screen(self):
		self.ids.first_row_wiener.clear_widgets()
		self.ids.second_row_wiener.clear_widgets()
		self.ids.gaussian_row.clear_widgets()
		
		if self.ids.wienerbutton.active == True:
			self.ids.first_row_wiener.add_widget(self.ids.boxone)
			self.ids.first_row_wiener.add_widget(self.ids.boxtwo)
			self.ids.first_row_wiener.add_widget(self.ids.boxthree)
			self.ids.first_row_wiener.add_widget(self.ids.boxfour)
			self.ids.second_row_wiener.add_widget(self.ids.boxfive)
			self.ids.second_row_wiener.add_widget(self.ids.boxsix)
			self.ids.second_row_wiener.add_widget(self.ids.boxseven)
			self.ids.second_row_wiener.add_widget(self.ids.boxeight)

		if self.ids.gaussianbutton.active == True:
			self.ids.gaussian_row.add_widget(Tabs.label)
			self.ids.gaussian_row.add_widget(Tabs.label2)
			self.ids.gaussian_row.add_widget(Tabs.sigma)

		if not(self.ids.wienerbutton.active) and not(self.ids.gaussianbutton.active):
			text = Label(text="Please select a filter")
			self.ids.gaussian_row.add_widget(text)
	
	# tomogram extraction. Here a tomogram may be extracted from a text file containing 3 column coordinates. Additional files containing other points may optionally be used to generate rotation vectors. Files need to match in length
	def extract(self):
		# Recursive Batch Extraction
		if self.ids.tomoFolder.active:
			folder = self.ids.tomo.text
			# Iterate over the files in the directory
			# ATB: changed listdir to walk for a recursive walk. Jan 27, 2024
			for root, dirs, files in os.walk(folder):
				for name in dirs:
					tomoFolder = os.path.join(root,name)
					# Get tomogram and coordsfile from tomogram folder
					tomogram = ''
					coordfile = ''
					# ATB: added optional vectorStart and vectorEnd fields, Jan. 25 2024
					coordStart = ''
					coordEnd = ''
					for file in os.listdir(tomoFolder):
						if file.endswith('.mrc'):
							tomogram = os.path.join(tomoFolder, file)
						if file.endswith('.coords'):
							coordfile = os.path.join(tomoFolder, file)
						# ATB: added optional vectorStart and vectorEnd fields, Jan. 25 2024
						if file.endswith('.coordsM'):
							coordStart = os.path.join(tomoFolder, file)
						if file.endswith('.coordsC'):
							coordEnd = os.path.join(tomoFolder, file)
					# ATB: if there is no .mrc and no .coord file in that directory do not perform the extraction. Silent exit. January 27, 2024
					if tomogram == '':
						continue
					if coordfile == '':
						continue
					# Perform extraction
					self.extract_helper(tomogram, coordfile, coordStart, coordEnd)
		# Regular Extraction
		else:
			tomogram = self.ids.tomo.text
			coordfile = self.ids.tomocoords.text
			# ATB: added vectorStart and vectorEnd fields, Jan. 25 2024
			coordStart = self.ids.vectorStart.text
			coordEnd = self.ids.vectorEnd.text            
			self.extract_helper(tomogram, coordfile, coordStart, coordEnd)

	# extraction helper function
	def extract_helper(self, tomogram, coordfile, coordStart, coordEnd):
		# tomogram path
		direct = '/'.join(tomogram.split('/')[:-3]) + '/'
		# tomogram date and name
		tomDate = tomogram.split('/')[-3]
		tomName = tomogram.split('/')[-2]
		tomogName = tomogram.split('/')[-1].replace('.mrc', '')
		# use for star file micrographName and imageName
		micrograph = tomDate + '/' + tomName + '/' + tomogram.split('/')[-1]
		subdirect = tomDate + '/' + tomName + '/sub/'
		# set wedge file name
		# check if Choose Wedge File or the word Choose is contained in the text input
		if self.ids.mainwedge.text == 'Choose Wedge File' or 'Choose' or '' in self.ids.mainwedge.text:
			wedge = 'NA'
		else:
			wedge = (self.ids.mainwedge.text).replace(direct, '')
		# use for full path containing subtomograms
		directory = direct + subdirect
		# check that the tomogram path exists
		if os.path.isfile(tomogram) == False:
			print('Error: Tomogram path does not exist')
			return
		# memory map the tomogram
		tomogram = mrcfile.mmap(tomogram)
		# ATB: calculate the size of 3D tomogram volume. Jan 21, 2024
		TomogramSize = tomogram.data.shape
		boxsize = float(self.ids.px1.text)
		angpix = float(self.ids.A1.text)
		if os.path.isdir(directory) == False:
			os.makedirs(directory)
		# ATB: create array of center positions, Jan 24, 2024
		icoor=0
		with open(coordfile, 'r') as coord:
			coord = coord.readlines()
			coordnumber = len(coord)
			xposarray = np.zeros(coordnumber)
			yposarray = np.zeros(coordnumber)
			zposarray = np.zeros(coordnumber)
			newangs = np.zeros((coordnumber, 3))
			for line in coord:
				# access center positions from coords file
				if line != '':
					line = line.strip()
					pos = []
					pos = line.split() # splits line by whitespace
					# append the x,y,z from each coord file to row (converted to float)
					xposarray[icoor] = float(pos[0])
					yposarray[icoor] = float(pos[1])
					zposarray[icoor] = float(pos[2])
					icoor=icoor+1
		# ATB: optionally read the vector start / end positions and calculate angles, Jan 24, 2024
		if os.path.isfile(coordStart) and os.path.isfile(coordEnd):
			data = []
			iangle=0
			with open(coordStart, 'r') as mem, open(coordEnd, 'r') as cen:
				for lineM, lineC in zip(mem, cen):
					if lineM != '' and lineC != '':
						lineM = lineM.strip()
						lineC = lineC.strip()
						posM = re.split(r'[,\.;:\s]+', lineM) # splits line by delimiters including one or more whitespaces, commas, periods, colons, and semi-colons
						posC = re.split(r'[,\.;:\s]+', lineC) # splits line by delimiters including one or more whitespaces, commas, periods, colons, and semi-colons
						# append the x,y,z from each coord file to row
						row = [posM[0], posM[1], posM[2], posC[0], posC[1], posC[2]]
						data.append(row)
						iangle=iangle+1
			columns = ['Xmem', 'Ymem', 'Zmem', 'Xcen', 'Ycen', 'Zcen']
			# convert data to dataframe
			dataframe = pd.DataFrame(data, columns=columns)
			# call calcangles function from tom.py
			newangs = tom.calcangles(dataframe)
			if icoor != iangle:
				print ('Error: the length of vector start/end files do not match the length of coordinate file')
				return
	
		# create an empty data list for the rows
		data = []
		def extractLoop(i):
			# create subtomogram file name
			number = '000000' + str(i)
			number = number[-6:]
			name = directory + tomogName + number + '.mrc'
			# create imageName for star file
			starName = subdirect + tomogName + number + '.mrc'
			# calculate top left corner of boxsize for extraction
			x = xposarray[i] - boxsize/2
			y = yposarray[i] - boxsize/2
			z = zposarray[i] - boxsize/2
			# calculate bounds
			bound = np.zeros(3)
			bound[0] = z + boxsize - 1
			bound[1] = y + boxsize - 1
			bound[2] = x + boxsize - 1
			# rounding
			bound = np.round(bound).astype(int)
			z = np.round(z).astype(int)
			y = np.round(y).astype(int)
			x = np.round(x).astype(int)
			# ATB: check if subtomogram is within tomogram bounds. Jan 21, 2024
			if (z>=0 and y>=0 and x>=0 and bound[0]+1<=TomogramSize[0] and bound[1]+1<=TomogramSize[1] and bound[2]+1<=TomogramSize[2]):
				# create and append star file rows for subtomogram
				row = [micrograph, x, y, z, starName, wedge, 0, 0, newangs[i,0], newangs[i,1], newangs[i,2], 0, 0, 0, 0, 0, 0, 0]
				data.append(row)
				# cut the tomogram
				out = tomogram.data[z:(bound[0]+1), y:(bound[1]+1), x:(bound[2]+1)]
				# invert subtomograms if selected
				if self.ids.extractInvert.active == True:
					out = out * -1
				# create subtomogram
				mrcfile.new(name, out, overwrite=True)
				# ATB: print extracted coordinate position. Jan 21, 2024
				print('Extracted subtomogram ' + name + ' at center position ', xposarray[i], yposarray[i], zposarray[i])
				# change pixel size
				with mrcfile.open(name, 'r+') as mrc:
					mrc.voxel_size = angpix
			else:
				print ('Extraction with specified box size exceeds tomogram borders. Not extracted: ' + name + ' at center position ', xposarray[i],yposarray[i],zposarray[i]) 

		# thread in batches to optimize runtime
		threads = []
		batch_size = int(self.ids.CPU.text)
		lenCoord = len(xposarray)
		fileLen = range(lenCoord)
		batches = [fileLen[i:i+batch_size] for i in range(0, lenCoord, batch_size)]
		for batch in batches:
			for i in batch:
				threads.append(Thread(target = extractLoop, args = (i,)))
				threads[i].start()
			for i in batch:
				threads[i].join()
		for thread in threads:
			thread.join()

		# create data frame for star file
		columns=['rlnMicrographName', 'rlnCoordinateX', 'rlnCoordinateY', 'rlnCoordinateZ', 'rlnImageName', 'rlnCtfImage', 'rlnGroupNumber', 'rlnOpticsGroup', 'rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi', 'rlnAngleTiltPrior', 'rlnAnglePsiPrior', 'rlnOriginXAngst', 'rlnOriginYAngst', 'rlnOriginZAngst', 'rlnClassNumber', 'rlnNormCorrection']
		df = pd.DataFrame(data, columns=columns)
		extractStar = {"optics": pd.DataFrame(), "particles": df}
		# ATB: include the tomDate directory in the filename of the star file, January 27, 2024
		starfile.write(extractStar, direct + tomDate + '_' + tomogName + '.star', overwrite=True)
		#print('Extraction Complete')
		print('New Star File Created: ' + direct + tomDate + '_' + tomogName + '.star\n')
		self.ids.mainstar.text = direct + tomDate + '_' + tomogName + '.star'
		self.ids.mainsubtomo.text = direct
	
	# # check if mrc filter is active
	# def mrcWords(self):
	# 	if self.ids.mrcfilter.active == True:
	# 		self.ids.mainmrc.hint_text = 'Enter/Choose Mrc Directory'
	# 		self.ids.mainmrc.readonly = False
	# 		self.ids.mainmrc.cursor_blink = True
	# 		self.ids.mainmrc.foreground_color = (0,0,0,1)
	# 		self.ids.mainmrc.background_color = (1,1,1,.7)
	# 		self.ids.mainmrc.cursor_color = (0,0,0,1)
	# 		self.ids.mainmrc.selection_color = (0.1843, 0.6549, 0.8313, .5)
	# 	else:
	# 		self.ids.mainmrc.text = ''
	# 		self.ids.mainmrc.hint_text = ''
	# 		self.ids.mainmrc.readonly = True
	# 		self.ids.mainmrc.cursor_blink = False
	# 		self.ids.mainmrc.foreground_color = (0,0,0,0)
	# 		self.ids.mainmrc.background_color = (1,1,1,0)
	# 		self.ids.mainmrc.cursor_color = (0,0,0,0)
	# 		self.ids.mainmrc.selection_color = (0.1843, 0.6549, 0.8313, 0)

	# graph for wiener function
	plt.ion()

	# wiener and gaussian filtering
	def filter_vol(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			direct = self.ids.mainmrc.text
			if self.ids.mainmrc.text:
				direct = Path(self.ids.mainmrc.text) #formerly self.ids.mainmrc.text = self.addslash(self.ids.mainmrc.text) (sept_3_2025) 
			wienerbutton = self.ids.wienerbutton.active
			gaussianbutton = self.ids.gaussianbutton.active
			angpix = float(self.ids.A1.text)
			if wienerbutton: 
				defoc = float(self.ids.defoc.text)
				snrratio = float(self.ids.snrval.text)
				highpassnyquist = float(self.ids.highpass.text)
				voltage = float(self.ids.voltage.text)
				cs = float(self.ids.cs.text)
				envelope = float(self.ids.envelope.text)
				bfactor = float(self.ids.bfactor.text)
				phasebutton = self.ids.phaseflip.active
			if gaussianbutton:
				sigval = float(self.ids.sigma.text)
			starf = self.ids.mainstar.text
			subtomodir = self.ids.mainsubtomo.text
			mrcButton = self.ids.mrcfilter.active
			starButton = self.ids.starfilter.active

			# create wiener filter save file
			def saveTxt(file):
				file.writelines('PxSize:' + '\t' + self.ids.A1.text + '\n')
				file.writelines('Defocus:' + '\t' + self.ids.defoc.text + '\n')
				file.writelines('SnrFall:' + '\t' + self.ids.snrval.text + '\n')
				file.writelines('Highpass:' + '\t' + self.ids.highpass.text + '\n')
				file.writelines('Voltage:' + '\t' + self.ids.voltage.text + '\n')
				file.writelines('CS:' + '\t' + self.ids.cs.text + '\n')
				file.writelines('Envelope:' + '\t' + self.ids.envelope.text + '\n')
				file.writelines('BFactor:' + '\t' + self.ids.bfactor.text + '\n')

			# check if at least one option is selected
			if wienerbutton == False and gaussianbutton == False:
				print("At least one filter option needs to be selected.")
				return

			# check that at least one directory option is selected
			if mrcButton == False and starButton == False:
				print("At least one directory option needs to be selected.")
				return

			# wiener
			if wienerbutton == True:
				if starButton:
					imageFileNames = starfile.read(starf)["particles"]["rlnImageName"]
					def wienerLoop(i):
						fileName = imageFileNames[i]
						# create folder
						folderPath = "/".join(fileName.split("/")[:-1]) + "/"
						filterout = subtomodir + folderPath + 'filtered/'
						if os.path.isdir(filterout) == False:
							os.makedirs(filterout, exist_ok=True) 

						# make project text file
						save = filterout + 'wienerSave.txt'
						file_opt = open(save, 'w')
						file_opt.writelines('StarFileUnfilt:' + '\t' + self.ids.mainstar.text + '\n')
						saveTxt(file_opt)
						file_opt.close()
						
						print('Now filtering ' + fileName)
						fullFilePath = subtomodir + fileName

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFilePath)
						subtomo_filt = tom.deconv_tomo(mrc, angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
						subtomo_filt = subtomo_filt.astype('float32')

						# write filtered .mrc file
						baseFileName = fullFilePath.split("/")[-1].split(".")[0]
						newFileName = os.path.join(filterout, baseFileName + '_filt.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)
						# correct the pixel size (angstroms)
						with mrcfile.open(newFileName, 'r+') as mrc:
							mrc.voxel_size = angpix
					
					# thread in batches to optimize runtime
					threads = []
					batch_size = int(self.ids.CPU.text)
					fileLen = range(len(imageFileNames))
					batches = [fileLen[i:i+batch_size] for i in range(0, len(imageFileNames), batch_size)]
					for batch in batches:
						for i in batch:
							threads.append(Thread(target = wienerLoop, args = (i,)))
							threads[i].start()
						for i in batch:
							threads[i].join()
					for thread in threads:
						thread.join()

					# make wiener graph
					tom.wienergraph(angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)

					#constructs star file
					star_data = starfile.read(starf)
					df = pd.DataFrame.from_dict(star_data["particles"])

					def replaceName(s):
						s = s.split("/")
						s.insert(-1, 'filtered')
						s = '/'.join(s)
						return s
					
					def addWiener(s):
						s = s.split("/")
						s[-1] = s[-1].split(".")[0] + "_filt.mrc"
						s = '/'.join(s)
						return s
			
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: addWiener(x))
					star_data["particles"] = df
					starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star', overwrite=True)
					self.ids.mainstarfilt.text = subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star'
					print('Wiener Filtering by Star File Complete')
					print('New Star File Created: ' + subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star\n')

				elif mrcButton:
					# create folder
					filterout = direct / 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
					
					# create project text file
					save = direct / 'filtered/wienerSave.txt'
					file_opt = open(save, 'w')
					file_opt.writelines('MrcPath:' + '\t' + self.ids.mainmrc.text + '\n')
					saveTxt(file_opt)
					file_opt.close()
					
					# apply filter to all .mrc files in the folder
					myFiles = [f for f in os.listdir(direct) if f.endswith(".mrc")]
					def wienerMrcLoop(i):
						f = myFiles[i]
						fullFileName = os.path.join(direct, f)
						print('Now filtering ' + fullFileName)

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFileName)
						
						subtomo_filt = tom.deconv_tomo(mrc, angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
						subtomo_filt = subtomo_filt.astype('float32')

						# write filtered .mrc file
						baseFileName, extension = os.path.splitext(f)
						newFileName = os.path.join(filterout, baseFileName + '_wiener.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)
						# correct the pixel size (angstroms)
						with mrcfile.open(newFileName, 'r+') as mrc:
							mrc.voxel_size = angpix
					
					# thread in batches to optimize runtime
					threads = []
					batch_size = int(self.ids.CPU.text)
					fileLen = range(len(myFiles))
					batches = [fileLen[i:i+batch_size] for i in range(0, len(myFiles), batch_size)]
					for batch in batches:
						for i in batch:
							threads.append(Thread(target = wienerMrcLoop, args = (i,)))
							threads[i].start()
						for i in batch:
							threads[i].join()
					for thread in threads:
						thread.join()
					# make wiener graph
					tom.wienergraph(angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
					print('Wiener Filtering by Subtomogram Directory Complete\n')
				
				plt.show(block=False)

			# gaussian
			if gaussianbutton == True:
				from scipy.ndimage import gaussian_filter
				if starButton:
					if starf.endswith('.star') == False:
						print('Must use proper .star file')
						return
					imageFileNames = starfile.read(starf)["particles"]["rlnImageName"]
					def gaussianLoop(i):
						fileName = imageFileNames[i]
						# create folder
						folderPath = "/".join(fileName.split("/")[:-1]) + "/"
						filterout = subtomodir + folderPath + 'filtered/'
						if os.path.exists(filterout) == False:
							os.mkdir(filterout)
						
						#create project text file
						save = filterout + '/gaussianSave.txt'
						file_opt = open(save, 'w')
						file_opt.writelines('StarFileUnfilt:' + '\t' + self.ids.mainstar.text + '\n')
						file_opt.writelines('Sigma:' + '\t' + self.ids.sigma.text + '\n')
						file_opt.close()

						print('Now filtering ' + fileName)
						fullFilePath = subtomodir + fileName

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFilePath)
						subtomo_filt = gaussian_filter(mrc, sigma=sigval)

						# write filtered .mrc file
						baseFileName = fullFilePath.split("/")[-1].split(".")[0]
						newFileName = os.path.join(filterout, baseFileName + '_gauss.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)
						# correct the pixel size (angstroms)
						with mrcfile.open(newFileName, 'r+') as mrc:
							mrc.voxel_size = angpix

					# thread in batches to optimize runtime
					threads = []
					batch_size = int(self.ids.CPU.text)
					fileLen = range(len(imageFileNames))
					batches = [fileLen[i:i+batch_size] for i in range(0, len(imageFileNames), batch_size)]
					for batch in batches:
						for i in batch:
							threads.append(Thread(target = gaussianLoop, args = (i,)))
							threads[i].start()
						for i in batch:
							threads[i].join()
					for thread in threads:
						thread.join()

					#constructs star file
					star_data = starfile.read(starf)
					df = pd.DataFrame.from_dict(star_data["particles"])

					def replaceName(s):
						s = s.split("/")
						s.insert(-1, 'filtered')
						s = '/'.join(s)
						return s
					
					def addGaussian(s):
						s = s.split("/")
						s[-1] = s[-1].split(".")[0] + "_gauss.mrc"
						s = '/'.join(s)
						return s
			
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: addGaussian(x))
					star_data["particles"] = df
					starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star', overwrite=True)
					self.ids.mainstarfilt.text = subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star'
					print('Gaussian Filtering by Star File Complete')
					print('New Star File Created: ' + subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star\n')

				elif mrcButton:
					# create folder
					filterout = direct + 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
						
					# create project text file
					save = direct + 'filtered/gaussianSave.txt'
					file_opt = open(save, 'w')
					file_opt.writelines('MrcPath:' + '\t' + self.ids.mainmrc.text + '\n')
					file_opt.writelines('Sigma:' + '\t' + self.ids.sigma.text + '\n')
					file_opt.close()

					# apply filter to all .mrc files in the folder
					myFiles = [f for f in os.listdir(direct) if f.endswith(".mrc")]
					def gaussianMrcLoop(i):
						f = myFiles[i]
						fullFileName = os.path.join(direct, f)
						print('Now filtering ' + fullFileName)

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFileName)
						subtomo_filt = gaussian_filter(mrc, sigma=sigval)

						# write filtered .mrc file
						baseFileName, extension = os.path.splitext(f)
						newFileName = os.path.join(filterout, baseFileName + '_gauss.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)
						# correct the pixel size (angstroms)
						with mrcfile.open(newFileName, 'r+') as mrc:
							mrc.voxel_size = angpix
					
					# thread in batches to optimize runtime
					threads = []
					batch_size = int(self.ids.CPU.text)
					fileLen = range(len(myFiles))
					batches = [fileLen[i:i+batch_size] for i in range(0, len(myFiles), batch_size)]
					for batch in batches:
						for i in batch:
							threads.append(Thread(target = gaussianMrcLoop, args = (i,)))
							threads[i].start()
						for i in batch:
							threads[i].join()
					for thread in threads:
						thread.join()
					print('Gaussian Filtering by Subtomogram Directory Complete\n')

		except FileNotFoundError:
			print("This directory does not exist")

	# function to check if the index is within the bounds of the star file
	def check_index(self):
		status = 0
		if self.ids.pickcoordFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.index2.text = str(len(imageNames))
			if int(self.ids.index.text) > int(self.ids.index2.text):
				self.ids.index.text = self.ids.index2.text
				print("Index out of bounds")
				self.ids.pickcoordtext.text = 'Index out of bounds - try again'
				status = 1
				return status
			if int(self.ids.index.text) < 1:
				self.ids.index.text = '1'
				print("Index out of bounds")
				self.ids.pickcoordtext.text = 'Index out of bounds - try again'
				status = 1
				return status
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.pickcoordtext.text = 'Star file does not exist - try again'
			status = 1
			return status
		
	# coordinate picker
	def pick_coord(self):
		try:
			ind_check = self.check_index()
			if ind_check == 1:
				return
			# initialize variables
			ChimeraX_dir = self.ids.chimera_path.text
			if self.ids.pickcoordFiltered.active == True:
				listName = self.ids.mainstarfilt.text
			else:
				listName = self.ids.mainstar.text
			# subtomo directory (add slash to the end of the path)
			direct = self.addslash(self.ids.mainsubtomo.text)
			# cmm directory (add slash to the end of the path)
			cmm_direct = self.addslash(self.ids.maincmm.text)
			pxsz = float(self.ids.A1.text)
			curindex = int(self.ids.index.text)
			self.ids.pickcoordtext.text = 'Please wait. Opening ChimeraX.'
			# find the filename and tomogram name for the current index
			imageNames = starfile.read(listName)["particles"]["rlnImageName"]
			folderNames = starfile.read(listName)["particles"]["rlnMicrographName"]
			starfinal = imageNames[curindex - 1]
			tomoName = folderNames[curindex - 1]
			tomoName = tomoName.split('/')[0]
			# set total index value
			self.ids.index2.text = str(len(imageNames))
			# ensure that the user-specified cmm files directory exists
			if os.path.isdir(cmm_direct) == False:
				os.mkdir(cmm_direct)
			# create and run python script to open ChimeraX
			chim3 = cmm_direct + 'chimcoord.py'
			tmpflnam = direct + starfinal
			# invert subtomogram if active
			if self.ids.pickcoordInvert.active == True:
				mrc = mrcfile.read(tmpflnam)
				mrc = mrc * -1
				mrcfile.write(tmpflnam, mrc, overwrite=True)
			# run ChimeraX
			file_opt = open(chim3, 'w')
			file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + cmm_direct + "\")" + "\n" + "run(session, \"open " + tmpflnam + "\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
			file_opt.close()
			print(subprocess.getstatusoutput(ChimeraX_dir + '/chimerax ' + chim3))
			# revert subtomogram to original state if necessary
			if self.ids.pickcoordInvert.active == True:
				mrc = mrcfile.read(tmpflnam)
				mrc = mrc * -1
				mrcfile.write(tmpflnam, mrc, overwrite=True)
			# create .cmm file inside of respective tomogram directory
			cmmflip = starfinal.replace('.mrc', '.cmm')
			endfile = os.path.split(cmmflip)
			endcmm = endfile[1]
			self.ids.filenameget.text = starfinal
			if os.path.exists(cmm_direct + '/' + tomoName) == False:
				os.makedirs(cmm_direct + '/' + tomoName)
			if os.path.exists(cmm_direct + '/coord.cmm') == True:
				# check if cmm file will be overwritten
				if os.path.exists(cmm_direct + '/' + tomoName + '/' + endcmm) == True:
					statstat = 2
				else:
					statstat = 1
				shutil.move(cmm_direct + '/coord.cmm', (cmm_direct + '/' + tomoName + '/' + endcmm))
			# no coordinates saved
			else:
				statstat = 0
			# signify whether coordinates have been saved or not, or if they are saved but overwritten
			if statstat == 1:
				self.ids.pickcoordtext.text = 'Coords saved.'
			elif statstat == 2:
				self.ids.pickcoordtext.text = 'Coords saved — WARNING: file overwritten'
			else:
				self.ids.pickcoordtext.text = 'No coords selected.'

			# reset coordinate picker note and remove temporary chim3 file
			self.ids.notecoord.text = ""
			self.ids.notesave.text = ""
			os.remove(chim3)

		except FileNotFoundError:
			print("This directory does not exist")
			self.ids.pickcoordtext.text = 'Click above to begin.'

		return

	# next subtomogram
	def right_pick(self):
		ind_check = self.check_index()
		if ind_check == 1:
			return
		if self.ids.pickcoordFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.index2.text = str(len(imageNames))
		except FileNotFoundError:
			print("This star file does not exist")
			return
		self.ids.pickcoordtext.text = 'Press Pick Coordinates'
		# increase index by one
		if int(self.ids.index.text) == int(self.ids.index2.text):
			print('Outside of index bounds')
			self.ids.pickcoordtext.text = 'Index out of bounds - try again'
			return
		self.ids.index.text = str((int(self.ids.index.text) + 1))
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			self.ids.pickcoordtext.text = 'Star file does not exist - try again'
			return
		return
	
	# next subtomogram * 10
	def fastright_pick(self):
		ind_check = self.check_index()
		if ind_check == 1:
			return
		if self.ids.pickcoordFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.index2.text = str(len(imageNames))
		except FileNotFoundError:
			print("This star file does not exist")
			return
		self.ids.pickcoordtext.text = 'Press Pick Coordinates'
		# increase index by one
		if int(self.ids.index.text) >= int(self.ids.index2.text) - 10:
			self.ids.index.text = self.ids.index2.text
		else:
			self.ids.index.text = str((int(self.ids.index.text) + 10))
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			self.ids.pickcoordtext.text = 'Star file does not exist - try again'
			return
		return

	# previous subtomogram
	def left_pick(self):
		ind_check = self.check_index()
		if ind_check == 1:
			return
		try:
			if self.ids.pickcoordFiltered.active == True:
				starf = self.ids.mainstarfilt.text
			else:
				starf = self.ids.mainstar.text
			self.ids.pickcoordtext.text = 'Press Pick Coordinates'
			# decrease index by one
			if int(self.ids.index.text) == 1:
				print('Outside of index bounds')
				self.ids.pickcoordtext.text = 'Index out of bounds - try again'
				return
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) + 1))
			self.ids.pickcoordtext.text = 'Star file does not exist - try again'
		return
	
	# previous subtomogram * 10
	def fastleft_pick(self):
		ind_check = self.check_index()
		if ind_check == 1:
			return
		try:
			if self.ids.pickcoordFiltered.active == True:
				starf = self.ids.mainstarfilt.text
			else:
				starf = self.ids.mainstar.text
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.pickcoordtext.text = 'Press Pick Coordinates'
			# decrease index by one
			if int(self.ids.index.text) <= 10:
				self.ids.index.text = '1'
			else:
				self.ids.index.text = str((int(self.ids.index.text) - 10))
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.pickcoordtext.text = 'Star file does not exist - try again'
		return

	# add coord picker note
	def note(self):
		# create note
		if self.ids.pickcoordFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		direct = "/".join(starf.split("/")[:-1]) + '/'
		filename = self.ids.filenameget.text
		subtom = filename.split('/')[-2]
		file_path = "coordnote" + subtom + ".txt" 
		coordFile = open(direct + file_path, "a")

		coordFile.writelines(self.ids.index.text + ' ' + self.ids.filenameget.text + ': ' + self.ids.notecoord.text + '\n')
		coordFile.close()
		self.ids.notesave.text = 'Saved'
		print('Saved to ' + direct + file_path)
		return
#This IS THE SUB-EXTRACTION/RE-EXTRACTION PORTION
	# re-extraction from picked coordinates
	def reextraction(self):
		# initialize variables
		starf = self.ids.mainstarfilt.text
		direct = self.ids.mainsubtomo.text
		cmm_direct = self.ids.maincmm.text
		angpix = float(self.ids.A1.text)
		if self.ids.mainsubtomo.text[-1] != '/':
				direct = self.ids.mainstubomo.tex + '/'

		# set directory path
		directory = cmm_direct
		# check that the folder exists
		if os.path.exists(directory) == False:
			print(directory + ' does not exist. Please save coordinates first.')
			return
		
		# import the starfile as star_data
		star_data = starfile.read(starf)
		# create a pandas dataframe from the particles (removes header)
		df = pd.DataFrame.from_dict(star_data['particles'])
		# create a new panda dataframe that will hold the new shifted file
		newDF = {'data': pd.DataFrame([])}  # Use a dictionary to encapsulate newDF

		# function to get the first element of a series
		def get_first(series):
			if series.shape[0] > 0:
				return series.iloc[0]
			return None

		# function to add a comment to a cmm file
		def add_comment_to_cmm(input_path, output_path, boxsize, pixelsize):
			try:
				with open(input_path, 'r') as file:
					content = file.read().strip()
					if not content:
						raise ValueError("The file is empty.")
				
				# parse the XML file
				tree = ET.ElementTree(ET.fromstring(content))
				root = tree.getroot()

				# create a comment element
				box_comment = ET.Comment(boxsize)
				box_comment.tail = '\n'

				# create a second comment element
				px_comment = ET.Comment(pixelsize)
				px_comment.tail = '\n'

				# add the comment to the root
				root.insert(0, box_comment)
				root.insert(1, px_comment)

				# write the new XML file
				tree.write(output_path, encoding='utf-8')

			except ET.ParseError as e:
				print(f"Error parsing XML file {input_path}: {e}")
			except ValueError as e:
				print(f"Error reading file {input_path}: {e}")
		
		# global counter and lock
		global_counter = defaultdict(lambda: 1)
		counter_lock = Lock()

		# coords files timestamp
		current_time = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

		# iterate through each folder in directory
		for root, dirs, files in os.walk(directory, topdown=False):
			# create a function to parallelize the re-extraction
			def reextractLoop(i, newDF, global_counter, counter_lock):
				# iterate through each file in the folder
				filename = files[i]
				cmmfile = os.path.join(root, filename)
				# check if the file is a cmm file
				if os.path.isfile(cmmfile) and filename.endswith('.cmm'):
					# get the original micrographname, imagename, and coordinates
					opd = os.path.basename(os.path.normpath(root))
					opf = filename.replace('.cmm', '.mrc') 
					# micrograph name
					mgName = get_first(df[df['rlnImageName'].str.contains(opd) & df['rlnImageName'].str.contains(opf)]['rlnMicrographName'])
					# image name
					imgName = get_first(df[df['rlnImageName'].str.contains(opd) & df['rlnImageName'].str.contains(opf)]['rlnImageName'])
					# check if the original coordinates exist
					if mgName is None:
						print(f'Could not find original coordinates for subtomogram: {opf}')
						return
					else:
						# cycle through the dataframe to get the original coordinates
						print(f'Found {cmmfile}')
						opXYZ = np.array([
							int(float(df[df['rlnImageName'].str.contains(opd) & df['rlnImageName'].str.contains(opf)]['rlnCoordinateX'])), 
							int(float(df[df['rlnImageName'].str.contains(opd) & df['rlnImageName'].str.contains(opf)]['rlnCoordinateY'])), 
							int(float(df[df['rlnImageName'].str.contains(opd) & df['rlnImageName'].str.contains(opf)]['rlnCoordinateZ']))
						])
						######### FOR RELION4/5 INCLUDE THE OTHER COLUMNS AS WELL And we'll need a checkbox to togel RELION4/5 vs RELION 3 file creation ########### 
							# FLAG either 
								# just have [micro image xyz], 
								# set [all columns to 0 (with new xyz) while keeping all columns],
								# ***retain all the original star file info (except new xyz)***

						# get the cmm files together
						with open(cmmfile, 'r') as cmmfile:

							# parse the cmm file
							tree = ET.parse(cmmfile)
							cmroot = tree.getroot()

							# get boxsize from subtomogram 
							boxsize = []
							newbox = []
							# Get boxsize from master key [NEED TO MODIFY THIS TO ADD A TEXT BOX THAT ALLOWS THE EXTRACTION TO BE PERFORMED WITH A DEFINED BOXSIZE WITHIN THIS TAB, PREFILLED WITH MASTERKEY VALUE]
							newbox = float(self.ids.newboxsize.text)
							newbox = [newbox, newbox, newbox]
							## fix pixel size grabbing from header ##
							pixelsize = []
							with counter_lock:
								with mrcfile.open(direct + imgName, 'r+', permissive=True) as mrc:
									boxsize.append(float(mrc.header.nx))
									boxsize.append(float(mrc.header.ny))
									boxsize.append(float(mrc.header.nz))
									pixelsize.append(round(float(mrc.voxel_size.x), 2))
									pixelsize.append(round(float(mrc.voxel_size.y), 2))
									pixelsize.append(round(float(mrc.voxel_size.z), 2))

							# temporary fix for pixel size [CURRENTLY PIXELSIZE IS NOT CORRECTLY WRITEEN TO MRC JL 8/20/2024]
							pixelsize = [angpix, angpix, angpix]

							# grabbing box size from subextraction tab
							newbox = float(self.ids.newboxsize.text)
							newbox = [newbox, newbox, newbox]

							# CONFIRM IF BOX SIZE IS CORRECTLY GRABBED
							print(f"Box size: {boxsize}")
							print(f"Pixel size: {pixelsize}")
							print(f"New box size: {newbox}")

							# iterate through each set of coordinates in the cmm file
							for child in cmroot:

								# get the coordinates from the cmm file
								cms = np.array([
									int(float(child.attrib['x'])), 
									int(float(child.attrib['y'])), 
									int(float(child.attrib['z']))
								])

								# get the center of mass shift
								cms = (np.array(boxsize)/2 - cms) #/ pixelsize[0] 12_13_2024 JL

								# FOR DEBUGGING
								print(f'boxsize: {newbox[0]}')
								# calculate the new shift
								new_shift = [round(e) - int(cms[c]) for c,e in enumerate(opXYZ)]

								# convert to integers and calculate top left corner of box
								xpos = int(new_shift[0])
								ypos = int(new_shift[1])
								zpos = int(new_shift[2])
								x = newbox[0]/2 - xpos
								y = newbox[1]/2 - ypos
								z = newbox[2]/2 - zpos
								# calculate bounds
								bound = np.zeros(3)
								bound[0] = z + (boxsize[2] - newbox[2]) - 1
								bound[1] = y + (boxsize[1] - newbox[1]) - 1
								bound[2] = x + (boxsize[0] - newbox[0]) - 1
								# rounding
								bound = np.round(bound).astype(int)
								z = np.round(z).astype(int)
								y = np.round(y).astype(int)
								x = np.round(x).astype(int)

								# set the output subtomogram name using the original subtomogram name with the counter
								def get_incremented_filename(opf, prefix):
									with counter_lock:
										#Check if prefix exists in the global counter
										if prefix not in global_counter:
											global_counter[prefix] = 1
											print(f"Initialized counter for {prefix}")
										
										#increment the global counter
										current_count = global_counter[prefix]
										print(f"Current counter for prefix '{prefix}'")
										counter_str = str(current_count).zfill(6)
										global_counter[prefix] += 1
									
									# replace the last six digits while preserving preceding digits
									def replace_last_six_digits(match):
										preceding_digits = match.group(1)
										return preceding_digits + counter_str
									
									subtomo = re.sub(r'(\d{0,})(\d{6})(?!.*\d{6})', replace_last_six_digits, opf)
									return subtomo

								# extract the prefix of the filename (before the last 6 digits)
								# Changed 1/13/2025
								combined_prefix = os.path.join(opd, opf)
								prefix_match = re.match(r'(.+?)(\d{6})(?=\D*$)', combined_prefix)
								if prefix_match:
									prefix = prefix_match.group(1)
								else:
									prefix = opf  # Fallback in case the regex doesn't match

								# get the incremented filename
								subtomo = get_incremented_filename(opf, prefix)

								# # remove the '_filt' suffix if it exists
								# subtomo = subtomo.replace('_filt', '')

								# set the output file path
								output_file = os.path.join(root, subtomo)

								# check if overwrite is selected
								if self.ids.reextractOverwrite.active == False:
									# check if the file already exists
									if os.path.exists(output_file):
										print(f"[NO OVERWRITE]: Subtomogram {output_file} already exists — skipping re-extraction of {subtomo}")
										return
								else:
									# check if the file already exists
									if os.path.exists(output_file):
										print(f"[OVERWRITE]: Subtomogram {output_file} already exists — overwriting re-extraction of {subtomo}")

								# change the imagename so that the last portion is the new subtomo
								new_imgName = imgName.split('/')
								new_imgName[-1] = subtomo
								new_imgName = '/'.join(new_imgName)

								# create a new row for the subtomogram
								row = {
									'cmmfile': filename, 
									'rlnMicrographName': mgName, 
									'rlnImageName': imgName, 
									'newImageName': new_imgName,
									'rlnCoordinateX': new_shift[0], 
									'rlnCoordinateY': new_shift[1], 
									'rlnCoordinateZ': new_shift[2], 
									'Original_X': opXYZ[0], 
									'Original_Y': opXYZ[1], 
									'Original_Z': opXYZ[2], 
									'cmm_shiftX': cms[0], 
									'cmm_shiftY': cms[1], 
									'cmm_shiftZ': cms[2], 
								}

								# initialize bound status
								bound_status = 'unchecked'

								# check if 'star file only' is unchecked
								if self.ids.reextractStar.active == False:
									# get the tomogram name from star file
									tomogram = direct + row['rlnMicrographName']
									# check if the tomogram file exists
									with counter_lock:
										if os.path.exists(tomogram):
											# open and memory map the tomogram
											tomogram = mrcfile.mmap(tomogram)
											# ATB: calculate the size of 3D tomogram volume. Jan 24, 2024
											TomogramSize = np.array(tomogram.data).shape
										else:
											print(f"Tomogram {tomogram} was not found — skipping re-extraction of {subtomo}")
											return
									
									# check if subtomogram is within tomogram bounds
									if (z>=0 and y>=0 and x>=0 and bound[0] + 1 <= TomogramSize[0] and bound[1] + 1 <= TomogramSize[1] and bound[2] + 1 <=TomogramSize[2]):
										with counter_lock:
											# signal that the subtomogram is within bounds
											bound_status = 'valid'
											# cut the tomogram
											subby = tomogram.data[z:(bound[0] + 1), y:(bound[1] + 1), x:(bound[2] + 1)]
											# invert contrast if selected
											if self.ids.reextractInvert.active == True:
												subby = subby * -1
											# write the new subtomogram
											mrcfile.new(output_file, subby, overwrite=True)
											with mrcfile.open(output_file, 'r+', permissive=True) as mrc:
												mrc.voxel_size = pixelsize[0]
									else:
										# signal that the subtomogram is out of bounds
										bound_status = 'invalid'
										print(f'Extraction with specified box size exceeds tomogram borders. Not extracted: {subtomo} at center position {xpos[i]}, {ypos[i]}, {zpos[i]}')

								# get the subtomogram name
								subName = row['rlnMicrographName'].split('/')[-1].replace('.mrc','')

								# add the row to the new dataframe - based on the bound status
								with counter_lock:
									# add the row to the new dataframe if subtomogram is within bounds
									if bound_status == 'valid':
										# add the row to the new dataframe
										newDF['data'] = pd.concat([newDF['data'], pd.DataFrame([row])])
										# add the coordinates to the .coords file #Changed 1/22/2025
										with open(root + '/' + subName + '_' + current_time + '_.coords', 'a') as file_opt:
											file_opt.writelines(f'{xpos} {ypos} {zpos}\n')
										# print extracted coordinate position
										print(f'[VALID BOUNDS] Re-extracted subtomogram {output_file} at center position {xpos}, {ypos}, {zpos}')
									# do not add the row to the new dataframe if subtomogram is out of bounds
									elif bound_status == 'invalid':
										# print that the subtomogram is out of bounds
										print(f'[INVALID BOUNDS] Extraction with specified box size exceeds tomogram borders. Not extracted: {output_file} at center position {xpos}, {ypos}, {zpos}')
									# if bounds were not checked (e.g. star file only) then warn the user but still add the row to the new dataframe
									else:
										# add the row to the new dataframe
										newDF['data'] = pd.concat([newDF['data'], pd.DataFrame([row])])
										# add the coordinates to the .coords file
										with open(directory + '/' + subName + '_' + current_time + '_.coords', 'a') as file_opt:
											file_opt.writelines(f'{xpos} {ypos} {zpos}\n')
										# print a warning that the subtomogram bounds were not checked
										print(f'[UNCHECKED BOUNDS WARNING] Extraction bounds not checked for {output_file} at center position {xpos}, {ypos}, {zpos}')
							
							# add the boxsize to the cmm file as a comment (once per cmm file)
							boxsize_comment = f'boxsize: {boxsize}'
							pixelsize_comment = f'pixel_size: {pixelsize}'
							cmm_file_path = os.path.join(root, filename)
							# check if boxsize and pixelsize comments are already present, ignore call for add_comment_to_cmm if they are
							with open(cmm_file_path, 'r') as file:
								content = file.read()
								if 'boxsize' in content and 'pixel_size' in content:
									return
							add_comment_to_cmm(cmm_file_path, cmm_file_path, boxsize_comment, pixelsize_comment)
		
			# parallelization: thread in batches to optimize runtime
			threads = []
			batch_size = int(self.ids.CPU.text)
			fileLen = range(len(files))
			batches = [fileLen[i:i+batch_size] for i in range(0, len(files), batch_size)]
			for batch in batches:
				for i in batch:
					threads.append(Thread(target = reextractLoop, args = (i, newDF, global_counter, counter_lock)))
					threads[-1].start()
				for thread in threads:
					thread.join()
				threads.clear()
		
		# check if newDF is empty
		if newDF['data'].empty:
			print('\nNo coordinates were extracted. Exiting re-extraction.')
			return
		
		# group newDF by rlnImage name and then sort within that by rlnCoordinateX in ascending order
		newDF['data'] = newDF['data'].groupby('rlnImageName').apply(lambda x: x.sort_values('rlnCoordinateX', ascending=True)).reset_index(drop=True)
		
		# write the newDF to a csv
		newDF['data'].to_csv(direct + 'reextract_log_' + current_time + '.csv', index=False)

		# create a new empty dataframe
		starDF = pd.DataFrame([])
		# go through newDF and grab the imagename and x y z and compare to original star file and then make new rows from that where every other column is the same
		for row in newDF['data'].iterrows():
			# get the original row from the original star file
			orig_row = df[df['rlnImageName'] == row[1]['rlnImageName']]
			
			# create a new row with the original row and the new xyz coordinates
			new_row = orig_row.copy()
			new_row['rlnCoordinateX'] = row[1]['rlnCoordinateX']
			new_row['rlnCoordinateY'] = row[1]['rlnCoordinateY']
			new_row['rlnCoordinateZ'] = row[1]['rlnCoordinateZ']
			new_row['rlnImageName'] = row[1]['newImageName']

			# add a new column 'rlnOGSubtomo' at the end of the row and set it to the original subtomogram name
			new_row['rlnOGSubtomo'] = row[1]['rlnImageName']

			# add the new row to the new dataframe
			starDF = pd.concat([starDF, new_row])

		# reset index for the new dataframe
		starDF.reset_index(drop=True, inplace=True)

		# write the new dataframe to a star file
		star_data['particles'] = starDF
		# write the new star file
		starfile.write(star_data, direct + starf.split("/")[-1].split(".")[0] + '_reextracted_' + current_time + '.star', sep='\t', overwrite=True)
		
		# print that the re-extraction is complete
		print('\nRe-extraction complete')
		print('New Star File Created: ' + direct + starf.split("/")[-1].split(".")[0] + '_reextracted_' + current_time + '.star\n')
		return

	# create masks
	def mask(self):
		try:
			direct = self.ids.mainsubtomo.text
			box = int(self.ids.px1.text)
			angpix = float(self.ids.A1.text)
			rad = float(self.ids.radius.text)
			height = float(self.ids.height.text)
			vertshift = float(self.ids.vertical.text)
			maskmrc = self.ids.maskname.text
			masktype = self.ids.spinner.text

			if masktype == 'Sphere':
				sphere = tom.spheremask(np.ones([box, box, box], np.float32), rad, [box, box, box], 1, [round(box/2), round(box/2), round(box/2)])
				sphere = sphere.astype('float32')
				newMask = os.path.join(direct, maskmrc)
				print('Now writing ' + newMask)
				mrcfile.new(newMask, sphere)
				with mrcfile.open(newMask, 'r+') as mrc:
					mrc.voxel_size = angpix

			if masktype == 'Cylinder':
				curve = 9649
				cylinder = tom.cylindermask(np.ones([box, box, box], np.float32), rad, 1, [round(box/2), round(box/2)])
				sph_top = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift-round(height/2)-curve])-1) * -1
				sph_bot = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift+round(height/2)+curve])-1) * -1
				mask_final = cylinder * sph_top * sph_bot

				mask_final = mask_final.astype('float32')
				newMask = os.path.join(direct, maskmrc)
				print('Now writing ' + newMask)
				mrcfile.new(newMask, mask_final)
				with mrcfile.open(newMask, 'r+') as mrc:
					mrc.voxel_size = angpix
			self.ids.maskwarning.text = ''
		except ValueError:
			self.ids.maskwarning.text = 'Filename already exists'

		return

	#CSV file browser
	def browse_csv_for_masks(self):
		content = LoadDialog(load=self.load_csv_for_masks, cancel=self.dismiss_popup)
		#Filter to show only CSV files
		content.ids.filechooser.filters = ['*.csv']
		self._popup = Popup(title="Load CSV File for Mask Creation",
			content=content,
			size_hint=(0.9, 0.9))
		self._popup.open()
		
	# Create mask from CSV
	def load_csv_for_mask_creation(csv_path):
		df_maskCSV = pd.read_csv(csv_path)
		required_cols = ['filename', 'min_avg_gap_10_40_px', 'Tomo_dataset'] #Need to Tomo_dataset to CSV during generation, ex: 201810XX_MPI 
		additional_cols = [col for col in required_cols if col not in df_maskCSV.columns]
		
		if missing_cols:
			raise ValueError(f"CSV appears to me missing one of the required columns: {missing_cols}")
		
		print(f"Loaded {len(df)} particles from CSV")
		return df_maskCSV
		
	def create_cylinder_mask_fromCSV(self):
		try:
			#Get CSV path from GUI
			csv_path = self.ids.csv_mask_path.text.strip() #needs to be added as input to the gui
			
			if not csv_path:
				self.ids.maskwarning.text = 'Plase specify CSV path, if you did, check it again'
				return
			
			#load the CSV
			df_maskCSV = load_csv_for_mask_creation(csv_path)
			
			#Get parameters from the GUI
			direct = self.ids.mainsubtomo.text
			box = int(self.ids.px1.text)
			angpix = float(self.ids.A1.text)
			rad = float(self.ids.radius.text)
			vertshift = float(self.ids.vertical.text)
			maskmrc = self.ids.maskname.text
			masktype = self.ids.spinner.text
			
			#Temp warning only works for cylinder at the moment
			if masktype != 'Cylinder':
				self.ids.maskwarning.text = 'CSV mask creation currently only works with Cylinder type'
				return
			
			#Create output directory if it doesn't exist
			mask_output_dir = os.path.join(direct, 'csv_masks')
			os.makedirs(mask_output_dir, exist_ok=True)
			
			print(f"Creating {len(df_maskCSV)} cylinder masks in {mask_output_dir}")
			
			#Loop through each row in CSV and create a mask. 
			for idx, row in df_maskCSV.iterrows():
				filename = row['filename']
				height = float(row['min_avg_gap_10_40_px'])
				dataset = row['Tomo_dataset']
				
				#Create dataset-specific subdirectory
				dataset_mask_dir = os.path.join(mask_output_dir, tomo_dataset)
				os.makedirs(dataset_mask_dir, exist_ok=True)
				
				#Create cylinder mask using tom toolbox
				if masktype == 'Cylinder': #Redundant, but leave so in future can expand to sphere
					curve = 9649
					cylinder = tom.cylindermask(np.ones([box, box, box], np.float32), rad, 1, [round(box/2), round(box/2)])
					sph_top = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift-round(height/2)-curve])-1) * -1
					sph_bot = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift+round(height/2)+curve])-1) * -1
					mask_final = cylinder * sph_top * sph_bot

					mask_final = mask_final.astype('float32')
					
					#Create mask filename based on the particle name
					base_name = os.path.splittext(os.path.basename(filename))[0]
					mask_filename = f"{base_name}_mask.mrc"
					newMask = os.path.join(dataset_mask_dir, mask_filename)
					
					#Save mask
					print(f"Writing mask {idx+1}/{len(df_maskCSV)}: {tomo_dataset}/{mask_filename} (height={height:.2f})")
					mrcfile.new(newMask, mask_final) #could add overwrite here.
					with mrcfile.open(newMask, 'r+') as mrc:
						mrc.voxel_size = angpix
				
				print(f"All masks created in {mask_output_dir}")
				self.ids.maskwarning.text = f'Created {len(df_maskCSV)} masks successfully'
				
		except Exception as e:
			self.ids.maskwarning.text = f'Error: {str(e)}'
				
			return

	# 3d signal subtraction
	def subtraction(self):
		mask = self.ids.maskpath.text
		starf = self.ids.mainstar.text
		# add slash to the end of the save path
		direc = self.addslash(self.ids.mainsubtomo.text)
		pxsz = float(self.ids.A1.text)
		filter = self.ids.filterbackground.active
		grow = float(self.ids.blurrate.text)
		normalizeit = self.ids.normalized.active
		sdrange = float(self.ids.sdrange.text)
		sdshift = float(self.ids.sdshift.text)
		blackdust = self.ids.blackdust.active
		whitedust = self.ids.whitedust.active
		shiftfil = self.ids.shiftbysd.active
		randfilt = self.ids.randnoise.active
		permutebg = self.ids.permutebg.active
		
		def cut_part_and_movefunc(maskname, listName, direc, pxsz, filter, grow, normalizeit, sdrange, sdshift, blackdust, whitedust, shiftfil, randfilt, permutebg):
			offSetCenter = [0, 0 ,0]
			fileNames, angles, shifts, list_length, pickPos, new_star_name = tom.readList(listName, pxsz, 'masked', None)
			fileNames = [direc + name for name in fileNames]
			maskh1 = mrcfile.read(maskname)
			posNew = []
			aa = time.perf_counter()
			# begin to loop through each subtomogram
			def processLoop(i):
				boxsize = []
				# define boxsize
				with mrcfile.open(fileNames[i]) as mrc:
					boxsize.append(float(mrc.header.nx))
					boxsize.append(float(mrc.header.ny))
					boxsize.append(float(mrc.header.nz))
				mrcName = fileNames[i].split('/')[-1]
				mrcDirec = "/".join(fileNames[i].split('/')[:-1])
				reextractDir = mrcDirec + '/masked/'
				print("Now masking " + mrcName)
				a = time.perf_counter()
				outH1, posNew[:i] = tom.processParticle(fileNames[i], angles[:,i].conj().transpose(), shifts[:,i], maskh1, pickPos[:,i].conj().transpose(), offSetCenter, boxsize, filter, grow, normalizeit, sdrange, sdshift,blackdust,whitedust,shiftfil,randfilt,permutebg)
				if os.path.isdir(reextractDir) == False:
					os.makedirs(reextractDir, exist_ok=True)
				mrcfile.write(reextractDir + mrcName, outH1, True)
				with mrcfile.open(reextractDir + mrcName, 'r+') as mrc:
					mrc.voxel_size = pxsz
				b = time.perf_counter()
				t1 = str(timedelta(seconds = b-a)).split(":")
				if int(t1[1]) > 0:
					print(f"Masking complete for {mrcName} in {t1[1]} minutes and {t1[2]} seconds" )
				else:
					print(f"Masking complete for {mrcName} in {t1[2]} seconds" )
			# thread in batches to optimize runtime
			threads = []
			batch_size = int(self.ids.CPU.text)
			fileLen = range(len(fileNames))
			batches = [fileLen[i:i+batch_size] for i in range(0, len(fileNames), batch_size)]
			for batch in batches:
				for i in batch:
					threads.append(Thread(target = processLoop, args = (i,)))
					threads[i].start()
				for i in batch:
					threads[i].join()
			for thread in threads:
				thread.join()
			bb = time.perf_counter()
			t2 = str(timedelta(seconds = bb-aa)).split(":")
			print(f'Total masking time: {t2[1]} minutes and {t2[2]} seconds')
			print('New starfile created: ' + new_star_name + '\n')
			self.ids.mainstar.text = new_star_name

		cut_part_and_movefunc(mask, starf, direc, pxsz, filter, grow, normalizeit, sdrange, sdshift, blackdust, whitedust, shiftfil, randfilt, permutebg)
		return

	# filter subtomograms by CCC
	def filter_ccc(self):
		volume = self.ids.volvol.text
		star = self.ids.mainstar.text
		wedge = self.ids.mainwedge.text
		cccthresh = float(self.ids.cccthresh.text)
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		zoom = float(self.ids.zoomrange.text)
		tom.ccc_loop(star, volume, cccthresh, boxsize, zoom, wedge)
		return

	# subtomogram rotation function
	def rotate_subtomos(self, listName, dir, pxsz, boxsize, shifton, ownAngs):
		boxsize = [boxsize, boxsize, boxsize]
		fileNames, angles, shifts, list_length, pickPos, new_star_name = tom.readList(listName, pxsz, 'rottrans', ownAngs)
		fileNames = [dir + name for name in fileNames]
		# for i in range(len(fileNames)):
		def rotateLoop(i):
			mrcName = fileNames[i].split('/')[-1]
			mrcDirec = "/".join(fileNames[i].split('/')[:-1])
			rotDir = mrcDirec + '/rottrans/'
			print('Now rotating ' + mrcName)
			if len(ownAngs) != 3:
				# star file rotation
				outH1 = tom.processParticler(fileNames[i], angles[:,i].conj().transpose() * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			else:
				# manual rotation
				outH1 = tom.processParticler(fileNames[i], ownAngs * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			outH1 = outH1.astype(np.float32)
			if os.path.isdir(rotDir) == False:
				os.makedirs(rotDir, exist_ok=True)
			mrcfile.write(rotDir + mrcName, outH1, True)
			with mrcfile.open(rotDir + mrcName, 'r+') as mrc:
				mrc.voxel_size = pxsz
			# ATB: changed print statement: both rotations and shifts are applied
			print('Rotation/shift complete for ' + mrcName)
		# thread in batches to optimize runtime
		threads = []
		batch_size = int(self.ids.CPU.text)
		fileLen = range(len(fileNames))
		batches = [fileLen[i:i+batch_size] for i in range(0, len(fileNames), batch_size)]
		for batch in batches:
			for i in batch:
				threads.append(Thread(target = rotateLoop, args = (i,)))
				threads[i].start()
			for i in batch:
				threads[i].join()
		for thread in threads:
			thread.join()
		return new_star_name

	# rotate by star file
	def rotate(self):
		starf = self.ids.mainstar.text
		# add slash to the end of the path
		dir = self.addslash(self.ids.mainsubtomo.text)
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = self.ids.applyTranslations.active
		ownAngs = []

		new_star_name = self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)
		print('Rotation by Star File Complete')
		print('New Star File Created: ' + new_star_name)
		self.ids.mainstar.text = new_star_name
		print('Note: new star file now populates the main star file field in Master Key\n')
		
		return
	
	# rotate by manual angle/axis
	def manualrotate(self):
		self.ids.noaxis.text = " "
		starf = self.ids.mainstar.text
		# add slash to the end of the path
		dir = self.addslash(self.ids.mainsubtomo.text)
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = False
		xaxis = self.ids.xaxis.active
		yaxis = self.ids.yaxis.active
		zaxis = self.ids.zaxis.active
		# get angle of rotation
		try:
			anglerotate = float(self.ids.anglerotation.text)
		except ValueError:
			self.ids.noaxis.text = "Angle not specified"
			return

		# X-axis  corresponds to  phi=0     psi=0   theta=alpha
        # Y-axis  corresponds to  phi=270   psi=90  theta=alpha
        # Z-axis  corresponds to  phi=alpha psi=0   theta=0

		ownAngs = []
		if xaxis or yaxis or zaxis:
			ownAngs = [0,0,0]
			if xaxis == True:
				ownAngs[2] = anglerotate
			if yaxis == True:
				ownAngs[0] = 270
				ownAngs[1] = 90
				ownAngs[2] = anglerotate
			if zaxis == True:
				ownAngs[0] = anglerotate
			ownAngs = np.array(ownAngs)
		else:
			self.ids.noaxis.text = "Axis of rotation not specified"
			return
		
		new_star_name = self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)
		print('Manual Rotation Complete')
		print('New Star File Created: ' + new_star_name)
		self.ids.mainstar.text = new_star_name
		print('Note: new star file now populates the main star file field in Master Key\n')

	# used to store a subtomogram's accepted/rejected status
	indexToVal = {}

	# visualize subtomograms
	def visualize(self):
		# view current subtomogram
		if self.ids.visualizeFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		subtomodir = self.ids.mainsubtomo.text
		chimeraDir = self.ids.chimera_path.text
		index = int(self.ids.visind1.text)
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
		except FileNotFoundError:
			print('Star file not found')
			return
		self.ids.visind2.text = str(len(imageNames))
		name = imageNames[index - 1]
		self.ids.visualizestep.text = 'Currently on file ' + "/".join(name.split("/")[-3:])
		fileName = subtomodir + name
		# invert subtomogram if active
		if self.ids.visualizeInvert.active == True:
			mrc = mrcfile.read(fileName)
			mrc = mrc * -1
			mrcfile.write(fileName, mrc, overwrite=True)
		# run ChimeraX
		vis = subtomodir + 'visualize.py'
		file_opt = open(vis, 'w')
		file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + subtomodir + "\")" + "\n" + "run(session, \"open " + fileName + "\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
		file_opt.close()
		print(subprocess.getstatusoutput(chimeraDir + '/chimerax ' + vis))
		os.remove(vis)
		# revert subtomogram to original state if necessary
		if self.ids.visualizeInvert.active == True:
			mrc = mrcfile.read(fileName)
			mrc = mrc * -1
			mrcfile.write(fileName, mrc, overwrite=True)
		self.ids.visualizefeedback.text = 'Accept or Reject the Subtomogram'
		self.ids.visualizefeedback.color = (.6,0,0,1)
		return

	# next subtomogram
	def right_visualize(self):
		if self.ids.visualizeFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		# set index max
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.visind2.text = str(len(imageNames))
		except FileNotFoundError:
			print('Star file not found')
			return
		# check if index limit reached
		if int(self.ids.visind1.text) == int(self.ids.visind2.text):
			print('Outside of index bounds')
			return
		# increase index by one
		self.ids.visind1.text = str(int(self.ids.visind1.text) + 1)
		# set current filename
		name = imageNames[int(self.ids.visind1.text) - 1]
		self.ids.visualizestep.text = 'Currently on file ' + "/".join(name.split("/")[-3:])
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return

	# next subtomogram * 10
	def fastright_visualize(self):
		if self.ids.visualizeFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		# set index max
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.visind2.text = str(len(imageNames))
		except FileNotFoundError:
			print('Star file not found')
			return
		# check if index is too high
		if int(self.ids.visind1.text) >= int(self.ids.visind2.text) - 10:
			self.ids.visind1.text = self.ids.visind2.text
		# increase index by ten
		else:
			self.ids.visind1.text = str(int(self.ids.visind1.text) + 10)
		# set current filename
		name = imageNames[int(self.ids.visind1.text) - 1]
		self.ids.visualizestep.text = 'Currently on file ' + "/".join(name.split("/")[-3:])
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return

	# previous subtomogram
	def left_visualize(self):
		if self.ids.visualizeFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		# check if index limit reached
		if int(self.ids.visind1.text) == 1:
			print('Outside of index bounds')
			return
		# decrease index by one
		self.ids.visind1.text = str(int(self.ids.visind1.text) - 1)
		# set current filename
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			name = imageNames[int(self.ids.visind1.text) - 1]
			self.ids.visualizestep.text = 'Currently on file ' + "/".join(name.split("/")[-3:])
		except FileNotFoundError:
			print('Star file not found')
			self.ids.visind1.text = str(int(self.ids.visind1.text) + 1)
			return
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return
		
	# previous subtomogram * 10
	def fastleft_visualize(self):
		if self.ids.visualizeFiltered.active == True:
			starf = self.ids.mainstarfilt.text
		else:
			starf = self.ids.mainstar.text
		# check if index is too low
		if int(self.ids.visind1.text) <= 10:
			self.ids.visind1.text = '1'
		# decrease index by ten
		else:
			self.ids.visind1.text = str(int(self.ids.visind1.text) - 10)
		# set current filename
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			name = imageNames[int(self.ids.visind1.text) - 1]
			self.ids.visualizestep.text = 'Currently on file ' + "/".join(name.split("/")[-3:])
		except FileNotFoundError:
			print('Star file not found')
			self.ids.visind1.text = str(int(self.ids.visind1.text) + 1)
			return
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return

	# accept the current subtomogram
	def saveVisual(self):
		index = int(self.ids.visind1.text) - 1
		self.indexToVal[index + 1] = "accepted"

		# ATB
		starf = self.ids.mainstarfilt.text # filtered star file 
		starUnf = self.ids.mainstar.text # unfiltered star file
		subtomodir = self.ids.mainsubtomo.text

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# create empty _accepted.star (filtered) if does not exist 
			if not(os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")):
				starAF = starfile.read(starf)
				df = pd.DataFrame.from_dict(starAF["particles"])
				df = df.drop(df.index)
				starAF["particles"] = df
				starfile.write(starAF, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
		# create empty _accepted.star (unfiltered) if does not exist 
		if not(os.path.exists(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star")):
			starAU = starfile.read(starUnf)
			dfUnf = pd.DataFrame.from_dict(starAU["particles"])
			dfUnf = dfUnf.drop(dfUnf.index)
			starAU["particles"] = dfUnf
			starfile.write(starAU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star")

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# isolate current index image name and row (filtered)
			row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
			starAF = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
			df = pd.DataFrame.from_dict(starAF["particles"]).dropna(how="all")
			nameF = row["rlnImageName"].values[0]
		# isolate current index image name and row (unfiltered)
		rowUnf = pd.DataFrame.from_dict(starfile.read(starUnf)["particles"]).iloc[[index]]
		starAU = starfile.read(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star")
		dfUnf = pd.DataFrame.from_dict(starAU["particles"]).dropna(how="all")
		nameUnf = rowUnf["rlnImageName"].values[0]

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# add row to accepted folder and add row to _accepted.star (filtered)
			if df[df["rlnImageName"] == nameF].shape[0] == 0:
				df = pd.concat([df, row])
				starAF["particles"] = df
				starfile.write(starAF, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)
		# add row to _accepted.star (unfiltered)
		if dfUnf[dfUnf["rlnImageName"] == nameUnf].shape[0] == 0:
			dfUnf = pd.concat([dfUnf, rowUnf])
			starAU["particles"] = dfUnf
			starfile.write(starAU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# remove .mrc files from _rejected.star (filtered)
			starRF_path = subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star"
			if os.path.exists(starRF_path):
				row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
				starRF = starfile.read(starRF_path)
				df = pd.DataFrame.from_dict(starRF["particles"]).dropna(how="all")
				nameF = row["rlnImageName"].values[0]
				df = df[df["rlnImageName"] != nameF]
				starRF["particles"] = df
				starfile.write(starRF, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)
		# remove .mrc files from _rejected.star (unfiltered)
		starRU_path = subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star"
		if os.path.exists(starRU_path):
			rowUnf = pd.DataFrame.from_dict(starfile.read(starUnf)["particles"]).iloc[[index]]
			starRU = starfile.read(starRU_path)
			dfUnf = pd.DataFrame.from_dict(starRU["particles"]).dropna(how="all")
			nameUnf = rowUnf["rlnImageName"].values[0]
			dfUnf = dfUnf[dfUnf["rlnImageName"] != nameUnf]
			starRU["particles"] = dfUnf
			starfile.write(starRU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)
		self.ids.visualizefeedback.text = 'Subtomogram Accepted'
		self.ids.visualizefeedback.color = (0,.3,0,1)

	# reject the current subtomogram
	def noSaveVisual(self):
		index = int(self.ids.visind1.text) - 1
		self.indexToVal[index + 1] = "rejected"
		starf = self.ids.mainstarfilt.text
		starUnf = self.ids.mainstar.text
		subtomodir = self.ids.mainsubtomo.text
	
		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# create _rejected.star (filtered) if it does not exist 
			if not(os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")):
				starRF = starfile.read(starf)
				df = pd.DataFrame.from_dict(starRF["particles"])
				df = df.drop(df.index)
				starRF["particles"] = df
				starfile.write(starRF, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")
		# create _rejected.star (unfiltered) if it does not exist 
		if not(os.path.exists(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star")):
			starRU = starfile.read(starUnf)
			dfUnf = pd.DataFrame.from_dict(starRU["particles"])
			dfUnf = dfUnf.drop(dfUnf.index)
			starRU["particles"] = dfUnf 
			starfile.write(starRU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star")

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# isolate current index image name and row (filtered)
			row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
			starRF = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")
			df = pd.DataFrame.from_dict(starRF["particles"]).dropna(how="all")
			nameF = row["rlnImageName"].values[0]
		# isolate current index image name and row (unfiltered)
		rowUnf = pd.DataFrame.from_dict(starfile.read(starUnf)["particles"]).iloc[[index]]
		starRU = starfile.read(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star")
		dfUnf = pd.DataFrame.from_dict(starRU["particles"]).dropna(how="all")
		nameUnf = rowUnf["rlnImageName"].values[0]

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# add mrc file path to _rejected.star (filtered)
			if df[df["rlnImageName"] == nameF].shape[0] == 0: # if file not in _rejected.star
				df = pd.concat([df, row])
				starRF["particles"] = df
				starfile.write(starRF, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)
		# add mrc file path to _rejected.star (unfiltered)
		if dfUnf[dfUnf["rlnImageName"] == nameUnf].shape[0] == 0: # if file not in _rejected.star
			dfUnf = pd.concat([dfUnf, rowUnf])
			starRU["particles"] = dfUnf
			starfile.write(starRU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)

		# ATB. Check if filtered flag is set. Jan 21 2024
		if self.ids.visualizeFiltered.active == True:
			# check if _accepted.star (filtered) exists and remove row
			if os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star"):
				starAF = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
				df = pd.DataFrame.from_dict(starAF["particles"]).dropna(how="all")
				if df[df["rlnImageName"] == nameF].shape[0] == 1:
					df = df[df["rlnImageName"] != nameF]
					starAF["particles"] = df
					starfile.write(starAF, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)
		# check if _accepted.star (unfiltered) exists and remove row
		if os.path.exists(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star"):
			starAU = starfile.read(subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star")
			dfUnf = pd.DataFrame.from_dict(starAU['particles']).dropna(how="all")
			if dfUnf[dfUnf["rlnImageName"] == nameUnf].shape[0] == 1:
				dfUnf = dfUnf[dfUnf["rlnImageName"] != nameUnf]
				starAU["particles"] = dfUnf
				starfile.write(starAU, subtomodir + starUnf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)
		self.ids.visualizefeedback.text = 'Subtomogram Rejected'
		self.ids.visualizefeedback.color = (0,.3,0,1)

	# plot back into tomogram
	def plotBack(self):
		subtomoDirect = self.ids.mainsubtomo.text
		starf = self.ids.mainstar.text
		# add slash to the end of the reference path
		classPath = self.addslash(self.ids.refPath.text)
		classBasename = self.ids.refBasename.text
		angpix = float(self.ids.A1.text)
		bxsz = float(self.ids.px1.text)
		boxsize = [bxsz, bxsz, bxsz]

		# get the models in the class that match basename
		folder = os.listdir(classPath)
		classes = [file for file in folder if classBasename in file]

		# read starfile as dataframe
		star_data = starfile.read(starf)["particles"]

		# parallelized loop — iterate through each row of dataframe
		def plotBackLoop(i):
			# get row data from star file for the subtomogram
			row = star_data.iloc[i]
			imgName = row.rlnImageName
            
			# get class number for the subtomogram and pad with zeros to left so that it is 3 digits
			classNum = str(row.rlnClassNumber).zfill(3)

			# testing for patrick:
			# classNum = str(random.randint(1, 3)).zfill(3)

			# get model associated with class num 
			model = classPath + [file for file in classes if classNum in file][0]
			# print(model)
			# create arrays for coords, angles, and shifts
			coords = np.array([int(row.rlnCoordinateX), int(row.rlnCoordinateY), int(row.rlnCoordinateZ)])
			angles = np.array([float(row.rlnAngleRot), float(row.rlnAngleTilt), float(row.rlnAnglePsi)])
			# ATB: divide shifts by pixel sizes to get pixel positions (similar to what is done in readList) since it calls the tom.shift() function which operates in pixel space
			shifts = np.array([float(row.rlnOriginXAngst) / angpix, float(row.rlnOriginYAngst) / angpix, float(row.rlnOriginZAngst) / angpix])

			# ATB: call eulerconvert_xmipp (similar to using tom.readList which is used in both the Rotate and Masking tasks),
			# but here we do not use readList to read the star file lines.

			# ATB: eulerconvert_xmipp converts Relion Euler rot, tilt, psi angles to the TOM Euler angle convention phi, psi, theta. 
			# TOM Euler angles are stored in the angles array in the order (phi,psi,theta) rather than the more customary
			# (phi,theta,psi). So to invert the TOM Euler angles, (-psi,-phi,-theta) should be used.
						
			euler_angles = tom.eulerconvert_xmipp(angles[0], angles[1], angles[2])
			angles = euler_angles

			# ATB: removed original code:
			# angs = np.flip(angles.conj().transpose())
			# transformed = tom.processParticler(model, angs, boxsize, shifts.conj().transpose() * -1, shifton=False)
            
			# ATB: this swaps values in tmpAng indexes 0 and 1 since they are swapped again processParticle
			# since angles are not negated, this effectively means that we apply the inverted rotation matrix to the model (similar to what is 
			# done when rotating masks which uses processParticle, not processPartiler)
			storey = angles[1]
			angles[1] = angles[0]
			angles[0] = storey

			# ATB: note that we do not negate angles and shifts here (unlike in the Rotate task)!

			# transform corresponding model by inversed angles and shifts specified in starfile
			transformed = tom.processParticler(model, angles, boxsize, shifts.conj().transpose(), shifton=True)

			# X-axis  corresponds to  phi=0     psi=0   theta=alpha
        	# Y-axis  corresponds to  phi=270   psi=90  theta=alpha
        	# Z-axis  corresponds to  phi=alpha psi=0   theta=0

			# create "plotback" folder
			folderPath = subtomoDirect + "/" + '/'.join(imgName.split('/')[:-1]) + "/plotback/"
			if not os.path.exists(folderPath):
				os.makedirs(folderPath)
			# create new mrcfile
			transformed = transformed.astype(np.float32)
			mrcName = imgName.split('/')[-1]
			mrcfile.new(folderPath + mrcName, transformed, overwrite=True)
			# shift model to coords specified in star file
			with mrcfile.open(folderPath + mrcName, 'r+') as mrc:
				mrc.voxel_size = angpix
				# ATB: changed from nxstart, nystart, nzstart to origin.x, origin.y, origin.z since that works more reliably in Chimera.
				# ATB: removed box size shift, Feb. 13, 2024
				mrc.header.origin.x = (coords[0]) * angpix
				mrc.header.origin.y = (coords[1]) * angpix
				mrc.header.origin.z = (coords[2]) * angpix

			# print that plot-back is complete for this subtomogram
			print(f'Plot-back rotation/shift complete for {mrcName}')
            
		# parallelization: thread in batches to optimize runtime
		threads = []
		batch_size = int(self.ids.CPU.text)
		fileLen = range(len(star_data))
		batches = [fileLen[i:i+batch_size] for i in range(0, len(star_data), batch_size)]
		for batch in batches:
			for i in batch:
				threads.append(Thread(target = plotBackLoop, args = (i,)))
				threads[i].start()
			for i in batch:
				threads[i].join()
		for thread in threads:
			thread.join()
		threads.clear()

		# print that plot-back is complete
		print('Plot-back complete')

		return
	
	def subPlotBack(self):
		# get the necessary variables from the GUI
		subtomoDirect = self.ids.mainsubtomo.text
		starf = self.ids.mainstarfilt.text
		newSubtomo = self.ids.newSubtomoName.text
		csvFile = self.ids.subCsvFile.text
		chimeraDir = self.ids.chimera_path.text
		# add slash to the end of the reference path
		classPath = self.addslash(self.ids.subRefPath.text)
		classBasename = self.ids.subRefBasename.text

		# get the models in the class that match basename
		folder = os.listdir(classPath)
		classes = [file for file in folder if classBasename in file]

		# read starfile as dataframe
		star_data = starfile.read(starf)["particles"]

		# read the csv file
		csv = pd.read_csv(csvFile)
		# extract the row that contains the newSubtomo name under the newImageName column
		row = csv.loc[csv['newImageName'] == newSubtomo]

		# get the rlnImageName from the row
		oldImgName = row['rlnImageName'].values[0]
		# get the new subtomo name from the row
		newImgName = row['newImageName'].values[0]

		# create a new folder for the plot back in the folder that the newImgName file exists
		plotbackFolder = subtomoDirect + '/'.join(newImgName.split('/')[:-1]) + "/plotback/"
		if not os.path.exists(plotbackFolder):
			os.makedirs(plotbackFolder)

		# put together the file names
		oldImgFile = subtomoDirect + oldImgName
		newImgFile = plotbackFolder + newImgName.split('/')[-1]

		# get the boxsize and pixelsize of the old subtomogram
		boxsize = []
		angpix = []
		with mrcfile.open(oldImgFile, 'r+', permissive=True) as mrc:
			boxsize.append(float(mrc.header.nx))
			boxsize.append(float(mrc.header.ny))
			boxsize.append(float(mrc.header.nz))
			angpix.append(round(float(mrc.voxel_size.x), 2))
			angpix.append(round(float(mrc.voxel_size.y), 2))
			angpix.append(round(float(mrc.voxel_size.z), 2))
		
		# ensure that a boxsize and pixel size were found
		if len(boxsize) == 0:
			bxsz = self.ids.px1.text
			boxsize = [bxsz, bxsz, bxsz]
		
		if len(angpix) == 0:
			pxsz = self.ids.A1.text
			angpix = [pxsz, pxsz, pxsz]

		angpix = angpix[0]

		# pull the class number from the star file for the row with the old image name
		oldRow = star_data.loc[star_data['rlnImageName'] == oldImgName]
		classNum = str(oldRow['rlnClassNumber'].values[0]).zfill(3)

		# for patrick testing: classNum = '001'

		# get model associated with class num
		model = classPath + [file for file in classes if classNum in file][0]
		# check that model exists
		if not os.path.exists(model):
			print('Model does not exist - check the class path and basename')
			return

		# create arrays for angles and coordinates
		angles = np.array([float(oldRow['rlnAngleRot']), float(oldRow['rlnAngleTilt']), float(oldRow['rlnAnglePsi'])])
		og_coords = np.array([float(row['Original_x']) / angpix, float(row['Original_Y']) / angpix, float(row['Original_Z']) / angpix])
		new_coords = np.array([float(row['rlnCoordinateX']) / angpix, float(row['rlnCoordinateY']) / angpix, float(row['rlnCoordinateZ']) / angpix])

		# converts Relion Euler rot, tilt, psi angles to the TOM Euler angle convention phi, psi, theta
		euler_angles = tom.eulerconvert_xmipp(angles[0], angles[1], angles[2])
		angles = euler_angles

		# swap values in tmpAng indexes 0 and 1 since they are swapped again processParticler
		storey = angles[1]
		angles[1] = angles[0]
		angles[0] = storey

		# transform corresponding model by inversed angles specified in starfile
		transformed_model = tom.processParticler(model, angles, boxsize, new_coords, shifton=False)
		transformed_model = transformed_model.astype(np.float32)
		
		# write the new subtomogram
		transformed_subtomo = mrcfile.read(oldImgFile)
		mrcfile.new(newImgFile, transformed_subtomo, overwrite=True)
		with mrcfile.open(newImgFile, 'r+', permissive=True) as mrc:
			mrc.voxel_size = angpix
			mrc.header.origin.x = new_coords[0]
			mrc.header.origin.y = new_coords[1]
			mrc.header.origin.z = new_coords[2]
		
		# create new mrcfile for the transformed model
		newModel = subtomoDirect + 'transformed_model.mrc'
		mrcfile.new(newModel, transformed_model, overwrite=True)
		# shift model to boxsize specified in mrc file
		with mrcfile.open(newModel, 'r+', permissive=True) as mrc:
			mrc.voxel_size = angpix
			mrc.header.origin.x = new_coords[0]
			mrc.header.origin.y = new_coords[1]
			mrc.header.origin.z = new_coords[2]

		# alter the original subtomogram
		with mrcfile.open(oldImgFile, 'r+', permissive=True) as mrc:
			mrc.voxel_size = angpix
			mrc.header.origin.x = og_coords[0]
			mrc.header.origin.y = og_coords[1]
			mrc.header.origin.z = og_coords[2]

		# run ChimeraX to visualize the transformed model and subtomogram, as well as the original subtomogram
		vis = subtomoDirect + 'visualize.py'
		file_opt = open(vis, 'w')
		file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"open " + newImgFile + "\")" + "\n" + "run(session, \"open " + newModel + "\")" + "\n" + "run(session, \"open " + oldImgFile + "\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
		file_opt.close()
		print(subprocess.getstatusoutput(chimeraDir + '/chimerax ' + vis))
		os.remove(vis)

		# print that plot-back is complete
		print('Subtomogram Plot-back complete')

		return

	pass

#run CrESTA
Cresta().run()