% https://stackoverflow.com/questions/28139871/how-can-i-get-coefficients-of-filter-in-matlab
% Notes: the verilog in daq_v2 refers to direct form II transposed 
% a1 coefficient is not included in either stage of the verilog 

% Direct Form transpose II 
% Verilog addresses 

% should coefficients all be wrritten at once. 

% scale1 [0] sfix32_en31 
% section 1
% b1 [1] sfix32_en29
% b2 [2] sfix32_en29
% b3 [3] sfix32_en29
% a2 [4] sfix32_en30
% a3 [5] sfix32_en30

% scale2 [8] sfix32_en31 [-1, 1)
% scale3 [7] sfix32_en31 
% section 2 
% b1 [9] sfix32_en29  [-4, 4) numerator 
% b2 [10] sfix32_en29
% b3 [11] sfix32_en29 
% a2 [12] sfix32_en30 [-2, 2)
% a3 [13] sfix32_en30

% // Input               : s16,15 -> [-1 1)
% // Section Input       : s16,15 -> [-1 1)
% // Section Output      : s16,14 -> [-2 2)
% // Output              : s14,8 -> [-32 32)

% Hd.ScaleValues (addr 0, addr 8 is scale, addr 7 is scale)
% the coefficients do not have a1 

%% DSP Filter
%% Generate SOS Matrix
fc = 500e3;
fs = 5e6;
order = 4;

[z, p, k] = butter(order, fc/(fs/2));

[sos, g] = zp2sos(z, p, k);
% zp2sos: If g is not specified the gain is embedded in the 1st structure.
sos1 = zp2sos(z, p, k);  % creates a response with magnitude of 1, equivalent to multiplying b coefficients of SOS by g. 
figure(1);
freqz(sos1, 512, fs); % bode plot
%% Input
T = 1/fs;             % Sampling period       
fsine = 50e3;        % frequency of test sinewave
L = round(((1/fsine)/T))*20;
t = (0:L-1)*T;        % Time vector

codes = fi( (0.45*sin(2*pi*fsine/10*t) + 0.45), 1, 16,15);
% codes = fi(ones(length(t),1)*0.8, 1, 16,15);

[Hd] = FourthOrderD2T(sos, g);
% [Hd] = FourthOrderD2T(sos, 1);
clc
fprintf(' ----------- Coefficients ------------- \n');
c = coeffs(Hd);
fprintf('Section 1 b coefficients (numerator) \n')
hex(fi(c.SOSMatrix(1,1:3), Hd.CustomNumeratorCoefficientsDataType))
fprintf('Section 1 a coefficients (denominator) (skip first) \n')
hex(fi(c.SOSMatrix(1,4:6), Hd.CustomDenominatorCoefficientsDataType))
fprintf('Section 2 b coefficients (numerator) \n')
hex(fi(c.SOSMatrix(2,1:3), Hd.CustomNumeratorCoefficientsDataType))
fprintf('Section 2 a coefficients (denominator) (skip first) \n')
hex(fi(c.SOSMatrix(2,4:6), Hd.CustomDenominatorCoefficientsDataType))

fprintf('Scale values \n')
hex(fi(c.ScaleValues, Hd.CustomScaleValuesDataType))

% format as a Python dictionary
python_dict = '{';
python_dict = [python_dict, sprintf('%d:0x%s, \n',0,hex(fi(c.ScaleValues(1), Hd.CustomScaleValuesDataType)))];
section = 1;
for i = 1:3
    python_dict = [python_dict, sprintf('%d:0x%s, \n',i,hex(fi(c.SOSMatrix(section,i), Hd.CustomNumeratorCoefficientsDataType)))];
end
for i = 2:3
    python_dict = [python_dict, sprintf('%d:0x%s, \n',i+2,hex(fi(c.SOSMatrix(section,i+3), Hd.CustomDenominatorCoefficientsDataType)))];
end
% scale values 
python_dict = [python_dict, sprintf('%d:0x%s, \n',7,hex(fi(c.ScaleValues(3), Hd.CustomScaleValuesDataType)))];
python_dict = [python_dict, sprintf('%d:0x%s, \n',8,hex(fi(c.ScaleValues(2), Hd.CustomScaleValuesDataType)))];

section = 2;
for i = 1:3
    python_dict = [python_dict, sprintf('%d:0x%s, \n',8+i,hex(fi(c.SOSMatrix(section,i), Hd.CustomNumeratorCoefficientsDataType)))];
