%% Ian Delgadillo Bonequi
% clear all;
% close all;
% clc;

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

y = hdf5read(['/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/covg_pi_ctrl_files/PI_ctrl_data.h5'],'/adc');

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
t3 = t3-min(t3);

%% Observer Definitions and Matrices - Code is based off Dr. Secord's Vm Control Driver Script
OBSERVER = 1;
SIM = 1;

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
    C1 = 47e-12; % change to 47 pF 

    tau1 = (Rf + Rpc + Rsa)*Cma;
    tau2 = (R3*C1);
    rho = (Rf + Rpc)/(Rf + Rpc + Rsa);
    g = R2/(R1 + R2);
    AOL = 5e6; % was 1e7
    
    Ts = 1; % sampling time in us
    
    A = [-1/tau1 -AOL/tau1; 
        (-rho*(tau2 - tau1))/(tau1*tau2*(AOL*(1-rho)+g)) -(AOL*R4*tau1 + R3*g*tau1 + R4*g*tau1 - AOL*R4*rho*tau1 + AOL*tau2*R4*rho)/(tau1*tau2*R4*(AOL*(1-rho)+g))];
    Ad = A*Ts*1e-6 + [1 0; 0 1];
    B = [0; (R3*g)/(tau2*R4*(AOL*(1-rho)+g))];
    Bd = B*Ts*1e-6;
    C = [-1/(Rf + Rpc + Rsa) -AOL/(Rf + Rpc + Rsa); rho -(1-rho)*AOL];
    Cd = C;
    
    D = [0; 0];

    sys = ss(A,B,C,D);
    step(sys)

    % Observer pole placement as multiplicative factor on plant pole
    % place based on continuous time matrices 
    speedFactor = [3; 5];
    pObs = speedFactor.*eig(A);
    L = place(A',C',pObs)';
    Ld = L*Ts*1e-6;

    % place using discrete time matrices 
    %pObs = speedFactor.*eig(Ad);
    %L2 = place(Ad',Cd',pObs)';

    % convert L2 calculated with discrete time to discrete time
    %Ld2 = L2*Ts*1e-6;

    % for the simulink simulation
    % A = Ad;
    % L = Ld;
    % B = Bd; 

    % L = [0 0; 0 0];
    % A = [0 0; 0 0];
    Ts = 1e-6;

    %% Setting Inputs to Simulink Observer Model and Plotting Simulation Output
    % Defining Inputs to Observer
    Im = [(t3 + 3277.2).', (current_data(1:5:end)*ADC_to_uA)*1e-3];
    Vp1 = [(t3 + 3277.2).', (p1_data*ADS_to_mV*(1/fbck_gain)*(1/10))];
    Vcmd = [(t3 + 3277.2).', ((resample(cmd_data, 2, 5)-8192)*DAC_to_mV)];
    
    Im(:,1) = Im(:,1)*Ts;
    Vp1(:,1) = Vp1(:,1)*Ts;
    Vcmd(:,1) = Vcmd(:,1)*Ts;

    %Im = (current_data(1:5:end)*ADC_to_uA)*1e-3;
    %Vp1 = (p1_data*ADS_to_mV*(1/fbck_gain)*(1/10));
    %Vcmd = ((resample(cmd_data, 2, 5)-8192)*DAC_to_mV);

    % Run Simulink Simulation and Grab Observer Output
    % set_param('mymodel','StartTime',1,'StopTime', 8192);

    %NEXT: I think the mismatch and issues are start time and sampling
    %time. Since the matrices are using Rs, and Cs the time units must be
    %in seconds 
end
if SIM == 1
    simResults = sim('../control_system/control_system_observer', 'StartTime', '0', 'StopTime', '0.008192');
    Vm_estimate = simResults.Vm_estimate.Data;
    Im_estimate = simResults.Im_estimate.Data;
    Observer_error = simResults.Observer_error.Data;
    Cmd_in = simResults.Cmd_in.Data;

    % Plot Actual Measured Vm vs Estimator Vm
    figure(5);
    grid on;
    %plot(t3, vm_data*ADS_to_mV, '-*', 'LineWidth', 2);
    plot(vm_data*ADS_to_mV, '-*', 'LineWidth', 2);
    xlim([-75 175]);
    % ylim([-300 100]);
    hold on;
    %plot(t3(1:length(Vm_estimate)), Vm_estimate, '-*', 'LineWidth', 2);
    %plot(t3(1:length(Cmd_in)), Cmd_in, '-*', 'LineWidth', 2);
    plot(Vm_estimate, '-*', 'LineWidth', 2);
    %plot(Cmd_in, '-*', 'LineWidth', 2);

    title('Vm vs Vm Estimate');
    xlabel('t (μs)');
    ylabel('Voltage (mV)');
    legend('Vm Actual', 'Estimated', 'Location', 'southeast');
end