# EMG Analysis and Twitch Characterization
Application for mouse EMG analysis and REM sleep muscle characterization

# Table of Contents:

1. Description
2. Installation
3. How to Use
4. Methodology
5. Output File
6. Editing Parameters
7. Editing or Adding Plugins (Data Import Types)

# 1. Description

This program takes in a dataset file of sleep recordings and analyzes EMG data of each REM phase,
characterizing all twitches that occur in REM sleep.

The information is outputted into an .xlsx spreadsheet for subsequent analysis.
A Baseline vs Experiment analysis is included as a .xlsm file

# 2. Installation

1. Download the .zip folder and unzip it to location of choice
2. Launch EMGanalysis.exe file.

# 3. How to Use

Default Parameters are stored in the config file called "parameters.py". They may be edited to suit your needs. **DO NOT** move the file, change the file name or change the parameter names!

When you start up the application, it will open a command line interface. 
You will be asked to select a Data Import Type at the beginning of the program. 
A Data Import Type sets out the standards for reading data files. The underlying data structure is set forth 
by the standards found in the Standards folder. 
Just follow the instructions and enjoy!
It will prompt you to select the files to be analyzed. You may select one or multiple files in the same folder. Please refer to the file requirements specified by the data import type module you are choosing to use. These file standards may be found in the File Standards folder.

Once the file is successfully read in, the application will move to calculating all sleep phases and
characterizing twitches. Once the application displays that it has completed the file(s), you may open the .xls spreadsheets. Opening before the application is finished calculations will prevent it from continuing to write to the sheets and cause a fatal error. Once all files are completely analyzed, the application will close.

# 4. Methodology

When files have been selected for analysis, the application will sequentially analyze each file. Only when it has completed analysis for one file does the application move to the next file. When moving to the next file, if the program encounters an unsolvable error, as in bad file or missing channels, it will either prompt you for the correct solution or print a warning message and move to the next file without prompt.

For each file, the application does the following:
* Sets Resolution based upon the given resolution data found in the EMG channel information
* Indexes the entire dataset of EMG data for referencing of time
* Examines the Sleep Epochs information channel following REM Isolation Method (a)
* For each REM phase identified, deteremines threshold following Threshold Determination Method (b)
* Examines data for the particular REM phase, retaining only the data points that exceed the threshold
* Examines these "spikes" and groups them into "twitches"
* As it does so, it characterizes these twitches with duration, average amplitude and total activity (measured by the summation of EMG activity over the course of the twitch).
* Creates a summarization of data for the whole REM phase
* Exports data into a sheet in an xlsx document that follows <EMG file name>-analysis.xlsx and is located in the same folder as the EMG file

### (a) REM Isolation Method

To identify and isolate REM phases in the dataset, the application runs through the Sleep Epochs information channel (to simplify the amount of data it must iterate over). The application identifies groups of Epochs labeled 'R' and determines their corresponding start and end times. This allows the application to align the Epochs as accurately as possible to the correct set of EMG data points. Each REM Phase's corresponding EMG data points are stored in their own arrays.

### (b) Threshold Determination Method

The application preferentially uses the "window" method; failing to succeed in determining a reasonable threshold, the application will then use the "percentile" method.

**"Window" Method:**
The application takes the first FIRST_TIME ms of the REM "phase" as the "window". The default is 1500ms. It finds the BASELINE_PERCENTILE-th percentile of this "window" and sets this as the "potential threshold". The default is the 99.99th percentile. To maximize chances that this "potential threshold" is a "good" threshold to use, the application	makes two comparisons:
  i. To check if the "potential threshold" is not a "twitch" compared to the rest of the window,
    (MEAN*[mean of "window"]+REM_STD*[std of "window"])/["potential threshold"]
    must be greater than TWITCH_THRESHOLD.
    The default is ([mean of "window"]+2*[std of "window"])/["potential threshold"]
    must be greater than 0.475.
  ii. To check if the "window" is not at an elevated signal level in comparison to the rest of the 
    phase (e.g. the "window" contains enough twitches that (i) still passes),
    (MEAN*[mean of "phase"]+SAMPLE_STD*[std of "phase"])/["potential threshold"]
    must be greater than SAMPLE_THRESHOLD.
    The default is ([mean of "phase"]+2*[std of "phase"])/["potential threshold"]
    must be greater than 0.475.
If either of these conditions fail, the "potential threshold" is deemed not an ideal threshold to use. The application then moves the "window" half of FIRST_TIME ms forward. The default is to move the window 750ms forward. This is to give the "windows" overlap to allow a higher maximum number of calculations and reuse potentially good data points for threshold calculations. If both conditions pass, the application proceeds to twitch characterization using the current "potential threshold" as the threshold value.

If the application runs through the entire "phase" without finding an ideal threshold to use that passes both
conditions, the application resorts to the "Percentile" method.

**"Percentile" Method:**
As the application examines each "window", if the "window" fails to pass, the "potential threshold" is stored
in a list. When the program resorts to this method, it takes the SAMPLE_PERCENTILE-th percentile of these failed "thresholds"
to set as the final threshold value. The default is to take the 50th percentile.

# 5. Output File

The application exports all data into a xlsx spreadsheet named <EMG file name>-output.xlsx in the same location as the
EMG file.

It is formatted as the following:
* Each sheet corresponds to one REM phase, titled and in the order they occur in the dataset
* In each sheet:
	* The full list of twitches is found with the start time (in seconds, where the first datapoint in the set is 0s)
	* The Threshold as determined by the Threshold Determination Method
	* The Number of Twitches
	* The Start and End time of the REM phase, as well as the duration of the phase in seconds (once again, the start and end times are based on where the first datapoint in the set is 0s)
	* The Percentage and Amount of Time (s) that twitches and atonia account for the REM phase
	* The Method the application used for the Threshold Determination Method (Either "window" or "percentile")
	* The Parameters used for the file
	* The full list of calculations used in the "window" method for threshold determination for transparency/debugging	

# 6. Editing Parameters

The Parameters that can be customized are located in "parameters.config" which MUST be located in the same folder as this application's executable and CANNOT be renamed to anything other than "parameters.config". You can open and edit the config file in any word processing file (notepad is simplest) This is the only location in which these parameters may be edited. Once the application is launched, for as long as the application is running continuously, it will use the parameters as they were when the application was started. If the parameters are subsequently changed, they do not take effect until you restart the application.

It is IMPORTANT that the parameter names are not changed!

# 7. Adding or Editing Plugins (Data Import Types)

Data Import Types are accepted file types and associated file reading methods for analysis. They can be found in
the plugins folder. It is IMPORTANT that this folder is not moved!

Plugins are dynamically loaded at the time of application launch. They follow the structure 
set out by the DataObject abstract base class. The DataObject abstract class is NOT a properly 
usable Data Import Type; rather, it is the superclass that defines how all Data Import Types should 
behave. This allows the application to be independent of Data Import Types.

Data Import Types must be named the same in the file name as well as the class name, otherwise the 
plugin loader will experience a fatal import error.


<sub>
Peever Lab, 
Jeffrey Wang
</sub>
