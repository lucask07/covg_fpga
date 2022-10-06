%% Ian Delgadillo Bonequi
clear all;
close all;
clc;

%% Plot CMD Signal

SAVE_FIG = true;

%Grab CMD data from .h5 file
% configure directory of the captured data
data_dir = '/home/delg/OneDrive/clamp test files/';
% data_dir = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/std_rs_comp_h5_data';

y = hdf5read(fullfile(data_dir, 'alpha_0.7_data.h5'),'/adc');
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
if SAVE_FIG
    saveas(figure(1), 'EndToEndLatencyMeasMATLAB.png');
end
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
if SAVE_FIG
    saveas(figure(2), 'FilterLatencyMeasMATLAB.png');
end
%% Plot CMD, Im, P1, and Vm

f = figure(3);
LineStyles = {'-o','-+','-v','-s','-x','-d','-*','->','-h','-^'};
LineStyleIdx = 1;
t = t-3277.2;
t2 = t2-3277.2;
set(gcf, 'Position', get(0, 'Screensize'));
tiledlayout(2, 2, 'TileSpacing', 'compact')
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
DAC_to_mV = (DAC_amplitude_gain/2^13)*DAQ_to_DC_gain;
ADS_to_mV = (ADS_amplitude_Gain/2^15);

alphas = [0.0, 0.25, 0.5, 0.75];
risetimes = [];
overshoots = [];
settlingtimes = [];

for alpha = (0)

    % Special case for α=0 .h5 file
    if(alpha == 0)
%         y = hdf5read(['SeriesResData\alpha_0.0_data.h5'],'/adc');
%         y = hdf5read(['C:\Users\iande\OneDrive - University of St. Thomas\clamp test files\alpha_0.0_data.h5'],'/adc');
%         y = hdf5read(fullfile(data_dir, 'alpha_0.0_data.h5'),'/adc');
        y = hdf5read(['/home/delg/OneDrive/covg_pi_ctrl_files/PI_ctrl_data.h5'],'/adc');
    else
%         y = hdf5read(['SeriesResData\alpha_', num2str(alpha, 2), '_data.h5'],'/adc');
%         y = hdf5read(['C:\Users\iande\OneDrive - University of St. Thomas\clamp test files\alpha_', num2str(alpha, 2), '_data.h5'],'/adc');
        y = hdf5read(fullfile(data_dir, ['alpha_', num2str(alpha, 2), '_data.h5']),'/adc');
    end

    % Grab CMD, Im, P1, and Vm data from .h5 file
    cmd_data = y(2:2:end,5);
    cmd_data = double(cmd_data);
    current_data = dec2bin(y(:,1));
    current_data = typecast(uint16(bin2dec(current_data)), 'int16');
    current_data = double(-current_data);
%     p1_data = dec2bin(y(1:10:end,8));
    p1_data = dec2bin(y(1:5:end,8));
    p1_data = typecast(uint16(bin2dec(p1_data)), 'int16');
    p1_data = double(p1_data);
%     vm_data = dec2bin(y(2:10:end,8));
    vm_data = dec2bin(y(1:5:end,7));
    vm_data = typecast(uint16(bin2dec(vm_data)), 'int16');
    vm_data = double(vm_data);

    % 1 MSPS time array
%     t3 = (1:length(p1_data))*2000e-3;
    t3 = (1:length(p1_data))*1000e-3;
    t3 = t3-3277.2;
    
    if(isempty(setdiff(round(alpha,2), alphas)))

        % Plot CMD for current α
        axes(a);
        plot(t, (cmd_data-8192)*DAC_to_mV, LineStyles{LineStyleIdx}, 'LineWidth', 2);
        xlim([-25 175]);
        hold on;
        
        % Plot Im for current α
        axes(b)
        plot(t2, current_data*ADC_to_uA, LineStyles{LineStyleIdx}, 'LineWidth', 2);
        xlim([-25 175]);
        hold on;

        % Plot Vm for current α
        axes(c)
        plot(t3(1:length(vm_data)), vm_data*ADS_to_mV, LineStyles{LineStyleIdx}, 'LineWidth', 2);
        xlim([-25 175]);
        hold on;
        
        % Plot P1 for current α
        axes(d);
        plot(t3(1:length(p1_data)), p1_data*ADS_to_mV*(1/fbck_gain)*(1/10), '-*', 'LineWidth', 2);
        xlim([-75 175]);
        hold on;

        LineStyleIdx = LineStyleIdx + 1;
    
        %display step response metrics for Vm
%         rise_time = risetime(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000));
        rise_time = risetime(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000));
        risetimes = [risetimes; rise_time];
        disp(['For α=',num2str(alpha,2), ' Vm rise time is: ', num2str(rise_time, 4), ' us']);

%         over_shoot = overshoot(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000));
        over_shoot = overshoot(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000));
        overshoots = [overshoots; over_shoot];
        disp(['For α=',num2str(alpha,2), ' Vm overshoot is: ', num2str(over_shoot, 4), ' %']);

