import numpy as np

# DataObject defines the Class structure and necessary components
#	to a Data Import Type plugin
class DataObject:
	standard = "unspecified files"
	filetypes = []

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

	def createName(self):
		raise NotImplementedError( "No createName function implemented" )

	def read(self, *args, **kwargs):
		raise NotImplementedError( "No read function implemented" )

	def get(self, arr, i, k=None):
		if len(arr) == 0:
			return False
		if isinstance(k, int):
			return arr[i:k]
		else:
			return arr[i]

	def getData(self, i, k=None):
		return self.get(self.data, i, k)

	def getIndices(self, i, k=None):
		return self.get(self.indices, i, k)

	def getScores(self, i, k=None):
		return self.get(self.scores, i, k)

	def getTimes(self, i, k=None):
		return self.get(self.times, i, k)
