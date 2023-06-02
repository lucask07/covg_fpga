function obsvInfo = obsvEnhanced(A,C) 
% FUNCTION: OBSVENHANCED 
% PURPOSE: PROVIDE AN ENHANCED VERSION OF OBSV  
%    
% SYNTAX:   
% function obsvInfo = obsvEnhanced(A,C) 
% 
% INPUTS: 
% A - System matrix 
% C - Output matrix
% 
% OUTPUTS: 
% obsvInfo - Structure
% 
% See also ctrbEnhanced 
%
% AUTHOR    : Tom Secord 
% DATE      : Sat 13-Mar-2021 at 4:35:40 PM 
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
obsvMat = obsv(A,C);

[nR,nC] = size(obsvMat);

if nR == nC % Then matrix is square and determinant can be computed
    obsvInfo.obsvMatrixDet = det(obsvMat);
else
    obsvInfo.obsvMatrixDet = 'N/A. System has multiple outputs';
end
    
obsvInfo.obsvMatrixRank = rank(obsvMat);
obsvInfo.obsvMatrixCondNum = cond(obsvMat);
obsvInfo.obsvMatrix = obsvMat;

if rank(obsvMat) == min(nR,nC)
    obsvInfo.conclusion = 'System is Observable';
else
    obsvInfo.conclusion = 'System is Not Observable';
end
%--------------------------------------------------------------------------