function [pk_err, rms_err, cnt_same] = extract_error(x1, x2)

% determine 
avg_val = (x1+x2)/2;
norm_err = (x1-x2)./avg_val;
pk_err = max(norm_err);
rms_err = rms(norm_err);

cnt_same = sum(x1==x2);

end