# The smrEMG Data Import Type Standard

This is a Data Import Type Standard that uses .mat files in the format as exported
by Spike2 v7.

The underlying data structure of the dataset is as follows:
1. The data structure is a dictionary with key-value pairs
2. The overall file contains Channels, each named as [title]_Ch[X]
	1. This is found in the keys of the data structure, e.g. data[channel]
3. At least ONE channel contains the EMG data to be analyzed
	1. A "title" which contains the name of the channel
		1. This is found in data[channel][0][0][0][0]
		2. The default name that this Standard looks for is "MASS"
	2. A "resolution" of the channel recording, containing the time resolutionof the recording in seconds
		1. This is found in data[channel][0][0][2][0][0]
	3. A "length" of the channel recording, containing the number of samples
		1. This is found in data[channel][0][0][7][0][0]
	4. A "data-stream" of the channel recording, containing the actual samples
		1. This is found in data[channel][0][0][8]
4. At least ONE channel contains the State Classifications (Scores) of the recording
	1. A "title" which contains the name of the channel
		1. This is found in data[channel][0][0][0][0]
		2. The default name that this Standard looks for is "SCORE"
	2. A "times-stream" of the channel recording, containing the times each epoch starts in seconds
		1. This is found in data[channel][0][0][5]
	3. A "scores-stream" of the channel recording, containing the Scores
		1. This is found in data[channel][0][0][7]
		2. The term that corresponds to a REM sleep epoch must be the same in parameters.py
