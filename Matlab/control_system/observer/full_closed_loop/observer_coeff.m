function [Ldp, Bdp, Adp, A, B, C, D] = observer_coeff(Ts, RF, C1, Im_scale, VP1_scale, dac_scale, total_scale)

    % calculate full precision observer coefficients 
    % function so that this can be called by Python using the MATLAB engine

    Cma = 33e-9;
    % RF = 332e3; % Current sense resistor: ranges from 10k, to 10Meg
    RPC = 5e3;
    Rsa = 1e3;
    AOL =5e6; % Open loop gain of op amps
    
    % C1 = 47e-12; % compensator. Programmable from 47 pF to 5 nF
    R3 = 20e3;
    R1 = 2.1e3;
    R2 = 3.01e3;
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
    
%     in_amp = 1;
%     diff_buf = 499/(120+1500); % correct, refering to signal_chain.py 
%     % scaling of digitized current and voltage 
%     dn_per_amp = (2^15/4.096)*(RF*in_amp*diff_buf); % correct 
%     Im_scale = dn_per_amp;
%     
%     ads_full_scale = 10;
%     dn_per_volt = (2^16/ads_full_scale); %correct
%     VP1_scale = dn_per_volt*11*1.7; %  
%     
%     dac_scale = 2^14/0.589; % TODO: verify this  
%     dac_scale = 2^14; % TODO: verify this  
%     obsv_scale = dac_scale;
%     total_scale = 1; % observer is 16-bit, DAC is 14-bit
    
    % scale L matrix to cancel scaling of the measured Vm and Im 
    Ldp = Ldp*[1/Im_scale, 0; 0, 1/VP1_scale]*total_scale;
    Bdp = Bdp/dac_scale*total_scale;
    Adp = Adp; % never scale A matrix since that would "count" double. 

end
