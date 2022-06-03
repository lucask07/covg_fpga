function [adc_data, timestamp, dac_data, ads, error] = data_to_names(chan_data, data_version)
% intended to emulate the Python function data_to_names 

%         Put deswizzled data into dictionaries with names that match with the data sources. 
%         Complete twos complement conversion where necessary. Check timestamps for skips.
%         Check the constant values for errors.
% 
%         This supports 2 versions of the FPGA code:
%         'ADC_NO_TIMESTAMPS': DDR data is only the fast ADC. AD7961
%         'TIMESTAMPS': DDR data is numerous. AD7961, AD5453 out, ADS8686, timestamps, readcheck

if nargin < 2
    data_version = 'TIMESTAMPS';
end

if strcmp(data_version, 'ADC_NO_TIMESTAMPS')  % first version of ADC data before DACs + timestamps are stored
    adc_data = chan_data;
    timestamp = [];
    dac_data = [];
    ads = [];
end

if strcmp(data_version, 'TIMESTAMPS')  % first version of ADC data before DACs + timestamps are stored            
    adc_data = zeros(4,length(chan_data));
    for i = 1:4
        adc_data(i,:) = twos_comp(chan_data(i,:), 16);
    end
    lsb = chan_data(7, 1:5:end);
    mid_b = chan_data(7, 2:5:end)*2^16; % type conversion?
    msb = chan_data(8, 3:5:end)*2^32;  % type conversion>
    t_len = length(msb);
    % add together but make sure they have the same length
    timestamp = lsb(1:(t_len-1)) + mid_b(1:(t_len-1)) + msb(1:(t_len-1));

    read_check = {};
    read_check{1} = chan_data(8, 4:10:end);
    read_check{2} = chan_data(8, 5:5:end);
    read_check{3} = chan_data(8, 9:10:end);

    dac_data = zeros(4, length(chan_data(4, 1:2:end)));
    dac_data(1,:) = chan_data(5, 1:2:end);
    dac_data(2,:) = chan_data(5, 2:2:end);
    dac_data(3,:) = chan_data(6, 1:2:end);
    dac_data(4,:) = chan_data(6, 2:2:end);
    % dac channels 4,5 are available but not every sample. skip for now. TODO: add channels 4,5

    ads = struct();
    ads.A = twos_comp(chan_data(7, 1:5:end), 16);
    ads.B = twos_comp(chan_data(7, 2:5:end), 16);

    error = 0;
    % check that the constant values are constant 
    constant_values = [0xaa55, 0x28ab, 0x77bb];
    for i = 1:length(constant_values)
        if ~all(read_check{i} == constant_values(i))
            fprintf('Error in constant value: %d ', constant_values(i))
            fprintf('Number of errors: {np.sum(read_check[i] != constant_values[i])}')
            error = 1;
        end
    end
    % check the timestamps for a skip
    unq_time_intervals = unique(diff(timestamp));
    if length(unq_time_intervals) > 1
        fprintf('Warning: Multiple time intervals \n')
        error = 1;
    end
end

end