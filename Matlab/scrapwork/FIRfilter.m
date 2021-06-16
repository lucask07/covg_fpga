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
