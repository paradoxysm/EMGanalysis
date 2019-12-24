from dataobject import *
from scipy.io import loadmat
import numpy as np

class ChannelError(Exception):
	def __init__(self, c, channels, message):
		self.c = c
		self.channels = channels
		self.message = message
		
class ChannelNotImplementedError(Exception):
	def __init__(self, c, channels, message):
		self.c = c
		self.channels = channels
		self.message = message


class smrEMG(DataObject):
	def __init__(self, filepath, name=""):
		super().__init__(filepath, name=name)
		self.channel = ""
		self.scoreChannel = ""
		self.scores = np.zeros(0)
		self.times = np.zeros(0)
		
	def read(self):
		if self.channel == "" or self.scoreChannel == "":
			raise NotImplementedError( "EMG channel or score channel has not been specified" )
		matfile = loadmat(filepath)
		for field in matfile.keys():
			if '_Ch' in field:
				if self.channel == matfile[field][0][0][0][0]:
					self.data = (matfile[field][0][0][8]).flatten()
					self.resolution = matfile[field][0][0][2]
					self.length = matfile[field][0][0][7]
				elif self.scoreChannel == matfile[field][0][0][0][0]:
					self.scores = matfile[field][0][0][7]
					self.times = matfile[field[0][0][5]
		if self.data.size == 0 or self.scores.size == 0 or self.times.size == 0:
			channels = []
			for field in matfile.keys():
				channels.append(matfile[field][0][0][0][0])
			if self.data.size == 0:
				raise ChannelError(self.channel, channels, "EMG channel not found")
			else:
				raise ChannelError(self.scoreChannel, channels, "Score channel not found")
		self.data = np.absolute(self.data)
		
	def selectChannel(self, channel):
		self.channel = str(channel)
		
	def selectScoreChannel(self, channel):
		self.scoreChannel = str(channel)