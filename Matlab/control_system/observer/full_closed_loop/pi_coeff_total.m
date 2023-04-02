function [b0_h, b1_h, a1_h] = pi_coeff_total(Ac, fc_pi, Ts, open_loop)

    % both functions together so that this can be called in total from
    % Python
    [b0,b1,a1,~] = pi_controller_coeff(Ac, fc_pi, Ts, open_loop);  
    [b0_f, b1_f, a1_f] = pi_coeff_fixed(b0, b1, a1);

    b0_h = (int(b0_f));
    b1_h = (int(b1_f));
    a1_h = (int(a1_f));    

end