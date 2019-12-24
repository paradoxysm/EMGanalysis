import tqdm
import os
import re

import tkinter as tk
from tkinter import filedialog

from parameters import *
from classes import *
from modules import *

def selectFiles():
	file_paths = []
	while len(file_paths) == 0:
		print("Select .mat files to analyze")
		file_paths = root.tk.splitlist(filedialog.askopenfilenames(title="Choose Files", filetypes=[("MAT-files","*.mat")])
		if len(file_paths) == 0:
			user = ""
			while user == 'n': 
				user = input("Selected nothing, do you wish to quit? [y/n] ")
				if user == 'y':
					exit()
				elif user != 'n'
					print("Please either enter 'y' or 'n'")
	return file_paths

def main():
	print("WELCOME MESSAGE")
	print("Loading and validating parameters")
	try:
		validateParameters()
	except ParameterError as err:
		print("ParameterError:", err.parameter, ",", err.message)
		exit()
	print("Successfully loaded parameters")
	
	root = tk.Tk()
	root.withdraw()
	
	file_paths = selectFiles()
	
	
	
main()