function y = SinglePoleIIRFunction(x)
%DOFILTER Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 30-Jul-2021 19:01:04

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    % The following code was used to design the filter coefficients:
    %
    % N    = 1;        % Order
    % F3dB = 400;      % 3-dB Frequency
    % Fs   = 2500000;  % Sampling Frequency
    %
    % h = fdesign.lowpass('n,f3db', N, F3dB, Fs);
    %
    % Hd = design(h, 'butter', ...
    %     'SystemObject', true);
    
    Hd = dsp.BiquadFilter( ...
        'Structure', 'Direct form II', ...
        'SOSMatrix', [1 1 0 1 -0.998995195336138 0], ...
        'ScaleValues', [0.000502402331930983; 1], ...
        'SectionInputDataType', 'Custom', ...
        'CustomSectionInputDataType', numerictype([],16,20), ...
        'SectionOutputDataType', 'Custom', ...
        'CustomSectionOutputDataType', numerictype([],16,11), ...
        'NumeratorCoefficientsDataType', 'Custom', ...
        'CustomNumeratorCoefficientsDataType', numerictype([],32,30), ...
        'DenominatorCoefficientsDataType', 'Custom', ...
        'CustomDenominatorCoefficientsDataType', numerictype([],32,30), ...
        'ScaleValuesDataType', 'Custom', ...
        'CustomScaleValuesDataType', numerictype([],32,41), ...
        'NumeratorProductDataType', 'Custom', ...
        'CustomNumeratorProductDataType', numerictype([],48,45), ...
        'DenominatorProductDataType', 'Custom', ...
        'CustomDenominatorProductDataType', numerictype([],48,45), ...
        'NumeratorAccumulatorDataType', 'Custom', ...
        'CustomNumeratorAccumulatorDataType', numerictype([],50,45), ...
        'DenominatorAccumulatorDataType', 'Custom', ...
        'CustomDenominatorAccumulatorDataType', numerictype([],50,45), ...
        'StateDataType', 'Custom', ...
        'CustomStateDataType', numerictype([],16,15), ...
        'OutputDataType', 'Custom', ...
        'CustomOutputDataType', numerictype([],14,9), ...
        'RoundingMethod', 'Convergent');
end

s = fi(x,1,16,15,'RoundingMethod', 'Round', 'OverflowAction', 'Saturate');
y = step(Hd,s);

