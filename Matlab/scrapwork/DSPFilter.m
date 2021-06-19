%% DSP Filter
%% Input
Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
L = 100;             % Length of signal
t = (0:L-1)*T;        % Time vector

O = numerictype([],16,0);
%below are a bunch of step functions that are being input into the for loop
%j = 0.0002*(t>1e-5);
j = 4.096*(t>1e-5);
%j = fi(j, 'numerictype', O);
%j = (4.096*(t>1e-5))-(4.096/2);
%j = 4.096*((0.5e-5<t)&(t<1.5e-5));
%F = fft(j);

%c1 = numerictype([],16,0);
%codes = int16.empty;
codes = fi('numerictype', O);
figure(1);
%loop that takes the input step function and outputs the hex codes that the
%AD7961 would output
for x = (1:L)
    if (j(x)/4.096)>0
        %code = int16((j(x)/4.096)*(2^15-1));
        code = fi((j(x)/4.096)*(2^15-1), 'numerictype', O);
    elseif (j(x)/4.096)<0
        %code = int16((j(x)/4.096)*(2^15));
        code = fi((j(x)/4.096)*(2^15), 'numerictype', O);
    else
        %code = int16(0);
        code = fi(0, 'numerictype', O);
    end
    codes = [codes; code];
    out = IIRfilter(code);
    plot(t(x), out, '*');
    hold on;
end
plot(t, codes/32767);%normalized the step function here to be able to view both filter output and step voltage
title('Original Signal and Step Response of IIR LP filter');
xlabel('t[s]');
ylabel('Amplitude');


%plotting the original step function and then the hex codes
figure(2);
subplot(1,2,1);
plot(t,j);
subplot(1,2,2);
plot(t, codes);
% subplot(1,3,3);
% plot(t, fi(codes));

%% Plotting the outputs of several filters...filter type is listed in the title of each graph
figure(3);
out = doFilter(codes);
subplot(2,2,1);
plot(t,codes);
title('Original Signal');
xlabel('t[s]');
ylabel('Amplitude');

subplot(2,2,2);
plot(t, out);
title('Filtered Signal (Filter Builder - FIR)');
xlabel('t[s]');
ylabel('Amplitude');

subplot(2,2,3);
out2 = FIRfilter(codes);
plot(t, out2);
title('Filtered Signal (Filter Designer - FIR)');
xlabel('t[s]');
ylabel('Amplitude');

subplot(2,2,4);
out3 =IIRfilter(codes);
plot(t, out3);
title('Filtered Signal (Filter Designer - IIR)');
xlabel('t[s]');
ylabel('Amplitude');

%figure(4);
% %subplot(3,2,4);
% out4 =IIR(codes);
% plot(t, 2^8*out4);
% title('Filtered Signal (Filter Builder - IIR)');
% xlabel('t[s]');
% ylabel('Amplitude');


% numerator = [1, 2, 3];
% denominator = [3, 2, 1];
% tf(numerator, denominator, 200, 'nanoseconds');
%% Working on making a filter identical to the IIR filter in figure 3, subplot (2, 2, 4) but using the dsp.SOSFilter function(s)
figure(4);

% sos = [1 2 1 1 -1.72868912225509 0.822065283793064; 1 2 1 1 ...
%         -1.51115501871521 0.592780947472364; 1 1 0 1 -0.720925717959358 0];
% y = sosfilt(sos, double(codes));
sos = dsp.SOSFilter('Structure', 'Direct Form II',... 
        'CoefficientSource', 'Input port',...
        'HasScaleValues', true,...
        'RoundingMethod', 'Convergent',...
        'SectionInputDataType', numerictype(1,16,11),...
        'SectionOutputDataType', numerictype(1,16,10),...
        'ScaleValuesDataType', numerictype(1,16,17),...
        'StateDataType', numerictype(1,16,15),...
        'DenominatorAccumulatorDataType', numerictype(1,34,29),...
        'OutputDataType', numerictype(1,14,8));
    
%'NumeratorDataType', numerictype([],16,13),...
%'DenominatorDataType', numerictype([],16,14),...
%'HasScaleValues', true,...
%'ScaleValues',[0.0233440403844928; 0.0204064821892894; 0.139537141020321; 1], ...

%         'SectionInputDataType', 'Custom', ...
%         'CustomSectionInputDataType', numerictype([],16,11), ...
%         'SectionOutputDataType', 'Custom', ...
%         'CustomSectionOutputDataType', numerictype([],16,10), ...
%         'NumeratorCoefficientsDataType', 'Custom', ...
%         'CustomNumeratorCoefficientsDataType', numerictype([],16,13), ...
%         'DenominatorCoefficientsDataType', 'Custom', ...
%         'CustomDenominatorCoefficientsDataType', numerictype([],16,14), ...
%         'ScaleValuesDataType', 'Custom', ...
%         'CustomScaleValuesDataType', numerictype([],16,17), ...
%         'NumeratorProductDataType', 'Custom', ...
%         'CustomNumeratorProductDataType', numerictype([],32,28), ...
%         'DenominatorProductDataType', 'Custom', ...
%         'CustomDenominatorProductDataType', numerictype([],32,29), ...
%         'NumeratorAccumulatorDataType', 'Custom', ...
%         'CustomNumeratorAccumulatorDataType', numerictype([],34,28), ...
%         'DenominatorAccumulatorDataType', 'Custom', ...
%         'CustomDenominatorAccumulatorDataType', numerictype([],34,29), ...
%         'StateDataType', 'Custom', ...
%         'CustomStateDataType', numerictype([],16,15), ...
%         'OutputDataType', 'Custom', ...
%         'CustomOutputDataType', numerictype([],14,8), ...
%         'RoundingMethod', 'Convergent');
n = numerictype(1,16,13);
%num = fi([1 2 1; 1 2 1; 1 1 0], 'numerictype', n);
num = fi([1 2 1; 1 2 1; 1 1 0], 'numerictype', n);

