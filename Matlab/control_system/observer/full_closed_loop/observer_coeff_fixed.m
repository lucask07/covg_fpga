function [Ldp_f, Bdp_f, Adp_f] = observer_coeff_fixed(Ldp, Bdp, Adp)

    fprintf("Calculating fixed point Observer Coefficients\n");
    Ldp_f(1,1) = fi(-Ldp(1,1), 1, 32, 50); % negative because the measured current is inverted by the daughter-card
    Ldp_f(2,1) = fi(-Ldp(2,1), 1, 32, 50); % negative because the measured current is inverted by the daughter-card
    Ldp_f(1,2) = fi(Ldp(1,2), 1, 32, 50);
    Ldp_f(2,2) = fi(Ldp(2,2), 1, 32, 50);
    Adp_f(1,1) = fi(Adp(1,1), 1, 32, 24);
    Adp_f(2,1) = fi(Adp(2,1), 1, 32, 24);
    Adp_f(1,2) = fi(Adp(1,2), 1, 32, 24);
    Adp_f(2,2) = fi(Adp(2,2), 1, 32, 24);
    Bdp_f(1,1) = fi(Bdp(1,1), 1, 32, 50); % why are these coefficients unsigned? only changes the value if negative
    Bdp_f(2,1) = fi(Bdp(2,1), 1, 32, 50); % why are these coefficients unsigned?

end