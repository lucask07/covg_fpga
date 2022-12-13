% generate a test bench for a 16 bit wide x 16 bit wide 2x2 matrix
% multiplier.
% HDL coder project: matrix_mul.prj 
% Folded Verilog 
% Lucas Koerner, 2022/12/13

t = 1:100;
for i = t

    a = 1;
    b = -1;
    A = a + (b-a)*rand(2,2);
    y = a + (b-a)*rand(2,1);

    full_prec(:,i) = A*y;  % 2x1 output 

    [out] = matrix_mul(A(:), y); % 2x1 output 

    out_t(:,i) = out;
end

subplot(2,1,1)
plot(t, full_prec(1,:));
plot(t, out_t(1,:));

hold on;
subplot(2,1,2)
plot(t, full_prec(2,:));
plot(t, out_t(2,:));  hold on;