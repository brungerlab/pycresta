
#kivy needed for app
import kivy
kivy.require('2.1.0')

#python packages
import os, subprocess
from threading import Thread
import re
import shutil
import time
import pandas as pd
import numpy as np
import starfile
import mrcfile
import matplotlib.pyplot as plt
import weakref
from datetime import timedelta
import random
import mrcfile
import starfile

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
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
Window.size = (900,800)

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
    
class Tabs(TabbedPanel):
	
	label = Label(text="Sigma")
	label2 = Label(text=" ", size_hint_y=.8)
	sigma = TextInput(text="5", multiline=False, size_hint_x=.12, size_hint_y=1.9, pos_hint={'center_x': .5, 'center_y': .5})

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
		starfpath = filename
		if len(starfpath) != 0:
			if starfpath.endswith('.star') == False:
				self.ids.mainstar.text = 'Not a ".star" file — Choose Unfiltered Star File Path'
			else:
				self.ids.mainstar.text = starfpath
				self.ids.mainsubtomo.text = "/".join(self.ids.mainstar.text.split("/")[:-1]) + '/'
				starfilted = starfpath.replace('.star', '_filtered.star')
				if os.path.isfile(starfilted) == True:
					self.ids.mainstarfilt.text = starfilted
				else:
					self.ids.mainstarfilt.text = 'Choose Filtered Star File Path'
		elif len(starfpath) == 0:
			self.ids.mainstar.text = 'Choose Unfiltered Star File Path'
		self.dismiss_popup()

	# star file filtered save
	def show_starfilt(self):
		content = StarFiltFinder(stardfiltsave=self.starfiltsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Filtered Star File", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def starfiltsave(self, path, filename):
		starfiltpath = filename
		if len(starfiltpath) != 0:
			if starfiltpath.endswith('.star') == False:
				self.ids.mainstarfilt.text = 'Not a ".star" file — Choose Unfiltered Star File Path'
			else:
				self.ids.mainstarfilt.text = starfiltpath
				self.ids.mainsubtomo.text = "/".join(self.ids.mainstarfilt.text.split("/")[:-1]) + '/'
		elif len(starfiltpath) == 0:
			self.ids.mainstarfilt.text = 'Choose Filtered Star File Path'
		self.dismiss_popup()

	# subtomogram directory save
	def show_subtomo(self):
		content = SubtomoFinder(subtomodsave=self.subtomosave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Subtomogram Directory", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def subtomosave(self, path, filename):
		subtomopath = path
		if len(subtomopath) != 0:
			self.ids.mainsubtomo.text = subtomopath + '/'
		elif len(subtomopath) == 0:
			self.ids.mainsubtomo.text = 'Choose Subtomogram Directory'
		self.dismiss_popup()

	# mrc directory save
	def show_mrc(self):
		content = MrcFinder(mrcdsave=self.mrcsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Mrc Directory", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def mrcsave(self, path, filename):
		mrcpath = path
		if len(mrcpath) != 0:
			self.ids.mainmrc.text = mrcpath + '/'
		elif len(mrcpath) == 0:
			self.ids.mainmrc.text = 'Choose Mrc Directory'
		self.dismiss_popup()

	# tomogram path save
	def show_tomo(self):
		content = TomoFinder(tomodsave=self.tomosave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Tomogram Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def tomosave(self, path, filename):
		tomopath = filename
		if len(tomopath) != 0:
			if tomopath.endswith('.mrc') == False:
				self.ids.tomo.text = 'Not a ".mrc" file — Choose Tomogram Path'
			else:
				self.ids.tomo.text = tomopath
		elif len(tomopath) == 0:
			self.ids.tomo.text = 'Choose Tomogram Path'
		self.dismiss_popup()

	# tomogram coords path save
	def show_tomocoords(self):
		content = TomoCoordsFinder(tomocoordsdsave=self.tomocoordssave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Tomogram Coords Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def tomocoordssave(self, path, filename):
		tomocoordspath = filename
		if len(tomocoordspath) != 0:
			self.ids.tomocoords.text = tomocoordspath
		elif len(tomocoordspath) == 0:
			self.ids.tomocoords.text = 'Choose Coords Path'
		self.dismiss_popup()

	# start vector path save
	def show_startvec(self):
		content = StartVecFinder(startvecdsave=self.startvecsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Start Vector Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def startvecsave(self, path, filename):
		startvecpath = filename
		if len(startvecpath) != 0:
			self.ids.vectorStart.text = startvecpath
		elif len(startvecpath) == 0:
			self.ids.vectorStart.text = 'Choose Vector Start Path'
		self.dismiss_popup()

	# end vector path save
	def show_endvec(self):
		content = EndVecFinder(endvecdsave=self.endvecsave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save End Vector Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def endvecsave(self, path, filename):
		endvecpath = filename
		if len(endvecpath) != 0:
			self.ids.vectorEnd.text = endvecpath
		elif len(endvecpath) == 0:
			self.ids.vectorEnd.text = 'Choose Vector End Path'
		self.dismiss_popup()

	# mask path save
	def show_mask(self):
		content = MaskFinder(maskdsave=self.masksave, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save Mask Path", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def masksave(self, path, filename):
		maskpath = filename
		if len(maskpath) != 0:
			if maskpath.endswith('.mrc') == False:
				self.ids.maskpath.text = 'Not a ".mrc" file — Choose Mask Path'
			else:
				self.ids.maskpath.text = maskpath
		elif len(maskpath) == 0:
			self.ids.maskpath.text = 'Choose Mask Path'
		self.dismiss_popup()

	# save project info
	def savedata(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			if self.ids.save.text[-1] != '/':
				self.ids.save.text = self.ids.save.text + '/'
			# create text file with saved project data and text inputs
			save = self.ids.save.text + self.ids.savename.text + '.txt'
			file_opt = open(save, 'w')
			file_opt.writelines('Project ' + self.ids.savename.text + '\n')
			file_opt.writelines('StarFileUnfilt:' + '\t' + self.ids.mainstar.text + '\n')
			file_opt.writelines('StarFileFilt:' + '\t' + self.ids.mainstarfilt.text + '\n')
			file_opt.writelines('SubtomoPath:' + '\t' + self.ids.mainsubtomo.text + '\n')
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
			file_opt.writelines('CCCVolone:' + '\t' + self.ids.cccvolone.text + '\n')
			file_opt.writelines('CCCVoltwo:' + '\t' + self.ids.cccvoltwo.text + '\n')
			file_opt.writelines('CCCWedge:' + '\t' + self.ids.cccwedge.text + '\n')
			file_opt.writelines('Volvol:' + '\t' + self.ids.volvol.text + '\n')
			file_opt.writelines('Volwedge:' + '\t' + self.ids.volwedge.text + '\n')
			file_opt.writelines('RefPath:' + '\t' + self.ids.refPath.text + '\n')
			file_opt.writelines('RefBasename:' + '\t' + self.ids.refBasename.text + '\n')
			file_opt.close()
			self.ids.pullpath.text = save
		except IndexError:
			print('Enter a project directory and name')

	# load existing project information
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
						yank = pinfo[1]
					except IndexError:
						yank = ''
					if re.search('StarFileUnfilt', line):
						self.ids.mainstar.text = yank
					if re.search('StarFileFilt', line):
						self.ids.mainstarfilt.text = yank
					if re.search('SubtomoPath', line):
						self.ids.mainsubtomo.text = yank
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
					if re.search('CCCVolone', line):
						self.ids.cccvolone.text = yank
					if re.search('CCCVoltwo', line):
						self.ids.cccvoltwo.text = yank
					if re.search('CCCWedge', line):
						self.ids.cccwedge.text = yank
					if re.search('Volvol', line):
						self.ids.volvol.text = yank
					if re.search('Volwedge', line):
						self.ids.volwedge.text = yank
					if re.search('RefPath', line):
						self.ids.refPath.text = yank
					if re.search('RefBasename', line):
						self.ids.refBasename.text = yank
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
	
	# tomogram extraction
	def extract(self):
		tomogram = self.ids.tomo.text
		coordfile = self.ids.tomocoords.text
		# tomogram path
		direct = '/'.join(tomogram.split('/')[:-3]) + '/'
		# tomogram date and name
		tomDate = tomogram.split('/')[-3]
		tomName = tomogram.split('/')[-2]
		tomogName = tomogram.split('/')[-1].replace('.mrc', '')
		# use for star file micrographName and imageName
		micrograph = tomDate + '/' + tomName + '/' + tomogram.split('/')[-1]
		subdirect = tomDate + '/' + tomName + '/Sub/'
		# use for full path containing subtomograms
		directory = direct + subdirect
		# memory map the tomogram
		tomogram = mrcfile.mmap(tomogram)
		boxsize = float(self.ids.px1.text)
		angpix = float(self.ids.A1.text)
		if os.path.isdir(directory) == False:
			os.makedirs(directory)
		with open(coordfile, 'r') as coord:
			coord = coord.readlines()
			# create an empty data list for the rows
			data = []
			def extractLoop(i):
				# create subtomogram file name
				number = '000000' + str(i)
				number = number[-6:]
				name = directory + tomogName + number + '.mrc'
				# create imageName for star file
				starName = subdirect + tomogName + number + '.mrc'
				# access coordinates from coords file
				line = coord[i]
				pos = line.split(' ')[1:]
				# convert coordinates to integers
				x = int(pos[0])
				y = int(pos[1])
				z = int(pos[2].strip())
				# create and append star file rows for subtomogram
				row = [micrograph, x, y, z, starName, 'wedgefx2.mrc', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				data.append(row)
				# shift coordinates to top left corner of the boxsize for extraction
				x = x - boxsize/2
				y = y - boxsize/2
				z = z - boxsize/2
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
				# cut the tomogram
				out = tomogram.data[z:(bound[0]+1), y:(bound[1]+1), x:(bound[2]+1)]
				# invert subtomograms if selected
				if self.ids.extractInvert.active == True:
					out = out * -1
				# create subtomogram
				mrcfile.new(name, out, overwrite=True)
				print('Extracted ' + name)
				# change pixel size
				with mrcfile.open(name, 'r+') as mrc:
					mrc.voxel_size = angpix

			# thread in batches to optimize runtime
			threads = []
			batch_size = int(self.ids.CPU.text)
			lenCoord = len(coord)
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
			starfile.write(extractStar, direct + tomogName + '.star', overwrite=True)
			print('Extraction Complete\n')
			self.ids.mainstar.text = direct + tomogName + '.star'
			self.ids.mainsubtomo.text = direct

	# calculate subtomogram angles
	def calculateAngles(self):
		# read coord files and unfiltered star file
		coordStart = self.ids.vectorStart.text
		coordEnd = self.ids.vectorEnd.text
		starf = self.ids.mainstar.text
		starf = starfile.read(starf)
		# initialize data list
		data = []
		# open and loop through the vector start and end files
		with open(coordStart, 'r') as mem, open(coordEnd, 'r') as cen:
			for lineM, lineC in zip(mem, cen):
				lineM = lineM.strip()
				lineC = lineC.strip()
				posM = lineM.split(' ')
				posC = lineC.split(' ')
				# append the x,y,z from each coord file to row
				row = [posM[0], posM[1], posM[2], posC[0], posC[1], posC[2]]
				data.append(row)
		columns = ['Xmem', 'Ymem', 'Zmem', 'Xcen', 'Ycen', 'Zcen']
		# convert data to dataframe
		dataframe = pd.DataFrame(data, columns=columns)
		# call calcangles function from tom.py
		newangs = tom.calcangles(dataframe)
		# insert the angles into the star file
		star_data = pd.DataFrame.from_dict(starf['particles'])
		star_data.loc[:, ['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']] = newangs
		starf['particles'] = star_data
		starfile.write(starf, self.ids.mainstar.text, overwrite=True)

	# graph for wiener function
	plt.ion()
	# wiener and gaussian filtering
	def filter_vol(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			direct = self.ids.mainmrc.text
			if self.ids.mainmrc.text[-1] != '/':
				direct = self.ids.mainmrc.text + '/'
			wienerbutton = self.ids.wienerbutton.active
			gaussianbutton = self.ids.gaussianbutton.active
			angpix = float(self.ids.A1.text)
			defoc = float(self.ids.defoc.text)
			snrratio = float(self.ids.snrval.text)
			highpassnyquist = float(self.ids.highpass.text)
			if gaussianbutton == True:
				sigval = float(self.ids.sigma.text)
			voltage = float(self.ids.voltage.text)
			cs = float(self.ids.cs.text)
			envelope = float(self.ids.envelope.text)
			bfactor = float(self.ids.bfactor.text)
			phasebutton = self.ids.phaseflip.active
			starf = self.ids.mainstar.text
			subtomodir = self.ids.mainsubtomo.text
			mrcButton = self.ids.mrcfilter.active
			starButton = self.ids.starfilter.active

			if wienerbutton == False and gaussianbutton == False:
				print("At least one option needs to be selected.")
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

						print('Now filtering ' + fileName)
						fullFilePath = subtomodir + fileName

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFilePath)
						subtomo_filt = tom.deconv_tomo(mrc, angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
						subtomo_filt = subtomo_filt.astype('float32')

						# write filtered .mrc file
						baseFileName = fullFilePath.split("/")[-1].split(".")[0]
						newFileName = os.path.join(filterout, baseFileName + '_wiener.mrc')
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
						s[-1] = s[-1].split(".")[0] + "_wiener.mrc"
						s = '/'.join(s)
						return s
			
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: addWiener(x))
					star_data["particles"] = df
					starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star', overwrite=True)
					self.ids.mainstarfilt.text = subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered.star'
					print('Wiener Filtering by Star File Complete\n')

				elif mrcButton:
					# create folder
					filterout = direct + 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
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
					print('Gaussian Filtering by Star File Complete\n')

				elif mrcButton:
					# create folder
					filterout = direct + 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
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

	# coordinate picker
	def pick_coord(self):
		try:
			# initialize variables
			ChimeraX_dir = self.ids.chimera_path.text
			if self.ids.pickcoordFiltered.active == True:
				listName = self.ids.mainstarfilt.text
			else:
				listName = self.ids.mainstar.text
			direct = self.ids.mainsubtomo.text
			if self.ids.mainsubtomo.text[-1] != '/':
				direct = self.ids.mainsubtomo.text + '/'
			pxsz = float(self.ids.A1.text)
			curindex = int(self.ids.index.text)
			self.ids.pickcoordtext.text = 'Please wait. Opening ChimeraX.'
			# find the filename and tomogram name for the current index
			imageNames = starfile.read(listName)["particles"]["rlnImageName"]
			folderNames = starfile.read(listName)["particles"]["rlnMicrographName"]
			starfinal = imageNames[curindex - 1]
			tomoName = folderNames[curindex - 1]
			tomoName = tomoName.split('/')[0] + '/' + tomoName.split('/')[1]
			# set total index value
			self.ids.index2.text = str(len(imageNames))

			# create subcoord_files folder inside subtomogram directory specified on master key
			cmmdir = direct + 'subcoord_files'
			if os.path.isdir(cmmdir) == False:
				os.mkdir(cmmdir)

			# create and run python script to open ChimeraX
			chim3 = direct + 'chimcoord.py'
			tmpflnam = direct + starfinal
			# invert subtomogram if active
			if self.ids.pickcoordInvert.active == True:
				mrc = mrcfile.read(tmpflnam)
				mrc = mrc * -1
				mrcfile.write(tmpflnam, mrc, overwrite=True)
			# run ChimeraX
			file_opt = open(chim3, 'w')
			file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + cmmdir + "\")" + "\n" + "run(session, \"open " + tmpflnam + "\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
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
			if os.path.exists(cmmdir + '/' + tomoName) == False:
				os.makedirs(cmmdir + '/' + tomoName)
			if os.path.exists(cmmdir + '/coord.cmm') == True:
				# check if cmm file will be overwritten
				if os.path.exists(cmmdir + '/' + tomoName + '/' + endcmm) == True:
					statstat = 2
				else:
					statstat = 1
				shutil.move(cmmdir + '/coord.cmm', (cmmdir + '/' + tomoName + '/' + endcmm))
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

			self.ids.notecoord.text = ""
			self.ids.notesave.text = ""
			os.remove(chim3)

		except FileNotFoundError:
			print("This directory does not exist")
			self.ids.pickcoordtext.text = 'Click above to begin.'

		return

	# next subtomogram
	def right_pick(self):
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
			return
		self.ids.index.text = str((int(self.ids.index.text) + 1))
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			self.ids.pickcoordtext.text = 'Click above to begin.'
			return
		return
	
	# next subtomogram * 10
	def fastright_pick(self):
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
			self.ids.pickcoordtext.text = 'Click above to begin.'
			return
		return

	# previous subtomogram
	def left_pick(self):
		try:
			if self.ids.pickcoordFiltered.active == True:
				starf = self.ids.mainstarfilt.text
			else:
				starf = self.ids.mainstar.text
			self.ids.pickcoordtext.text = 'Press Pick Coordinates'
			# decrease index by one
			if int(self.ids.index.text) == 1:
				print('Outside of index bounds')
				self.ids.pickcoordtext.text = 'Click above to begin.'
				return
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) + 1))
			self.ids.pickcoordtext.text = 'Click above to begin.'
		return
	
	# previous subtomogram * 10
	def fastleft_pick(self):
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

	# re-extraction from picked coordinates
	def reextraction(self):
		# initialize variables
		starf = self.ids.mainstarfilt.text
		direct = self.ids.mainsubtomo.text
		angpix = float(self.ids.A1.text)
		imgToCmmCor = {}
		if self.ids.mainsubtomo.text[-1] != '/':
				direct = self.ids.mainsubtomo.text + '/'

		# set directory path
		directory = direct + 'subcoord_files/'

		# check that /subcoord_files/ folder exists
		if os.path.exists(directory) == False:
			print(directory + ' does not exist. Please save coordinates first.')
			return

		# iterate through each folder in directory
		for file1 in os.listdir(directory):
			folder1 = directory + file1
			if folder1[-1] != '/':
				folder1 = folder1 + '/'
			if os.path.isdir(folder1) == True:
				for file in os.listdir(folder1):
					folder = folder1 + file
					# iterate through each .cmm file
					if os.path.isdir(folder) == True:
						for filename in os.listdir(folder):
							if filename.endswith('.cmm'):
								name = filename.replace('.cmm', '')
								with open(folder + '/' + filename) as ftomo:
									count = 1
									for line in ftomo:
										# finding selected .cmm coordinates and shifting based on box size
										if re.search('x', line):
											# read star file and extract original x, y, z coordinates
											star_data = starfile.read(starf)
											df = pd.DataFrame.from_dict(star_data['particles'])
											row = df[df['rlnImageName'].str.contains(name)]
											xCor = float(row['rlnCoordinateX'].iloc[0])
											yCor = float(row['rlnCoordinateY'].iloc[0])
											zCor = float(row['rlnCoordinateZ'].iloc[0])
											# get the tomogram name from star file and memory map it
											tomogram = direct + row['rlnMicrographName'].iloc[0]
											tomogram = mrcfile.mmap(tomogram)
											# get boxsize from subtomogram
											boxsize = []
											with mrcfile.open(direct + row['rlnImageName'].iloc[0], 'r+') as mrc:
												boxsize.append(float(mrc.header.nx))
												boxsize.append(float(mrc.header.ny))
												boxsize.append(float(mrc.header.nz))
											# find selected x, y, z coordinates from .cmm file
											xmid = re.search(' x="(.*)" y', line)
											x_coord = float(xmid.group(1)) / angpix
											cmmX = round(boxsize[0]/2 - x_coord)
											ymid = re.search(' y="(.*)" z', line)
											y_coord = float(ymid.group(1)) / angpix
											cmmY = round(boxsize[1]/2 - y_coord)
											zmid = re.search(' z="(.*)" r=', line)
											z_coord = float(zmid.group(1)) / angpix
											cmmZ = round(boxsize[2]/2 - z_coord)
											# calculate final x, y, z coordinates
											finalx = str(round(xCor) - int(cmmX))
											finaly = str(round(yCor) - int(cmmY))
											finalz = str(round(zCor) - int(cmmZ))
											# create a folder for each subtomogram
											subtomoName = row['rlnImageName'].iloc[0]
											subtomo = subtomoName.replace('_wiener', '')
											subtomo = subtomo.replace('_gauss', '')
											subtomo = subtomo.replace('filtered', subtomo.split("/")[-1].split('.')[0])
											subtomoFolder = '/'.join((direct + subtomo).split('/')[:-1])
											if os.path.isdir(subtomoFolder) == False:
												os.makedirs(subtomoFolder)
											# convert coordinates to integers
											x = int(finalx) - boxsize[0]/2
											y = int(finaly) - boxsize[1]/2
											z = int(finalz) - boxsize[2]/2
											# calculate bounds
											bound = np.zeros(3)
											bound[0] = z + boxsize[2] - 1
											bound[1] = y + boxsize[1] - 1
											bound[2] = x + boxsize[0] - 1
											# rounding
											bound = np.round(bound).astype(int)
											z = np.round(z).astype(int)
											y = np.round(y).astype(int)
											x = np.round(x).astype(int)
											# cut the tomogram
											subby = tomogram.data[z:(bound[0]+1), y:(bound[1]+1), x:(bound[2]+1)]
											# invert contrast if selected
											if self.ids.reextractInvert.active == True:
												subby = subby * -1
											# add new coords to dictionary
											if name in imgToCmmCor.keys(): #checks duplicate filename
												imgToCmmCor[name + count*"!"] = [x_coord, y_coord, z_coord, cmmX, cmmY, cmmZ, finalx, finaly, finalz, subtomo]
												count += 1
											else:
												imgToCmmCor[name] = [x_coord, y_coord, z_coord, cmmX, cmmY, cmmZ, finalx, finaly, finalz, subtomo]
											# create subtomograms
											if count > 1: #account for duplicates
												num = str(count - 1)
												subtomo = subtomo.replace('.mrc', '_' + num + '.mrc')
												mrcfile.new(direct + subtomo, subby, overwrite=True)
												with mrcfile.open(direct + subtomo, 'r+') as mrc:
													mrc.voxel_size = angpix
											else:
												subtomo = subtomo.replace('.mrc', '_0.mrc')
												mrcfile.new(direct + subtomo, subby, overwrite=True)
												with mrcfile.open(direct + subtomo, 'r+') as mrc:
													mrc.voxel_size = angpix
											# create .coords file
											subName = row['rlnMicrographName'].iloc[0].split('/')[-1].replace('.mrc','')
											file_opt = open(folder + '/' + subName + '.coords', 'a')
											file_opt.writelines(str(int(x_coord)) + ' ' + str(int(y_coord)) + ' ' + str(int(z_coord)) + '\n')
											file_opt.close()
		
		# add new information to intermediate star file
		star_data = starfile.read(starf)
		df = pd.DataFrame.from_dict(star_data['particles'])
		# define new columns
		df["rlnSubtomogramPosX"] = np.zeros(df.shape[0])
		df["rlnSubtomogramPosY"] = np.zeros(df.shape[0])
		df["rlnSubtomogramPosZ"] = np.zeros(df.shape[0])
		df["rlnCorrectedCoordsX"] = np.zeros(df.shape[0])
		df["rlnCorrectedCoordsY"] = np.zeros(df.shape[0])
		df["rlnCorrectedCoordsZ"] = np.zeros(df.shape[0])
		df["rlnCoordinateNewX"] = np.zeros(df.shape[0])
		df["rlnCoordinateNewY"] = np.zeros(df.shape[0])
		df["rlnCoordinateNewZ"] = np.zeros(df.shape[0])
		# iterate through each directory
		for file1 in os.listdir(directory):
			folder1 = directory + file1
			if folder1[-1] != '/':
				folder1 = folder1 + '/'
			if os.path.isdir(folder1) == True:
				for file in os.listdir(folder1):
					folder = folder1 + file
					# iterate through each .cmm file
					if os.path.isdir(folder) == True:
						for name in os.listdir(folder):
							if name.endswith('.cmm'):
								name = name.replace('.cmm', '')
								# paste in new information to each new column
								df.loc[df['rlnImageName'].str.contains(name), "rlnSubtomogramPosX"] = imgToCmmCor[name][0]
								df.loc[df['rlnImageName'].str.contains(name), "rlnSubtomogramPosY"] = imgToCmmCor[name][1]
								df.loc[df['rlnImageName'].str.contains(name), "rlnSubtomogramPosZ"] = imgToCmmCor[name][2]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCorrectedCoordsX"] = imgToCmmCor[name][3]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCorrectedCoordsY"] = imgToCmmCor[name][4]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCorrectedCoordsZ"] = imgToCmmCor[name][5]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCoordinateNewX"] = imgToCmmCor[name][6]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCoordinateNewY"] = imgToCmmCor[name][7]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCoordinateNewZ"] = imgToCmmCor[name][8]
								# os.remove(folder + '/' + name + '.cmm')
		# adding row for each duplicate filename to dictionary
		df1 = pd.DataFrame()
		for imgName in imgToCmmCor.keys():
			if df[df['rlnImageName'].str.contains(imgName)].shape[0] == 0:
				modifiedName = imgName.replace("!", "")
				row = df[df['rlnImageName'].str.contains(modifiedName)].to_dict()
				row["rlnSubtomogramPosX"] = imgToCmmCor[imgName][0]
				row["rlnSubtomogramPosY"] = imgToCmmCor[imgName][1]
				row["rlnSubtomogramPosZ"] = imgToCmmCor[imgName][2]
				row["rlnCorrectedCoordsX"] = imgToCmmCor[imgName][3]
				row["rlnCorrectedCoordsY"] = imgToCmmCor[imgName][4]
				row["rlnCorrectedCoordsZ"] = imgToCmmCor[imgName][5]
				row["rlnCoordinateNewX"] = imgToCmmCor[imgName][6]
				row["rlnCoordinateNewY"] = imgToCmmCor[imgName][7]
				row["rlnCoordinateNewZ"] = imgToCmmCor[imgName][8]
				df1 = pd.concat([df1, pd.DataFrame(row)])
		df = pd.concat([df, df1])
		df = df.sort_values(by="rlnImageName")
		star_data['particles'] = df
		starfile.write(star_data, directory + '/' + starf.split("/")[-1].split(".")[0] + '_cmm.star', overwrite=True)

		# create new star file
		cmmStar = directory + '/' + starf.split("/")[-1].split(".")[0] + '_cmm.star'
		star_data = starfile.read(cmmStar)
		df = pd.DataFrame.from_dict(star_data['particles'])
		df1 = pd.DataFrame.from_dict(star_data['particles'])
		df1 = df1.drop(df1.index)
		df1 = df1.dropna(how="all")

		for imageName in imgToCmmCor.keys():
			if '!' in imageName:
				duplicateNum = str(imageName.count("!"))
				duplicateName = imgToCmmCor[imageName][9].replace('.mrc', "_" + duplicateNum + ".mrc")
				modifiedName = imageName.replace("!", "")
				row = df[df['rlnImageName'].str.contains(modifiedName) & (df["rlnCoordinateNewX"] == float(imgToCmmCor[imageName][6]))].copy(deep=True)
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnCoordinateX"] = imgToCmmCor[imageName][6]
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnCoordinateY"] = imgToCmmCor[imageName][7]
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnCoordinateZ"] = imgToCmmCor[imageName][8]
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnOriginXAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnOriginYAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnOriginZAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(modifiedName), "rlnImageName"] = duplicateName				
			else:
				firstName = imgToCmmCor[imageName][9].replace('.mrc', '_0.mrc')
				row = df[df['rlnImageName'].str.contains(imageName) & (df["rlnCoordinateNewX"] == float(imgToCmmCor[imageName][6]))].copy(deep=True)
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnCoordinateX"] = imgToCmmCor[imageName][6]
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnCoordinateY"] = imgToCmmCor[imageName][7]
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnCoordinateZ"] = imgToCmmCor[imageName][8]
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnOriginXAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnOriginYAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnOriginZAngst"] = 0
				row.loc[row['rlnImageName'].str.contains(imageName), "rlnImageName"] = firstName
			
			df1 = pd.concat([df1, row])
		columnsDrop = df1.columns[df1.columns.get_loc("rlnSubtomogramPosX"):df1.columns.get_loc("rlnCoordinateNewZ")+1]
		df1 = df1.drop(columns = columnsDrop)
		
		star_data['particles'] = df1
		starfileName = starf.split("/")[-1].split(".")[0].replace('_filtered', '')
		starfile.write(star_data, direct + '/' + starfileName + '_reextract.star', overwrite=True)
		# remove intermediate star file
		os.remove(cmmStar)
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

	# 3d signal subtraction
	def subtraction(self):
		mask = self.ids.maskpath.text
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			direc = self.ids.mainsubtomo.text + '/'
		else:
			direc = self.ids.mainsubtomo.text
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
			fileNames, angles, shifts, list_length, pickPos, new_star_name = tom.readList(listName, pxsz, 'masked', [])
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

		cut_part_and_movefunc(mask, starf, direc, pxsz, filter, grow, normalizeit, sdrange, sdshift, blackdust, whitedust, shiftfil, randfilt, permutebg)
		return

	# calculate cross correlation coefficient
	def calculate_ccc(self):
		cccVol1 = self.ids.cccvolone.text
		cccVol2 = self.ids.cccvoltwo.text
		wedge = self.ids.cccwedge.text
		star = self.ids.mainstar.text
		zoom = 40
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		ccc = tom.ccc_calc(star, cccVol1, cccVol2, boxsize, zoom, wedge)
		print(ccc)
		return

	# filter subtomograms by CCC
	def filter_ccc(self):
		volume = self.ids.volvol.text
		star = self.ids.mainstar.text
		wedge = self.ids.volwedge.text
		cccthresh = float(self.ids.cccthresh.text)
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		zoom = float(self.ids.zoomrange.text)
		tom.ccc_loop(star, volume, cccthresh, boxsize, zoom, wedge)
		return
	
	# flip a random subset of subtomograms by 180 degrees
	def randFlip(self):
		self.ids.randaxis.text = ""
		starf = self.ids.mainstar.text
		xflip = self.ids.xflip.active
		yflip = self.ids.yflip.active
		zflip = self.ids.zflip.active
		if xflip or yflip or zflip:
			if xflip == True:
				axis = 0
			if yflip == True:
				axis = 1
			if zflip == True:
				axis = 2
		else:
			self.ids.randaxis.text = "Axis of rotation not specified"
			return
		
		randPercent = float(self.ids.percentflip.text)
		_, ext = os.path.splitext(starf)
		if ext == '.star':
			star_data = starfile.read(starf)["particles"]
			new_star = starfile.read(starf)
			
			df = pd.DataFrame.from_dict(new_star["particles"])
			numFiles = len(star_data['rlnImageName'])
			randIdx = random.sample(range(numFiles), round(numFiles*randPercent/100))
			if axis == 0:
				df.loc[randIdx, "rlnAngleRot"] += 180
			if axis == 1:
				df.loc[randIdx, "rlnAngleTilt"] += 180
			if axis == 2:
				df.loc[randIdx, "rlnAnglePsi"] += 180
			flipped = np.zeros((numFiles,), dtype=int)
			for i in range(numFiles):
				if i in randIdx:
					flipped[i] = 1
			df["Flipped"] = flipped
			new_star["particles"] = df
			starfile.write(new_star, _ + "_randFlip" + ".star", overwrite=True)

		else:
			raise ValueError("Unsupported file extension.")
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
				outH1 = tom.processParticler(fileNames[i], angles[:,i].conj().transpose() * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			else:
				outH1 = tom.processParticler(fileNames[i], ownAngs * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			outH1 = outH1.astype(np.float32)
			if os.path.isdir(rotDir) == False:
				os.makedirs(rotDir, exist_ok=True)
			mrcfile.write(rotDir + mrcName, outH1, True)
			with mrcfile.open(rotDir + mrcName, 'r+') as mrc:
				mrc.voxel_size = pxsz
			print('Rotation complete for ' + mrcName)
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
		return
	
	# rotate by star file
	def rotate(self):
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			dir = self.ids.mainsubtomo.text + '/'
		else:
			dir = self.ids.mainsubtomo.text
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = self.ids.applyTranslations.active
		ownAngs = []

		self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)
		print('Rotation by Star File Complete\n')
		return
	
	# rotate by manual angle/axis
	def manualrotate(self):
		self.ids.noaxis.text = " "
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			dir = self.ids.mainsubtomo.text + '/'
		else:
			dir = self.ids.mainsubtomo.text
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = False
		xaxis = self.ids.xaxis.active
		yaxis = self.ids.yaxis.active
		zaxis = self.ids.zaxis.active
		anglerotate = float(self.ids.anglerotation.text)

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
		
		self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)
		print('Manual Rotation Complete\n')

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
		starf = self.ids.mainstarfilt.text # filtered star file 
		starUnf = self.ids.mainstar.text # unfiltered star file
		subtomodir = self.ids.mainsubtomo.text
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
		if self.ids.refPath.text[-1] != '/':
			classPath = self.ids.refPath.text + '/'
		else:
			classPath = self.ids.refPath.text
		classBasename = self.ids.refBasename.text
		angpix = float(self.ids.A1.text)
		bxsz = float(self.ids.px1.text)
		boxsize = [bxsz, bxsz, bxsz]
		# get models in class that matches basename
		folder = os.listdir(classPath)
		classes = [file for file in folder if classBasename in file]
		# read starfile as dataframe
		star_data = starfile.read(starf)["particles"]
		# iterate through each row of dataframe
		for row in star_data.itertuples(index=False):
			imgName = row.rlnImageName
			# classNum = row.rlnClassNumber (use this when class number is starfile is accurate)
			classNum = str(random.randint(1, 3))
			# get model associated with class num
			model = classPath + [file for file in classes if "00" + classNum in file][0]
			coords = np.array([int(row.rlnCoordinateX), int(row.rlnCoordinateY), int(row.rlnCoordinateZ)])
			angles = np.array([float(row.rlnAngleRot), float(row.rlnAngleTilt), float(row.rlnAnglePsi)])
			shifts = np.array([float(row.rlnOriginXAngst), float(row.rlnOriginYAngst), float(row.rlnOriginZAngst)])
			# transform corresponding model by inversed angles and shifts specified in starfile
			transformed = tom.processParticler(model, angles, boxsize, shifts, shifton=True)
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
				mrc.header.nxstart = coords[0] - bxsz
				mrc.header.nystart = coords[1] - bxsz
				mrc.header.nzstart = coords[2] - bxsz
		return

	pass

#run CrESTA
Cresta().run()