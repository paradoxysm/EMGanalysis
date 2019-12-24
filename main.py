import tqdm
import os
import re

import tkinter as tk
from tkinter import filedialog

from parameters import *
from classes import smrEMG

def defaultQuitPrompt():
	user = ""
	while user == 'n': 
		user = input("Selected nothing, do you wish to quit? [y/n] ")
		if user == 'y':
			exit()
		elif user != 'n':
			print("Please either enter 'y' or 'n'")

def selectFiles(root):
	file_paths = []
	while len(file_paths) == 0:
		print("Select .mat files to analyze")
		file_paths = root.tk.splitlist(filedialog.askopenfilenames(title="Choose Files", filetypes=[("MAT-files","*.mat")]))
		if len(file_paths) == 0:
			defaultQuitPrompt()
			print("Try again!")
	return file_paths

def loadFile(filepath):
	loading = True
	while loading:
		data = smrEMG.smrEMG(filepath)
		channel = input("Enter the name of the EMG channel to be analyzed [Default: 'MASS'] ")
		data.selectChannel(channel)
		score = input("Enter the name of the Score channel [Default: 'SCORE'] ")
		data.selectScoreChannel(score)
		try:
			data.read()
			loading = False
		except ChannelNotImplementedError as err:
			print("ChannelNotImplementedError:", err.message)
		except ChannelError as err:
			print("ChannelError:",err.message," - Input:", err.c, " - Found:", err.channels)
		except FileNotFoundError as err:
			print("FileNotFoundError:", err.message)
		except:
			print("Something unexpected went wrong! Let's try again")
		if loading:
			defaultQuitPrompt()
			print("Try again!")
	return data
	
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
	
	file_paths = selectFiles(root)
	
	for file in file_paths:
		data = loadFile(file)
		
	
main()