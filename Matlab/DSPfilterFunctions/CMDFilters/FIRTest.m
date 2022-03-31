%% DSP Work
%% Calculating coefficients - Generate SOS Matrix
fc = 80000;
fs = 2.5e6;
order = 15;

figure(1);

% B = 32; % Number of bits
% L = floor(log2((2^(B-1)-1)/max(max(sos))));  % Round towards zero to avoid overflow
% bsc = sos*2^L;
% gsc = g*2^L;
%b = firpm(order, [0, fc/(fs/2), (fc/(fs/2))*2, 1], [1, 1/(sqrt(2)), (1/(sqrt(2)))/2, 0]);
c = fir1(order, fc/(fs/2));
freqz(c, 1, 512, fs);

%% Input
Fs = fs;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
L = 100;             % Length of signal
fsine = 10000;        % frequency of test sinewave
%L = round(((1/fsine)/T))*4;
t = (0:L-1)*T;        % Time vector

O = numerictype([],32,31);
j = (t>1e-5);
%j = sin(2*pi*fsine*t);

codes = fi('numerictype', O);
m = numerictype([], 66, 64);
output = fi('numerictype', m);
out = fi('numerictype', m);
figure(2);
%loop that takes the input step function and outputs the hex codes that the
%AD7961 would output
for x = (1:L)
    code = fi(j(x), 'numerictype', O);
    codes = [codes; code];
    %out = freqSamplingFIR(code, c);
    out = HammingWindowFIR(code, c);
    output = [output, out];
end

% Plotting Input and Output on same graph
%plot(t, codes*2^-15);%normalized the step function here to be able to view both filter output and step voltage
plot(t, codes);
hold on;
plot(t, output);
title('Original Signal and Step Response of IIR LP filter');
xlabel('t[s]');
ylabel('Amplitude');

%% Truncation Error
outputNew = fi(output, 1, 14, 13);
figure(8);
plot(t, output);
hold on;
plot(t, outputNew);

%% Amplitude Spectrum of input/output

Y = fft(double(codes));
Y2 = fft(double(output));

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

P4 = abs(Y2/L);
P3 = P4(1:L/2+1);
P3(2:end-1) = 2*P3(2:end-1);

f = Fs*(0:(L/2))/L;

figure(4);
subplot(2, 1, 1);
stem(f,P1);
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');

subplot(2, 1, 2);
stem(f,P3); 
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');

%% Plotting Group Delay
figure(5);
grpdelay(c, 512, fs);
title('Group Delay');

%% Plotting Phase Delay
figure(6);
phasedelay(c, 512, fs);
title('Phase Delay');

%% Step Response
figure(7);
stepz(c);
grid;

% step response info/measurements
[h, t] = stepz(c);
S = stepinfo(h, t);
disp(S);

%%
function y = freqSamplingFIR(x, c)
%FREQSAMPLINGFIR Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 29-Jul-2021 13:19:37

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    % Numerator coefficient vector
    %Numerator = [0.00070403 0.088936 0.39331 0.088936 0.00070403];
    Numerator = c;
    
    Hd = dsp.FIRFilter( ...
        'Numerator', Numerator, ...
        'CoefficientsDataType', 'Custom', ...
        'CustomCoefficientsDataType', numerictype(true,32,33));
end

% s = fi(x,1,32,31,'RoundingMethod','Round','OverflowAction','Saturate');
% y = step(Hd,s);
y = Hd(x);

% [EOF]
end

%%
function y = HammingWindowFIR(x, c)
%HAMMINGWINDOWFIR Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 30-Jul-2021 09:55:49

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    % Numerator coefficient vector
%     Numerator = [0.0068937 0.011519 0.024437 0.045017 0.070404 0.096086 ...
%         0.11697 0.12867 0.12867 0.11697 0.096086 0.070404 ...
%         0.045017 0.024437 0.011519 0.0068937];
    Numerator = c;
    
    Hd = dsp.FIRFilter( ...
        'Numerator', Numerator, ...
        'CoefficientsDataType', 'Custom', ...
        'CustomCoefficientsDataType', numerictype(true,32,33));
end

 s = fi(x,1,32,31,'RoundingMethod','Round','OverflowAction','Saturate');
 y = step(Hd,s);
%y = Hd(x);

% [EOF]
end