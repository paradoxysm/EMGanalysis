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


# DataObject defines the Class structure and necessary components
#	to a Data Import Type plugin
class DataObject(ABC):
	standard = "unspecified files"
	filetypes = []

	@classmethod
	def __init__(self, filepath, name=""):
		self.filepath = filepath
		self.name = name
		self.data = np.zeros(0)
		self.indices = np.zeros(0)
		self.resolution = -1
		self.length = -1
		self.scores = np.zeros(0)
		self.times = np.zeros(0)
		self.scoreLength = -1
		
	def __str__(self):
		return type(self).__name__ + ": " + self.name + " at " + self.filepath
		
	@abstractmethod
	def createName(self):
		raise NotImplementedError( "No createName function implemented" )
		
	@abstractmethod
	def read(self, *args, **kwargs):
		raise NotImplementedError( "No read function implemented" )
		
	@classmethod
	def get(self, arr, i, k=None):
		if len(arr) == 0:
			return False
		if isinstance(k, int):
			return arr[i:k]
		else:
			return arr[i]

	@classmethod
	def getData(self, i, k=None):
		return self.get(self.data, i, k)

	@classmethod
	def getIndices(self, i, k=None):
		return self.get(self.indices, i, k)
	
	@classmethod
	def getScores(self, i, k=None):
		return self.get(self.scores, i, k)
	
	@classmethod
	def getTimes(self, i, k=None):
		return self.get(self.times, i, k)
	