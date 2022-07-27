%% Ian Delgadillo Bonequi
clear all;
close all;
clc;
%% Plot CMD Signal

%Grab CMD data from .h5 file
% y = hdf5read('SeriesResData\alpha_0.7_data.h5','/adc');
y = hdf5read('C:\Users\iande\OneDrive - University of St. Thomas\clamp test files\alpha_0.7_data.h5','/adc');
cmd_data = y(2:2:end,5);
t = (1:length(cmd_data))*400e-3;

%plot CMD
figure(1);
subplot(2, 1, 1);
plot(t, cmd_data, '-*');
xlim([6450 6750]);
ylim([5000 9200]);
grid on;
title('Cmd Signal Summed With Filtered Current Measurements');
xlabel('t (μs)');
ylabel('Hexadecimal DAC Codes');

%Now zoomed in plot
subplot(2, 1, 2);
plot(t, cmd_data, '-*');
xlim([6548 6565]);
ylim([7000 7800]);
grid on;
title('Zoomed In On Discontinuity');
xlabel('t (μs)');
ylabel('Hexadecimal DAC Codes');
saveas(figure(1), 'EndToEndLatencyMeasMATLAB.png');

%% Plot CMD Signal and Current on Same Plot

%Grab Im data from .h5 file
current_data = dec2bin(y(:,1));
current_data = typecast(uint16(bin2dec(current_data)), 'int16');
current_data = double(current_data);

%5 MSPS time array
t2 = (1:length(current_data))*200e-3;

%plot CMD
figure(2);
subplot(2, 1, 1);
plot(t, cmd_data, '-*');
hold on;

%plot Im
plot(t2, current_data*0.125 + 8192, '-*');
xlim([6450 6750]);
ylim([5000 12000]);
grid on;
title('Cmd Signal Summed and Filtered Current Measurements');
xlabel('t (μs)');
ylabel('Hexadecimal DAC/ADC Codes');
legend('CMD', 'Current Meas', 'Location', 'southwest');

%Now, zoomed in plot
subplot(2, 1, 2);
plot(t, cmd_data, '-*');
hold on;
plot(t2, current_data*0.125 + 8192, '-*');
xlim([6548 6565]);
ylim([7000 8500]);
grid on;
title('Zoomed In On Discontinuity');
xlabel('t (μs)');
ylabel('Hexadecimal DAC/ADC Codes');
legend('CMD', 'Current Meas', 'Location', 'southwest');
saveas(figure(2), 'FilterLatencyMeasMATLAB.png');

%% Plot CMD, Im, P1, and Vm

f = figure(3);
t = t-3277.2;
t2 = t2-3277.2;
set(gcf, 'Position', get(0, 'Screensize'));
tiledlayout('flow', 'TileSpacing', 'compact')
a = nexttile;
b = nexttile;
c = nexttile;
d = nexttile;

% Constants for calculating voltage/current conversion from DAC/ADC codes
ADG_RES = 100000; % Ohms
inamp_gain = 1;
AD7961_driver_gain = 0.308;
DAC_amplitude_gain = 5000; % mV
fbck_gain = 1.697;
DAQ_to_DC_gain = 0.1;
ADS_amplitude_Gain = 5000; % mV

% ADC/DAC code to voltage/current conversion factors
ADC_to_uA = (1/8)*(1/(ADG_RES*1e-6))*(1/inamp_gain)*(1/AD7961_driver_gain)*1e-3;
DAC_to_mV = (1/fbck_gain)*(DAC_amplitude_gain/2^13)*DAQ_to_DC_gain;
ADS_to_mV = (ADS_amplitude_Gain/2^15);

alphas = [0.0, 0.25, 0.5, 0.55, 0.6, 0.65, 0.75];
risetimes = [];
overshoots = [];
settlingtimes = [];

for alpha = (0:0.05:0.75)

    % Special case for α=0 .h5 file
    if(alpha == 0)
%         y = hdf5read(['SeriesResData\alpha_0.0_data.h5'],'/adc');
        y = hdf5read(['C:\Users\iande\OneDrive - University of St. Thomas\clamp test files\alpha_0.0_data.h5'],'/adc');
    else
