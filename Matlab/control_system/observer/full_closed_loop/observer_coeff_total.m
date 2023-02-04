function [Ldp_h, Bdp_h, Adp_h] = observer_coeff_total(Ts, RF, C1, Im_scale, VP1_scale, dac_scale, total_scale)

    % both functions together so that this can be called in total from
    % Python
    [Ldp, Bdp, Adp] = observer_coeff(Ts, RF, C1, Im_scale, VP1_scale, dac_scale, total_scale);    
    [Ldp_f, Bdp_f, Adp_f] = observer_coeff_fixed(Ldp, Bdp, Adp);

    Ldp_h = (int(Ldp_f));
    Bdp_h = (int(Bdp_f));
    Adp_h = (int(Adp_f));    

end