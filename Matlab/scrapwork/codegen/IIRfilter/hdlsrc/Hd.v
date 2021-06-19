// -------------------------------------------------------------
// 
// File Name: C:\Users\iande\Desktop\covg_fpga\Matlab\scrapwork\codegen\IIRfilter\hdlsrc\Hd.v
// Created: 2021-06-16 10:06:29
// 
// Generated by MATLAB 9.9, MATLAB Coder 5.1 and HDL Coder 3.17
// 
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: Hd
// Source Path: IIRfilter_fixpt/Hd
// Hierarchy Level: 1
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module Hd
          (clk,
           reset,
           enb,
           Hd_in,
           Hd_out);


  input   clk;
  input   reset;
  input   enb;
  input   signed [15:0] Hd_in;  // sfix16_En15
  output  signed [13:0] Hd_out;  // sfix14_En8


  wire signed [15:0] scaleconst1;  // sfix16_En17
  wire signed [31:0] multiplier_mul_temp;  // sfix32_En32
  wire signed [36:0] scale1;  // sfix37_En32
  wire signed [15:0] scaletypeconvert1;  // sfix16_En11
  wire signed [33:0] inputconv1;  // sfix34_En29
  wire signed [15:0] coeff_a2_section1;  // sfix16_En14
  wire signed [15:0] coeff_a3_section1;  // sfix16_En14
  wire signed [15:0] delay_section1 [0:1];  // sfix16_En15 [2]
  wire signed [15:0] delay_section1_1;  // sfix16_En15
  wire signed [31:0] a3mul1;  // sfix32_En29
  wire signed [33:0] a1sum1_cast2;  // sfix34_En29
  wire signed [15:0] typeconvert1;  // sfix16_En15
  reg signed [15:0] delay_process_section1_reg [0:1];  // sfix16 [2]
  wire signed [15:0] delay_process_section1_reg_next [0:1];  // sfix16_En15 [2]
  wire signed [15:0] delay_section1_0;  // sfix16_En15
  wire signed [31:0] a2mul1;  // sfix32_En29
  wire signed [33:0] a2sum1_cast2;  // sfix34_En29
  wire signed [34:0] Sub_sub_cast;  // sfix35_En29
  wire signed [34:0] Sub_sub_cast_1;  // sfix35_En29
  wire signed [34:0] a2sum1_temp;  // sfix35_En29
  wire signed [33:0] a2sum1;  // sfix34_En29
  wire signed [34:0] Sub_sub_cast_2;  // sfix35_En29
  wire signed [34:0] Sub_sub_cast_3;  // sfix35_En29
  wire signed [34:0] a1sum1_temp;  // sfix35_En29
  wire signed [33:0] a1sum1;  // sfix34_En29
  wire signed [31:0] b1mul1;  // sfix32_En28
  wire signed [33:0] b1multypeconvert1;  // sfix34_En28
  wire signed [31:0] b2mul1;  // sfix32_En28
  wire signed [33:0] adder_add_cast;  // sfix34_En28
  wire signed [33:0] b2sum1;  // sfix34_En28
  wire signed [31:0] b3mul1;  // sfix32_En28
  wire signed [33:0] adder_add_cast_1;  // sfix34_En28
  wire signed [33:0] b1sum1;  // sfix34_En28
  wire signed [15:0] section_result1;  // sfix16_En10
  wire signed [15:0] scaleconst2;  // sfix16_En17
  wire signed [31:0] multiplier_mul_temp_1;  // sfix32_En27
  wire signed [36:0] scale2;  // sfix37_En32
  wire signed [15:0] scaletypeconvert2;  // sfix16_En11
  wire signed [33:0] inputconv2;  // sfix34_En29
  wire signed [15:0] coeff_a2_section2;  // sfix16_En14
  wire signed [15:0] coeff_a3_section2;  // sfix16_En14
  wire signed [15:0] delay_section2 [0:1];  // sfix16_En15 [2]
  wire signed [15:0] delay_section2_1;  // sfix16_En15
  wire signed [31:0] a3mul2;  // sfix32_En29
  wire signed [33:0] a1sum2_cast2;  // sfix34_En29
  wire signed [15:0] typeconvert2;  // sfix16_En15
  reg signed [15:0] delay_process_section2_reg [0:1];  // sfix16 [2]
  wire signed [15:0] delay_process_section2_reg_next [0:1];  // sfix16_En15 [2]
  wire signed [15:0] delay_section2_0;  // sfix16_En15
  wire signed [31:0] a2mul2;  // sfix32_En29
  wire signed [33:0] a2sum2_cast2;  // sfix34_En29
  wire signed [34:0] Sub_sub_cast_4;  // sfix35_En29
  wire signed [34:0] Sub_sub_cast_5;  // sfix35_En29
  wire signed [34:0] a2sum2_temp;  // sfix35_En29
  wire signed [33:0] a2sum2;  // sfix34_En29
  wire signed [34:0] Sub_sub_cast_6;  // sfix35_En29
  wire signed [34:0] Sub_sub_cast_7;  // sfix35_En29
  wire signed [34:0] a1sum2_temp;  // sfix35_En29
  wire signed [33:0] a1sum2;  // sfix34_En29
  wire signed [31:0] b1mul2;  // sfix32_En28
  wire signed [33:0] b1multypeconvert2;  // sfix34_En28
  wire signed [31:0] b2mul2;  // sfix32_En28
  wire signed [33:0] adder_add_cast_2;  // sfix34_En28
  wire signed [33:0] b2sum2;  // sfix34_En28
  wire signed [31:0] b3mul2;  // sfix32_En28
  wire signed [33:0] adder_add_cast_3;  // sfix34_En28
  wire signed [33:0] b1sum2;  // sfix34_En28
  wire signed [15:0] section_result2;  // sfix16_En10
  wire signed [15:0] scaleconst3;  // sfix16_En17
  wire signed [31:0] multiplier_mul_temp_2;  // sfix32_En27
  wire signed [36:0] scale3;  // sfix37_En32
  wire signed [15:0] scaletypeconvert3;  // sfix16_En11
  wire signed [33:0] inputconv3;  // sfix34_En29
  wire signed [15:0] coeff_a2_section3;  // sfix16_En14
  wire signed [15:0] a1sumtypeconvert3;  // sfix16_En15
  reg signed [15:0] delay_section3;  // sfix16_En15
  wire signed [31:0] a2mul3;  // sfix32_En29
  wire signed [33:0] a1sum3_cast2;  // sfix34_En29
  wire signed [34:0] Sub_sub_cast_8;  // sfix35_En29
  wire signed [34:0] Sub_sub_cast_9;  // sfix35_En29
  wire signed [34:0] a1sum3_temp;  // sfix35_En29
  wire signed [33:0] a1sum3;  // sfix34_En29
  wire signed [31:0] b1mul3;  // sfix32_En28
  wire signed [33:0] b1multypeconvert3;  // sfix34_En28
  wire signed [31:0] b2mul3;  // sfix32_En28
  wire signed [33:0] adder_add_cast_4;  // sfix34_En28
  wire signed [33:0] b1sum3;  // sfix34_En28
  wire signed [13:0] output_typeconvert;  // sfix14_En8


  assign scaleconst1 = 16'sb0000101111110100;



  assign multiplier_mul_temp = Hd_in * scaleconst1;
  assign scale1 = {{5{multiplier_mul_temp[31]}}, multiplier_mul_temp};



  assign scaletypeconvert1 = scale1[36:21] + $signed({1'b0, scale1[20] & (scale1[21] | (|scale1[19:0]))});



  assign inputconv1 = {scaletypeconvert1, 18'b000000000000000000};



  assign coeff_a2_section1 = 16'sb1001000101011101;



  assign coeff_a3_section1 = 16'sb0011010010011101;



  assign delay_section1_1 = delay_section1[1];

  assign a3mul1 = delay_section1_1 * coeff_a3_section1;



  assign a1sum1_cast2 = {{2{a3mul1[31]}}, a3mul1};



  always @(posedge clk or posedge reset)
    begin : delay_process_section1_process
      if (reset == 1'b1) begin
        delay_process_section1_reg[0] <= 16'sb0000000000000000;
        delay_process_section1_reg[1] <= 16'sb0000000000000000;
      end
      else begin
        if (enb) begin
          delay_process_section1_reg[0] <= delay_process_section1_reg_next[0];
          delay_process_section1_reg[1] <= delay_process_section1_reg_next[1];
        end
      end
    end

  assign delay_section1[0] = delay_process_section1_reg[0];
  assign delay_section1[1] = delay_process_section1_reg[1];
  assign delay_process_section1_reg_next[0] = typeconvert1;
  assign delay_process_section1_reg_next[1] = delay_process_section1_reg[0];



  assign delay_section1_0 = delay_section1[0];

  assign a2mul1 = delay_section1_0 * coeff_a2_section1;



  assign a2sum1_cast2 = {{2{a2mul1[31]}}, a2mul1};



  assign Sub_sub_cast = {inputconv1[33], inputconv1};
  assign Sub_sub_cast_1 = {a2sum1_cast2[33], a2sum1_cast2};
  assign a2sum1_temp = Sub_sub_cast - Sub_sub_cast_1;



  assign a2sum1 = a2sum1_temp[33:0];



  assign Sub_sub_cast_2 = {a2sum1[33], a2sum1};
  assign Sub_sub_cast_3 = {a1sum1_cast2[33], a1sum1_cast2};
  assign a1sum1_temp = Sub_sub_cast_2 - Sub_sub_cast_3;



  assign a1sum1 = a1sum1_temp[33:0];



  assign typeconvert1 = a1sum1[29:14] + $signed({1'b0, a1sum1[13] & (a1sum1[14] | (|a1sum1[12:0]))});



  // coeff_b1_section1
  assign b1mul1 = {{3{typeconvert1[15]}}, {typeconvert1, 13'b0000000000000}};



  assign b1multypeconvert1 = {{2{b1mul1[31]}}, b1mul1};



  // coeff_b2_section1
  assign b2mul1 = {{2{delay_section1_0[15]}}, {delay_section1_0, 14'b00000000000000}};



  assign adder_add_cast = {{2{b2mul1[31]}}, b2mul1};
  assign b2sum1 = b1multypeconvert1 + adder_add_cast;



  // coeff_b3_section1
  assign b3mul1 = {{3{delay_section1_1[15]}}, {delay_section1_1, 13'b0000000000000}};



  assign adder_add_cast_1 = {{2{b3mul1[31]}}, b3mul1};
  assign b1sum1 = b2sum1 + adder_add_cast_1;



  assign section_result1 = b1sum1[33:18] + $signed({1'b0, b1sum1[17] & (b1sum1[18] | (|b1sum1[16:0]))});



  assign scaleconst2 = 16'sb0000101001110011;



  assign multiplier_mul_temp_1 = section_result1 * scaleconst2;
  assign scale2 = {multiplier_mul_temp_1, 5'b00000};



  assign scaletypeconvert2 = scale2[36:21] + $signed({1'b0, scale2[20] & (scale2[21] | (|scale2[19:0]))});



  assign inputconv2 = {scaletypeconvert2, 18'b000000000000000000};



  assign coeff_a2_section2 = 16'sb1001111101001001;



  assign coeff_a3_section2 = 16'sb0010010111110000;



  assign delay_section2_1 = delay_section2[1];

  assign a3mul2 = delay_section2_1 * coeff_a3_section2;



  assign a1sum2_cast2 = {{2{a3mul2[31]}}, a3mul2};



  always @(posedge clk or posedge reset)
    begin : delay_process_section2_process
      if (reset == 1'b1) begin
        delay_process_section2_reg[0] <= 16'sb0000000000000000;
        delay_process_section2_reg[1] <= 16'sb0000000000000000;
      end
      else begin
        if (enb) begin
          delay_process_section2_reg[0] <= delay_process_section2_reg_next[0];
          delay_process_section2_reg[1] <= delay_process_section2_reg_next[1];
        end
      end
    end

  assign delay_section2[0] = delay_process_section2_reg[0];
  assign delay_section2[1] = delay_process_section2_reg[1];
  assign delay_process_section2_reg_next[0] = typeconvert2;
  assign delay_process_section2_reg_next[1] = delay_process_section2_reg[0];



  assign delay_section2_0 = delay_section2[0];

  assign a2mul2 = delay_section2_0 * coeff_a2_section2;



  assign a2sum2_cast2 = {{2{a2mul2[31]}}, a2mul2};



  assign Sub_sub_cast_4 = {inputconv2[33], inputconv2};
  assign Sub_sub_cast_5 = {a2sum2_cast2[33], a2sum2_cast2};
  assign a2sum2_temp = Sub_sub_cast_4 - Sub_sub_cast_5;



  assign a2sum2 = a2sum2_temp[33:0];



  assign Sub_sub_cast_6 = {a2sum2[33], a2sum2};
  assign Sub_sub_cast_7 = {a1sum2_cast2[33], a1sum2_cast2};
  assign a1sum2_temp = Sub_sub_cast_6 - Sub_sub_cast_7;



  assign a1sum2 = a1sum2_temp[33:0];



  assign typeconvert2 = a1sum2[29:14] + $signed({1'b0, a1sum2[13] & (a1sum2[14] | (|a1sum2[12:0]))});



  // coeff_b1_section2
  assign b1mul2 = {{3{typeconvert2[15]}}, {typeconvert2, 13'b0000000000000}};



  assign b1multypeconvert2 = {{2{b1mul2[31]}}, b1mul2};



  // coeff_b2_section2
  assign b2mul2 = {{2{delay_section2_0[15]}}, {delay_section2_0, 14'b00000000000000}};



  assign adder_add_cast_2 = {{2{b2mul2[31]}}, b2mul2};
  assign b2sum2 = b1multypeconvert2 + adder_add_cast_2;



  // coeff_b3_section2
  assign b3mul2 = {{3{delay_section2_1[15]}}, {delay_section2_1, 13'b0000000000000}};



  assign adder_add_cast_3 = {{2{b3mul2[31]}}, b3mul2};
  assign b1sum2 = b2sum2 + adder_add_cast_3;



  assign section_result2 = b1sum2[33:18] + $signed({1'b0, b1sum2[17] & (b1sum2[18] | (|b1sum2[16:0]))});



  assign scaleconst3 = 16'sb0100011101110001;



  assign multiplier_mul_temp_2 = section_result2 * scaleconst3;
  assign scale3 = {multiplier_mul_temp_2, 5'b00000};



  assign scaletypeconvert3 = scale3[36:21] + $signed({1'b0, scale3[20] & (scale3[21] | (|scale3[19:0]))});



  assign inputconv3 = {scaletypeconvert3, 18'b000000000000000000};



  assign coeff_a2_section3 = 16'sb1101000111011100;



  always @(posedge clk or posedge reset)
    begin : delay_process_section3_process
      if (reset == 1'b1) begin
        delay_section3 <= 16'sb0000000000000000;
      end
      else begin
        if (enb) begin
          delay_section3 <= a1sumtypeconvert3;
        end
      end
    end



  assign a2mul3 = delay_section3 * coeff_a2_section3;



  assign a1sum3_cast2 = {{2{a2mul3[31]}}, a2mul3};



  assign Sub_sub_cast_8 = {inputconv3[33], inputconv3};
  assign Sub_sub_cast_9 = {a1sum3_cast2[33], a1sum3_cast2};
  assign a1sum3_temp = Sub_sub_cast_8 - Sub_sub_cast_9;



  assign a1sum3 = a1sum3_temp[33:0];



  assign a1sumtypeconvert3 = a1sum3[29:14] + $signed({1'b0, a1sum3[13] & (a1sum3[14] | (|a1sum3[12:0]))});



  // coeff_b1_section3
  assign b1mul3 = {{3{a1sumtypeconvert3[15]}}, {a1sumtypeconvert3, 13'b0000000000000}};



  assign b1multypeconvert3 = {{2{b1mul3[31]}}, b1mul3};



  // coeff_b2_section3
  assign b2mul3 = {{3{delay_section3[15]}}, {delay_section3, 13'b0000000000000}};



  assign adder_add_cast_4 = {{2{b2mul3[31]}}, b2mul3};
  assign b1sum3 = b1multypeconvert3 + adder_add_cast_4;



  assign output_typeconvert = b1sum3[33:20] + $signed({1'b0, b1sum3[19] & (b1sum3[20] | (|b1sum3[18:0]))});



  assign Hd_out = output_typeconvert;

endmodule  // Hd