d = numerictype(1,16,14);
%den = fi([1 -1.72868912225509 0.822065283793064; 1 -1.51115501871521...
%    0.592780947472364; 1 -0.720925717959358 0], 'numerictype', d);
den = fi([1 -0.72868912225509 0.822065283793064; 1 -0.51115501871521...
    0.592780947472364; 1 -0.120925717959358 0], 'numerictype', d);

G = numerictype(1,16,17);
g = fi([0.0233440403844928 0.0204064821892894 0.139537141020321 1],...
    'numerictype', G);

y = sos(codes, num, den, g);

plot(t, y);
%hold on;
%plot(t, codes);


%% making FIR filter with tunable coefficients

% All frequency values are in Hz.
Fs = 5000000;  % Sampling Frequency

Fpass = 2000000;         % Passband Frequency
Fstop = 2200000;         % Stopband Frequency
Dpass = 0.057501127785;  % Passband Ripple
Dstop = 0.1;             % Stopband Attenuation
flag  = 'scale';         % Sampling Flag

% Calculate the order from the parameters using KAISERORD.
[N,Wn,BETA,TYPE] = kaiserord([Fpass Fstop]/(Fs/2), [1 0], [Dstop Dpass]);

% Calculate the coefficients using the FIR1 function.
b  = fir1(N, Wn, TYPE, kaiser(N+1, BETA), flag);
coeff = fi(b, 'numerictype', numerictype(1, 16, 15));

Hd = dsp.FIRFilter('FullPrecisionOverride', false,...
        'Structure', 'Direct form', ...
        'NumeratorSource', 'Input port',...
        'RoundingMethod', 'Convergent',...
        'ProductDataType', 'Custom',...
        'CustomProductDataType', numerictype(1,31,30),...
        'AccumulatorDataType', 'Custom',...
        'CustomAccumulatorDataType', numerictype(1,33,30),...
        'OutputDataType', 'Custom', ...
        'CustomOutputDataType', numerictype(1,14,8));
    
out5 = Hd(codes, coeff);
figure(5);
plot(t, out5);

