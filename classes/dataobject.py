import numpy as np

class DataObject:
	def __init__(self, filepath, name=""):
		self.filepath = filepath
		self.name = name
		self.data = np.zeros(0)
		self.resolution = -1
		self.length = -1
		
	def __str__(self):
		return type(self).__name__ + ": " + self.name + " at " + self.filepath
		
	def read(self):
		raise NotImplementedError( "No read function implemented" )
		
	def get(self, i, k=None):
		if isinstance(k, int):
			return self.data[i:k]
		else:
			return self.data[i]
		
	