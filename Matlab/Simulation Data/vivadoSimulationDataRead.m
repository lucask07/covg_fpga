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
% t = (0:714)*T;

Amplitude = 16383; %amplitude
Offset = 16384; %offset

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
plot(t1(1:2:end), y(1:2:length(t1),5), '-*');
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
plot(t1, AD796x_LPF_data_modify_fixpt(output), '-*');
legend('DDR Bench Meas', 'Vivado Sim', 'Matlab');
saveas(figure(3), 'VivadoSimResults.png');

%% Bode Plot
amplitude = [];
freq = [];
gain = [];
gain_RMS_array = [];
gain_FFT_array = [];

y = hdf5read('test100Hz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 100];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];


y = hdf5read('test1kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 1e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test10kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 10e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test100kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 100e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test200kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 200e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test300kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 300e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test400kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 400e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test500kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 500e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test600kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 600e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test700kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 700e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test800kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 800e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test900kHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 900e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

y = hdf5read('test1MHz.h5','/adc');
amplitude = [amplitude, (max(y(:,5)) - min(y(:,5)))/2];
gain_RMS = ((rms(y(:,5) - mean(y(:,5))))*sqrt(2))/((rms(y(:,3) - mean(y(:,3))))*sqrt(2));
gain_RMS_array = [gain_RMS_array, gain_RMS];
gain = [gain, (max(y(:,5)) - min(y(:,5)))/(max(y(:,3)) - min(y(:,3)))];
freq = [freq, 1000e3];

o = y(:,5) - mean(y(:,5));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
o = y(:,3) - mean(y(:,3));
Y = fft(o);
L = length(o);
f = Fs*(0:(L/2))/L;
P4 = abs(Y/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);
gain_FFT = max(P1)/max(P3);
gain_FFT_array = [gain_FFT_array, gain_FFT];

freq = 2*freq;

figure(4);
semilogx(freq, 20*log(gain/max(gain)), '-*', 'LineWidth', 2);
hold on;
grid on;
ylim([-80 10]);
yticks(-80:4:10);
title('Bode Plot');
xlabel('Frequency (Hz)');
ylabel('Magnitude (dB)');

semilogx(freq, 20*log(gain_RMS_array/max(gain_RMS_array)), '-*', 'LineWidth', 2);
hold on;

[hideal,f] = freqz(sos1, 512, fs);
Hideal = 20*log10(abs(hideal));
plot(f, Hideal, 'LineWidth', 2);
hold on;

semilogx(freq, 20*log(gain_FFT_array/max(gain_FFT_array)), '-*', 'LineWidth', 2);
hold on;

yline(-3, '--');
legend('DDR Bench Meas', 'DDR Bench Meas (RMS calc)', 'Matlab', 'DDR Bench Meas (FFT calc)', 'Location', 'southwest');

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

s = fi(x,1,16,15,'RoundingMethod', 'Round', 'OverflowAction', 'Wrap');
y = step(Hd,s);
% y = Hd(x);


% [EOF]
end
%%
function dout = AD796x_LPF_data_modify(din)
    dout = fi(2^13, 1, 14, 0)*din;
    dout = fi(dout+8192, 0, 14, 0);
end
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                          %
%          Generated by MATLAB 9.10 and Fixed-Point Designer 7.2           %
%                                                                          %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%#codegen
function dout = AD796x_LPF_data_modify_fixpt(din)
    fm = get_fimath();

    x = fi(2^13, 1, 14, 0)*din;
    dout = fi(x+fi(8192, 0, 14, 0, fm), 0, 14, 0);
end


function fm = get_fimath()
	fm = fimath('RoundingMethod', 'Floor',...
	     'OverflowAction', 'Wrap',...
	     'ProductMode','FullPrecision',...
	     'MaxProductWordLength', 128,...
	     'SumMode','FullPrecision',...
	     'MaxSumWordLength', 128);
end
