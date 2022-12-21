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
discrete = false;
discrete_reorder = true;

VmDes = 0.05;
x0 = [0.1*VmDes 0]'; % Assume non-zero initial condition to help check observer


MSPS = 5;
Ts = 1/(MSPS*1e6);  % allow to set this externally
N = 3;              % allow to set this externally
Tsim = 150e-6;
dTMax = 1e-7;
t = 0:Ts:Tsim;

Cma = 33e-9;
RF = 10e3; % Current sense resistor: ranges from 10k, to 10Meg
RPC = 5e3;
Rsa = 1e3;
AOL = 5e6; % Open loop gain of op amps

C1 = 47e-12; % compensator. Programmable from 47 pF to 5 nF
R3 = 20e3;
R1 = 1e4;
R2 = 1e4;
R4 = 20e3;

% Definitions for convenience
rho = (RF + RPC)/(RF + RPC + Rsa);
g = R2/(R1+R2);

tau1 = (RF+RPC+Rsa)*Cma;
tau2 = R3*C1;
tau3 = R4*C1;

w1 = 1/tau1;
w2 = 1/tau2;
w3 = 1/tau3;

wVM = (w1*w2*rho*(tau1-tau2)/(g + AOL*(1-rho)));
wV3 = (g/(g+AOL*(1-rho)))*((AOL*rho*w1/g) + w2 + AOL*(1-rho)*w2/g + w3);
wVcmd = g*w3/(g+AOL*(1-rho));


A11 = -w1;
A12 = -AOL*w1;
A21 = wVM;
A22 = -wV3;

B11 = 0;
B21 = wVcmd;

C11 = 1;
C12 = 0;
C21 = -1/(RF+RPC+Rsa);
C22 = -AOL/(RF+RPC+Rsa);
C31 = rho;
C32 = -(1-rho)*(AOL);

A = [A11 A12;A21 A22];
B = [B11;B21];
C = [C11 C12;C21 C22;C31 C32]; % Outputs are Vm, Im, and Vp1
D = zeros(3,1);


% Observer, use same model except only allow for measurement of Im and Vp1
Ao = [A11 A12;A21 A22];
Bo = [B11;B21];
Co = [C21 C22;C31 C32]; % Im and Vp1 is outputs in observer model to compare with measurements
Do = zeros(2,1);

% Check observability
obsvInfo = obsvEnhanced(Ao,Co);
disp(obsvInfo.conclusion)

% Observer Design
pPlant = eig(A);
pDes = [3*max(pPlant) 5*max(pPlant)]; % Move both poles to left of fastest plant eigenvalue
L = placeO(Ao,Co,pDes);

% discrete version
Ad = eye(size(Ao)) + Ts*Ao;
Bd = Bo*Ts;
Cd = Co; % Im and Vp1 is outputs in observer model to compare with measurements
Dd = Do;
Ld = L*Ts;

% discrete reorder version 
LdC_inv = inv(eye(size(Ao)) + Ld*Cd);
Adp = LdC_inv*Ad;
Adp2 = (eye(size(Ao)) + Ld*Cd)\Ad;  % these are the same results 
Bdp = LdC_inv*Bd;
Ldp = LdC_inv*Ld;

in_amp = 1;
diff_buf = 499/(120+1500); % correct, refering to signal_chain.py 
% scaling of digitized current and voltage 
dn_per_amp = (2^15/5)*(RF*in_amp*diff_buf); % correct 
Im_scale = dn_per_amp;

Im_scale = dn_per_amp;

ads_full_scale = 2.5;
dn_per_volt = (2^15/ads_full_scale); %correct
VP1_scale = dn_per_volt;

dac_scale = VP1_scale; % TODO: this is temporary 

% scale L matrix to cancel scaling of the measured Vm and Im 
Ldp = Ldp*[1/Im_scale, 0; 0, 1/VP1_scale];
Bdp = Bdp/dac_scale;

fixed_pt_scaling = 1;

% if false execute a floating point simulation
% if true create fixed point representations of the matrices A,B,L -- confirmed that there is good matching using the floating point version 
FIXPT = true; 

Adp_sim.time = t;
if FIXPT
    Adp_sim.signals.values = fi(repmat(Adp(:)', length(t), 1), 1, 16, 5);
else
    Adp_sim.signals.values = repmat(Adp(:)', length(t), 1);
end    
Adp_sim.signals.dimensions = length(Adp(:));

Bdp_sim.time = t;
if FIXPT
    Bdp_sim.signals.values = fi(repmat(Bdp(:)', length(t), 1), 1, 16, 38);
else
    Bdp_sim.signals.values = repmat(Bdp(:)', length(t), 1);
end
Bdp_sim.signals.dimensions = length(Bdp(:));

Ldp_sim.time = t;
if FIXPT
    Ldp_sim.signals.values = fi(repmat(Ldp(:)', length(t),1), 1, 16, 32);
else
    Ldp_sim.signals.values = repmat(Ldp(:)', length(t), 1);
end
Ldp_sim.signals.dimensions = length(Ldp(:));

%pPlant = eig(A);
%pDes = [3*max(pPlant) 5*max(pPlant)]; % Move both poles to left of fastest plant eigenvalue
%Ld = placeO(Ao,Co,pDes);

% PI Controller Design
s = tf('s');
Ac = 5; % Lower for less agressive bandwidth. 5 was nominal design

Gc = -Ac*(s+3.14e4)/s;
Gcd = c2d(Gc,Ts,'tustin');

b0 = Gcd.num{1}(1);
b1 = Gcd.num{1}(2);
b2 = 0;
a1 = -1;
a2 = 0;
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
