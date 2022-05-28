%% Script to Read Vivado Simulation Results
% Ian Delgadillo Bonequi
clear all;
close all;
clc;

%% Generate SOS Matrix
fc = 500e3;
fs = 5e6;
order = 4;
[z, p, k] = butter(order, fc/(fs/2));
[sos, g] = zp2sos(z, p, k);
sos1 = zp2sos(z, p, k);
figure(1);
freqz(sos1, 512, fs);

%% Create Input Data Array for Vivado (.dat file)

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
fsig = 100000;        % frequency of test sinewave
t = (0:714)*T;        % Time vector

Amplitude = 2048; %amplitude
Offset = 4096; %offset

j = Amplitude*sin(2*pi*fsig*t)+Offset;
%j = 2^15*(t>1e-5);

input = int16(j);

figure(2);
plot(t, input);
hold on;
plot(t, j, '-*');
xlabel('time (s)');
ylabel('Hex Code');
title('input to filter');
xlim([0 t(length(t))]);

fileID = fopen('..\..\fpga_XEM7310\fpga_XEM7310.sim\sim_1\behav\xsim\filter_in.dat','w');
%fprintf(fileID, '%s\r\n', '// Input data for filter_in');
for i = (1:length(input))
    %fprintf(fileID,'%s%d%s%s\r\n', 'filter_in[', i, '] <= 16h''', dec2hex(input(i)));
    fprintf(fileID,'%s\r\n', dec2hex(input(i)));
end
fclose(fileID);

%% Read simulate.log

fileID = fopen('..\..\fpga_XEM7310\fpga_XEM7310.sim\sim_1\behav\xsim\simulate.log','r');

for z= 0:8 
    fgets(fileID); %skip lines
end
fgets(fileID);

formatSpec = '%d'; %read data
sizeA = [Inf];
A = fscanf(fileID, formatSpec, sizeA);
fclose(fileID);

%% Raw Vivado Simulation Results

% Fs = 5e6;            % Sampling frequency                    
% T = 1/Fs;             % Sampling period
t1 = (0:length(A)-1)*T;        % Time vector
% 
% figure(2);
% plot(t1, A, '-*');
% grid on;
% title('Vivado Simulation Results');
% xlabel('Time (s)');
% ylabel('Hex Code');
% xlim([0 t1(length(t1))]);
% ylim([8000 10000]);
% saveas(figure(2), 'VivadoSimResults.png');

% vivadoGain = (max(A(20:end-1)-min(A(20:end-1))))/(max(j)-min(j))

%% Overlaying Normalized Input and Normalized Output
% A_normalized = (A-8191)/8192; %normalize and cancel offset of output
% in_normalized = j/32768;
% in_normalized = in_normalized/max(in_normalized);
% A_normalized = A_normalized/max(in_normalized);
% 
% figure(3);
% plot(t1, A_normalized);
% grid on;
% title('Normalized Input and Output');
% xlabel('Time (s)');
% ylabel('Hex Code');
% xlim([0 t1(length(t1))]);
% ylim([min(in_normalized) max(in_normalized)]);
% hold on;
% plot(t, in_normalized);

%% Reading Python Output
figure(3);
y = hdf5read('test100kHz.h5','/adc');
plot(t1, y(1:length(t1),5), '-*');
%plot(y(:,5));

hold on;
plot(t1, A, '-*');
%plot(y(:,3));
grid on;
hold on;
title('Vivado and DDR and MATLAB Output');
xlabel('Time (s)');
ylabel('Hex Code');
xlim([0.2e-4 1e-4]);

%% Theoretical Filter Output
m = numerictype([], 14, 12);
output = fi('numerictype', m);

%loop that takes the input step function and outputs the hex codes that the
%AD7961 would output
for x = (1:length(t1))
    out = FourthOrderChebOne(j(x)*2^-15, sos, g);
    output = [output, out];
end

% Plotting Input and Output on same graph
plot(t1, AD796x_LPF_data_modify(output), '-*');
legend('DDR Bench Meas', 'Vivado Sim', 'Matlab');
saveas(figure(3), 'VivadoSimResults.png');

%% Bode Plot
amplitude = [];
freq = [];
gain = [];

y = hdf5read('test100Hz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 100];

y = hdf5read('test1kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 1e3];

y = hdf5read('test10kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 10e3];

y = hdf5read('test100kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 100e3];

y = hdf5read('test200kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 200e3];

y = hdf5read('test300kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 300e3];

y = hdf5read('test400kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 400e3];

y = hdf5read('test500kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 500e3];

y = hdf5read('test600kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 600e3];

y = hdf5read('test700kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 700e3];

y = hdf5read('test800kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 800e3];

y = hdf5read('test900kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 900e3];

y = hdf5read('test1MHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 1000e3];

figure(4);
semilogx(freq, 20*log(gain/max(gain)), 'LineWidth', 2);
hold on;
grid on;
ylim([-80 10]);
yticks(-80:4:10);
title('Bode Plot');
xlabel('Frequency - Hz');
ylabel('Magnitude - dB');
saveas(figure(4), '4thOrderButterWorthBode.png');

%%
% figure(5);
% semilogx([10e3 100e3 200e3 300e3 400e3 500e3 600e3 700e3 800e3 800e3 1000e3], 20*log(g/max(g)), 'LineWidth', 2);
% hold on;
% grid on;
% ylim([-80 10]);
% yticks(-80:4:10);
% title('Bode Plot');
% xlabel('Frequency - Hz');
% ylabel('Magnitude - dB');
% saveas(figure(6), '4thOrderButterWorthBodeVivado.png');

%% Cheby One Function
function y = FourthOrderChebOne(x, sos, g)
%SIXTHORDERCHEBTWO Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 28-Jun-2021 11:48:16

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    Gain       = g;  % Gain coefficient vector
    
    % SOS_Matrix coefficient vector
    SOS_Matrix = sos;
    
    Hd = dsp.BiquadFilter( ...
        'SOSMatrix', SOS_Matrix, ...
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
        'CustomStateDataType', numerictype([],16,14), ...
        'OutputDataType', 'Custom', ...
        'CustomOutputDataType', numerictype([],14,12), ...
        'RoundingMethod', 'Convergent');
end

% s = fi(x,1,16,15,'RoundingMethod', 'Round', 'OverflowAction', 'Saturate');
% y = step(Hd,s);
y = Hd(x);


% [EOF]
end
%%
function dout = AD796x_LPF_data_modify(din)
    dout = fi(2^13, 1, 14, 0)*din;
    dout = fi(dout+8192, 0, 14, 0);
end
