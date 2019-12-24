from .dataobject import *
from scipy.io import loadmat
import numpy as np

from parameters import *


class smrEMG(DataObject):
	def __init__(self, filepath, name=""):
		super().__init__(filepath, name=name)
		
	def createName(self):
		self.name = self.filepath.split('/')[-1].split('.mat')[0]
		return self.name
		
	def read(self, c="", s=""):
		if c == "" or s == "":
			raise ChannelNotImplementedError("EMG channel or score channel has not been specified")
		try:
			matfile = loadmat(filepath)
		except:
			raise FileNotFoundError("No such file or directory: " + filepath)
		for field in matfile.keys():
			if '_Ch' in field:
				if c == matfile[field][0][0][0][0]:
					self.data = self.zip((matfile[field][0][0][8]).flatten())
					self.resolution = matfile[field][0][0][2]
					self.length = matfile[field][0][0][7]
				elif s == matfile[field][0][0][0][0]:
					self.scores = matfile[field][0][0][7]
					self.times = matfile[field][0][0][5]
					self.scoreLength = len(self.scores)
		if self.data.size == 0 or self.scores.size == 0 or self.times.size == 0:
			channels = []
			for field in matfile.keys():
				channels.append(matfile[field][0][0][0][0])
			if self.data.size == 0:
				raise ChannelError(c, channels, "EMG channel not found")
			else:
				raise ChannelError(s, channels, "Score channel not found")
		self.data = np.absolute(self.data)
		