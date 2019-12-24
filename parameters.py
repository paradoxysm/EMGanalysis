#Do not change any parameter names

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