%% DSP Filter
%% Generate SOS Matrix
fc = 500e3;
fs = 5e6;
order = 4;

[z, p, k] = butter(order, fc/(fs/2));

%[b,a] = butter(order, fc/(fs/2));

% figure(1);
% phasez(sos, 512, fs);

[sos, g] = zp2sos(z, p, k);
sos1 = zp2sos(z, p, k);
figure(1);
freqz(sos1, 512, fs);
%% Input
Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
%L = 200;             % Length of signal
fsine = 10000;        % frequency of test sinewave
L = round(((1/fsine)/T))*2;
t = (0:L-1)*T;        % Time vector

O = numerictype([],16,0);
%j = 4.096*(t>1e-5);
j = 4.096*sin(2*pi*fsine*t);

codes = fi('numerictype', O);
m = numerictype([], 14, 8);
output = fi('numerictype', m);
figure(2);
%loop that takes the input step function and outputs the hex codes that the
%AD7961 would output
for x = (1:L)
    if (j(x)/4.096)>0
        code = fi((j(x)/4.096)*(2^15-1), 'numerictype', O);
    elseif (j(x)/4.096)<0
        code = fi((j(x)/4.096)*(2^15), 'numerictype', O);
    else
        code = fi(0, 'numerictype', O);
    end
    codes = [codes; code];
    %out = FourthOrderButter(code*2^-15, g, sos);
    %out = doFilter(code);
    out = FourthOrderChebOne(code*2^-15, sos, g);
    output = [output, out];
    stem(t(x), out);
    hold on;
    newOut = AD796x_LPF_data_modify(out);
end

% Plotting Input and Output on same graph
plot(t, codes*2^-15);%normalized the step function here to be able to view both filter output and step voltage
%plot(t, codes);
title('Original Signal and Step Response of IIR LP filter');
xlabel('t[s]');
ylabel('Amplitude');

%% Xtra Math
% newOut = fi(2^8, 1, 14, 0)*output;
% newOut1 = newOut*32;
% newOut2 = fi(newOut1, 1, 14, 0);
%newOut = AD796x_LPF_data_modify(output);
% figure(3);
% subplot(2, 1, 1);
% plot(t, newOut);
% subplot(2, 1, 2);
% plot(t, newOut2+8192);