%         [s,slev,sinst] = settlingtime(vm_data(1000:3000)*ADS_to_mV, t3(1000:3000), 500, 'Tolerance', 5);
        [s,slev,sinst] = settlingtime(vm_data(1000:6000)*ADS_to_mV, t3(1000:6000), 500, 'Tolerance', 5);
        settlingtimes = [settlingtimes; sinst];
        disp(['For α=',num2str(alpha,2), ' Vm settling time is: ', num2str(sinst, 4), ' us']);
        fprintf('\n');
    end
end

% Axes label for CMD
axes(a);
title('Vcmd(t)');
xlabel('t (μs)');
ylabel('Voltage (mV)');
grid on;

% Axes label for Im
axes(b);
title('Im');
xlabel('t (μs)');
ylabel('Current (μA)');
grid on;

% Axes label for Vm
axes(c);
title('Vm');
xlabel('t (μs)');
ylabel('Voltage (mV)');
grid on;

% Axes label for P1
axes(d);
title('P1 (tracks Vm)');
xlabel('t (μs)');
ylabel('Voltage (mV)');
grid on;

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

% Define table data entries
% data = horzcat(risetimes, overshoots, settlingtimes);

% Replace legend labels with LaTeX compatible character for α
% legend_array = replace(legend_array, 'α', '$\alpha$');

% Create table from the data matrix
% rs_table = array2table(round(data,1), 'VariableNames', {'RiseTime [$\mu$s]', 'Percent Overshoot', ...
% 'Settling Time [$\mu$s]'}, 'RowNames', legend_array);

% Create .tex file from MATLAB table (output to the same directory as this script)
% table2latex(rs_table, 'StepResponseMetrics');

%% Observer Definitions and Matrices - Code is based off Dr. Secord's Vm Control Driver Script
OBSERVER = 1;

if OBSERVER
    % VARIABLE AND PARAMETER DEFINITIONS
    %-----------------------------------
    Cma = 33e-9;
    Rma = 4.7e6;
    Rpc = 5e3;
    Rsa = 1e3;
    Rcc = 7.12e3;
    Ccc = 4.7e-9;
    Rf = 100e3;
    R1 = 2.1e3;
    R2 = 3.01e3;
    R3 = 20e3;
    R4 = 20e3;
    C1 = 4.7e-12;

    tau1 = (Rf + Rpc + Rsa)*Cma;
    tau2 = (R3*C1);
    rho = (Rf + Rpc)/(Rf + Rpc + Rsa);
    g = R2/(R1 + R2);
    AOL = 10000;
    
    Ts = 1; % sampling time in us
    
    A = [-1/tau1 -AOL/tau1; (rho*(tau2 - tau1))/(tau1*tau2*(AOL*(1-rho)+g)) (AOL*R4*tau1 + R3*g*tau1 + R4*g*tau1 - AOL*R4*rho*tau1 + AOL*tau2*R4*rho)/(tau1*tau2*R4*(AOL*(1-rho)+g))]*Ts*1e-6 + [1 0; 0 1];
    B = [0; (R3*g)/(tau2*R4*(AOL*(1-rho)+g))]*Ts*1e-6;
    C = [-1/(Rf + Rpc + Rsa) -AOL/(Rf + Rpc + Rsa); rho -(1-rho)*AOL];
    D = [0; 0];
    
    % Observer pole placement as multiplicative factor on plant pole
    speedFactor = [3; 5];
    pObs = speedFactor.*eig(A);
    L = place(A',C',pObs)'*Ts*1e-6;

    %% Setting Inputs to Simulink Observer Model and Plotting Simulation Output
    
    % Defining Inputs to Observer
    Im = [(t3 + 3277.2).', (current_data(1:5:end)*ADC_to_uA)*1e-3];
    Vp1 = [(t3 + 3277.2).', (p1_data*ADS_to_mV*(1/fbck_gain)*(1/10))];
    Vcmd = [(t3 + 3277.2).', ((resample(cmd_data, 2, 5)-8192)*DAC_to_mV)];
    
    % Run Simulink Simulation and Grab Observer Output
    simResults = sim('../control_system/control_system_observer');
    Vm_estimate = simResults.Vm_estimate.Data;
    Im_estimate = simResults.Im_estimate.Data;
    Observer_error = simResults.Observer_error.Data;
    
    % Plot Actual Measured Vm vs Estimator Vm
    figure(5);
    grid on;
    plot(t3, vm_data*ADS_to_mV, '-*', 'LineWidth', 2);
    xlim([-75 175]);
    hold on;
    plot(t3(1:length(Vm_estimate)), Vm_estimate, '-*', 'LineWidth', 2);
    title('Vm vs Vm Estimate');
    xlabel('t (μs)');
    ylabel('Voltage (mV)');
    legend('Vm Actual', 'Estimated', 'Location', 'southeast');
end