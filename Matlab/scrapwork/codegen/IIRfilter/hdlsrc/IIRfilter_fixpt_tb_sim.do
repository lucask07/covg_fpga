onbreak resume
onerror resume
vsim -voptargs=+acc work.IIRfilter_fixpt_tb

add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/clk
add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/reset
add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/clk_enable
add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/x
add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/ce_out
add wave sim:/IIRfilter_fixpt_tb/u_IIRfilter_fixpt/y
add wave sim:/IIRfilter_fixpt_tb/y_ref
run -all
