# EMG Analysis and Twitch Characterization
MATLAB application for mouse EMG analysis and REM sleep muscle characterization

# Table of Contents:

1. Description
2. Installation
3. How to Use
4. Methodology
5. Output File
6. Editing Parameters
7. Release Log

# 1. Description

This program takes in a .mat file of sleep recordings and analyzes EMG data of each REM phase,
characterizing all twitches that occur in REM sleep.

The information is outputted into an xlsx spreadsheet for subsequent analysis.

# 2. Installation

1. Launch application installer.
2. Follow instructions; it may ask to download and install MATLAB runtime for you if you do not have it already
3. Launch EMGanalysis.exe file.

# 3. How to Use

Default Parameters are stored in the config file called "parameters.config". They may be edited to suit your needs. Do not move the file, change the file name or change the parameter names.

When you start up the application, it will open a command window. It will prompt you to select the files to be analyzed. You may select one or multiple files in the same
folder. 

The requirements of the files are:
	a. Must be a .mat file
	b. Must contain ONE channel in which the "comment" of the channel contains "AW|QW|NR|R|" in an unbroken string
		i. This channel must contain a field called "text" which contains the level of consciousness scoring
			that uses 'R' for REM sleep
		ii. This channel must contain a field called "times" which contains the times in seconds that corresponds
			to the intervals of each Epoch
	c. Must contain ONE channel in which the "title" of the channel contains "mass" in any case
		i. This channel must contain a field called "values" which contains the EMG data
		ii. This channel must contain a field called "interval" which contains the resolution in seconds of the data
    
If (b) and/or (c) are not met, the application will prompt you to input the correct "comment" for the Sleep Epochs
and the corrent "title" for the EMG channel. If the sub-requirements of (b) and/or (c), the application will prompt you for the correct field names. In either situation, you may enter q to quit. Consequently, don't go about naming your channels and fields 'q'! Cancelling the selection of files will prompt you to select again or quit, which you can do by entering 'q' and pressing enter.

Once the file is successfully read in, the application will move to calculating all sleep phases and
characterizing twitches. Once the application displays that it has completed the file(s), you may open the xlsx spreadsheets. Opening before the application is finished calculations will prevent it from continuing to write to the sheets and cause a fatal error. Once all files are completely analyzed, you may have the application analyze more or enter 'q' to quit.

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
* Exports data into a sheet in an xlsx document that follows <EMG file name>-output.xlsx and is located in the same folder as the EMG file

### (a) REM Isolation Method

To identify and isolate REM phases in the dataset, the application runs through the Sleep Epochs information channel (to simplify the amount of data it must iterate over).	The application identifies groups of Epochs labeled 'R' and determines their corresponding start and end times. This allows the application to align the Epochs as accurately as possible to the correct set of EMG data points. Each REM Phase's corresponding EMG data points are stored in their own arrays.

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
* Each sheet corresponds to one REM phase, in the order they occur in the dataset
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

It is IMPORTANT that the parameter names are not changed and that there is always EXACTLY 1 space before and after the =
for each parameter!

# 7. Release Log

v0.8.0: May 13, 2019
   - Implemented characterization choice between neck, masseter or all

v0.7.0: February 8, 2019
 - Implemented calculation and display of twitch activity, measured as the summation of EMG activity in a twitch
 - Hotfix for phases with zero twitches

v0.6.0: August 9, 2018
 - Fixed variable name bug for improper stage times variable name
 - Improved algorithm for average amplitude BELOW threshold

v0.5.92: July 30, 2018
 - Add output of average amplitude for all data BELOW threshold for each REM phase

v0.5.91: July 26, 2018
 - Hotfix for values dataset from columns to rows

v0.5.9: July 20, 2018
 - Properly implemented channel and field name checking
 - Updated application icon

v0.5.8: July 14, 2018
 - Config file implemented, removing parameter input from application startup
 - Fixed semantic errors in FIRST_TIME parameter limitations
 - Renamed PERCENTILE to BASELINE_PERCENTILE to distinguish from SAMPLE_PERCENTILE
 - Prevent fatal error when channels do not have default field names; instead, prompts user input to correct
 - Prevent fatal error when REM phase has no "spikes", counting for 0 twitches
 - Writes full threshold determination calculations to each REM phase sheet for transparency/debugging
 - Included this handy-dandy README file!

================================

Peever Lab, 2019
Jeffrey Wang
