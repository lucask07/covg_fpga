onbreak resume
onerror resume
vsim -voptargs=+acc work.Chebyshev_tb
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/clk
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/clk_enable
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/reset
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/filter_in
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/write_enable
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/write_done
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/write_address
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/coeffs_in
add wave sim:/Chebyshev_tb/u_FourthOrderChebyshev/filter_out
add wave sim:/Chebyshev_tb/filter_out_ref
run -all
