function [b0,b1,a1,Gc] = pi_controller_coeff(Ac, fc_pi, Ts, open_loop)

% ----------- PI Controller Design -------------
s = tf('s');
%Ac = 5; % Lower for less agressive bandwidth. 5 was nominal design
%fc_pi = 5e3;
Gc = -Ac*(s+fc_pi*2*pi)/s;  % nominally 5 kHz
Gcd = c2d(Gc,Ts,'tustin');

b0 = Gcd.num{1}(1);
b1 = Gcd.num{1}(2);
a1 = -1;

if open_loop % make the PI filter a direct pass through
    b0=1;
    b1=0;
    a1=0;
end

