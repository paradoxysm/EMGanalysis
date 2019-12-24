#DO NOT change any parameter names

#Percentile to take for setting "threshold" of given window: Between 0 and 100, inclusive
BASELINE_PERCENTILE = 99.99

#Size of window (in ms) to calculate "threshold": Must be an integer greater than 0
FIRST_TIME = 1500

#Multiplier of mean of the window for calculation: Must be a non-negative number
REM_MEAN = 1

#Multiplier of mean of the sleep phase for calculation: Must be a non-negative number
SAMPLE_MEAN = 1

#Multiplier of Standard Deviations of the window: Must be a non-negative number
REM_STD = 2

#Multiplier of Standard Deviations of the sleep phase: Must be a non-negative number
SAMPLE_STD = 2

#Minimum Ratio between window check and "threshold": Must be a non-negative number
TWITCH_THRESHOLD = 0.475

#Minimum Ratio between phase check and "threshold": Must be a non-negative number
SAMPLE_THRESHOLD = 0.475

#Failing the window method, percentile of all "thresholds" to set as threshold: Must be between 0 and 1, inclusive
SAMPLE_PERCENTILE = 0.5

#Minimim time (in ms) between spikes to be registered as separate twitches: Must be a non-negative integer
MIN_INTERVAL_TIME = 20


#Validation Function
#DO NOT edit

class ParameterError(Exception):
	def __init__(self, parameter, message):
		self.parameter = parameter
		self.message = message
		

def validateParameters():
	if  not (isinstance(BASELINE_PERCENTILE, float) or isinstance(BASELINE_PERCENTILE, int)) or \
			BASELINE_PERCENTILE < 0 or BASELINE_PERCENTILE > 100:
		raise ParameterError("BASELINE_PERCENTILE","Must be between 0 and 100, inclusive")
	if  not isinstance(FIRST_TIME, int) or FIRST_TIME <= 0:
		raise ParameterError("FIRST_TIME","Must be a positive, non-zero integer")
	if  not (isinstance(REM_MEAN, float) or isinstance(REM_MEAN, int)) or REM_MEAN < 0:
		raise ParameterError("REM_MEAN","Must be a non-negative number")
	if not (isinstance(SAMPLE_MEAN, float) or isinstance(SAMPLE_MEAN, int)) or SAMPLE_MEAN < 0:
		raise ParameterError("SAMPLE_MEAN","Must be a non-negative number")
	if not (isinstance(REM_STD, float) or isinstance(REM_STD, int)) or REM_STD < 0:
		raise ParameterError("REM_STD","Must be a non-negative number")
	if not (isinstance(SAMPLE_STD, float) or isinstance(SAMPLE_STD, int)) or SAMPLE_STD < 0:
		raise ParameterError("SAMPLE_STD","Must be a non-negative number")
	if not (isinstance(TWITCH_THRESHOLD, float) or isinstance(TWITCH_THRESHOLD, int)) or TWITCH_THRESHOLD < 0:	
		raise ParameterError("TWITCH_THRESHOLD","Must be a non-negative number")
	if not (isinstance(SAMPLE_THRESHOLD, float) or isinstance(SAMPLE_THRESHOLD, int)) or SAMPLE_THRESHOLD < 0:	
		raise ParameterError("SAMPLE_THRESHOLD","Must be a non-negative number")
	if not (isinstance(SAMPLE_PERCENTILE, float) or isinstance(SAMPLE_PERCENTILE, int)) or \
			SAMPLE_PERCENTILE < 0 or SAMPLE_PERCENTILE > 1:	
		raise ParameterError("SAMPLE_PERCENTILE","Must be between 0 and 1, inclusive")
	if not isinstance(MIN_INTERVAL_TIME, int) or SAMPLE_PERCENTILE < 0:	
		raise ParameterError("MIN_INTERVAL_TIME","Must be a non-negative integer")
	return True