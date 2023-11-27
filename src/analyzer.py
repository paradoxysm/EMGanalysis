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


# Analyzer: Executes all the necessary analysis and user interactions for an EMG analysis
class Analyzer:
	# Construct an Analyzer with the Data Import Type as dataobject and import parameters
	def __init__(self, dataobject):
		self.dataobject = dataobject
		self.parameters = import_module('parameters')

		# Set up tkinter to allow for file selection dialog windows
		self.root = tk.Tk()
		self.root.withdraw()

	# Identification of Data Import Type assigned to this Analyzer
	def __str__(self):
		return type(self).__name__ + ": " + self.dataobject.__name__

	# Loop to prompt quitting or remaining on application
	def defaultQuitPrompt(self):
		user = ""
		while user != "n":
			user = input("Selected nothing, do you wish to quit? [y/n] ")
			if user == 'y':
				print("Goodbye!")
				sys.exit()
			elif user != 'n':
				print("Please either enter 'y' or 'n'")

	# Select all files to be analyzed
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

	# Load the contents of the data file according to the Data Import Type specifications
	def loadFile(self, filepath):
		loading = True
		print("Loading contents of the file at", filepath)
		# Create a DataObject
		data = self.dataobject(filepath)
		print("Dataset is named:", data.createName())

		# Identify the necessary data channels
		while loading:
			channel = input("Enter the name of the EMG channel to be analyzed [Default: 'MASS']: ")
			if channel == "":
				channel = "MASS"
			score = input("Enter the name of the Score channel [Default: 'SCORE']: ")
			if score == "":
				score = "SCORE"
			# Attempt to read the data channels
			try:
				data.read(c=channel, s=score)
				loading = False
			# An error occurred in finding the file or extracting data from the file
			except FileNotFoundError as err:
				print("FileNotFoundError:", err)
			# Running a DataObject that does not have its read function implemented
			except NotImplementedError as err:
				print("NotImplementedError:", err)
			# Some other unexpected error
			except Exception:
				print("Something unexpected went wrong! Let's try again")
			if loading:
				self.defaultQuitPrompt()
				print("Try again!")
		return data

	# Parse the score data to identify REM sleep episodes and return a list of such intervals
	def parseREM(self, data):
		print("Parsing through dataset")
		print("Found", data.length, "samples and", data.scoreLength, "epochs")
		rem_start = 0
		rem_end = 0
		rem_idx = []
		for i in tqdm(range(data.scoreLength)):
			# If the epoch is classified as REM, set up the REM sleep interval
			# 	and expand it as the REM sleep episode continues
			if data.getScores(i) == self.parameters.REM:
				if rem_end - rem_start <= 0 :
					rem_start = i
					rem_end = i
				rem_end += 1
            # If the REM episode ends or at the end of the recording, calculate the sample indices for
			#	the REM sleep interval
			if (data.getScores(i) != self.parameters.REM or i == data.scoreLength-1) and rem_end - rem_start > 0 :
				rem_start_time = floor(data.getTimes(rem_start) / data.resolution)+1
				rem_end_time = floor(data.getTimes(rem_end) / data.resolution)
				rem_idx.append([rem_start_time, rem_end_time])
				rem_start = rem_end
		num_rem = len(rem_idx)
		# Convert to a numpy array
		rem_idx = np.array(rem_idx)
		print("Found", num_rem, "REM episodes")
		return rem_idx

	# Parse through a REM sleep episode (as determined by a REM sleep interval)
	#	and determine the threshold for twitches
	def determineThreshold(self, data, i, rem):
		print("Determining threshold for REM episode", i, "found at", rem)
		method = ''
		# Set up the Window
		FIRST_SAMPLES = self.parameters.FIRST_TIME / (data.resolution * 1000)
		# Grab the EMG data for the REM sleep interval
		rem_data = data.getData(int(rem[0]), k=int(rem[1]))

		# Setup variables
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

		# Attempt to find an appropriate threshold via the Window method
		#	Failing to do so at the end, resort to Percentile method
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

			# Suitable threshold determined
			if twitch_check / threshold_rem > self.parameters.TWITCH_THRESHOLD and sample_check / threshold_rem > self.parameters.SAMPLE_THRESHOLD:
				method = 'Window';
			else:
				# Move window a half-length forward
				start = int(round(start + 0.5*FIRST_SAMPLES))
				# Reaching the end of the REM sleep episode without a satisfactory threshold
				#	thus resorting to the Percentile method
				if start + FIRST_SAMPLES > len(rem_data):
					threshold_rem = np.percentile(checks['thresholds'],self.parameters.SAMPLE_PERCENTILE)
					method = 'Percentile'
		print("Threshold for REM episode at", rem, "is set to", threshold_rem, "using the", method, "method")
		return method, threshold_rem, checks

	# Filter EMG data based on the threshold to return filtered data and unfiltered data
	#	Includes corresponding indices
	def filter(self, data, i, rem, threshold):
		print("Filtering REM episode", i, "at", rem, "with a threshold of", threshold)
		# Grab the EMG data and the indices for the REM sleep interval
		rem_data = data.getData(int(rem[0]), k=int(rem[1]))
		rem_indices = data.getIndices(int(rem[0]), k=int(rem[1]))

		#Setup variables
		filtered = []
		filtered_indices = []
		unfiltered = []
		unfiltered_indices = []

		# Filter the data
		for i in tqdm(range(len(rem_data))):
			if rem_data[i] > threshold:
				filtered.append(rem_data[i])
				filtered_indices.append(rem_indices[i])
			else:
				unfiltered.append(rem_data[i])
				unfiltered_indices.append(rem_indices[i])

		# Convert arrays to numpy arrays
		filtered = np.array(filtered)
		filtered_indices = np.array(filtered_indices)
		unfiltered = np.array(unfiltered)
		unfiltered_indices = np.array(unfiltered_indices)
		print("Filtered!")
		return filtered, filtered_indices, unfiltered, unfiltered_indices

	# Analyze filtered data for a REM sleep episode to characterize twitches
	def analyze(self, peaks, peaks_idx, i, rem, resolution):
		print("Analyzing for twitches")
		#Set up variables
		length = len(peaks)
		analysis = {'event_starts':[],'num_events':0,'avg_amp':[],'int_amp':[],
					'durations':[], 'time':length * resolution,
					'start':rem[0] * resolution, 'end':rem[1] * resolution,
					'event%':length/(rem[1]-rem[0]+1),'base%':1-length/(rem[1]-rem[0]+1)
					}
		# Only run if there are actually twitches
		if length > 0:
			# Set up the twitch interval
			MIN_INTERVAL = self.parameters.MIN_INTERVAL_TIME / (resolution * 1000)
			MIN_DURATION = self.parameters.MIN_TWITCH_DURATION / (resolution * 1000)

			# Set up variables for a single twitch event
			event = [peaks[0]]
			event_idx = [peaks_idx[0]]

			# Iterate through all filtered data and identify twitch events
			for i in tqdm(range(1, length+1)):
				# A twitch has been found belonging to the current twitch event
				if i < length and peaks_idx[i] - event_idx[-1] < MIN_INTERVAL:
					event.append(peaks[i])
					event_idx.append(peaks_idx[i])
				# A twitch event has been found to completion (i.e. the
				#	currently examined twitch belongs to the next event
				else:
					# The twitch event meets the minimum duration criteria
					if event_idx[-1] - event_idx[0] >= MIN_DURATION:
						analysis['event_starts'].append(event_idx[0] * resolution)
						analysis['num_events'] += 1
						analysis['avg_amp'].append(np.mean(event))
						analysis['int_amp'].append(np.sum(event))
						analysis['durations'].append((event_idx[-1] - event_idx[0]) * resolution)
					if i < length:
						event = [peaks[i]]
						event_idx = [peaks_idx[i]]
		print("Twitches analyzed!")
		print("Found", analysis['num_events'], "twitches")
		return analysis

	# Select the export folder location
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

	# Format all analysis results and write to an .xls temporary file
	#	Each sheet represents a single REM sleep episode
	def export(self, location="", i="", analysis={}, method="", threshold_rem=-1, checks={}, below_avg=-1):
		# Ensure that all arguments are set up
		if location == "" or i == "" or len(analysis) == 0 or method == "" or threshold_rem == -1 or len(checks) == 0 or below_avg == -1:
			raise TypeError("Not enough arguments to properly export data")

		# Format all the analysis results
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

		# Check if the file exists already (Analysis was done previously or is currently ongoing)
		if not os.path.isfile(location):
			wb = Workbook()
		else:
			rb = open_workbook(location)
			# If the analysis was done previously, ask if it should be overwritten
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
				# Delete the old file if it should be overwritten and create a new one
				os.remove(location)
				wb = Workbook()
			else:
				wb = copy(rb)

		# Add a sheet for the REM sleep episode
		ws = wb.add_sheet(sheet_name)

		# Write all the data into the sheet
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

	# Convert an xls file to an xlsx file
	#	Used at the end of analysis to allow compatibility with the xlsm Analysis Macro
	def xls2xlsx(self, location):
		excel = win32.gencache.EnsureDispatch('Excel.Application')
		wb = excel.Workbooks.Open(location)
		output_file = pathlib.Path('{}x'.format(location))
		wb.SaveAs(str(output_file), FileFormat = 51)    #FileFormat = 51 is for .xlsx extension
		wb.Close()                               		#FileFormat = 56 is for .xls extension
		excel.Application.Quit()
		os.remove(location)

	# Run the Analyzer
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
				except Exception as err:
					print("RuntimeError:", err)
					sys.exit()
			print("Completed analyzing file at", file)
			if len(rem_idx) > 0:
				print("Converting .xls file to .xlsx")
				self.xls2xlsx(location)
			print("-"*30)
		print("Completed all requested analyses")
