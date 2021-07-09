// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Thu Jul  8 11:28:24 2021
// Host        : LAPTOP-RK0H8TS5 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ blk_mem_gen_0_stub.v
// Design      : blk_mem_gen_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a75tfgg484-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* x_core_info = "blk_mem_gen_v8_4_1,Vivado 2018.2" *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix(clka, ena, wea, addra, dina, clkb, rstb, enb, addrb, doutb, 
  rsta_busy, rstb_busy)
/* synthesis syn_black_box black_box_pad_pin="clka,ena,wea[3:0],addra[31:0],dina[31:0],clkb,rstb,enb,addrb[31:0],doutb[31:0],rsta_busy,rstb_busy" */;
  input clka;
  input ena;
  input [3:0]wea;
  input [31:0]addra;
  input [31:0]dina;
  input clkb;
  input rstb;
  input enb;
  input [31:0]addrb;
  output [31:0]doutb;
  output rsta_busy;
  output rstb_busy;
endmodule
