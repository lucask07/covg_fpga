onbreak resume
onerror resume
vsim -voptargs=+acc work.Butter_tb
add wave sim:/Butter_tb/u_Butterworth/clk
add wave sim:/Butter_tb/u_Butterworth/clk_enable
add wave sim:/Butter_tb/u_Butterworth/reset
add wave sim:/Butter_tb/u_Butterworth/filter_in
add wave sim:/Butter_tb/u_Butterworth/write_enable
add wave sim:/Butter_tb/u_Butterworth/write_done
add wave sim:/Butter_tb/u_Butterworth/write_address
add wave sim:/Butter_tb/u_Butterworth/coeffs_in
add wave sim:/Butter_tb/u_Butterworth/filter_out
add wave sim:/Butter_tb/filter_out_ref
run -all
