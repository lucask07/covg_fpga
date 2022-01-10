// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Jan  7 10:20:30 2022
// Host        : LAPTOP-RK0H8TS5 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub
//               c:/Users/iande/Desktop/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_stub.v
// Design      : mult_gen_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a75tfgg484-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* x_core_info = "mult_gen_v12_0_14,Vivado 2018.2" *)
module mult_gen_0(CLK, A, B, P)
/* synthesis syn_black_box black_box_pad_pin="CLK,A[15:0],B[31:0],P[47:0]" */;
  input CLK;
  input [15:0]A;
  input [31:0]B;
  output [47:0]P;
endmodule
