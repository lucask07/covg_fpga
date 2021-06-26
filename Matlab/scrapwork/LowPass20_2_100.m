%% Input
%%Time specifications:
   Fs = 5e6;                   % samples per second
   dt = 1/Fs;                   % seconds per sample
   StopTime = 10e-6;             % seconds
   t = (0:dt:StopTime-dt)';     % seconds
   %%Sine wave:
   Fc = 200000;                     % hertz
   j = 4.096*cos(2*pi*Fc*t);
%%
O = numerictype([],16,0);
codes = fi('numerictype', O);
figure(1);
%loop that takes the input step function and outputs the hex codes that the
%AD7961 would output

for x = (1:length(t))
    if (j(x)/4.096)>0
        %code = int16((j(x)/4.096)*(2^15-1));
        code = fi((j(x)/4.096)*(2^15-1), 'numerictype', O);
    elseif (j(x)/4.096)<0
        %code = int16((j(x)/4.096)*(2^15));
        code = fi((j(x)/4.096)*(2^15), 'numerictype', O);
    else
        %code = int16(0);
        code = fi(0, 'numerictype', O);
    end
    codes = [codes; code];
%     out = IIRfilter(code);
%     out = BesselApproxFIR(code);
%     out = untitled(code);
%     plot(t(x), out, '*');
%     hold on;
end
%plot(t, codes/32767);%normalized the step function here to be able to view both filter output and step voltage
plot(t, codes);
title('Original Signal and Step Response of IIR LP filter');
xlabel('t[s]');
ylabel('Amplitude');


% plotting the original step function and then the hex codes
% figure(2);
% subplot(1,2,1);
% plot(t,j);
% subplot(1,2,2);
% plot(t, codes);
% subplot(1,3,3);
% plot(t, fi(codes));

%%
%%Time specifications:
   Fs = 5e6;                   % samples per second
   dt = 1/Fs;                   % seconds per sample
   StopTime = 100000e-6;             % seconds
   t = (0:dt:StopTime-dt)';     % seconds
   %%Sine wave:
   Fc = 200000;                     % hertz
   x = 0.08*cos(2*pi*Fc*t)+4.096*cos(2*pi*(Fc/10000)*t);
   % Plot the signal versus time:
   figure(2);
   plot(t,x);
   xlabel('time (in seconds)');
   title('Signal versus Time');
   zoom xon;
%% Sampling and constants

fc = 2000;
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

%% Use the filter to process a signal

t = 0:1/fs:2;

x = cos(2*pi*(5).*t) + cos(2*pi*(10).*t) + cos(2*pi*(50).*t);

nfft = 10*numel(x);
f = fs.*(-nfft/2:nfft/2-1)./nfft;

figure;
subplot(2, 1, 1);
plot(f, abs(fftshift(fft(x, nfft)./nfft)).^2);
xlim([-100 100])
xlabel("Frequency (Hz)");
ylabel("Magnitude");
title("Original Signal");

subplot(2, 1, 2);
plot(f, abs(fftshift(fft(filter(b, a, x), nfft)./nfft)).^2);
xlim([-100 100])
xlabel("Frequency (Hz)");
ylabel("Magnitude");
title("Filtered Signal");