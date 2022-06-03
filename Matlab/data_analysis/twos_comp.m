function [val] = twos_comp(val, bits)
%%%compute the 2's complement of int value val
%    handle an array (list or numpy)
%%%

val = val - 2*bitand(val, 2^(bits-1));

end