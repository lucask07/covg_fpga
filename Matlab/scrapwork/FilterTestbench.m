%% Input
Fs = 5e6;            % Sampling frequency                    
T = 1/Fs;             % Sampling period       
L = 100;             % Length of signal
t = (0:L-1)*T;        % Time vector

%j = 4.096*(t>1e-5);
%j = 4.096*((0.5e-5<t)&(t<1.5e-5));
j = (4.096*(t>1e-5))-(4.096/2);

%codes = int16.empty;
for x = (1:L)
    if (j(x)/4.096)>0
        code = int16((j(x)/4.096)*(2^15-1));
    elseif (j(x)/4.096)<0
        code = int16((j(x)/4.096)*(2^15));
    else
        code = int16(0);
    end
    %codes = [codes; code];
    out = IIRfilter(code);
end

%out = IIRfilter(codes);