%         y = hdf5read(['SeriesResData\alpha_', num2str(alpha, 2), '_data.h5'],'/adc');
        y = hdf5read(['C:\Users\iande\OneDrive - University of St. Thomas\clamp test files\alpha_', num2str(alpha, 2), '_data.h5'],'/adc');
    end

    % Grab CMD, Im, P1, and Vm data from .h5 file
    cmd_data = y(2:2:end,5);
    cmd_data = double(cmd_data);
    current_data = dec2bin(y(:,1));
    current_data = typecast(uint16(bin2dec(current_data)), 'int16');
    current_data = double(current_data);
    p1_data = dec2bin(y(1:10:end,8));
%     p1_data = dec2bin(y(1:5:end,8));
    p1_data = typecast(uint16(bin2dec(p1_data)), 'int16');
    p1_data = double(p1_data);
    vm_data = dec2bin(y(2:10:end,8));
%     vm_data = dec2bin(y(2:5:end,8));
    vm_data = typecast(uint16(bin2dec(vm_data)), 'int16');
    vm_data = double(vm_data);

    % 1 MSPS time array
    t3 = (1:length(p1_data))*2000e-3;
%     t3 = (1:length(p1_data))*1000e-3;
    t3 = t3-3277.2;
    
    if(isempty(setdiff(round(alpha,2), alphas)))
        % Plot CMD for current α
        axes(a);
        plot(t, (cmd_data-8192)*DAC_to_mV, '-*', 'LineWidth', 2);
        xlim([-75 175]);
        hold on;
        
        % Plot Im for current α
        axes(b)
        plot(t2, current_data*ADC_to_uA, '-*', 'LineWidth', 2);
        xlim([-75 175]);
        hold on;
        
        % Plot P1 for current α
        axes(c);
        plot(t3(1:length(p1_data)), p1_data*ADS_to_mV*(1/fbck_gain), '-*', 'LineWidth', 2);
        xlim([-75 175]);
        hold on;
    
        % Plot Vm for current α
        axes(d)
        plot(t3(1:length(vm_data)), vm_data*ADS_to_mV, '-*', 'LineWidth', 2);
        xlim([-75 175]);
        hold on;
    
        %display step response metrics for Vm
        rise_time = risetime(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000));
%         rise_time = risetime(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000));
        risetimes = [risetimes; rise_time];
        disp(['For α=',num2str(alpha,2), ' Vm rise time is: ', num2str(rise_time, 4), ' us']);

        over_shoot = overshoot(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000));
%         over_shoot = overshoot(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000));
        overshoots = [overshoots; over_shoot];
        disp(['For α=',num2str(alpha,2), ' Vm overshoot is: ', num2str(over_shoot, 4), ' %']);

        [s,slev,sinst] = settlingtime(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000), 500, 'Tolerance', 5);
%         [s,slev,sinst] = settlingtime(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000), 500, 'Tolerance', 5);
        settlingtimes = [settlingtimes; sinst];
        disp(['For α=',num2str(alpha,2), ' Vm settling time is: ', num2str(sinst, 4), ' us']);
        fprintf('\n');
    end
end

% Axes label for CMD
axes(a);
title('CMD');
xlabel('t (μs)');
ylabel('Voltage (mV)');
grid on;

% Axes label for Im
axes(b);
title('Im');
xlabel('t (μs)');
ylabel('Current (μA)');
grid on;

% Axes label for P1
axes(c);
title('P1 (tracks Vm)');
xlabel('t (μs)');
ylabel('Voltage (mV)');
grid on;

% Axes label for Vm
axes(d);
title('Vm');
xlabel('t (μs)');
ylabel('Voltage (mV)');

% Shared Legend
legend_array = {};
for i = 1:length(alphas)
    temp = ['α=', num2str(alphas(i))];
    legend_array = [legend_array; temp];
end
lgd = legend(legend_array, 'Location', 'northeast');
lgd.FontSize = 18;
lgd.Location = 'northeastoutside';
grid on;

saveas(figure(3), 'series_res_comp_data_full.png');

%% Table with Step Response Metrics

