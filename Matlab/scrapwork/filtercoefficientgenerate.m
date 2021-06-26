fc = 200e3;
fs = 5e6;
stop = 400e3;

% Wp = fc/(fs/2);
% Ws = stop/(fs/2);
% [n,Wn] = buttord(Wp,Ws,1,20);
% [z, p, k] = butter(n, Wn);
[z, p, k] = butter(4, fc/(fs/2));

%freqz(b,a)
[sos, g] = zp2sos(z, p, k, 'down');
freqz(sos);