x = (0:0.01:10);
y = 4.096*sin(x);
figure(1);
plot(x, y);

z = 4.096*sin(x)./4.096;
codes = int16.empty;
previousval = 0;
movingaverage = int16.empty;
for x = (0:0.01:10)
    if (4.096*sin(x)/4.096)>0
        code = int16((4.096*sin(3*x)/4.096)*(2^15-1));
    elseif (4.096*sin(x)/4.096)<0
        code = int16((4.096*sin(3*x)/4.096)*(2^15));
    else
        code = int16(0);
    end
    codes = [codes; code];
    average = (previousval/2 + code/2);
    previousval = code;
    movingaverage = [movingaverage; average];
end

figure(2);
stem(codes);
figure(3);
stem(movingaverage);

%% filter part
Fs = 1.1E+4;                                            % Sampling Frequency
Fn = Fs/2;                                              % Nyquist Frequency
Wp = 2.40E+3/Fn;                                        % Passband Frequencies (Normalized)
Ws = 2.41E+3/Fn;                                        % Stopband Frequencies (Normalized)
Rp = 10;                                                % Passband Ripple (dB)
Rs = 50;                                                % Stopband Ripple (dB)
%[n,Ws] = cheb2ord(Wp,Ws,Rp,Rs);                         % Filter Order
%[c,b,a] = cheby2(n,Rs,Ws);                              % Filter Design
%[sosbp,gbp] = zp2sos(c,b,a);                            % Convert To Second-Order-Section For Stability
figure(4)
%freqz(sosbp, 2^16, Fs)                                  % Bode Plot Of Filter

