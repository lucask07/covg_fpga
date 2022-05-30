
fc = 1000e3;
fs = 5e6;
order = 4;

% create full precision filter 
[z, p, k] = butter(order, fc/(fs/2));
sos = zp2sos(z, p, k); % gain is embedded in the first section
g = 1;

% create full precision filter 
H_full = sos;
% create fixed precision filter 
H_fixed = generic_biquad(g, sos);

% inputing fixed type seems to "convert" the filter to fixed type
O = numerictype([],16,0);  % setup default numerictype 
x = randn(1024,1);
code = fi(x/4096*(2^15-1), 'numerictype', O); % 0 defaults to word length of 16, fraction length of 0
test = H_fixed(code);
% generate impulse, sine-wave, ramp, step 

% step response -- use stepz 
N_step = 1000;
y_full = stepz(H_full, N_step, fs);
y_fix = stepz(H_fixed, N_step, fs);
[pk_err, rms_err, cnt_same] = extract_error(y_full, y_fix);

% impulse - impz 

% release(H) releases system resources, such as memory, file handles, and hardware connections, 
% and lets you change any properties or input characteristics.

% quantify differences between full precision, fixed precision (%, vs. bit
% depth)

% run Xilinx .do simulation 

