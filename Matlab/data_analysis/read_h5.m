function [t, adc_data] = read_h5(data_dir, file_name)
% Read in h5 data and return the time and adc_data for the channels in input list

%Arguments
%---------
%data_dir (string): directory of h5 file
%file_name (string): file name (must include extension)
%chan_list (list of ints): adc channels to return

%Returns
%-------
%(numpy.ndarray) time
%(array) adc data
SAMPLE_PERIOD = 200e-9;
chan_list = 1:8;

data_name = fullfile(data_dir, file_name);

dset = h5read(data_name, "/adc");

t = 0:SAMPLE_PERIOD:((length(dset)-1)*SAMPLE_PERIOD); 
adc_data = zeros(max(chan_list), length(dset));
for ch = chan_list
    adc_data(ch,:) = dset(:, ch); % convert types?
end

end
