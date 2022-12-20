function L = placeO(A,C,pDesO) 
% FUNCTION: PLACEO 
% PURPOSE: SERVE AS AN ANALOG TO THE PLACE FUNCTION FOR OBSERVER DESIGN 
%    
% SYNTAX:   
% function L = placeO(A,C,pDesO) 
% 
% INPUTS: 
% A - System matrix 
% C - Output matrix
% pDesO - Desired pole location array
% 
% OUTPUTS: 
% L - observer gain matrix 
% 
% See also ackerO 
%
% AUTHOR    : Tom Secord 
% DATE      : Sun 18-Apr-2021 at10:34:45 AM 
% REVISION  : 1.00 
% DEVELOPED : 9.6.0.1072779 (R2019a) 


% INPUT CHECKING
%--------------------------------------------------------------------------
if nargin == 0
clc
help(mfilename);
return
end
%--------------------------------------------------------------------------


% CALCULATIONS
%--------------------------------------------------------------------------
L = place(A',C',pDesO)';
%--------------------------------------------------------------------------