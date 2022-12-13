// -------------------------------------------------------------
// 
// File Name: /Users/koer2434/My Drive/UST/research/covg/manuscripts/control_system/secord_memos/obersver_nov_update/codegen/observer_fixedpt/hdlsrc/observer_fixedpt_fixpt.v
// Created: 2022-12-10 07:33:51
// 
// Generated by MATLAB 9.12, MATLAB Coder 5.4 and HDL Coder 3.20
// and then considerably modified by Lucas Koerner to use a folded approach 
// 
// 
// -- -------------------------------------------------------------
// -- Rate and Clocking Details
// -- -------------------------------------------------------------
// Design base rate: 0.025
// Explicit user oversample request: 40x
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
// out_0                          ce_out        1
// out_1                          ce_out        1
// -- -------------------------------------------------------------
// 
// This matrix muliplier retains full precision. 16 bits in * 16 bits in and output is 33 bits 
//  rounding and other scaling should be done outside of the module (or by scaling the inputs)
// -------------------------------------------------------------


`timescale 1 ns / 1 ns

module observer_fixpt_folded
          (clk,
           reset,
           clk_enable,
           y1,
           y2,
           u,
           L_0,
           L_1,
           L_2,
           L_3,
           A_0,
           A_1,
           A_2,
           A_3,
           B_0,
           B_1,
           ce_out,
           out_0,
           out_1);

  input   clk;
  input   reset;
  input   clk_enable;
  input   signed [15:0] y1;  // sfix16_En15
  input   signed [15:0] y2;  // sfix16_En15
  input   signed [15:0] u;  // sfix16_En15
  input   signed [15:0] L_0;  // sfix16_En15
  input   signed [15:0] L_1;  // sfix16_En15
  input   signed [15:0] L_2;  // sfix16_En15
  input   signed [15:0] L_3;  // sfix16_En15
  input   signed [15:0] A_0;  // sfix16_En15
  input   signed [15:0] A_1;  // sfix16_En15
  input   signed [15:0] A_2;  // sfix16_En15
  input   signed [15:0] A_3;  // sfix16_En15
  input   signed [15:0] B_0;  // sfix16_En15
  input   signed [15:0] B_1;  // sfix16_En15
  output  reg ce_out;
  output  reg signed [15:0] out_0;  // sfix16_En13
  output  reg signed [15:0] out_1;  // sfix16_En13

  wire ce_out1;
  wire ce_out2;
  wire ce_out3;

  wire signed [32:0] out_0_A;
  wire signed [32:0] out_1_A;
  wire signed [32:0] out_0_B;
  wire signed [32:0] out_1_B;
  wire signed [32:0] out_0_L;
  wire signed [32:0] out_1_L;

  reg signed [32:0] out_0_A_reg;
  reg signed [32:0] out_1_A_reg;
  reg signed [32:0] out_0_B_reg;
  reg signed [32:0] out_1_B_reg;
  reg signed [32:0] out_0_L_reg;
  reg signed [32:0] out_1_L_reg;

  reg signed [35:0] yest_1;
  reg signed [35:0] yest_2;

  parameter S0=2'd0; // calculating  
  parameter S1=2'd1; //
  parameter S2=2'd2;
  parameter S3=2'd3;

  reg [3:0] state;
  reg [3:0] nextstate;

  reg ce_out_all;
  reg time_to_sum;

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      state<=S0;
    end
    else begin 
      state<=nextstate;
    end
  end

  always @(*) begin
    case(state)
    S0: if (ce_out1==1) nextstate = S1; //TODO: making the assumption that all ce_out are synchronized
    S1: nextstate = S2; 
    S2: nextstate = S3;
    S3: if (clk_enable==1) nextstate = S0;
    default nextstate = S0;
  end

  always @(*) begin
    case (state)
    S0: ce_out <= 0; time_to_sum <=0;
    S1: ce_out <= 0; time_to_sum <=1;
    S2: ce_out <= 1; time_to_sum <=0;
    S3: ce_out <= 0; time_to_sum <=0;    
  end

    matrix_mul_fixpt u_matrix_mul_fixpt (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(A_0),  // sfix16_En15 0,0
                                                       .A_1(A_1),  // sfix16_En15 1,0
                                                       .A_2(A_2),  // sfix16_En15 0,1
                                                       .A_3(A_3),  // sfix16_En15 1,1
                                                       .B_0(B_0),  // sfix16_En15
                                                       .B_1(B_1),  // sfix16_En15
                                                       .ce_out(ce_out1),
                                                       .out_0(out_0_A),  // sfix33_En30
                                                       .out_1(out_1_A)  // sfix33_En30
                                                       );

    matrix_mul_fixpt u_matrix_mul_fixpt (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(B_0),  // sfix16_En15 0,0
                                                       .A_1(B_1),  // sfix16_En15 1,0
                                                       .A_2(0),  // sfix16_En15 0,1
                                                       .A_3(0),  // sfix16_En15 1,1
                                                       .B_0(u),  // sfix16_En15
                                                       .B_1(0),  // sfix16_En15
                                                       .ce_out(ce_out2),
                                                       .out_0(out_0_B),  // sfix33_En30
                                                       .out_1(out_1_B)  // sfix33_En30
                                                       );

    matrix_mul_fixpt u_matrix_mul_fixpt (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(L_0),  // sfix16_En15 0,0
                                                       .A_1(L_1),  // sfix16_En15 1,0
                                                       .A_2(L_2),  // sfix16_En15 0,1
                                                       .A_3(L_3),  // sfix16_En15 1,1
                                                       .B_0(y1),  // sfix16_En15
                                                       .B_1(y2),  // sfix16_En15
                                                       .ce_out(ce_out3),
                                                       .out_0(out_0_L),  // sfix33_En30
                                                       .out_1(out_1_L)  // sfix33_En30
                                                       );

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      output_0_A_reg<=0;
      output_1_A_reg<=0;
    end
    else if (ce_out1==1) begin 
      output_0_A_reg <= output_0_A;
      output_1_A_reg <= output_1_A;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      output_0_B_reg<=0;
      output_1_B_reg<=0;
    end
    else if (ce_out2==1) begin 
      output_0_B_reg <= output_0_B;
      output_1_B_reg <= output_1_B;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      output_0_L_reg<=0;
      output_1_L_reg<=0;
    end
    else if (ce_out3==1) begin 
      output_0_L_reg <= output_0_L;
      output_1_L_reg <= output_1_L;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      out_0<=0;
      out_1<=0;
    end
    else if (time_to_sum==1) begin 
      out_0 <= output_0_A_reg + output_0_B_reg + output_0_L_reg; //TODO: resizing and cast! 
      out_1 <= output_1_A_reg + output_1_B_reg + output_1_L_reg;
    end
  end 


endmodule  