f = figure(4);
f.Units = 'normalized';
f.Position = [0.5 0.5 .236 .18 ];

data = horzcat(risetimes, overshoots, settlingtimes);
rs_table = uitable(f, 'Units', 'normalized', 'Data', data, 'ColumnName', {'Rise Time [us] ', 'Percent Overshoot ', ...
    'Settling Time [us] '}, 'RowName', legend_array, 'Position', [0 0 1 1]);
saveas(figure(4), 'std_rs_comp_step_response_metrics.png');

%% Plot Function Generator Data

figure(5);

ADS_to_V = (ADS_amplitude_Gain/(2^15*1000));
fn_gen_data = double(y(6:10:end,8));
risetime(fn_gen_data*ADS_to_V, t3);
title('Function Generator Data');
xlabel('t (μs)');
ylabel('Voltage (V)');

rise_time = risetime(fn_gen_data*ADS_to_V, t3);
disp(['Rise time is: ', num2str(mean(rise_time), 4), ' us']);
fprintf('\n');
disp(['Magnitude is: ', num2str((max(fn_gen_data*ADS_to_V) - min(fn_gen_data*ADS_to_V))/2)]);

%% FFT of Function Generator Data

figure(6);
Fs = 500e3;

Y = fft(fn_gen_data*ADS_to_V);
L = length(fn_gen_data);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
plot(f,P1); 
title('Single-Sided Amplitude Spectrum of X(t)');
xlabel('f (Hz)');
ylabel('|P1(f)|');

%% From Dr. Secord's Vm Control Driver Script

% VARIABLE AND PARAMETER DEFINITIONS - REFER TO SCHEMATIC (p 137 in notebook)
%--------------------------------------------------------------------------
Cma = 33e-9;
Rpc = 5e3;
Rsa = 1e3;
Vp2Lim = 10;

% Plant model with Vm as output
A = [-1/((Rpc + Rsa)*Cma)];
B = [1/((Rpc + Rsa)*Cma)];
C = [1];
D = [0];

% True dynamics (will differ from above in practice)
% For now, assume our model of A and B is perfect
AT = A;
BT = B;

% Define output that represents actual measurements
% y = [Vm Im]'
rhoA = Rsa/(Rpc+Rsa);
gamma = 1/(Rpc+Rsa);
Cmeas = [1-rhoA;-gamma];
Dmeas = [rhoA;gamma];

% Augmented model with integrator
Atilde = [A 0;-C 0];
Btilde = [B;-D];

% Find state gain and integrator gain with LQI method
sys = ss(A,B,C,D);
Qvm = 1e-5;    % State penalty for large Vm
Qint = 1e6;   % Penalty on large integrator values
R = 1e-7;      % Penalty on Vp2 control input magnitude
Q = diag([Qvm Qint]);

K = lqi(sys,Q,R); % [Kvm Ki]
Kvm = K(1);
Ki = K(2);

% Observer pole placement as multiplicative factor on plant pole
speedFactor = 10;
pObs = speedFactor*eig(A);
L = place(A',Cmeas',pObs)';

%% Setting Inputs to Simulink Observer Model and Plotting Simulation Output

Ts = 2; % sampling time in us

Vp2 = [t3.', ((cmd_data(1:5:end)-8192)*DAC_to_mV)];
Vp1_Im = [t3.', (p1_data*ADS_to_mV*(1/fbck_gain)), (current_data(1:10:end)*ADC_to_uA)];

simResults = sim('control_system_observer');
Vm_estimate = simResults.Vm_estimate.Data;

plot(t3, vm_data*ADS_to_mV, '-*', 'LineWidth', 2);
xlim([-75 175]);
hold on;
plot(t3(1:length(Vm_estimate)), Vm_estimate, '-*', 'LineWidth', 2);
hold on;
plot(t3, p1_data*ADS_to_mV*(1/fbck_gain), '-*', 'LineWidth', 2);
title('Vm vs Vm Estimate');
xlabel('t (μs)');
ylabel('Voltage (mV)');
legend('Vm', 'Observer Estimate', 'Vp1', 'Location', 'northeast');
