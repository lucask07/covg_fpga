// -------------------------------------------------------------
// 
// File Name: /Users/koer2434/My Drive/UST/research/covg/manuscripts/control_system/secord_memos/obersver_nov_update/codegen/matrix_mul_fixedpt/hdlsrc/matrix_mul_fixedpt_fixpt_tc.v
// Created: 2022-12-13 08:05:52
// 
// Generated by MATLAB 9.12, MATLAB Coder 5.4 and HDL Coder 3.20
// 
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: matrix_mul_fixedpt_fixpt_tc
// Source Path: matrix_mul_fixedpt_fixpt_tc
// Hierarchy Level: 1
// 
// Master clock enable input: clk_enable
// 
// enb_40_1_0  : identical to clk_enable
// enb_1_1_1   : 40x slower than clk with phase 1
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module matrix_mul_fixpt_tc
          (clk,
           reset,
           clk_enable,
           enb_40_1_0,
           enb_1_1_1,
           count40);


  input   clk;
  input   reset;
  input   clk_enable;
  output  enb_40_1_0;
  output  enb_1_1_1;
  output reg [5:0] count40;  // ufix6
  
  wire phase_all;
  reg  phase_1;
  wire phase_1_tmp;


  always @ (posedge clk or posedge reset)
    begin: Counter40
      if (reset == 1'b1) begin
        count40 <= 6'b000001;
      end
      else begin
        if (clk_enable == 1'b1) begin
          if (count40 >= 6'b100111) begin
            count40 <= 6'b000000;
          end
          else begin
            count40 <= count40 + 6'b000001;
          end
        end
      end
    end // Counter40

  assign phase_all = clk_enable ? 1'b1 : 1'b0;

  always @ (posedge clk or posedge reset)
    begin: temp_process1
      if (reset == 1'b1) begin
        phase_1 <= 1'b1;
      end
      else begin
        if (clk_enable == 1'b1) begin
          phase_1 <= phase_1_tmp;
        end
      end
    end // temp_process1

  assign  phase_1_tmp = (count40 == 6'b000000 && clk_enable == 1'b1) ? 1'b1 : 1'b0;

  assign enb_40_1_0 =  phase_all & clk_enable;

  assign enb_1_1_1 =  phase_1 & clk_enable;


endmodule  // matrix_mul_fixedpt_fixpt_tc

