import sys, os
from importlib import import_module

import analyzer
import welcome


if __name__ == "__main__":
	welcome.printWelcome()
	sys.path.append(os.path.dirname(sys.executable))
	loader = import_module('pluginloader')
	modules = loader.loadPlugins()
	if len(modules) == 0:
		print("No recognized Data Import Types!")
		print("Goodbye!")
		sys.exit()
	import_type = ""
	analyzerObject = None
	while analyzerObject is None:
		print("Recognized Data Import Types:")
		for i in range(len(modules)):
			print(" " + str(i+1) + ".", modules[i].__name__)
		try:
			import_type = input("Select a data import type by entering corresponding number; quit by entering 'q': ")
		except ValueError as err:
			print("ValueError:", err)
			import_type = ""
		if import_type == 'q':
			print("Goodbye!")
			sys.exit()
		else:
			try:
				import_type = int(import_type)
			except ValueError as err:
				print("Seems like you picked something wrong try again!")
				import_type = ""
			else:
				if import_type <= len(modules) and import_type > 0:
					import_type = modules[import_type-1]
					try:
						analyzerObject = analyzer.Analyzer(import_type)
					except ImportError as err:
						print("ImportError:", err)
						analyzerObject = None
						import_type = ""
				else:
					print("Seems like you picked something wrong try again!")
					import_type = ""
	analyzerObject.run()