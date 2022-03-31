%% Script to Read Vivado Simulation Results
% Ian Delgadillo Bonequi
clear all;
close all;
clc;

%% Create Input Data Array

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
fsig = 50000;        % frequency of test sinewave
L = round(((1/fsig)/T))*5; %Length of Signal
t = (0:L-1)*T;        % Time vector

%j = 2^15*(t>1e-5);
j = 2^15*sin(2*pi*fsig*t);
input = int16(j);

figure(1);
plot(t, input);
xlabel('time (s)');
ylabel('Hex Code');
xlim([0 t(length(t))]);

fileID = fopen('test.v','w');
fprintf(fileID, '%s\r\n', '// Input data for filter_in');
for i = (1:length(input))
    fprintf(fileID,'%s%d%s%s\r\n', 'filter_in[', i, '] <= 16h''', dec2hex(input(i)));
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

%%
Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period
t = (0:length(A)-1)*T;        % Time vector

figure(2);
plot(t, A); %plot with offset to center around y=0
grid on;
title('Vivado Simulation Results');
xlabel('Time (s)');
ylabel('Hex Code');
xlim([0 t(length(t))]);
saveas(figure(2), 'StepResponse.png');