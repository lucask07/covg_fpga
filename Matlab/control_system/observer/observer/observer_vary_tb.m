% create fixed point inputs 

% y1 = fi(y1, 1, 16,15); % Im 
% y2 = fi(y2, 1, 16,15); % Vp1 
% cmd = fi(cmd, 1, 16,15);

%Cma = 33e-9;
%RF = 100e3;

for Cma = [10e-9 33e-9 200e-9] % membrane capacitance 
    for RF = [10e3 100e3] % Current sense resistor: ranges from 10k, to 100k 
                          % 1 Meg and beyond probably requires successful
                          % capacitive compensation (CC terminal)

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
        
        bio_dynamics = ss(A,B,C,D); 

        Ts = 200e-9;
        % Observer, use same model except only allow for measurement of Im and Vp1
        Ao = [A11 A12;A21 A22];
        Bo = [B11;B21];
        Co = [C21 C22;C31 C32]; % Im and Vp1 is outputs in observer model to compare with measurements
        Do = zeros(2,1);
        
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
        Adp = LdC_inv*Ad; %#ok
        Bdp = LdC_inv*Bd; %#ok
        Ldp = LdC_inv*Ld; %#ok
        
        t = 0:Ts:10e-3;
        f1 = 1e3;
        amp = 300e-3; % 300 mV (a very large amplitude command signal) 
        cmd = amp*sin(t*2*pi*f1);

        % the biological model works in physical units of volts and amps 
        %  need to convert cmd back to DAC codes 
        y = lsim(bio_dynamics, cmd, t);
        y1_amps = y(:,2); % convert Im to ADC codes (or develop a pre-scaling of Im-code to Im-Amps)
        in_amp = 1; % correct, with Rg = None
        diff_buf = 499/(120+1500); % correct, refering to signal_chain.py 

        dn_per_amp = (2^15/5)*(RF*in_amp*diff_buf); % correct 
        
        ads_full_scale = 2.5; % +/-10, +/- 5V, +/- 2.5. Recall the overrange bit (20%) 
        dn_per_volt = (2^15/ads_full_scale); %correct

        y1 = dn_per_amp*y1_amps; % Need to equalize the scaling in the L matrix *(dac_per_volt/dac_per_amp);
        Ldp = Ldp*[1/dn_per_amp,0; 0, 1/dn_per_volt];

        y2_volts = y(:,3); % convert Vm to ADC codes (or develop a pre-scaling of Vm-code to Vm-volts)
        y2 = dn_per_volt*y2_volts;
        
        vm_actual = y(:,1); 

        cmd = cmd*dn_per_volt;

        % clamp digitized values (both DACs are signed 16 bits)
        dac_max = 32768-1; % 2^15-1 
        dac_min = -32768;  % 2^15

        y1(y1>dac_max) = dac_max;
        y1(y1<dac_min) = dac_min;

        y2(y2>dac_max) = dac_max;
        y2(y2<dac_min) = dac_min;

        vm_out = ones(1,length(t));
        for t_idx = 1:length(t)
            [vm] = observer(y1(t_idx), y2(t_idx), cmd(t_idx), Ldp(:), Adp(:), Bdp);
            vm_out(t_idx) = vm(1);
        end
        
        vm_out = vm_out / dn_per_volt;

        % scaling of the CMD signal 
        dn_per_volt_cmd = 1e3;
        vm_dac_error = vm_out * dn_per_volt_cmd;

        % PI filter scaling is not yet implemented

        figure;
        subplot(3,1,1)
        plot(t, cmd, 'b'); hold on;
        plot(t, y2, 'r')

        subplot(3,1,2)
        plot(t, y1);
        hold on;
        subplot(3,1,3)
        plot(t, vm_out);  hold on;
        plot(t, vm_actual, 'r');

        % compare estimate to actual 
        figure
        subplot(2,1,1);
        plot(t, vm_actual-vm_out(:))
        ylim([-10e-3 10e-3])
        subplot(2,1,2);
        plot(t, (vm_actual-vm_out(:))./vm_actual*100)
        ylabel('Perc. error')
        ylim([-10 10])
    end
end