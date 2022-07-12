%% Ian Delagadillo Bonequi
clear all;
close all;
clc;

%% Frequency Array
start_exp = 2;
end_exp = 6;
logfreq = logspace(start_exp,end_exp,5);
freq = [];
for i=1:(length(logfreq)-1)
    for j=2:19
        freq = [freq, logfreq(i)*j*0.5];
    end
end
freq = [freq, 10^end_exp];

%% Generate SOS Matrix
fc = 250e3;
fs = 2.5e6;
order = 4;
[z, p, k] = butter(order, fc/(fs/2));
[sos, g] = zp2sos(z, p, k);
sos1 = zp2sos(z, p, k);

%% Bode Plot
amplitude = [];
%freq = [];
gain = [];
gain_RMS_array = [];
t = 0:(1/2.5e6):1;

for i=1:length(freq)
    filter_input = 8191*sin(2*pi*freq(i)*t)+8192;
    filename = ['BodePlotData\test', num2str(freq(i)), 'Hz.h5'];
    y = hdf5read(filename,'/adc');
    gain = [gain, (max(y(501:2:end,5)) - min(y(501:2:end,5)))/(max(filter_input) - min(filter_input))];
    %gain_RMS = ((rms(y(1:2:end,5) - mean(y(1:2:end,5))))*sqrt(2))/((rms(filter_input - mean(filter_input)))*sqrt(2));
    %gain_RMS_array = [gain_RMS_array, gain_RMS];
end

figure(1);
%semilogx(freq, 20*log(gain_RMS_array/max(gain_RMS_array)), '-*', 'LineWidth', 2);
semilogx(freq, 20*log(gain/max(gain)), '-*', 'LineWidth', 2);
hold on;
grid on;
ylim([-80 10]);
yticks(-80:4:10);
title('4th Order IIR Bode Plot');
xlabel('Frequency (Hz)');
ylabel('Magnitude (dB)');
[hideal,f] = freqz(sos1, 512, fs);
Hideal = 20*log10(abs(hideal));
plot(f, Hideal, 'LineWidth', 2);
hold on;
yline(-3, '--');
legend('DDR Bench Meas', 'Matlab', 'Location', 'southwest');

saveas(figure(1), '4thOrderButterWorthBode.png');