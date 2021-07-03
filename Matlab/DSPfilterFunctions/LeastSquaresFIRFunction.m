function y = LeastSquaresFIRFunction(x)
%LEASTSQUARESFIRFUNCTION Filters input x and returns output y.

% MATLAB Code
% Generated by MATLAB(R) 9.9 and DSP System Toolbox 9.11.
% Generated on: 30-Jun-2021 13:38:43

%#codegen

% To generate C/C++ code from this function use the codegen command.
% Type 'help codegen' for more information.

persistent Hd;

if isempty(Hd)
    
    % Numerator coefficient vector
    Numerator = [-0.018089 0.029217 0.091916 0.15511 0.20194 0.21921 ...
        0.20194 0.15511 0.091916 0.029217 -0.018089];
    
    Hd = dsp.FIRFilter( ...
        'Numerator', Numerator, ...
        'CoefficientsDataType', 'Custom', ...
        'CustomCoefficientsDataType', numerictype(true,16,17));
end

s = fi(x,1,16,15,'RoundingMethod','Round','OverflowAction','Saturate');
y = step(Hd,s);


% [EOF]
end