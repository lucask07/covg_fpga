// -------------------------------------------------------------
// 
// File Name: C:\Users\iande\Desktop\covg_fpga\Matlab\scrapwork\codegen\IIRfilter\hdlsrc\IIRfilter_fixpt.v
// Created: 2021-06-16 10:06:29
// 
// Generated by MATLAB 9.9, MATLAB Coder 5.1 and HDL Coder 3.17
// 
// 
// 
// -- -------------------------------------------------------------
// -- Rate and Clocking Details
// -- -------------------------------------------------------------
// Design base rate: 1
// 
// 
// Clock Enable  Sample Time
// -- -------------------------------------------------------------
// ce_out        1
// -- -------------------------------------------------------------
// 
// 
// Output Signal                 Clock Enable  Sample Time
// -- -------------------------------------------------------------
// y                             ce_out        1
// -- -------------------------------------------------------------
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: IIRfilter_fixpt
// Source Path: IIRfilter_fixpt
// Hierarchy Level: 0
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module IIRfilter_fixpt
          (clk,
           reset,
           clk_enable,
           x,
           ce_out,
           y);


  input   clk;
  input   reset;
  input   clk_enable;
  input   signed [15:0] x;  // sfix16
  output  ce_out;
  output  signed [13:0] y;  // sfix14_En8


  wire signed [15:0] s;  // sfix16_En15


  assign s = ((x[15] == 1'b0) && (x[14:0] != 15'b000000000000000) ? 16'sb0111111111111111 :
              ((x[15] == 1'b1) && (x[14:0] != 15'b111111111111111) ? 16'sb1000000000000000 :
              {x[0], 15'b000000000000000}));



  Hd u_Hd (.clk(clk),
           .reset(reset),
           .enb(clk_enable),
           .Hd_in(s),  // sfix16_En15
           .Hd_out(y)  // sfix14_En8
           );

  assign ce_out = clk_enable;

endmodule  // IIRfilter_fixpt
