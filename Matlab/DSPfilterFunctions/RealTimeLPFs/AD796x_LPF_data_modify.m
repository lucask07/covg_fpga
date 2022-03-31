function dout = AD796x_LPF_data_modify(din)
    x = fi(2^13, 1, 14, 0)*din;
    dout = fi(x+8192, 0, 14, 0);
end

