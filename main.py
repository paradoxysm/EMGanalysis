import tqdm
import os
import re
from importlib import import_module
import tkinter as tk
from tkinter import filedialog
from math import floor

from parameters import *
from classes.dataobject import *

class Analyzer:
	def __init__(self, dataobject, filetypes):
		self.module = import_module("classes." + dataobject)
		self.dataobject = getattr(module, dataobject)
		self.filetypes = filetypes
		self.root = tk.Tk()
		self.root.withdraw()
		
	def __str__(self):
		return type(self).__name__ + ": " + self.dataobject.__name__

	def defaultQuitPrompt(self):
		user = ""
		while user == 'n': 
			user = input("Selected nothing, do you wish to quit? [y/n] ")
			if user == 'y':
				exit()
			elif user != 'n':
				print("Please either enter 'y' or 'n'")

	def selectFiles(self):
		file_paths = []
		while len(file_paths) == 0:
			print("Select files to analyze")
			print("This analyzer is configured according to the specifications of", self.dataobject.__name__)
			print("This specification accepts", self.dataobject.standard)
			file_paths = self.root.tk.splitlist(filedialog.askopenfilenames(title="Choose Files", filetypes=self.filetypes))
			if len(file_paths) == 0:
				self.defaultQuitPrompt()
				print("Try again!")
		return file_paths

	def loadFile(filepath):
		loading = True
		print("Loading contents of the file at", filepath)
		data = self.dataobject(filepath)
		print("Dataset is named:", data.createName())
		while loading:
			channel = input("Enter the name of the EMG channel to be analyzed [Default: 'MASS'] ")
			score = input("Enter the name of the Score channel [Default: 'SCORE'] ")
			try:
				data.read(c=channel, s=score)
				loading = False
			except ChannelNotImplementedError as err:
				print("ChannelNotImplementedError:", err.message)
			except ChannelError as err:
				print("ChannelError:",err.message," - Input:", err.c, " - Found:", err.channels)
			except FileNotFoundError as err:
				print("FileNotFoundError:", err)
			except NotImplementedError as err:
				print("NotImplementedError:", err)
			except:
				print("Something unexpected went wrong! Let's try again")
			if loading:
				self.defaultQuitPrompt()
				print("Try again!")
		return data
	
	def parseREM(self, data):
		print("Parsing through dataset")
		print("Found", data.length, "samples and", data.scoreLength, "epochs")
		rem_start = 0
		rem_end = 0
		rem_idx = np.zeros((0,2))
		for i in tqdm(range(data.scoreLength+1)):
			if data.scores[i] == 'R' and i < data.scoreLength:
				if rem_end - rem_start <= 0:
					rem_start = i
					rem_end = i
				rem_end += 1
			else:
				if rem_end - rem_start > 0:
					rem_start_time = floor(data.times[rem_start] / data.resolution)+1
					rem_end_time = floor(data.times[rem_end] / data.resolution)
					rem_idx = np.concatenate((rem_idx, (rem_start_time, rem_end_time), axis=0)
		num_rem = rem_idx.shape[0]
		print("Found", num_rem, "REM episodes")
		return rem_idx	

	def determineThreshold(self, data, rem):
		print("Determining threshold for REM episode found at", rem)
		method = ''
		FIRST_SAMPLES = FIRST_TIME / (data.resolution * 1000)
		rem_data = data.get(rem[0], k=rem[1])[:,1]
		
		start = 0
		threshold_rem = 0
		checks = {'thresholds':[], 'rem_means':[], 'rem_stds':[],
					'twitch_checks':[], 'twitch_ratios':[],
					'sample_means':np.mean(rem_data), 'sample_stds':np.std(rem_data),
					'sample_checks':SAMPLE_MEAN*sample_mean + SAMPLE_STD*sample_std,
					'sample_ratios':[]
				}
		
		while method == '':
			rem_end = round(start + FIRST_SAMPLES)
			rem_sample = rem_data[start:rem_end]
			threshold_rem = np.percentile(rem_sample, BASELINE_PERCENTILE)
			rem_mean = np.mean(rem_sample)
			rem_std = np.std(rem_sample)
			twitch_check = REM_MEAN*rem_mean + REM_STD*rem_std
			
			checks['thresholds'].append(threshold_rem)
			checks['rem_means'].append(rem_mean)
			checks['rem_stds'].append(rem_std)
			checks['twitch_checks'].append(twitch_check)
			checks['twitch_ratios'].append(twitch_check/threshold_rem)
			checks['sample_ratios'].append(sample_check/threshold_rem)
				
			if twitch_check / threshold_rem > TWITCH_THRESHOLD and sample_check / threshold_rem > SAMPLE_THRESHOLD:
				method = 'Window';
			else:		
				start = round(start + 0.5*FIRST_SAMPLES);
				if start + FIRST_SAMPLES > rem_data.shape[0]:
					threshold_rem = np.percentile(thresholds,SAMPLE_PERCENTILE);
					method = 'Percentile';
		print("Threshold for REM episode at", rem, "is set to", threshold_rem, "using the", method, "method")
		return method, threshold_rem, checks
		
	def filter(self, data, rem, threshold):
		print("Filtering REM episode at", rem, "with a threshold of", threshold)
		rem_data = data.get(rem[0], k=rem[1])
		filtered = np.zeros((0,2))
		unfiltered = np.zeros((0,2))
		for i in tqdm(range(rem_data.shape[0])):
			if rem_data[i,1] > threshold:
				filtered = np.concatenate((filtered,rem_data[i]),axis=0)
			else:
				unfiltered = np.concatenate((unfiltered,rem_data[i]),axis=0)
		print("Filtered!")
		return filtered, unfiltered
		
	def analyze(self, peaks, rem, resolution):
		print("Analyzing for twitches")
		length = peaks.shape[0]
		analysis = {'events':[],'num_events':0,'avg_amp':[],'int_amp':[],
					'durations':[], 'time':length * resolution,
					'start':rem[0] * resolution, 'end':rem[1] * resolution,
					'event%':length/(rem[1]-rem[0]+1),'base%':1-length/(rem[1]-rem[0]+1)
					}
		if length > 0:
			event = np.array([peaks[0]])
			for i in tqdm(range(1, length+1)):
				if peaks[i,0] - event[-1][0] < MIN_INTERVAL and i < length:
					event = np.concatenate((event, np.array([peaks[i]])), axis=0)
				else:
					analysis['event_starts'].append(event[0,0] * resolution)
					analysis['num_events'] += 1
					analysis['avg_amp'].append(np.mean(event[:,1]))
					analysis['int_amp'].append(np.sum(event[:,1]))
					analysis['durations'].append(event.shape[0] * resolution)
					if i < length:
						event = np.array([peaks[i]])
		print("Twitches analyzed!")
		print("Found", analysis['num_events'], "twitches")
		return analysis		
	
	def export(self):
		pass
	
	def run(self):
		print("WELCOME MESSAGE")
		print("Loading and validating parameters")
		try:
			validateParameters()
		except ParameterError as err:
			print("ParameterError:", err.parameter, ",", err.message)
			exit()
		print("Successfully loaded parameters")

		file_paths = selectFiles()
		
		for file in file_paths:
			data = self.loadFile(file)
			rem_idx = self.parseREM(data)
			for rem in rem_idx:
				method, threshold_rem, checks = self.determineThreshold(data, rem)
				peaks, below = self.filter(data, rem, threshold_rem)
				analysis = self.analyze(peaks, rem, data.resolution)
				below_avg = np.mean(below[:,1])
				