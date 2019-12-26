import sys, os
from importlib.machinery import SourceFileLoader

plugins = ['smrEMG']

def loadPlugins():
	modules = []
	modules.append(getattr(SourceFileLoader("smrEMG", "./plugins/smrEMG.py").load_module(), "smrEMG"))
	return modules