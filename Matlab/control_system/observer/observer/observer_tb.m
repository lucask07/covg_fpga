% generate a test bench for a 16 bit wide x 16 bit wide 2x2 matrix
% multiplier.
% HDL coder project: matrix_mul.prj 
% Folded Verilog 
% Lucas Koerner, 2022/12/13

t = 1:100;

for i = t

    a = 1;
    b = -1;
%     A = a + (b-a)*rand(2,2);
    A = [0.982162315008215 -69.3545467490562; 1.39993846996797e-04 0.962728868603733];
    y1 = (a + (b-a)*rand(1,1))*32768;
    y2 = (a + (b-a)*rand(1,1))*32768;
    u = (a + (b-a)*rand(1,1))*32768;
    
%     L = a + (b-a)*rand(2,2);
    L = [-5.97334600776244e-07 1.47873538994281e-06; -3.96871392524270e-12 6.22527098028660e-11];
%     B = a + (b-a)*rand(2,1);
    B = [5.94431346500218e-08; 3.19447388238764e-11];

    [out] = observer(y1, y2, u, L(:), A(:), B(:)); % 2x1 output 

    out_t(:,i) = out;
end

subplot(2,1,1)
%plot(t, full_prec(1,:));
plot(t, out_t(1,:));

hold on;
subplot(2,1,2)
%plot(t, full_prec(2,:));
plot(t, out_t(2,:));  hold on;