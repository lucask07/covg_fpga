// -------------------------------------------------------------
// 
// File Name: C:\Users\iande\Desktop\biquad_hdlcoder\biquad_hdlcoder\codegen\mlhdlc_biquad\hdlsrc\mlhdlc_biquad_fixpt.v
// Created: 2022-06-01 10:46:35
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
// y_out                         ce_out        1
// -- -------------------------------------------------------------
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: mlhdlc_biquad_fixpt
// Source Path: mlhdlc_biquad_fixpt
// Hierarchy Level: 0
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module mlhdlc_biquad_fixpt_folded
          (clk,
           reset,
           clk_enable,
           x_in,
           b_0,
           b_1,
           b_2,
           a_0,
           a_1,
           a_2,
           ce_out,
           y_out);


  input   clk;
  input   reset;
  input   clk_enable;
  input   signed [15:0] x_in;  // sfix16_En15
  input   [15:0] b_0;  // ufix16_En18
  input   [15:0] b_1;  // ufix16_En18
  input   [15:0] b_2;  // ufix16_En18
  input   signed [15:0] a_0;  // sfix16_En14
  input   signed [15:0] a_1;  // sfix16_En14
  input   signed [15:0] a_2;  // sfix16_En14
  output  reg ce_out;
  output  signed [15:0] y_out;  // sfix16_En15

  wire [15:0] b [0:2];  // ufix16_En18 [3]
  wire signed [15:0] a [0:2];  // sfix16_En14 [3]
  wire signed [15:0] tmp;  // sfix16_En16
  wire signed [16:0] p7tmp_cast;  // sfix17_En18
  reg signed [32:0] p7tmp_mul_temp;  // sfix33_En33
  wire signed [31:0] p7tmp_sub_cast;  // sfix32_En33
  wire signed [36:0] p7tmp_sub_cast_1;  // sfix37_En33
  reg signed [31:0] p7tmp_mul_temp_1;  // sfix32_En29
  wire signed [36:0] p7tmp_sub_cast_2;  // sfix37_En33
  wire signed [36:0] p7tmp_sub_temp;  // sfix37_En33
  reg signed [15:0] s2;  // sfix16_En16
  wire signed [15:0] tmp_1;  // sfix16_En15
  wire signed [33:0] p5tmp_add_cast;  // sfix34_En33
  wire signed [16:0] p5tmp_cast;  // sfix17_En18
  reg signed [32:0] p5tmp_mul_temp;  // sfix33_En33
  wire signed [31:0] p5tmp_add_cast_1;  // sfix32_En33
  wire signed [33:0] p5tmp_add_cast_2;  // sfix34_En33
  wire signed [33:0] p5tmp_add_temp;  // sfix34_En33
  wire signed [36:0] p5tmp_sub_cast;  // sfix37_En33
  reg signed [31:0] p5tmp_mul_temp_1;  // sfix32_En29
  wire signed [36:0] p5tmp_sub_cast_1;  // sfix37_En33
  wire signed [36:0] p5tmp_sub_temp;  // sfix37_En33
  reg signed [15:0] s1;  // sfix16_En15
  wire signed [34:0] p3y_out_add_cast;  // sfix35_En33
  wire signed [16:0] p3y_out_cast;  // sfix17_En18
  reg signed [32:0] p3y_out_mul_temp;  // sfix33_En33
  wire signed [31:0] p3y_out_add_cast_1;  // sfix32_En33
  wire signed [34:0] p3y_out_add_cast_2;  // sfix35_En33
  wire signed [34:0] p3y_out_add_temp;  // sfix35_En33


  assign b[0] = b_0;
  assign b[1] = b_1;
  assign b[2] = b_2;

  assign a[0] = a_0;
  assign a[1] = a_1;
  assign a[2] = a_2;

  //assign enb = clk_enable;
  reg [20:0] enb_reg;
  wire enb;

  always @(posedge clk) begin
    if (reset == 1'b1) begin
      enb_reg[20:0] <= 11'b0;  
    end
    else begin
      enb_reg[0] <= clk_enable;
      enb_reg[20:1] <= enb_reg[19:0];
    end
  end
  assign enb= enb_reg[13];

  //  initial value   = 1
  //  step value      = 1
  //  count to value  = 15
  reg [5:0] counter; 
  always @(posedge clk or posedge reset)
    begin : slow_clock_enable_process
      if (reset == 1'b1) begin
        counter <= 6'b000001;
      end
      else begin
        if (counter >= 6'd15 && clk_enable == 1'b1) begin
          counter <= 6'b000001;
        end
        else begin
          counter <= counter + 6'b000001;
        end
      end
    end

  reg signed [15:0] x_store;  // sfix14_En12
  reg signed [16:0] m_coeff;
  reg signed [15:0] m_in;

  always @(posedge clk) begin
    if (clk_enable == 1'b1) x_store <= x_in;
  end

  always @(posedge clk) begin 
    ce_out <= 1'b0;
    if (reset == 1'b1) begin
      p3y_out_mul_temp <= 33'd0;
    end
    case(counter)
      0: begin 
        m_coeff <= 16'b0;
        m_in <= 15'b0;
        //$display("counter %d: coeff: %d x_in: %d", counter, m_coeff, x_store);
      end
      1: begin
        m_coeff <= {1'b0, b[0]};
        m_in <= x_store;
        //$display("counter %d: coeff: %d x_in: %d", counter, m_coeff, x_store);
      end
      2: begin
        m_coeff <= {1'b0, b[1]};
        m_in <= x_store;
        //$display("counter %d: coeff: %d x_in: %d", counter, m_coeff, x_store);
      end
      3: begin
        m_coeff <= {1'b0, b[2]};
        m_in <= x_store;
        //$display("counter %d: coeff: %d x_in: %d", counter, m_coeff, x_store);
      end
      4: begin
        m_coeff <= 16'b0;
        m_in <= x_store;
        //$display("Multiplier out %d, counter %d", m_out, counter);
      end
      5: begin
        m_coeff <= 16'b0;
        m_in <= x_store;
        //$display("Multiplier out %d, counter %d", m_out, counter);
        p3y_out_mul_temp <= m_out;
      end
      6: begin
//        m_coeff <= 16'b0; 
        p5tmp_mul_temp <= m_out;
        //$display("Multiplier out %d, counter %d", m_out, counter);
      end            
      7: begin
        m_coeff <= a[1]; 
        m_in <= y_out; // must wait until y_out is ready ... requires p3y_out_mul_temp
        p7tmp_mul_temp <= m_out;
        //$display("p3y_out_mult_tmp %d", p3y_out_mul_temp);        
        //$display("s1 = %d; s2 = %d", s1, s2);
      end
      8: begin
        m_coeff <= a[2]; 
        m_in <= y_out; // must wait until y_out is ready ... requires p3y_out_mul_temp
      end
      11: begin
        //$display("p7tmp_mul_temp_1 %h and Muliplier out %h", p7tmp_mul_temp_1, m_out);
        p5tmp_mul_temp_1 <= m_out[31:0]; //omit the sign bit
      end

      12: begin
        p7tmp_mul_temp_1 <= m_out[31:0]; //omit the sign bit
  //        $display("p7tmp_mul_temp_1 %h and Muliplier out %h", p7tmp_mul_temp_1, m_out);

      end

      13: begin
        //$display("p7tmp_mul_temp_1 %h and Muliplier out %h", p7tmp_mul_temp_1, m_out);
      end

      14: begin
        ce_out <= 1'b1; // since y_out is ready can indicate to next stage.
          //$display("p7tmp_mul_temp_1 %h and Muliplier out %h", p7tmp_mul_temp_1, m_out);
      end
      default: begin
        m_coeff <= 16'b0;
        m_in <= 15'b0;
      end
      endcase 
  end

  wire signed [32:0] m_out;
  mult_gen_0 u2_mult(.CLK(clk), .SCLR(reset), .B(m_coeff), .A(m_in), .P(m_out));

  // state 2 
  assign p7tmp_cast = {1'b0, b[2]};
  //assign p7tmp_mul_temp = p7tmp_cast * x_in;
  assign p7tmp_sub_cast = p7tmp_mul_temp[31:0];
  assign p7tmp_sub_cast_1 = {{5{p7tmp_sub_cast[31]}}, p7tmp_sub_cast};
  //assign p7tmp_mul_temp_1 = a[2] * y_out;
  assign p7tmp_sub_cast_2 = {p7tmp_mul_temp_1[31], {p7tmp_mul_temp_1, 4'b0000}};
  assign p7tmp_sub_temp = p7tmp_sub_cast_1 - p7tmp_sub_cast_2;
  assign tmp = p7tmp_sub_temp[32:17];



  // state 1 
  always @(posedge clk)
    begin : s2_reg_process
      if (reset == 1'b1) begin
        s2 <= 16'sb0000000000000000;
      end
      else begin
        if (enb) begin
          s2 <= tmp;
          $display("Folded: s2 = %h", s2);
        end
      end
    end



  assign p5tmp_add_cast = {s2[15], {s2, 17'b00000000000000000}};
  assign p5tmp_cast = {1'b0, b[1]};
  //assign p5tmp_mul_temp = p5tmp_cast * x_in;
  assign p5tmp_add_cast_1 = p5tmp_mul_temp[31:0];
  assign p5tmp_add_cast_2 = {{2{p5tmp_add_cast_1[31]}}, p5tmp_add_cast_1};
  assign p5tmp_add_temp = p5tmp_add_cast + p5tmp_add_cast_2;
  assign p5tmp_sub_cast = {{3{p5tmp_add_temp[33]}}, p5tmp_add_temp};
  //assign p5tmp_mul_temp_1 = a[1] * y_out;
  assign p5tmp_sub_cast_1 = {p5tmp_mul_temp_1[31], {p5tmp_mul_temp_1, 4'b0000}};
  assign p5tmp_sub_temp = p5tmp_sub_cast - p5tmp_sub_cast_1;
  assign tmp_1 = p5tmp_sub_temp[33:18];



  // HDL code generation from MATLAB function: mlhdlc_biquad_fixpt
  // 
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // 
  //                                                                          %
  // 
  //           Generated by MATLAB 9.9 and Fixed-Point Designer 7.1           %
  // 
  //                                                                          %
  // 
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // 
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // 
  // MATLAB design: Biquad for IIR
  // 
  // 
  // 
  // Introduction: https://ccrma.stanford.edu/~jos/fp/Transposed_Direct_Forms.html
  // 
  // Transposed DF-II
  // 
  //   Modified by LJK from MATLAB IIR example
  // 
  //   This has been shown to match the MATLAB dsp.BiquadFilter 
  // 
  // %%%%%%% 
  // 
  // IIR biquad Filter
  // 
  // declare and initialize the delay registers
  // 
  // filtered output (order of update to y_out, s1, s2 might matter so update
  // 
  //   registers that impact other registers last)
  always @(posedge clk)
    begin : s1_reg_process
      if (reset == 1'b1) begin
        s1 <= 16'sb0000000000000000;
      end
      else begin
        if (enb) begin
          s1 <= tmp_1;
          $display("Folded: s1 = %h", s1);
        end
      end
    end

  assign p3y_out_add_cast = {s1[15], {s1, 18'b000000000000000000}};
  assign p3y_out_cast = {1'b0, b[0]};
  //assign p3y_out_mul_temp = p3y_out_cast * x_in;
  assign p3y_out_add_cast_1 = p3y_out_mul_temp[31:0];
  assign p3y_out_add_cast_2 = {{3{p3y_out_add_cast_1[31]}}, p3y_out_add_cast_1};
  assign p3y_out_add_temp = p3y_out_add_cast + p3y_out_add_cast_2;
  assign y_out = p3y_out_add_temp[33:18];

endmodule  // mlhdlc_biquad_fixpt

