// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* x_core_info = "fifo_generator_v13_2_2,Vivado 2018.2" *)
module fifo_w32_1024_r256_128(rst, wr_clk, rd_clk, din, wr_en, rd_en, dout, full, 
  empty, valid, rd_data_count, wr_data_count);
  input rst;
  input wr_clk;
  input rd_clk;
  input [31:0]din;
  input wr_en;
  input rd_en;
  output [255:0]dout;
  output full;
  output empty;
  output valid;
  output [6:0]rd_data_count;
  output [9:0]wr_data_count;
endmodule
