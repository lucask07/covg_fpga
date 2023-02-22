% VMPIWithObserverDriver
% PURPOSE: Set parameters and run simulink model of PI closed loop control with observer 
%    
%    
% AUTHOR    : Tom Secord 
% DATE      : 22-Nov-2022 13:03:05 
% REVISION  : 2.00: Use more sophisticated op-amp analysis (yet ignore
%                   their first order response characteristics to keep model 2nd order)
% DEVELOPED : 9.10.0.1739362 (R2021a) Update 5 
% FILENAME  : C:\Users\seco6437\OneDrive - University of St. Thomas\Research\COVG Control\

% provide access to the fixed point observer "reorder" function
addpath('/Users/koer2434/Documents/covg_fpga/Matlab/control_system/observer/observer/codegen/observer/fixpt')

% CLEAR SCREEN, CLOSE PLOTS, AND CLEAR VARIABLES
%--------------------------------------------------------------------------
clc
% clear
close all
%--------------------------------------------------------------------------


% VARIABLE AND PARAMETER DEFINITIONS
%--------------------------------------------------------------------------
% determines the type of simulation 
discrete = false;
discrete_reorder = true;

VmDes = 0.025; % mV final membrane voltage 
x0 = [0.1*VmDes 0]'; % Assume non-zero initial condition to help check observer


MSPS = 2.5;         % Sample rate in Mega-samples
Ts = 1/(MSPS*1e6);  % period for Simulink 
N = 3;              % Latency of 
Tsim = 150e-6;
dTMax = 1e-7;
t = 0:Ts:Tsim;

% 
RF = 332e3; % Current sense resistor: ranges from 10k, to 10Meg
C1 = 47e-12; % compensator. Programmable from 47 pF to 5 nF

in_amp = 1;
diff_buf = 499/(120+1500); % correct, refering to signal_chain.py 
% scaling of digitized current and voltage 
dn_per_amp = (2^15/4.096)*(RF*in_amp*diff_buf); % correct 
Im_scale = dn_per_amp;  % DN/Amp 

ads_full_scale = 10;
dn_per_volt = (2^16/ads_full_scale); %correct
VP1_scale = dn_per_volt*11; % DN / Volt at Vm  

%dac_scale = 2^14/0.589; % TODO: verify this  
dac_scale = 2^14*4; % TODO: verify this  
obsv_scale = dac_scale;
total_scale = 1; % observer is 16-bit, DAC is 14-bit

[Ldp, Bdp, Adp, A, B, C, D] = observer_coeff(Ts, RF, C1, Im_scale, VP1_scale, dac_scale, total_scale);

% if false execute a floating point simulation
% if true create fixed point representations of the matrices A,B,L -- confirmed that there is good matching using the floating point version 
FIXPT = true; 

