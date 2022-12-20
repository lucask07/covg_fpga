These folders work to implement the membrane voltage observer designed by Tom Secord into the FPGA. 

To implement into the FPGA the 


*matrix_mul* implements a 2x2 matrix multiplication using a multiplier with a parameterizable pipeline dela. The input widths are parameterizable and the resulting output width has a width of A_wid+B_wid. The folded version is a custom design with a folding factor of x40 (200 MHz/5 MHz). 

*observer* The observer is implemented after rearranging the expression so that only 3 matrix multiplications are nneed. The modified expression is:

```
yest[n] = Ldp*y + Adp*yest[n-1] + Bdp*u 
```
With the discrete and modified matrices calculated as:

```
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
```
The folded observer Verilog has been shown to be bit accurate with the MATLAB generated Verilog. Those simulations were multiplications of widths: 16x16 + 16x33 + 16x16.

*full_closed_loop* This folder holds the simulink models and the MATLAB code to run them. A MATLAB function block is used to implement the observer and compare its outputs with the Simulink observer outputs. Results match when using the file PIControlWithObserverR2_discrete_reorder.slx. However, the fixed point implementation of the observer (as a function block) in the file PIControlWithObserverR2_discrete_reorder_fixedpt.slx is not yet giving correct results. The fixed point widths and decimals need adjustment. In this implementation the scaling between volts and amps to DAC codes has been added which is most certainly the reason for issues. 

*Next steps* 
1. Correct the scaling and fixed point sizing in the ...discrete_reorder_fixedpt.slx file. 
2. Implement an interpolator of the ADS Vp1 measurement (1:5). 
3. Add to the FPGA and send the observer outputs to DDR.  

