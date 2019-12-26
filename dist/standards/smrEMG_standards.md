# The smrEMG Data Import Type Standard

This is a Data Import Type Standard that uses .mat files in the format as exported
by Spike2 v7.

The underlying data structure of the dataset is as follows:
	1. The data structure is a dictionary with key-value pairs
	2. The overall file contains Channels, each named as [title]_Ch[X]
		a. This is found in the keys of the data structure, e.g. data[channel]
	3. At least ONE channel contains the EMG data to be analyzed
		a. A "title" which contains the name of the channel
			i. This is found in data[channel][0][0][0][0]
			ii. The default name that this Standard looks for is "MASS"
		b. A "resolution" of the channel recording, containing the time resolutionof the recording in seconds
			i. This is found in data[channel][0][0][2][0][0]
		c. A "length" of the channel recording, containing the number of samples
			i. This is found in data[channel][0][0][7][0][0]
		d. A "data-stream" of the channel recording, containing the actual samples
			i. This is found in data[channel][0][0][8]
	4. At least ONE channel contains the State Classifications (Scores) of the recording
		a. A "title" which contains the name of the channel
			i. This is found in data[channel][0][0][0][0]
			ii. The default name that this Standard looks for is "SCORE"
		d. A "times-stream" of the channel recording, containing the times each epoch starts in seconds
			i. This is found in data[channel][0][0][5]
		e. A "scores-stream" of the channel recording, containing the Scores
			i. This is found in data[channel][0][0][7]
			ii. The term that corresponds to a REM sleep epoch must be the same in parameters.py