function [out] = matrix_mul_fixedpt(A, B)
    % Lucas Koerner 
    % 2022/12/06
    % fixed point design of 2x2 * 2x1 matrix multiplication

    % inputs 
    % A,B

    Am = reshape(A,2,2);
    Bm = reshape(B,2,1); % this is a Nx1 vector so reshape is uncessary 

    out = Am*Bm;

end

% function fm = my_fimath()
% 	fm = fimath('RoundingMethod', 'Floor',...
% 	     'OverflowAction', 'Wrap',...
% 	     'ProductMode','FullPrecision',...
% 	     'MaxProductWordLength', 128,...
% 	     'SumMode','FullPrecision',...
% 	     'MaxSumWordLength', 128);
% end

% DSP slices with 25 x 18 multiplier, 48-bit accumulator, and pre-adder
% for high-performance filtering, including optimized symmetric
% coefficient filtering.