end
for i = 2:3
    python_dict = [python_dict, sprintf('%d:0x%s, \n',10+i,hex(fi(c.SOSMatrix(section,i+3), Hd.CustomDenominatorCoefficientsDataType)))];
end

% replace last comma with a }
idx = strfind(python_dict, ',');
python_dict(idx(end)) = '}';
fprintf(python_dict)

% Plotting Input and Output on same graph
% this maninpulation of codes creates a 32 word length, 29 fraction length value 
% filter input and generate output 
output = Hd(codes);
figure(2);
plot(t, codes, 'b.');
hold on;
plot(t, output, 'm*');
legend('input', 'output');
%plot(t, codes);
title('Original Signal and Response of IIR LP filter');
xlabel('t[s]');
ylabel('Amplitude');

figure(12);
release(Hd);
flat = fi(ones(length(t))*0.95, 1, 16,15);
plot(t, flat);
hold on;
output_flat = Hd(flat);
plot(t, output_flat);
title('Flat Signal and Response of IIR LP filter');
ylabel('Amplitude');

%% Amplitude Spectrum of input/output

Y = fft(double(codes));
Y2 = fft(double(output));

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

P4 = abs(Y2/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);

f = fs*(0:(L/2))/L;

figure(3);
subplot(2, 1, 1);
stem(f,P1);
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');

subplot(2, 1, 2);
stem(f,P3); 
title('Single-Sided Amplitude Spectrum of Output');
xlabel('f (Hz)');
ylabel('|P3(f)|');

%% Plotting Group Delay
figure(4);
grpdelay(sos, 512, fs);
title('Group Delay');

%% Plotting Phase Delay
figure(5);
phasedelay(sos, 512, fs);
title('Phase Delay');

%% Step Response
figure(6);
time_steps = 50;
stepz(sos1, time_steps, fs) % 50 time steps
grid

% step response info/measurements
[h, t_step] = stepz(sos1, 50, fs);
S = stepinfo(h, t_step);
disp(S);

% %% time domain simulation 
% release(Hd);
% y = Hd(codes*2^(-15));
% plot(y)


% % make a pass through
% sos(:,1) = 1;
% sos(:,2:3) = 0;
% sos(:,5:6) = 0;
% sos1 = sos;


%% Cheby One Function
function [Hd] = FourthOrderD2T(sos, g)
% Generates fourth other filter


% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 28-Jun-2021 11:48:16

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

% persistent Hd;

%if isempty(Hd)
    
    Gain       = g;  % Gain coefficient vector
    
    % SOS_Matrix coefficient vector
    SOS_Matrix = sos;
    
    Hd = dsp.BiquadFilter( ...
        'SOSMatrix', SOS_Matrix, ...  # default is Direct form II transposed
        'ScaleValues', Gain, ...
        'SectionInputDataType', 'Custom', ...
        'CustomSectionInputDataType', numerictype([],16,15), ...
        'SectionOutputDataType', 'Custom', ...
        'CustomSectionOutputDataType', numerictype([],16,14), ...
        'NumeratorCoefficientsDataType', 'Custom', ...
        'CustomNumeratorCoefficientsDataType', numerictype([],32,29), ...
        'DenominatorCoefficientsDataType', 'Custom', ...
        'CustomDenominatorCoefficientsDataType', numerictype([],32,30), ...
        'ScaleValuesDataType', 'Custom', ...
        'CustomScaleValuesDataType', numerictype([],32,31), ...
        'NumeratorProductDataType', 'Custom', ...
        'CustomNumeratorProductDataType', numerictype([],48,44), ...
        'DenominatorProductDataType', 'Custom', ...
        'CustomDenominatorProductDataType', numerictype([],48,44), ...
        'NumeratorAccumulatorDataType', 'Custom', ...
        'CustomNumeratorAccumulatorDataType', numerictype([],49,44), ...
        'DenominatorAccumulatorDataType', 'Custom', ...
        'CustomDenominatorAccumulatorDataType', numerictype([],49,44), ...
        'StateDataType', 'Custom', ...
        'CustomStateDataType', numerictype([],16,15), ...
        'OutputDataType', 'Custom', ...
        'CustomOutputDataType', numerictype([],14,8), ...
        'RoundingMethod', 'Convergent');
%end

% [EOF]
end