%% DSP Filter function
function y = doFilter(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 14-Jun-2021 14:45:45

persistent Hd;

if isempty(Hd)
    
    Fpass = 300000;   % Passband Frequency
    Fstop = 476800;   % Stopband Frequency
    Apass = 1;        % Passband Ripple (dB)
    Astop = 20;       % Stopband Attenuation (dB)
    Fs    = 5000000;  % Sampling Frequency
    
    h = fdesign.lowpass('fp,fst,ap,ast', Fpass, Fstop, Apass, Astop, Fs);
    
    Hd = design(h, 'ifir');
    
    set(Hd.Stage(1), 'Arithmetic', 'fixed', ...
        'InputWordLength', 16, ...
        'InputFracLength', 0, ...
        'CoeffWordLength', 16, ...
        'CoeffAutoScale', true, ...
        'FilterInternals', 'Fullprecision');
    set(Hd.Stage(2), 'Arithmetic', 'fixed', ...
        'InputWordLength', 16, ...
        'InputFracLength', 0, ...
        'CoeffWordLength', 16, ...
        'CoeffAutoScale', true, ...
        'FilterInternals', 'Fullprecision');
    
    
    set(Hd,'PersistentMemory',true);
    
end

y = filter(Hd,x);
end
%% FIR filter (filter designer)
function y = FIRfilter(x)
%FIRFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 15-Jun-2021 09:57:17

%#codegen

% To generate C/C++ code from this function use the codegen command. Type
% 'help codegen' for more information.

% The following code was used to design the filter coefficients:
% % Interpolated FIR Lowpass filter designed using the IFIR function.
%
% % All frequency values are in Hz.
% Fs = 5000000;  % Sampling Frequency
%
% Fpass = 200000;          % Passband Frequency
% Fstop = 476800;          % Stopband Frequency
% Dpass = 0.057501127785;  % Passband Ripple
% Dstop = 0.1;             % Stopband Attenuation
% L     = 4;               % Interpolation Factor
%
% % Calculate the coefficients using the IFIR function.
% [h, g] = ifir(L, 'low', [Fpass Fstop]/(Fs/2), [Dpass Dstop]);


%% Construction
persistent filter1 filter2
if isempty(filter1)
    filter1 = dsp.FIRFilter(  ...
        'Numerator', [-0.07502182644916526 0 0 0 0.080795018473145214 0 0 0 ...
        0.48502135547034186 0 0 0 0.48502135547034186 0 0 0 0.080795018473145214 ...
        0 0 0 -0.07502182644916526]);
    filter2 = dsp.FIRFilter(  ...
        'Numerator', [-0.038541944347873509 -0.0070793099742488558 ...
        0.026205668845601996 0.081486429744326239 0.14460708478219247 ...
        0.1949004698410795 0.2140890789562408 0.1949004698410795 ...
        0.14460708478219247 0.081486429744326239 0.026205668845601996 ...
        -0.0070793099742488558 -0.038541944347873509]);
end


%% Process
y1 = filter1( x );
y  = filter2( y1);




% [EOF]
end

%% IIR filter

function y = IIRfilter(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 15-Jun-2021 12:26:08

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    % The following code was used to design the filter coefficients:
    %
    % Fpass = 200000;   % Passband Frequency
    % Fstop = 400000;   % Stopband Frequency
    % Apass = 1;        % Passband Ripple (dB)
    % Astop = 20;       % Stopband Attenuation (dB)
    % Fs    = 5000000;  % Sampling Frequency
    %
    % h = fdesign.lowpass('fp,fst,ap,ast', Fpass, Fstop, Apass, Astop, Fs);
    %
    % Hd = design(h, 'butter', ...
    %     'MatchExactly', 'stopband', ...
    %     'SystemObject', true);
    
    Hd = dsp.BiquadFilter( ...
        'Structure', 'Direct form II', ...
        'SOSMatrix', [1 2 1 1 -1.72868912225509 0.822065283793064; 1 2 1 1 ...
        -1.51115501871521 0.592780947472364; 1 1 0 1 -0.720925717959358 0], ...
        'ScaleValues', [0.0233440403844928; 0.0204064821892894; ...
        0.139537141020321; 1], ...
        'SectionInputDataType', 'Custom', ...
        'CustomSectionInputDataType', numerictype([],16,11), ...
        'SectionOutputDataType', 'Custom', ...
        'CustomSectionOutputDataType', numerictype([],16,10), ...
        'NumeratorCoefficientsDataType', 'Custom', ...
        'CustomNumeratorCoefficientsDataType', numerictype([],16,13), ...
        'DenominatorCoefficientsDataType', 'Custom', ...
        'CustomDenominatorCoefficientsDataType', numerictype([],16,14), ...
        'ScaleValuesDataType', 'Custom', ...
        'CustomScaleValuesDataType', numerictype([],16,17), ...
        'NumeratorProductDataType', 'Custom', ...
        'CustomNumeratorProductDataType', numerictype([],32,28), ...
        'DenominatorProductDataType', 'Custom', ...
        'CustomDenominatorProductDataType', numerictype([],32,29), ...
        'NumeratorAccumulatorDataType', 'Custom', ...
        'CustomNumeratorAccumulatorDataType', numerictype([],34,28), ...
        'DenominatorAccumulatorDataType', 'Custom', ...
        'CustomDenominatorAccumulatorDataType', numerictype([],34,29), ...
        'StateDataType', 'Custom', ...
        'CustomStateDataType', numerictype([],16,15), ...
        'OutputDataType', 'Custom', ...
        'CustomOutputDataType', numerictype([],14,8), ...
        'RoundingMethod', 'Convergent');
end

s = fi(x,1,16,15,'RoundingMethod', 'Round', 'OverflowAction', 'Saturate');
y = step(Hd,s);
end

%%

function y = IIR(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 15-Jun-2021 12:34:07

persistent Hd;

if isempty(Hd)
    
    Fpass = 200000;   % Passband Frequency
    Fstop = 400000;   % Stopband Frequency
    Apass = 1;        % Passband Ripple (dB)
    Astop = 20;       % Stopband Attenuation (dB)
    Fs    = 5000000;  % Sampling Frequency
    
    h = fdesign.lowpass('fp,fst,ap,ast', Fpass, Fstop, Apass, Astop, Fs);
    
    Hd = design(h, 'butter', ...
        'MatchExactly', 'stopband', ...
        'SOSScaleNorm', 'Linf');
    
    set(Hd, 'Arithmetic', 'fixed', ...
        'InputWordLength', 16, ...
        'InputFracLength', 0, ...
        'CoeffWordLength', 16, ...
        'CoeffAutoScale', true, ...
        'SectionInputWordLength', 16, ...
        'SectionInputAutoScale', true, ...
        'SectionOutputWordLength', 16, ...
        'SectionOutputAutoScale', true, ...
        'StateWordLength', 16, ...
        'StateFracLength', 15, ...
        'ProductMode', 'Fullprecision', ...
        'AccumMode', 'KeepMSB', ...
        'AccumWordLength', 40, ...
        'CastBeforeSum', true, ...
        'OutputWordLength', 14, ...
        'OutputMode', 'Avoidoverflow', ...
        'RoundMode', 'convergent', ...
        'OverflowMode', 'wrap');
    
    set(Hd,'PersistentMemory',true);
    
end

y = filter(Hd,x);
end