Adp_sim.time = t;
if FIXPT
    Adp_sim.signals.values = fi(repmat(Adp(:)', length(t), 1), 1, 32, 24);
else
    Adp_sim.signals.values = repmat(Adp(:)', length(t), 1);
end    
Adp_sim.signals.dimensions = length(Adp(:));

Bdp_sim.time = t;
if FIXPT
    Bdp_sim.signals.values = fi(repmat(Bdp(:)', length(t), 1), 0, 32, 50);
else
    Bdp_sim.signals.values = repmat(Bdp(:)', length(t), 1);
end
Bdp_sim.signals.dimensions = length(Bdp(:));

Ldp_sim.time = t;
if FIXPT
    Ldp_sim.signals.values = fi(repmat(Ldp(:)', length(t),1), 1, 32, 50);
else
    Ldp_sim.signals.values = repmat(Ldp(:)', length(t), 1);
end
Ldp_sim.signals.dimensions = length(Ldp(:));

% ----------- PI Controller Design -------------
s = tf('s');
Ac = 5; % Lower for less agressive bandwidth. 5 was nominal design
fc_pi = 2.5e3;
Gc = -Ac*(s+fc_pi*2*pi)/s;  % nominally 5 kHz
Gcd = c2d(Gc,Ts,'tustin');

b0 = Gcd.num{1}(1);
b1 = Gcd.num{1}(2);
b2 = 0;
a1 = -1;
a2 = 0;
bode(Gc);
%--------------------------------------------------------------------------

% RUN SIMULATION
%--------------------------------------------------------------------------
if discrete
    fprintf('Running discrete simulation \n');
    out = sim('PIControlWithObserverR2_discrete.slx');
elseif (discrete_reorder && FIXPT) 
    fprintf('Running reordered discrete time simulation, with fixed point observer \n')
    out = sim('PIControlWithObserverR2_discrete_reorder_fixedpt.slx');
elseif (discrete_reorder && ~FIXPT) 
    fprintf('Running reordered discrete time simulation \n')
    out = sim('PIControlWithObserverR2_discrete_reorder.slx');
else
    fprintf('Running continuous time simulation \n')
    out = sim('PIControlWithObserverR2.slx');
end
Vm = out.Vm.Data;
Im = out.Im.Data;
t = out.Vm.Time;

% -----------------
% plots to check observer 
% -----------------
figure
plot(Im)
subplot(2,1,1)
plot(t,Im)
subplot(2,1,2)
plot(t,Vm)
hold on
plot(out.VmHat.Time, out.VmHat.Data, 'g')
plot(out.Est_fixed.Time, out.Est_fixed.Data(1,:), 'r')
legend('Vm', 'VmHat', 'Vm-Estimator')
figure 
subplot(2,1,1);
plot(out.VCmd.Time, out.VCmd.Data, 'g');
hold on
plot(out.SetPt.Time, out.SetPt.Data, 'r');
legend('Vcmd', 'SetPt')

subplot(2,1,2);
plot(out.Cmd_prePI.Time, out.Cmd_prePI.Data, 'k');
hold on;
plot(out.Cmd_afterPI.Time, out.Cmd_afterPI.Data, 'b');

legend('prePI', 'postPI')
title('Vcmd')

% --------------
% Check max values
% --------------
max(abs(out.VCmd.Data))
max(abs(out.Im.Data))
max(abs(out.Vm.Data))
max(abs(out.VmHat.Data))
max(abs(out.V3.Data))

max(Ldp)
max(Adp)  % a down scaling here may be ok since yest is a longer word (33 bits?) 

performanceInfo = stepinfo(Vm,t,VmDes);
Tsettle = performanceInfo.SettlingTime*1e6; % us
OS = performanceInfo.Overshoot;
Tpeak = performanceInfo.PeakTime*1e6; % us
[~,iPeak] = min(abs(t*1e6-Tpeak));
VmPeak = Vm(iPeak);
%--------------------------------------------------------------------------


% PLOTTING
%--------------------------------------------------------------------------
lw = 3;
fs = 14;
fn = 'arial';
fw = 'bold';
wFig = 0.5; % Width of figure in screen normalized units
aspect = 1; % Aspect ratio of height to width
pos = [0.1 0.1 wFig aspect*wFig];

figure
plot(t*1e6,Vm,'LineWidth',lw,'Color','b')

% Settling time label
line(Tsettle*[1 1],[0 VmDes],'Color','k','LineStyle','--','LineWidth',2)
text(Tsettle,VmDes/2,['T_{settle} = ' num2str(Tsettle,'%.1f') ' \mus'],...
    'HorizontalAlignment','center','FontSize',fs,'FontWeight',fw,...
    'FontName',fn,'BackgroundColor','w')

% Overshoot label
if OS > 0
    line(Tpeak*[1 1],[0 VmPeak],'Color','k','LineStyle','--','LineWidth',2)
    text(Tpeak,VmDes/1.5,['%OS = ' num2str(OS,'%.1f') '%'],...
    'HorizontalAlignment','center','FontSize',fs,'FontWeight',fw,...
    'FontName',fn,'BackgroundColor','w')
end

xlabel('Time (\mus)','FontSize',fs,'FontWeight',fw,'FontName',fn);
ylabel('Membrane Voltage (V)','FontSize',fs,'FontWeight',fw,'FontName',fn);
set(gca,'FontSize',fs,'FontWeight',fw,'FontName',fn);
grid on
set(gcf,'Color','w','Units','normalized','Position',pos);

figure
plot(t*1e6,Im*1e3,'LineWidth',lw,'Color','b')
xlabel('Time (\mus)','FontSize',fs,'FontWeight',fw,'FontName',fn);
ylabel('Membrane Current (mA)','FontSize',fs,'FontWeight',fw,'FontName',fn);
set(gca,'FontSize',fs,'FontWeight',fw,'FontName',fn);
grid on
set(gcf,'Color','w','Units','normalized','Position',pos);
%--------------------------------------------------------------------------

%% print fixed point observer coefficients

[Ldp_f, Bdp_f, Adp_f] = observer_coeff_fixed(Ldp, Bdp, Adp);

fprintf("Fixed pt Observer Coefficients\n");
fprintf("{0:0x%s,\n", hex(Ldp_f(1,1)));
fprintf("1:0x%s,\n", hex(Ldp_f(2,1)));  
fprintf("2:0x%s,\n", hex(Ldp_f(1,2)));
fprintf("3:0x%s,\n", hex(Ldp_f(2,2)));
fprintf("4:0x%s,\n", hex(Adp_f(1,1)));
fprintf("5:0x%s,\n", hex(Adp_f(2,1)));
fprintf("6:0x%s,\n", hex(Adp_f(1,2)));
fprintf("7:0x%s,\n", hex(Adp_f(2,2)));
fprintf("8:0x%s,\n", hex(Bdp_f(1,1))); 
fprintf("9:0x%s}\n", hex(Bdp_f(2,1))); 

%% print PI coefficients
fprintf("\nController Coefficients\n");
fprintf("1: 0x%s,\n", hex(fi(-b0/2, 1, 32, 29)))
fprintf("2: 0x%s,\n", hex(fi(-b1/2, 1, 32, 29)))
fprintf("9: 0x%s,\n", hex(fi(-a1, 1, 32, 30)))  % TODO: check this sign, was originally a1 

% close all;