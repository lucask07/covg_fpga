%% Script to Read Vivado Simulation Results
% Ian Delgadillo Bonequi
clear all;
close all;
clc;

%% Create Input Data Array for Vivado (.dat file)

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
fsig = 300000;        % frequency of test sinewave
L = round(((1/fsig)/T))*5; %Length of Signal
%t = (0:L-1)*T;        % Time vector
t = (0:714)*T;        % Time vector

%j = 2^15*(t>1e-5);
j = (2^15/2)*sin(2*pi*fsig*t);
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
plot(t1, A);
grid on;
title('Vivado Simulation Results');
xlabel('Time (s)');
ylabel('Hex Code');
xlim([0 t1(length(t1))]);
saveas(figure(2), 'StepResponse.png');

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
