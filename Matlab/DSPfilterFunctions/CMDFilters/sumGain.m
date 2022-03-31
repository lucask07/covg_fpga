function y = sumGain(in1, in2, in3, g1, g2, g3, scaleVal)
%function to take in gains of the three CMD filters, and apply them to
%filter outputs and scale the output back to 14 bits

% gtype = numerictype([], 64, 32);
% gtotal = fi('numerictype', gtype);
% g1 = fi(g1,0, 32, 16);
% g2 = fi(g2,0, 32, 16);
% g3 = fi(g3,0, 32, 16);
% scaleVal = fi(scaleVal, 0, 32, 0);
%outputType = numerictype(1, 14, 13);
% addType = numerictype(0, 34, 0);

gtotal = g1 + g2 + g3;
% gintermediate = add(addType, g1, g2);
% gtotal = add(addType, gintermediate, g3);

% out1 = fi(((g1/gtotal)*in1), 1, 14, 13);
% out2 = fi(((g2/gtotal)*in2), 1, 14, 13);
% out3 = fi(((g3/gtotal)*in3), 1, 14, 13);

out1 = (g1/gtotal)*in1;
out2 = (g2/gtotal)*in2;
out3 = (g3/gtotal)*in3;


% out1 = fi((divide(numerictype(1, 14, 13), g1, gtotal)*in1), 1, 14, 13);
% out2 = fi((divide(numerictype(1, 14, 13), g2, gtotal)*in2), 1, 14, 13);
% out3 = fi((divide(numerictype(1, 14, 13), g3, gtotal)*in3), 1, 14, 13);

%y1 = fi((out1 + out2 + out3), 1, 14, 13);
y1 = (out1 + out2 + out3);


%y = fi((y1/scaleVal), 1, 14, 13);
y2 = y1/scaleVal;
y = fi(y2, 1, 14, 13);
%y = divide(numerictype(1, 14, 13), y1, scaleVal);

end