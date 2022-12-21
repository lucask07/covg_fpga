%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                          %
%          Generated by MATLAB 9.12 and Fixed-Point Designer 7.4           %
%                                                                          %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%#codegen
function [out] = observer_fixpt(y1, y2, u, L, A, B)
    % Lucas Koerner 
    % 2022/12/06
    % fixed point design of x3 2x2 * 2x1 matrix multiplication and then sum

    % inputs 
    % y1, y2, y3, L, A, B
    fm = get_fimath();

    persistent yest;
    if isempty(yest)
        %yest = fi([0 0]', 1, 33);
        yest = fi([0 0]', 1, 16, 17, fm);
    end

    Lm = fi(reshape(L,2,2), 1, 16, 32, fm);
    Am = fi(reshape(A,2,2), 1, 16, 5, fm);
    Bm = fi(reshape(B,2,1), 0, 16, 38, fm); % this is a Nx1 vector so reshape is uncessary 

    yest(:) = Am*yest + Bm*u + Lm*[fi(y1, 1, 16, 0, fm) y2]'; 
    out = fi(yest, 1, 16, 17, fm);
end


function fm = get_fimath()
	fm = fimath('RoundingMethod', 'Floor',...
	     'OverflowAction', 'Wrap',...
	     'ProductMode','FullPrecision',...
	     'SumMode','FullPrecision');
end
