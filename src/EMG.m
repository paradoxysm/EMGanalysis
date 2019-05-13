disp('Initializing...');
disp('Configuring parameters...');
disp('When prompted, you can enter "q" to exit application.');
try
    parameters = fopen('parameters.config');
catch
    warning('Could not find parameters.config');
    warning('Ensure that parameters.config is located in the same folder this application is located');
    while true
        user = input('Enter "q" to acknowledge and exit','s');
        if strcmp(user,'q')
            return;
        else
            warning('Not a valid input');
        end
    end
end
% Read all lines & collect in cell array
txt = textscan(parameters,'%s','delimiter','\n'); 
txt = txt{1,1};
num_lines = numel(txt);
parameters = 1;
for line = 1:num_lines
    txt_line = char(txt{line,1});
    if ~isempty(strfind(txt_line,'BASELINE_PERCENTILE = '))
        split = strsplit(txt_line,' = ');
        BASELINE_PERCENTILE = str2double(split(1,2));
        if BASELINE_PERCENTILE < 0 || BASELINE_PERCENTILE > 100
            warning('BASELINE_PERCENTILE must be a number between 0 and 100');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'FIRST_TIME = '))
        split = strsplit(txt_line,' = ');
        FIRST_TIME = str2double(split(1,2));
        if FIRST_TIME <= 0 || (~mod(FIRST_TIME,1) == 0)
            warning('FIRST_TIME must be a positive integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'REM_MEAN = '))
        split = strsplit(txt_line,' = ');
        REM_MEAN = str2double(split(1,2));
        if REM_MEAN < 0
            warning('REM_MEAN must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'SAMPLE_MEAN = '))
        split = strsplit(txt_line,' = ');
        SAMPLE_MEAN = str2double(split(1,2));
        if SAMPLE_MEAN < 0
            warning('SAMPLE_MEAN must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'REM_STD = '))
        split = strsplit(txt_line,' = ');
        REM_STD = str2double(split(1,2));
        if REM_STD < 0
            warning('REM_STD must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'SAMPLE_STD = '))
        split = strsplit(txt_line,' = ');
        SAMPLE_STD = str2double(split(1,2));
        if SAMPLE_STD < 0
            warning('SAMPLE_STD must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'TWITCH_THRESHOLD = '))
        split = strsplit(txt_line,' = ');
        TWITCH_THRESHOLD = str2double(split(1,2));
        if TWITCH_THRESHOLD < 0
            warning('TWITCH_THRESHOLD must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'SAMPLE_THRESHOLD = '))
        split = strsplit(txt_line,' = ');
        SAMPLE_THRESHOLD = str2double(split(1,2));
        if SAMPLE_THRESHOLD < 0
            warning('SAMPLE_THRESHOLD must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'SAMPLE_PERCENTILE = '))
        split = strsplit(txt_line,' = ');
        SAMPLE_PERCENTILE = str2double(split(1,2));
        if SAMPLE_PERCENTILE < 0 || SAMPLE_PERCENTILE > 1
            warning('SAMPLE_PERCENTILE must be a non-negative integer');
            parameters = 0;
            break;
        end
    elseif ~isempty(strfind(txt_line,'MIN_INTERVAL_TIME = '))
        split = strsplit(txt_line,' = ');
        MIN_INTERVAL_TIME = str2double(split(1,2));
        if MIN_INTERVAL_TIME < 0
            warning('MIN_INTERVAL_TIME must be a non-negative integer');
            parameters = 0;
            break;
        end
    end
end

if parameters == 0
    warning('Please correct parameters.config and restart')
    while true
        user = input('Enter "q" to acknowledge and exit','s');
        if strcmp(user,'q')
            return;
        else
            warning('Not a valid input');
        end
    end
end

disp('Wrapping up parameters...');

%Load files in

repeat_input = 1;

while repeat_input
    user = input('Press Enter to load files or press "q" to quit','s');
    if ~isempty(user)
        if strcmp(user,'q')
            repeat_input = 0;
            return;
        else
            warning('Invalid input');
        end
    else
        [files, path] = uigetfile('MultiSelect','on');
        %If user cancels, exit program
        if isnumeric(files)
            warning('No file selected');
        else
            invalid = 0;
            files = cellstr(files);
            num_files = numel(files);
            for f = 1:num_files
                file = files(1,f);
                if isempty(strfind(file, '.mat'))
                    warning(['Invalid file selected: ',file]);
                    invalid = 1;
                    break;
                end
            end
            if invalid==0
                disp('Selected files. Analyzing...');
                for f = 1:num_files
                    file = files(1,f);
                    disp(['Loading file: ',char(file)]);
                    try
                        full_file_path = char(fullfile(path, file));
                        %full_file_path = cell2str(full_file_path(1,1));
                        EMGdata = load(full_file_path);
                        
                        data_valid = 0;
                        while true
                            user = input('Choose which muscle to examine or press "q" to exit ("m": mass; "n": neck)','s');
                            if strcmp(user,'q')
                                return;
                            elseif strcmp(user,'m')
                                EMG_name = 'mass';
                                break;
                            elseif strcmp(user,'n')
                                EMG_name = 'neck';
                                break;
                            else
                                warning('Not a valid input');
                            end
                        end
                        STAGE_name = 'AW|QW|NR|R|';
                        
                        while data_valid == 0
                            %Extract EMG table and Sleep Stage table
                            EMGChannels = fieldnames(EMGdata);
                            EMGChannel = {};
                            STAGEChannel = {};

                            EMG_unique = 1;
                           
                            for c = 1:numel(EMGChannels)
                                channel = EMGdata.(EMGChannels{c});

                                if ~isempty(strfind(lower(channel.title),EMG_name))
                                    EMG_unique = ~EMG_unique;
                                    EMGChannel = channel;
                                elseif ~isempty(strfind(channel.comment,STAGE_name))
                                    STAGEChannel = channel;
                                end
                            end
                            data_valid = 1;
                            if EMG_unique == 1 && ~isempty(EMGChannel)
                                warning('There can only be one EMG channel in the file');
                                data_valid = 0;
                            end
                            if isempty(EMGChannel)
                                warning(['Different naming or incorrect format of file ',full_file_path]);
                                data_valid = 0;
                                user = input(['Enter name of EMG channel title',...
                                    ' or enter "q" to quit. ',...
                                    'Default is ',EMG_name],'s');
                                if strcmp(user,'q')
                                    data_valid = 1;
                                    return;
                                elseif ~isempty(user)
                                    EMG_name = user;
                                end
                            elseif isempty(STAGEChannel)
                                warning(['Different naming or incorrect format of file ',full_file_path]);
                                data_valid = 0;
                                user = input(['Enter name of Sleep stage channel comment',...
                                    ' or enter "q" to quit. ',...
                                    'Default is ',STAGE_name],'s');
                                if strcmp(user,'q')
                                    data_valid = 1;
                                    return;
                                elseif ~isempty(user)
                                   	STAGE_name = user;
                                end
                            end
                        end
                        data_valid = 0;
                        values_name = 'values';
                        resolution_name = 'interval';
                        while data_valid == 0
                            %EMG Data
                            try 
                                values = extractfield(EMGChannel, values_name).';
                                data_valid = 1;
                            catch
                                warning('Different naming or incorrect format of field');
                                data_valid = 0;
                                user = input(['Enter data values field name',...
                                    ' or enter "q" to quit. ',...
                                    'Default is ',values_name],'s');
                                if strcmp(user,'q')
                                    data_valid = 1;
                                    return;
                                elseif ~isempty(user)
                                   	values_name = user;
                                    continue;
                                end
                            end
                            %Resolution of data in seconds
                            try
                                RESOLUTION = extractfield(EMGChannel, resolution_name);
                                data_valid = 1;
                            catch
                                warning('Different naming or incorrect format of field');
                                data_valid = 0;
                                user = input(['Enter resolution field name',...
                                    ' or enter "q" to quit. ',...
                                    'Default is ',values_name],'s');
                                if strcmp(user,'q')
                                    data_valid = 1;
                                    return;
                                elseif ~isempty(user)
                                   	resolution_name = user;
                                    continue;
                                end
                            end
                        end
                    catch
                        warning(['Failed to load file ',full_file_path]);
                        continue;
                    end

                    disp('Successfully loaded file. Extracting data...');              

                    %Number of samples for setting baseline threshold
                    FIRST_SAMPLES = FIRST_TIME / (RESOLUTION * 1000);

                    %Minimum interval of samples based on MIN_INTERVAL_TIME and RESOLUTION
                    MIN_INTERVAL = MIN_INTERVAL_TIME / (RESOLUTION * 1000);

                    %Get Sleep Stage Channel fields
                    data_valid = 0;
                    stages_name = 'text';
                    times_name = 'times';
                    while data_valid == 0
                        %Sleep stage values
                        try 
                            stages = extractfield(STAGEChannel, stages_name);
                            stages = cellstr(stages{1,1});
                            data_valid = 1;
                        catch
                            warning('Different naming or incorrect format of field');
                            data_valid = 0;
                            user = input(['Enter stage Epoch field name',...
                                ' or enter "q" to quit. ',...
                                'Default is ',stages_name],'s');
                            if strcmp(user,'q')
                                data_valid = 1;
                                return;
                            elseif ~isempty(user)
                                stages_name = user;
                                continue;
                            end
                        end
                        %Sleep stage time intervals
                        try
                            times = extractfield(STAGEChannel, times_name).';
                            data_valid = 1;
                        catch
                            warning('Different naming or incorrect format of field');
                            data_valid = 0;
                            user = input(['Enter times field name',...
                                ' or enter "q" to quit. ',...
                                'Default is ',times_name],'s');
                            if strcmp(user,'q')
                                data_valid = 1;
                                return;
                            elseif ~isempty(user)
                                times_name = user;
                                continue;
                            end
                        end
                    end
                    
                    %List of all indices of EMG values
                    idx = find(values>=0);
                    %2D List with indices and corresponding values
                    values_idx = [num2cell(idx), num2cell(values)];

                    %Number of samples in values_idx
                    length_values = numel(values);

                    %Number of stages marked
                    num_stages = numel(stages);

                    disp(['Found ', num2str(length_values), ' samples.']);
                    disp(['Found ', num2str(num_stages), '. Starting parsing...']);
                    disp('Selecting REM stage samples...');

                    %Iterate over all samples to organize REM events
                    rem_phase_start = 0;
                    rem_phase_end = 0;
                    rem_idx = {};
                    for i = 1:num_stages
                        disp(cell2mat(stages(i)));
                        if strcmp(cell2mat(stages(i)),'R')
                            if rem_phase_end - rem_phase_start <= 0
                                rem_phase_start = i-1;
                                rem_phase_end = i-1;
                            end
                            rem_phase_end = rem_phase_end + 1;
                        else
                            if rem_phase_end - rem_phase_start > 0
                                %Index by times
                                rem_start_time = times(rem_phase_start+1,1);
                                rem_end_time = times(rem_phase_end+1,1);
                                stage_start_time = rem_start_time / RESOLUTION;
                                stage_end_time = rem_end_time / RESOLUTION;
                                                               
                                values_start = floor(stage_start_time)+1;
                                values_end = floor(stage_end_time);
                                rem_idx = [rem_idx ; {values_idx(values_start:values_end,:)}];
                                rem_phase_start = rem_phase_end;
                            end
                        end
                        %Display progress
                        disp([num2str(i), ' of ',num2str(num_stages)]);
                    end
                    %Check the last set of states
                    if rem_phase_end - rem_phase_start > 0
                        rem_start_time = times(rem_phase_start+1,1);
                        rem_end_time = times(rem_phase_end,1);
                        stage_start_time = rem_start_time / RESOLUTION;
                        stage_end_time = rem_end_time / RESOLUTION;

                        values_start = floor(stage_start_time)+1;
                        values_end = floor(stage_end_time);
                        rem_idx = [rem_idx ; {values_idx(values_start:values_end,:)}];
                    end

                    %Calculate number of REM Phases found
                    num_rem = size(rem_idx);
                    num_rem = num_rem(1);

                    disp(['Found ', num2str(num_rem), ' REM phases']);

                    %Iterate over each REM phase
                    for i = 1:num_rem
                        disp(['Processing REM Phase ',num2str(i), '...']);
                        %Isolate REM phase
                        samples_rem = rem_idx{i,1};

                        %Define baseline threshold
                        start = 1;
                        thresholds = {};
                        rem_means = {};
                        rem_stds = {};
                        twitch_checks = {};
                        twitch_ratios = {};
                        sample_means = {};
                        sample_stds = {};
                        sample_checks = {};
                        sample_ratios = {};
                        method = '';
                        while true
                            rem_end = round(start+FIRST_SAMPLES);
                            rem_sample = cell2mat(samples_rem(start:rem_end,2)); 
                            threshold_rem = prctile(rem_sample,BASELINE_PERCENTILE);
                            
                            rem_mean = mean(rem_sample);
                            rem_std = std(rem_sample);
                            twitch_check = REM_MEAN*rem_mean + REM_STD*rem_std;
                            sample_mean = mean(cell2mat(samples_rem(:,2)));
                            sample_std = std(cell2mat(samples_rem(:,2)));
                            sample_check = SAMPLE_MEAN*sample_mean + SAMPLE_STD*sample_std;
                            
                            if twitch_check / threshold_rem > TWITCH_THRESHOLD && sample_check / threshold_rem > SAMPLE_THRESHOLD
                                thresholds = [thresholds; threshold_rem];
                                rem_means = [rem_means; rem_mean];
                                rem_stds = [rem_stds; rem_std];
                                twitch_checks = [twitch_checks; twitch_check];
                                twitch_ratios = [twitch_ratios; twitch_check/threshold_rem];
                                sample_means = [sample_means; sample_mean];
                                sample_stds = [sample_stds; sample_std];
                                sample_checks = [sample_checks; sample_check];
                                sample_ratios = [sample_ratios; sample_check/threshold_rem];
                                method = 'Window';
                                break;
                            else
                                thresholds = [thresholds ; threshold_rem];
                                rem_means = [rem_means; rem_mean];
                                rem_stds = [rem_stds; rem_std];
                                twitch_checks = [twitch_checks; twitch_check];
                                twitch_ratios = [twitch_ratios; twitch_check/threshold_rem];
                                sample_means = [sample_means; sample_mean];
                                sample_stds = [sample_stds; sample_std];
                                sample_checks = [sample_checks; sample_check];
                                sample_ratios = [sample_ratios; sample_check/threshold_rem];
                                
                                start = round(start + 0.5*FIRST_SAMPLES);
                                if start + FIRST_SAMPLES > numel(samples_rem(:,1))
                                    threshold_rem = prctile(cell2mat(thresholds),SAMPLE_PERCENTILE);
                                    method = 'Percentile';
                                    break;
                                end
                                
                            end
                        end
                        
                        disp(['Threshold for REM phase ', num2str(i), ' is ', num2str(threshold_rem)]);

                        %2D List with indices and corresponding values and sleep stage that exceed threshold
                        peaks_rem = {};

                        %Number of samples in this REM phase
                        length_rem = size(samples_rem);
                        length_rem = length_rem(1);

                        disp('Determining number of spikes in REM phase...');

                        %Populate peaks_rem with only samples that exceed threshold
                        for j = 1:length_rem
                            if cell2mat(samples_rem(j,2)) > threshold_rem
                                peaks_rem = [peaks_rem ; samples_rem(j,:)];
                            end
                        end

                        disp('Determining and analysing twitches...');

                        %Number of samples in peaks_rem
                        length_peaks = 0;
                        %List of "events", where events are a list of all values that occur within
                        %MIN_INTERVAL sample distance of each other
                        event_list = {};
                        %Number of events
                        num_events = 0;
                        %List of average amplitude of each events
                        avg_amp = {};
                        %List of amplitude integral of each events
                        int_amp = {};
                        %List of duration of each event (in s)
                        durations = {};
                        %List of sleep stage of each event
                        sleeps = {};
                        
                        if numel(peaks_rem) > 0
                            length_peaks = numel(peaks_rem(:,1));

                            %Single event containing 2D List of indices and corresponding values
                            event_array = peaks_rem(1,:);

                            %Indexing for iterative function
                            current_idx = cell2mat(event_array(1));

                            %Iterate through the rest of the list
                            for j = 2:length_peaks
                                %Index of currently examined row
                                next_idx = cell2mat(peaks_rem(j,1));
                                %If the two samples occur within MIN_INTERVAL interval
                                if next_idx - current_idx < MIN_INTERVAL
                                    %Concatenate event_array with current sample
                                    event_array = [event_array ; peaks_rem(j,:)];
                                %Else
                                else
                                    %Concatenate event_array to event_list
                                    event_list = [event_list ; {event_array}];
                                    %Add to number of events counted
                                    num_events = num_events + 1;
                                    %Calculate and concatenate average amplitude to list
                                    avg_amp = [avg_amp ; mean(cell2mat(event_array(:,2)))];
                                    %Calculate and concatenate integral
                                    %amplitude to list
                                    int_amp = [int_amp ; sum(cell2mat(event_array(:,2)))];
                                    %Calculate and concatenate duration to list
                                    durations = [durations ; (cell2mat(event_array(end,1)) - cell2mat(event_array(1,1))+1)*RESOLUTION];
                                    %Set event_array to current sample
                                    event_array = peaks_rem(j,:);
                                end
                                %Advance the index counter
                                current_idx = next_idx;

                                %Display progress
                                disp([num2str(j), ' of ',num2str(length_peaks)]);
                            end
                            %Add the last event_array to event_list
                            event_list = [event_list ; {event_array}];
                            %Add to number of events counted
                            num_events = num_events + 1;
                            %Calculate and concatenate average amplitude to list
                            avg_amp = [avg_amp ; mean(cell2mat(event_array(:,2)))];
                            %Calculate and concatenate integral amplitude to list
                            int_amp = [int_amp ; sum(cell2mat(event_array(:,2)))];
                            %Calculate and concatenate duration to list
                            durations = [durations ; (cell2mat(event_array(end,1)) - cell2mat(event_array(1,1))+1)*RESOLUTION];
                        end
                                                        
                        %Display progress
                        disp(['Finished parsing ', num2str(length_peaks), ' spikes...']);
                        disp(['Found ', num2str(num_events), ' twitches']);

                        disp('Wrapping up calculations...');
                        %Combine the data, amplitudes and durations into one array
                        events = [event_list, avg_amp, int_amp, durations];

                        event_starts = {};
                        for j = 1:num_events
                            event_start_idx = event_list{j,1}{1,1};
                            event_starts= [event_starts ; event_start_idx * RESOLUTION];
                        end

                        %Total time elapsed in data (in s)
                        time = length_rem * RESOLUTION;
                        %Start time of data (in s)
                        start_time = cell2mat(samples_rem(1,1)) * RESOLUTION;
                        %End time of data (in s)
                        end_time = cell2mat(samples_rem(end,1)) * RESOLUTION;
                        
                        %Percentage of samples spent in "events"
                        event_percent = length_peaks / length_rem;
                        %Percentage of samples spent at "baseline"
                        base_percent = 1 - event_percent;

                        %Amount of time spent in "events" (in s)
                        event_time = event_percent * time;
                        %Amount of time spent at "baseline"
                        base_time = base_percent * time;

                        %Calculate average amplitude of data BELOW
                        %threshold
                        low_data = {};
                        zero_point = samples_rem{1,1};
                        first_point = samples_rem{1,1};
                        last_point = 0;
                        if length_peaks > 0
                            peaks_idx = cell2mat(peaks_rem(:,1));
                        else
                            peaks_idx = {};
                        end
                        samples_idx = cell2mat(samples_rem(:,1));                        
                        for j = 1:numel(peaks_idx)
                            last_point = peaks_rem{j,1}-1;
                            if ~ismember(samples_rem{last_point-zero_point+1,1},peaks_idx)
                                low_data = [low_data ; samples_rem((first_point-zero_point+1):(last_point-zero_point+1),:)];
                            end
                            first_point = peaks_rem{j,1}+1;
                        end
                        low_data = [low_data ; samples_rem((first_point-zero_point+1):end,:)];
                        low_data = cell2mat(low_data);
                        low_avg = mean(low_data(:,2));                      
                        
                        disp('Formatting for export...');
                        %Format all data into appropriate tables for export
                        %Events
                        events_header = {'Event Start (s)','Avg Amplitude','Summation','Duration (s)'};
                        events_data = [event_starts, avg_amp, int_amp, durations];
                        events_export = [events_header; events_data];
                        
                        %Export data to output.xlsx located in the same folder as data
                        filename = [char(path), char(file), EMG_name, '_output.xlsx'];
                        disp(['Exporting to ', filename, ' ...'])
                        
                        xlswrite(filename, events_export,i);
                        xlswrite(filename, {'Threshold';threshold_rem},i,'F1:F2');
                        xlswrite(filename, {'Number of Events';num_events},i,'G1:G2');
                        xlswrite(filename, {'Avg Amplitude below Threshold';low_avg},i,'H1:H2');
                        xlswrite(filename, {'Start time (s)',start_time;
                            'End time (s)',end_time;'Total Duration', time},i,'I1:J3');
                        xlswrite(filename, {'Event Percent', 'Event Time (s)';
                            event_percent, event_time; 'Baseline Percent', 'Baseline Time (s)';
                            base_percent, base_time},i,'L1:M4');
                                             
                        xlswrite(filename, {'Method Used',method},i,'F4:G4');
                        
                        xlswrite(filename, {'Threshold Percentile';BASELINE_PERCENTILE},i,'F5:F6');
                        xlswrite(filename, {'Threshold Interval';FIRST_TIME},i,'G5:G6');
                        xlswrite(filename, {'Twitch SD Multiplier';REM_STD},i,'H5:H6');
                        xlswrite(filename, {'Sample SD Multiplier';SAMPLE_STD},i,'I5:I6');
                        xlswrite(filename, {'Twitch Ratio';TWITCH_THRESHOLD},i,'J5:J6');
                        xlswrite(filename, {'Sample Ratio';SAMPLE_THRESHOLD},i,'K5:K6');
                        xlswrite(filename, {'Sample Percentile';SAMPLE_PERCENTILE},i,'L5:L6');
                        
                        %Print out threshold, twitch mean, std, check,
                        %sample mean, std, check, ratio to twitch, ratio to
                        %sample
                        %End print out if used window method or percentile
                        %method
                        
                        xlswrite(filename, {'Window Threshold','Window Mean',...
                            'Window STD','Window Check',...
                            'Phase Mean','Phase STD','Phase Check',...
                            'Window Ratio','Phase Ratio'},i,'F8:N8');
                        export_length = numel(thresholds)+8;
                        export_range = strcat('F9:F',num2str(export_length));
                        xlswrite(filename, thresholds, i, export_range);
                        export_range = strcat('G9:G',num2str(export_length));
                        xlswrite(filename, rem_means, i, export_range);
                        export_range = strcat('H9:H',num2str(export_length));
                        xlswrite(filename, rem_stds, i, export_range);
                        export_range = strcat('I9:I',num2str(export_length));
                        xlswrite(filename, twitch_checks, i, export_range);
                        export_range = strcat('J9:J',num2str(export_length));
                        xlswrite(filename, sample_means, i, export_range);
                        export_range = strcat('K9:K',num2str(export_length));
                        xlswrite(filename, sample_stds, i, export_range);
                        export_range = strcat('L9:L',num2str(export_length));
                        xlswrite(filename, sample_checks, i, export_range);
                        export_range = strcat('M9:M',num2str(export_length));
                        xlswrite(filename, twitch_ratios, i, export_range);
                        export_range = strcat('N9:N',num2str(export_length));
                        xlswrite(filename, sample_ratios, i, export_range);

                        disp(['Completed REM phase ', num2str(i), '...']);
                    end
                    disp('Completed file!');
                end
                disp('Completed all files!');
            end
        end
    end
end
