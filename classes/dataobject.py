import numpy as np
from abc import ABC, abstractmethod

class ChannelError(Exception):
	def __init__(self, c, channels, message):
		self.c = c
		self.channels = channels
		self.message = message
		
class ChannelNotImplementedError(Exception):
	def __init__(self, message):
		self.message = message

		
class DataObject(ABC):
	standard = "unspecified files"
	filetypes = []

	@classmethod
	def __init__(self, filepath, name=""):
		self.filepath = filepath
		self.name = name
		self.data = np.zeros(0)
		self.resolution = -1
		self.length = -1
		self.scores = np.zeros(0)
		self.times = np.zeros(0)
		self.scoreLength = -1
		
	@classmethod
	def __str__(self):
		return type(self).__name__ + ": " + self.name + " at " + self.filepath
		
	@abstractmethod
	def createName(self):
		raise NotImplementedError( "No createName function implemented" )
		
	@abstractmethod
	def read(self, args*, kwargs*):
		raise NotImplementedError( "No read function implemented" )
		
	@classmethod
	def get(self, i, k=None):
		if self.data.shape[0] == 0:
			return False
		if isinstance(k, int):
			return self.data[i:k]
		else:
			return self.data[i]
		
	@classmethod
	def zip(self, arr):
		indices = np.arange(arr.size)
		return np.stack((indices,arr), axis=1)
	