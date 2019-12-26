from importlib.machinery import SourceFileLoader
dataObject = SourceFileLoader("dataobject", "./plugins/dataobject.py").load_module()

import numpy as np
from scipy.io import loadmat

# A Data Import Type (DataObject) for .mat files exported by Spike2 v7
class smrEMG(dataObject.DataObject):
	standard = ".mat files exported by Spike2 v7"
	filetypes = [("MAT-files", "*.mat")]

	def __init__(self, filepath, name=""):
		super().__init__(filepath, name=name)
		
	def __str__(self):
		return type(self).__name__ + ": " + self.name + " at " + self.filepath
		
	# Set up a default name based on the file name
	def createName(self):
		self.name = self.filepath.split('/')[-1].split('.mat')[0]
		return self.name
		
	# Read data out of the associated file
	def read(self, c="", s=""):
		if c == "" or s == "":
			raise dataObject.ChannelNotImplementedError("EMG channel or score channel has not been specified")
		try:
			matfile = loadmat(self.filepath)
		except:
			raise FileNotFoundError("No such file or directory: " + self.filepath)
		for field in matfile.keys():
			if '_Ch' in field:
				if c == matfile[field][0][0][0][0]:
					self.data = np.absolute((matfile[field][0][0][8]).flatten())
					self.indices = np.arange(self.data.size)
					self.resolution = matfile[field][0][0][2][0][0]
					self.length = matfile[field][0][0][7][0][0]
				elif s == matfile[field][0][0][0][0]:
					self.scores = matfile[field][0][0][7]
					self.times = matfile[field][0][0][5]
					self.scoreLength = len(self.scores)
		if self.data.size == 0 or self.scores.size == 0 or self.times.size == 0:
			channels = []
			for field in matfile.keys():
				channels.append(matfile[field][0][0][0][0])
			if self.data.size == 0:
				raise dataObject.ChannelError(c, channels, "EMG channel not found")
			else:
				raise dataObject.ChannelError(s, channels, "Score channel not found")
		