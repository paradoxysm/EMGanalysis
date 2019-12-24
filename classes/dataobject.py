class DataObject:
	def __init__(self, filepath):
		self.filepath = filepath
		self.name = ""
		self.data = []
		self.resolution = -1
		self.length = -1
		
	def __str__(self):
		return type(self).__name__ + ": " + self.name + " at " self.filepath
		
	def read(self):
		raise NotImplementedError( "No read function implemented" )
		
	def get(self, i, k=None):
		if isinstance(k, int):
			return self.data[i:k]
		else:
			return self.data[i]
		
	