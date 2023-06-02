function [b0_f, b1_f, a1_f] = pi_coeff_fixed(b0, b1, a1)

fprintf("Calculating fixed point PI Coefficients\n");
b0_f = fi(-b0/2, 1, 32, 29);
b1_f = fi(-b1/2, 1, 32, 29);
a1_f =  fi(-a1, 1, 32, 30);  % TODO: check this sign, was originally a1 

end