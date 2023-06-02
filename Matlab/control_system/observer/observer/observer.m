function [out] = observer(y1, y2, u, L, A, B)
    % Lucas Koerner 
    % 2022/12/06
    % fixed point design of x3 2x2 * 2x1 matrix multiplication and then sum

    % inputs 
    % y1, y2, y3, L, A, B
    persistent yest;
    if isempty(yest)
        %yest = fi([0 0]', 1, 33);
        yest = [0 0]';
    end

    Lm = reshape(L,2,2);
    Am = reshape(A,2,2);
    Bm = reshape(B,2,1); % this is a Nx1 vector so reshape is uncessary 

    yest(:) = Am*yest + Bm*u + Lm*[y1 y2]'; 
    out = yest;
end

% DSP slices with 25 x 18 multiplier, 48-bit accumulator, and pre-adder
% for high-performance filtering, including optimized symmetric
% coefficient filtering.
