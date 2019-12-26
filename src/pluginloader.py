import sys, os
from importlib.machinery import SourceFileLoader

# Easy reading of plugins installed - not actually used
plugins = ['smrEMG']

# Load all plugins specified
#	To install a plugin, add the following before after line 11
#		modules.append(getattr(SourceFileLoader("[pluginName]", "./plugins/[pluginName].py").load_module(), "[pluginName]"))
def loadPlugins():
	modules = []
	modules.append(getattr(SourceFileLoader("smrEMG", "./plugins/smrEMG.py").load_module(), "smrEMG"))
	return modules