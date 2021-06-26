%% Sampling and constants

fc = 500000;
fs = 5e6;
fn = fs/2;

% fc = 20;
% fs = 60e3;
% fn = fs/2;

q = 1/sqrt(2);
Q = 1/q;
%Q = 5;
Fc = 2*sin(pi*fc/fs);

%% Manually define the transfer function. Uncomment to generate and manually plot the frequency response.
% f = logspace(-10, pi, 1e5);
% w = 2.*pi.*f;
% z = exp(-1i.*w);
% 
% freqResponse = (Fc.^2.*z)./(1 - z.*(2 - Q.*Fc - Fc.^2) + z.^2.*(1 - Q.*Fc));
% 
% figure;
% semilogx(f, 20*log10(abs(freqResponse)));
% xlabel("Normalized Frequency (Hz/sample)");
% ylabel("Magnitude (dB)");
% axis tight;
% ylim([-120 10]);

%% Using built-in function filter()

b = [0 Fc.^2];
a = [1 -(2 - Q.*Fc - Fc.^2) (1 - Q.*Fc)];
[h, w] = freqz(b, a, 1e5);
%sos = [0 Fc.^2 0 1 -(2 - Q.*Fc - Fc.^2) (1 - Q.*Fc) ; 0 Fc.^2 0 1 -(2 - Q.*Fc - Fc.^2) (1 - Q.*Fc)];
sos = [0 Fc.^2 0 1 -(2 - Q.*Fc - Fc.^2) (1 - Q.*Fc)];
figure;
semilogx(w./(2*pi), 20*log10(abs(h)));
axis tight;
ylim([-120 10]);