%% Script to Read Vivado Simulation Results
% Ian Del%% Script to Read Vivado Simulation Results
% Ian Delgadillo Bonequi
clear all;
close all;
clc;

%% Create Input Data Array for Vivado (.dat file)

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
fsig = 10000;        % frequency of test sinewave
L = round(((1/fsig)/T))*5; %Length of Signal
%t = (0:L-1)*T;        % Time vector
t = (0:714)*T;        % Time vector

% Amplitude = 1; %amplitude in Volts
% Offset = 2; %offset in Volts

%j = ((Amplitude*sin(2*pi*fsig*t)+Offset)/4.096)*2^15;
j = (2048)*sin(2*pi*500000*t)+4096;
%j = 2^15*(t>1e-5);

input = int16(j);

figure(1);
plot(t, input);
xlabel('time (s)');
ylabel('Hex Code');
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
fgets(fileID); %skip two lines
fgets(fileID);
formatSpec = '%d'; %read data
sizeA = [Inf];
A = fscanf(fileID, formatSpec, sizeA);
fclose(fileID);

%% Raw Vivado Simulation Results

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period
t1 = (0:length(A)-1)*T;        % Time vector

figure(2);
plot(t1, A, '-*');
grid on;
title('Vivado Simulation Results');
xlabel('Time (s)');
ylabel('Hex Code');
xlim([0 t1(length(t1))]);
ylim([8000 10000]);
saveas(figure(2), 'VivadoSimResults.png');

% vivadoGain = (max(A(20:end-1)-min(A(20:end-1))))/(max(j)-min(j))

%% Overlaying Normalized Input and Normalized Output
A_normalized = (A-8191)/8192; %normalize and cancel offset of output
in_normalized = j/32768;
in_normalized = in_normalized/max(in_normalized);
A_normalized = A_normalized/max(in_normalized);

figure(3);
plot(t1, A_normalized);
grid on;
title('Normalized Input and Output');
xlabel('Time (s)');
ylabel('Hex Code');
xlim([0 t1(length(t1))]);
ylim([min(in_normalized) max(in_normalized)]);
hold on;
plot(t, in_normalized);

%% Reading Python Output
figure(4);
y = hdf5read('test500kHz.h5','/adc');
plot(t1, y(1:length(t1),5));
%plot(y(:,5));

hold on;
plot(t1, A, '-*');
%plot(y(:,3));
grid on;
xlabel('Time (s)');
ylabel('Hex Code');

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

figure(5);
semilogx(freq, 20*log(gain/max(gain)), 'LineWidth', 2);
hold on;
grid on;
ylim([-80 10]);
yticks(-80:4:10);
title('Bode Plot');
xlabel('Frequency - Hz');
ylabel('Magnitude - dB');
saveas(figure(5), '4thOrderButterWorthBode.png');
%%
% figure(6);
% semilogx([10e3 100e3 200e3 300e3 400e3 500e3 600e3 700e3 800e3 800e3 1000e3], 20*log(g/max(g)), 'LineWidth', 2);
% hold on;
% grid on;
% ylim([-80 10]);
% yticks(-80:4:10);
% title('Bode Plot');
% xlabel('Frequency - Hz');
% ylabel('Magnitude - dB');
% saveas(figure(6), '4thOrderButterWorthBodeVivado.png');
