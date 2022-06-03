% script to demonstrate reading of the h5 files.
% 2022/6/3

% set to directory of data files
data_dir = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/filter_tests/20220603/filtermeas';

[t, chan_data] = read_h5(data_dir, 'test400kHz.h5');
[adc_data, timestamp, dac_data, ads, error] = data_to_names(chan_data, 'TIMESTAMPS');

plot(t(1:2:end), dac_data(1,:), '-*');

[t, chan_data] = read_h5(data_dir, 'test400kHz_passthru.h5');
[adc_data, timestamp, dac_data, ads, error] = data_to_names(chan_data, 'TIMESTAMPS');

hold on;
plot(t(1:2:end), dac_data(1,:), 'r-*');


% check the timestamp
figure; 
plot(timestamp, '-*');
% looks like the first 48 or so data points are stale ... will need to
% compare data acquistion method of ddr_demo to the script used for filter
% capture. 