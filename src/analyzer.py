from tqdm import tqdm
import sys, os
import tkinter as tk
from tkinter import filedialog
from math import floor
from xlwt import Workbook
from xlrd import open_workbook
from xlutils.copy import copy
import win32com.client as win32
import pathlib

from importlib import import_module
sys.path.append(os.path.dirname(sys.executable))

from plugins.dataobject import *

class Analyzer:
	def __init__(self, dataobject):
		self.dataobject = dataobject
		self.parameters = import_module('parameters')
		self.root = tk.Tk()
		self.root.withdraw()
		
	def __str__(self):
		return type(self).__name__ + ": " + self.dataobject.__name__

	def defaultQuitPrompt(self):
		user = ""
		while user != "n": 
			user = input("Selected nothing, do you wish to quit? [y/n] ")
			if user == 'y':
				print("Goodbye!")
				sys.exit()
			elif user != 'n':
				print("Please either enter 'y' or 'n'")

	def selectFiles(self):
		file_paths = []
		while len(file_paths) == 0:
			print("Select files to analyze")
			print("This analyzer is configured according to the specifications of", self.dataobject.__name__)
			print("This specification accepts", self.dataobject.standard)
			file_paths = self.root.tk.splitlist(filedialog.askopenfilenames(title="Choose Files", filetypes=self.dataobject.filetypes))
			if len(file_paths) == 0:
				self.defaultQuitPrompt()
				print("Try again!")
		return file_paths

	def loadFile(self, filepath):
		loading = True
		print("Loading contents of the file at", filepath)
		data = self.dataobject(filepath)
		print("Dataset is named:", data.createName())
		while loading:
			channel = input("Enter the name of the EMG channel to be analyzed [Default: 'MASS']: ")
			if channel == "":
				channel = "MASS"
			score = input("Enter the name of the Score channel [Default: 'SCORE']: ")
			if score == "":
				score = "SCORE"
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
		rem_idx = []
		for i in tqdm(range(data.scoreLength+1)):
			if i < data.scoreLength and data.getScores(i) == self.parameters.REM:
				if rem_end - rem_start <= 0:
					rem_start = i
					rem_end = i
				rem_end += 1
			else:
				if rem_end - rem_start > 0:
					rem_start_time = floor(data.getTimes(rem_start) / data.resolution)+1
					rem_end_time = floor(data.getTimes(rem_end) / data.resolution)
					rem_idx.append([rem_start_time, rem_end_time])
					rem_start = rem_end
		num_rem = len(rem_idx)
		rem_idx = np.array(rem_idx)
		print("Found", num_rem, "REM episodes")
		return rem_idx	

	def determineThreshold(self, data, i, rem):
		print("Determining threshold for REM episode", i, "found at", rem)
		method = ''
		FIRST_SAMPLES = self.parameters.FIRST_TIME / (data.resolution * 1000)
		rem_data = data.getData(int(rem[0]), k=int(rem[1]))
		
		start = 0
		threshold_rem = 0
		sample_mean = np.mean(rem_data)
		sample_std = np.std(rem_data)
		sample_check = self.parameters.SAMPLE_MEAN*sample_mean + self.parameters.SAMPLE_STD*sample_std
		checks = {'thresholds':[], 'rem_means':[], 'rem_stds':[],
					'twitch_checks':[], 'twitch_ratios':[],
					'sample_means':np.mean(rem_data), 'sample_stds':np.std(rem_data),
					'sample_checks':sample_check,
					'sample_ratios':[]
				}
		
		while method == '':
			rem_end = int(round(start + FIRST_SAMPLES))
			rem_sample = rem_data[start:rem_end]
			threshold_rem = np.percentile(rem_sample, self.parameters.BASELINE_PERCENTILE)
			rem_mean = np.mean(rem_sample)
			rem_std = np.std(rem_sample)
			twitch_check = self.parameters.REM_MEAN*rem_mean + self.parameters.REM_STD*rem_std
			
			checks['thresholds'].append(threshold_rem)
			checks['rem_means'].append(rem_mean)
			checks['rem_stds'].append(rem_std)
			checks['twitch_checks'].append(twitch_check)
			checks['twitch_ratios'].append(twitch_check/threshold_rem)
			checks['sample_ratios'].append(sample_check/threshold_rem)
				
			if twitch_check / threshold_rem > self.parameters.TWITCH_THRESHOLD and sample_check / threshold_rem > self.parameters.SAMPLE_THRESHOLD:
				method = 'Window';
			else:		
				start = int(round(start + 0.5*FIRST_SAMPLES))
				if start + FIRST_SAMPLES > len(rem_data):
					threshold_rem = np.percentile(thresholds,self.parameters.SAMPLE_PERCENTILE)
					method = 'Percentile'
		print("Threshold for REM episode at", rem, "is set to", threshold_rem, "using the", method, "method")
		return method, threshold_rem, checks
		
	def filter(self, data, i, rem, threshold):
		print("Filtering REM episode", i, "at", rem, "with a threshold of", threshold)
		rem_data = data.getData(int(rem[0]), k=int(rem[1]))
		rem_indices = data.getIndices(int(rem[0]), k=int(rem[1]))
		filtered = []
		filtered_indices = []
		unfiltered = []
		unfiltered_indices = []
		for i in tqdm(range(len(rem_data))):
			if rem_data[i] > threshold:
				filtered.append(rem_data[i])
				filtered_indices.append(rem_indices[i])			
			else:
				unfiltered.append(rem_data[i])
				unfiltered_indices.append(rem_indices[i])
		filtered = np.array(filtered)
		filtered_indices = np.array(filtered_indices)
		unfiltered = np.array(unfiltered)
		unfiltered_indices = np.array(unfiltered_indices)
		print("Filtered!")
		return filtered, filtered_indices, unfiltered, unfiltered_indices
		
	def analyze(self, peaks, peaks_idx, i, rem, resolution):
		print("Analyzing for twitches")
		length = len(peaks)
		analysis = {'event_starts':[],'num_events':0,'avg_amp':[],'int_amp':[],
					'durations':[], 'time':length * resolution,
					'start':rem[0] * resolution, 'end':rem[1] * resolution,
					'event%':length/(rem[1]-rem[0]+1),'base%':1-length/(rem[1]-rem[0]+1)
					}
		if length > 0:
			MIN_INTERVAL = self.parameters.MIN_INTERVAL_TIME / (resolution * 1000)
			event = [peaks[0]]
			event_idx = [peaks_idx[0]]
			for i in tqdm(range(1, length+1)):
				if i < length and peaks_idx[i] - event_idx[-1] < MIN_INTERVAL:
					event.append(peaks[i])
					event_idx.append(peaks_idx[i])				
				else:
					analysis['event_starts'].append(event_idx[0] * resolution)
					analysis['num_events'] += 1
					analysis['avg_amp'].append(np.mean(event))
					analysis['int_amp'].append(np.sum(event))
					analysis['durations'].append(len(event) * resolution)
					if i < length:
						event = [peaks[i]]
						event_idx = [peaks_idx[i]]
		print("Twitches analyzed!")
		print("Found", analysis['num_events'], "twitches")
		return analysis
	
	def selectExportLocation(self, filepath):
		location = None
		while location is None:
			print("Select export location for dataset found at", filepath)
			location = filedialog.askdirectory(title="Choose Folder")
			if location is None or not os.path.isdir(location):
				location = None
				self.defaultQuitPrompt()
				print("Try again!")
		print("Analysis will be exported to", location)
		return location
	
	def export(self, location="", i="", analysis={}, method="", threshold_rem=-1, checks={}, below_avg=-1):
		if location == "" or i == "" or len(analysis) == 0 or method == "" or threshold_rem == -1 or len(checks) == 0 or below_avg == -1:
			raise TypeError("Not enough arguments to properly export data")
		print("Formatting REM episode", i, "for export to", location)
		events_header = np.array([['Event Start (s)','Avg Amplitude','Summation','Duration (s)']])
		events_data = np.stack((analysis['event_starts'], analysis['avg_amp'], analysis['int_amp'], analysis['durations']), axis=1)
		rem_stats = np.array([['Threshold','Number of Events','Avg Amplitude below Threshold'],
							[threshold_rem, analysis['num_events'], below_avg]])
		time = analysis['end'] - analysis['start']
		rem_duration = np.array([['Start Time (s)', analysis['start']],
								['End Time (s)', analysis['end']],
								['Total Duration (s)', time]])
		event_stats = np.array([['Event Percent', 'Event Time (s)'], [analysis['event%'], analysis['event%']*time],
								['Baseline Percent', 'Baseline Time (s)'], [analysis['base%'], analysis['base%']*time]])
		parameter_stats = np.array([['Threshold Percentile', 'Threshold Interval', 'Twich Mean Multiplier', 
								'Twitch SD Multiplier', 'Sample Mean Multiplier', 'Sample SD Multiplier',
								'Twitch Ratio', 'Sample Ratio', 'Sample Percentile', 'Minimum Interval Time'],
								[self.parameters.BASELINE_PERCENTILE, self.parameters.FIRST_TIME, self.parameters.REM_MEAN, 
								self.parameters.REM_STD, self.parameters.SAMPLE_MEAN, self.parameters.SAMPLE_STD, 
								self.parameters.TWITCH_THRESHOLD, self.parameters.SAMPLE_THRESHOLD, 
								self.parameters.SAMPLE_PERCENTILE, self.parameters.MIN_INTERVAL_TIME]])
		if method == "Window" or method == "Percentile":
			method_stats = np.array([['Method', method]])
			phase_header = np.array([['Phase Mean', 'Phase STD', 'Phase Check']])
			phase_stats = np.array([[checks['sample_means'], checks['sample_stds'], checks['sample_checks']]])
			checks_header = np.array([['Window Threshold', 'Window Mean', 'Window STD','Window Check',
										'Window Ratio','Phase Ratio']])
			checks_stats = np.stack((checks['thresholds'], checks['rem_means'], checks['rem_stds'], checks['twitch_checks'],
										checks['twitch_ratios'], checks['sample_ratios']), axis=1)
		else:
			raise RuntimeError("Something went wrong with the method type!")
		
		sheet_name = "REM " + i.split('/')[0]
		
		print("Exporting to", location)
		
		if not os.path.isfile(location):
			wb = Workbook()
		else:
			rb = open_workbook(location)
			if len(rb.sheet_names()) >= int(i.split('/')[0]):
				overwrite = ""
				while overwrite == "":
					print("This dataset has previously been analyzed")
					overwrite = input("Overwrite the .xls file? [y/n] ")
					if overwrite == "n":
						print("Choosing not to export and complete this analysis")
						return False
					elif overwrite == "y":
						print("Overwriting")
					else:
						print("Please either enter 'y' or 'n'")
						overwrite = ""
				os.remove(location)
				wb = Workbook()
			else:
				wb = copy(rb)
		
		ws = wb.add_sheet(sheet_name)
		
		for row in range(len(events_header)):
			for col in range(len(events_header[row])):
				ws.write(row, col, events_header[row][col])
		
		for row in range(1, 1+len(events_data)):
			for col in range(len(events_data[row-1])):
				ws.write(row, col, events_data[row-1][col])
		
		for row in range(len(rem_stats)):
			for col in range(5, 5+len(rem_stats[row])):
				ws.write(row, col, rem_stats[row][col-5])
		
		for row in range(len(rem_duration)):
			for col in range(8, 8+len(rem_duration[row])):
				ws.write(row, col, rem_duration[row][col-8])
		
		for row in range(len(event_stats)):
			for col in range(10, 10+len(event_stats[row])):
				ws.write(row, col, event_stats[row][col-10])
				
		for row in range(8, 8+len(method_stats)):
			for col in range(5, 5+len(method_stats[row-8])):
				ws.write(row, col, method_stats[row-8][col-5])
				
		for row in range(5, 5+len(parameter_stats)):
			for col in range(5, 5+len(parameter_stats[row-5])):
				ws.write(row, col, parameter_stats[row-5][col-5])
				
		for row in range(9, 9+len(phase_header)):
			for col in range(5, 5+len(phase_header[row-9])):
				ws.write(row, col, phase_header[row-9][col-5])
		
		for row in range(10, 10+len(phase_stats)):
			for col in range(5, 5+len(phase_stats[row-10])):
				ws.write(row, col, phase_stats[row-10][col-5])		
		
		for row in range(11, 11+len(checks_header)):
			for col in range(5, 5+len(checks_header[row-11])):
				ws.write(row, col, checks_header[row-11][col-5])
				
		for row in range(12, 12+len(checks_stats)):
			for col in range(5, 5+len(checks_stats[row-12])):
				ws.write(row, col, checks_stats[row-12][col-5])
				
		wb.save(location)
		print("Exported!")
		return True
		
	def xls2xlsx(self, location):
		excel = win32.gencache.EnsureDispatch('Excel.Application')
		wb = excel.Workbooks.Open(location)
		output_file = pathlib.Path('{}x'.format(location))
		wb.SaveAs(str(output_file), FileFormat = 51)    #FileFormat = 51 is for .xlsx extension
		wb.Close()                               		#FileFormat = 56 is for .xls extension
		excel.Application.Quit()
		os.remove(location)
	
	def run(self):
		print("-"*30)
		print("Running analysis as", str(self))
		print("Loading and validating self.parameters")
		try:
			self.parameters.validateParameters()
		except self.parameters.ParameterError as err:
			print("ParameterError:", err.parameter, ",", err.message)
			sys.exit()
		print("Successfully loaded self.parameters")
		print("-"*30)
		
		file_paths = self.selectFiles()
		
		for file in file_paths:
			data = self.loadFile(file)
			location = self.selectExportLocation(file) + '/' + data.name + '-analysis.xls'
			rem_idx = self.parseREM(data)
			for i in range(len(rem_idx)):
				episode = str(i+1) + "/" + str(len(rem_idx))
				method, threshold_rem, checks = self.determineThreshold(data, episode, rem_idx[i])
				peaks, peaks_idx, below, below_idx = self.filter(data, episode, rem_idx[i], threshold_rem)
				analysis = self.analyze(peaks, peaks_idx, episode, rem_idx[i], data.resolution)
				below_avg = np.mean(below)
				try:
					abort = self.export(location, episode, analysis, method, threshold_rem, checks, below_avg)
					if not abort:
						break
				except TypeError as err:
					print("TypeError:", err)
					sys.exit()
				except ValueError as err:
					print("ValueError:", err)
					sys.exit()
				except RuntimeError as err:
					print("RuntimeError:", err)
					sys.exit()
			print("Completed analyzing file at", file)
			print("Converting .xls file to .xlsx")
			self.xls2xlsx(location)
			print("-"*30)
		print("Completed all requested analyses")