%your_signal_filtered = filtfilt(sosbp, gbp, codes');

d = designfilt('lowpassfir', ...
    'PassbandFrequency',0.15,'StopbandFrequency',0.2, ...
    'PassbandRipple',1,'StopbandAttenuation',60, ...
    'DesignMethod','equiripple');
%y = filtfilt(d,x);
y1 = filtfilt(d,z);
plot(y1);

%%

%step(d);
 figure(5);
% syms n
% f = sin(n);
% ztrans(f)
% plot(f);

% dt = .01;
% maxt = 1;
% t = 0:dt:(maxt-dt);
% nt = length(t);  %length of t

Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
L = 100;             % Length of signal
t = (0:L-1)*T;        % Time vector

j = t>1e-5;
F = fft(j);
yrevon = ifft(F);
Y = complex2real(F);  %generates a structure of 'real' amplitudes and phases
subplot(1,2,1)
plot(t,j);

P2 = abs(F/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

subplot(1,2,2);
f = Fs*(0:(L/2))/L;
plot(f,P1);
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');
%%
[g, d1] = lowpass(single(j),1e5,5e6,'StopbandAttenuation', 20, 'ImpulseResponse', 'fir');
figure(7);
subplot(1,2,1)
plot(t,g);
xlabel('time [s]');
ylabel('Amplitude');
subplot(1,2,2);
plot(t,single(j));
xlabel('time [s]');
ylabel('Amplitude');
%%
% [g1, d2] = highpass(single(j),5e3,5e6,'StopbandAttenuation', 100, 'ImpulseResponse', 'iir');
% figure(11);
% subplot(1,2,1);
% plot(t,g1);
% subplot(1,2,2);
% plot(t,single(j));
g2 = g.^3;%g1 + g;
figure(12);
subplot(1,3,1);
plot(t,g);
subplot(1,3,2);
plot(t,g2);
subplot(1,3,3);
plot(t,single(j));
%%
g3 = filter(Hlp, single(j));
%g3 = doFilter(single(j));
figure(13);
subplot(1,3,1);
plot(t,g3);
subplot(1,3,2);
plot(t,g);
subplot(1,3,3);
plot(t,single(j));


%%
figure(9);
Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
L = 100;             % Length of signal
t = (0:L-1)*T;        % Time vector

j = (0.5e-5<t)&(t<1.5e-5);
F = fft(j);
yrevon = ifft(F);
Y = complex2real(F);  %generates a structure of 'real' amplitudes and phases
subplot(1,2,1)
plot(t,j);

P2 = abs(F/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

subplot(1,2,2);
f = Fs*(0:(L/2))/L;
plot(f,P1);
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');

%%

[g, d1] = lowpass(single(j),1e5,5e6,'StopbandAttenuation', 20, 'ImpulseResponse', 'fir');
figure(10);
subplot(1,2,1);
plot(t,g);
subplot(1,2,2);
plot(t,single(j));



%%
function [Y,t] = complex2real(F,t)
%Y = complex2real(F,[t])
%
%Returns the real-valued amplitudes and phases in a structure calcullated
%from the complex-valued vector F having the convention of fft's output.
%This is the inverse of the function 'real2complex'.
%
%Inputs:
%   F        complex-valued vector in the convention of fft's output.
%   t        time vector of size y (default is 1:length(F));
%
%Outputs:    Structure Y with fields:
%   dc       mean value of y
%   amp      vector of amplitudes (length ceil(length(t)/2))
%   ph       vector of phases (in degrees, cosine phase)
%   nt       length of t (needed for myifft)
%
%SEE ALSO    real2complex fft ifft
%
%Example:
%
%t = 0:.01:.99;
%y=t<.5; 
%Y = complex2real(fft(y),t);
%clf;subplot(1,2,1);stem(t,y);
%xlabel('Time (s)');
%subplot(1,2,2);stem(Y.freq,Y.amp);
%xlabel('Frequency (Hz)')

%4/15/09     Written by G.M. Boynton at the University of Washington


%Deal with defaults
if ~exist('t','var')
    t = 1:length(F);
end

if isempty(t)
    t = 1:length(F);
end

%Calculate values based on t
nt = length(t);
dt = t(2)-t(1);

%DC is first value scaled by nt
dc = F(1)/nt;
%'real' amplitudes scale the fft by 2/nt
amp = 2*abs(F)/nt;
%'real' phases are reversed (and converted to degrees)
ph = -180*angle(F)/pi;

%Pull out the first half (omitting 'negative' frequencies)
id = 2:(ceil(nt/2)+1);
if size(F,2) == 1;
    id = id';
end

%Stuff the values in to the fields of Y
Y.dc = dc;
Y.ph = ph(id); %cosine phase
Y.amp = amp(id);
Y.freq = (1:length(id))/(nt*dt);
if size(F,2) == 1;
    Y.freq = Y.freq';
end

%Hack to deal with even vs. odd lengths of time series

if mod(nt,2) %length is odd
    Y.amp(end) = 0;
else %length is even
    Y.amp(end) = Y.amp(end)/2;
end

Y.nt= nt;



end
%%
function y = doFilter(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 14-Jun-2021 13:41:47

persistent Hd;

if isempty(Hd)
    
    Fpass = 200000;   % Passband Frequency
    Fstop = 561100;   % Stopband Frequency
    Apass = 1;        % Passband Ripple (dB)
    Astop = 20;       % Stopband Attenuation (dB)
    Fs    = 5000000;  % Sampling Frequency
    
    h = fdesign.lowpass('fp,fst,ap,ast', Fpass, Fstop, Apass, Astop, Fs);
    
    Hd = design(h, 'kaiserwin', ...
        'MinOrder', 'any');
    
    set(Hd, 'Arithmetic', 'single');
    
    set(Hd,'PersistentMemory',true);
    
end

y = filter(Hd,x);
end
%%
function y = doFilter2(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 14-Jun-2021 14:45:45

persistent Hd;

if isempty(Hd)
    
    Fpass = 100000;   % Passband Frequency
    Fstop = 476800;   % Stopband Frequency
    Apass = 1;        % Passband Ripple (dB)
    Astop = 20;       % Stopband Attenuation (dB)
    Fs    = 5000000;  % Sampling Frequency
    
    h = fdesign.lowpass('fp,fst,ap,ast', Fpass, Fstop, Apass, Astop, Fs);
    
    Hd = design(h, 'ifir');
    
    set(Hd.Stage(0), 'Arithmetic', 'fixed', ...
        'InputWordLength', 16, ...
        'InputFracLength', 15, ...
        'CoeffWordLength', 16, ...
        'CoeffAutoScale', true, ...
        'FilterInternals', 'Fullprecision');
    set(Hd.Stage(2), 'Arithmetic', 'fixed', ...
        'InputWordLength', 16, ...
        'InputFracLength', 15, ...
        'CoeffWordLength', 16, ...
        'CoeffAutoScale', true, ...
        'FilterInternals', 'Fullprecision');
    
    
    set(Hd,'PersistentMemory',true);
    
end

y = filter(Hd,x);
end
