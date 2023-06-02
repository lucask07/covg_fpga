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
  input   signed [15:0] y1;  // sfix16_En0
  input   signed [15:0] y2;  // sfix16_En0
  input   signed [15:0] u;  // sfix16_En0
  input   signed [31:0] L_0;  // sfix32_En50
  input   signed [31:0] L_1;  // sfix32_En50
  input   signed [31:0] L_2;  // sfix32_En50
  input   signed [31:0] L_3;  // sfix32_En50
  input   signed [31:0] A_0;  // sfix32_En24
  input   signed [31:0] A_1;  // sfix32_En24
  input   signed [31:0] A_2;  // sfix32_En24
  input   signed [31:0] A_3;  // sfix32_En24
  input   signed [31:0] B_0;  // ufix32_En50
  input   signed [31:0] B_1;  // ufix32_En50
  output  reg ce_out;
  output  wire signed [15:0] out_0;  // sfix16_En17
  output  wire signed [15:0] out_1;  // sfix16_En17
  
  reg signed [73:0] out_0_cast; //sfix74_En56
  reg signed [73:0] out_1_cast; //sfix74_En56

  wire signed [32:0] yest [0:1]; //sfix33_32

  wire ce_out1;
  wire ce_out2;
  wire ce_out3;

  reg out_A_sum_rdy;
  reg out_B_sum_rdy;
  reg out_L_sum_rdy;

  wire signed [65:0] out_0_A;
  wire signed [65:0] out_1_A;
  wire signed [65:0] out_0_B;
  wire signed [65:0] out_1_B;
  wire signed [65:0] out_0_L;
  wire signed [65:0] out_1_L;

  reg signed [65:0] out_0_A_reg;
  reg signed [65:0] out_1_A_reg;
  reg signed [65:0] out_0_B_reg;
  reg signed [65:0] out_1_B_reg;
  reg signed [65:0] out_0_L_reg;
  reg signed [65:0] out_1_L_reg;

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
        S0: if (out_A_sum_rdy && out_B_sum_rdy && out_L_sum_rdy) nextstate = S1; //TODO: making the assumption that all ce_out are synchronized
        S1: nextstate = S2; 
        S2: nextstate = S3;
        S3: if (clk_enable==1) nextstate = S0;
        default nextstate = S0;
    endcase
  end

  always @(*) begin
    case (state)
    S0: begin 
        ce_out <= 0; time_to_sum <=0;
        end
    S1: begin 
        ce_out <= 0; time_to_sum <=1;
        end
    S2: begin 
        ce_out <= 1; time_to_sum <=0;
        end
    S3: begin 
        ce_out <= 0; time_to_sum <=0;    
        end
    endcase 
    end

    matrix_mul_fixpt_folded #(.A_wid(32), .B_wid(33)) u1_matrix_mul_fixpt_folded (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(A_0),  // sfix32_En24 0,0
                                                       .A_1(A_1),  // sfix32_En24 1,0
                                                       .A_2(A_2),  // sfix32_En24 0,1
                                                       .A_3(A_3),  // sfix32_En24 1,1
                                                       .B_0(yest[0]),  // sfix33_En32 -- eqv. to yest 
                                                       .B_1(yest[1]),  // sfix33_32
                                                       .ce_out(ce_out1),
                                                       .out_0(out_0_A),  // sfix66_En56
                                                       .out_1(out_1_A)  // sfix66_En56
                                                       );

    matrix_mul_fixpt_folded #(.A_wid(32), .B_wid(33)) u2_matrix_mul_fixpt_folded (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(B_0),  // ufix32_En50 0,0
                                                       .A_1(B_1),  // ufix32_En50 1,0
                                                       .A_2(32'd0),  // ufix32_En50 0,1
                                                       .A_3(32'd0),  // ufix32_En50 1,1
                                                       .B_0({{17{u[15]}}, u}),  // sfix16_En0, signext -> sfix33_En0
                                                       .B_1(33'd0),  // sfix16_En0, signext -> sfix33_En0
                                                       .ce_out(ce_out2),
                                                       .out_0(out_0_B),  // sfix66_En50
                                                       .out_1(out_1_B)  // sfix66_En50
                                                       );

    matrix_mul_fixpt_folded #(.A_wid(32), .B_wid(33)) u3_matrix_mul_fixpt_folded (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(clk_enable),
                                                       .A_0(L_0),  // sfix32_En50 0,0
                                                       .A_1(L_1),  // sfix32_En50 1,0
                                                       .A_2(L_2),  // sfix32_En50 0,1
                                                       .A_3(L_3),  // sfix32_En50 1,1
                                                       .B_0({{17{y1[15]}}, y1}),  // sfix16_En0, signext -> sfix33_En0
                                                       .B_1({{17{y2[15]}}, y2}),  // sfix16_En0, signext -> sfix33_En0
                                                       .ce_out(ce_out3),
                                                       .out_0(out_0_L),  // sfix66_En50
                                                       .out_1(out_1_L)  // sfix66_En50
                                                       );

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      out_0_A_reg<=66'd0;
      out_1_A_reg<=66'd0;
      out_A_sum_rdy<=1'b0;
    end
    else if (ce_out1==1) begin 
      out_0_A_reg <= out_0_A;
      out_1_A_reg <= out_1_A;
      out_A_sum_rdy <= 1'b1;
    end
    else if (time_to_sum) begin
      out_A_sum_rdy <= 1'b0;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      out_0_B_reg<=66'd0;
      out_1_B_reg<=66'd0;
      out_B_sum_rdy<=1'b0;
    end
    else if (ce_out2==1) begin 
      out_0_B_reg <= out_0_B;
      out_1_B_reg <= out_1_B;
      out_B_sum_rdy <= 1'b1;
    end
     else if (time_to_sum) begin
      out_B_sum_rdy <= 1'b0;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      out_0_L_reg<=66'd0;
      out_1_L_reg<=66'd0;
      out_L_sum_rdy<=1'b0;
    end
    else if (ce_out3==1) begin 
      out_0_L_reg <= out_0_L;
      out_1_L_reg <= out_1_L;
      out_L_sum_rdy <= 1'b1;
    end
     else if (time_to_sum) begin
      out_L_sum_rdy <= 1'b0;
    end
  end

  always @(posedge clk) begin
    if (reset == 1'b1) begin 
      out_0_cast <= 74'd0;
      out_1_cast <= 74'd0; //33En30 
    end
    else if (time_to_sum==1) begin 
      out_0_cast <= {{8{out_0_A_reg[65]}}, out_0_A_reg} + { {2{out_0_B_reg[48]}}, out_0_B_reg, 6'b0} + { {2{out_0_L_reg[48]}}, out_0_L_reg, 6'b0}; //sfix74_en56
      out_1_cast <= {{8{out_1_A_reg[65]}}, out_1_A_reg} + { {2{out_1_B_reg[48]}}, out_1_B_reg, 6'b0} + { {2{out_1_L_reg[48]}}, out_1_L_reg, 6'b0}; //sfix74_en56
    end
  end 

  reg signed [32:0] yest_reg_reg[0:1];

  always @(posedge clk or posedge reset)
    begin : yest_reg_process
      if (reset == 1'b1) begin
        yest_reg_reg[0] <= 33'sh000000000;
        yest_reg_reg[1] <= 33'sh000000000;
      end
      else begin
        if (clk_enable) begin
          yest_reg_reg[0] <= out_0_cast[56:24];
          yest_reg_reg[1] <= out_1_cast[56:24];
        end
      end
    end

assign yest[0] = out_0_cast[56:24];
assign yest[1] = out_1_cast[56:24];

assign out_0 = yest_reg_reg[0][32:17];
assign out_1 = yest_reg_reg[1][32:17];

endmodule  

