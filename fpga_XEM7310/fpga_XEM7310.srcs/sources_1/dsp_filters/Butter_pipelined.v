// -------------------------------------------------------------
//
// Module: Butter_pipelined
// Generated by MATLAB(R) 9.9 and Filter Design HDL Coder 3.1.8.
// Generated on: 2022-01-05 13:21:30
// -------------------------------------------------------------

// -------------------------------------------------------------
// HDL Code Generation Options:
//
// ResetType: Synchronous
// OptimizeForHDL: on
// TargetDirectory: C:\Users\iande\Desktop\FilterCoefficients
// AddPipelineRegisters: on
// Name: Butter_pipelined
// CoefficientSource: ProcessorInterface
// TargetLanguage: Verilog
// TestBenchStimulus: step 
// GenerateHDLTestBench: off

// -------------------------------------------------------------
// HDL Implementation    : Fully parallel
// -------------------------------------------------------------
// Filter Settings:
//
// Discrete-Time IIR Filter (real)
// -------------------------------
// Filter Structure    : Direct-Form II Transposed, Second-Order Sections
// Number of Sections  : 2
// Stable              : Yes
// Linear Phase        : No
// Arithmetic          : fixed
// Numerator           : s32,29 -> [-4 4)
// Denominator         : s32,30 -> [-2 2)
// Scale Values        : s32,31 -> [-1 1)
// Input               : s16,15 -> [-1 1)
// Section Input       : s16,15 -> [-1 1)
// Section Output      : s16,14 -> [-2 2)
// Output              : s14,12 -> [-2 2)
// State               : s16,14 -> [-2 2)
// Numerator Prod      : s48,44 -> [-8 8)
// Denominator Prod    : s48,44 -> [-8 8)
// Numerator Accum     : s49,44 -> [-16 16)
// Denominator Accum   : s49,44 -> [-16 16)
// Round Mode          : convergent
// Overflow Mode       : wrap
// Cast Before Sum     : false
// -------------------------------------------------------------




`timescale 1 ns / 1 ns

module Butter_pipelined
               (
                clk,
                clk_enable,
                reset,
                filter_in,
                write_enable,
                write_done,
                write_address,
                coeffs_in,
                filter_out
                );

  input   clk; 
  input   clk_enable; 
  input   reset; 
  input   signed [15:0] filter_in; //sfix16_En15
  input   write_enable; 
  input   write_done; 
  input   [3:0] write_address; //ufix4
  input   signed [31:0] coeffs_in; //sfix32
  output  signed [13:0] filter_out; //sfix14_En12

////////////////////////////////////////////////////////////////
//Module Architecture: Butter_pipelined
////////////////////////////////////////////////////////////////
  // Local Functions
  // Type Definitions
  // Constants
  // Signals
  reg  signed [15:0] input_register; // sfix16_En15
  reg  write_enable_reg; // boolean
  reg  write_done_reg; // boolean
  reg  [3:0] write_address_reg; // ufix4
  reg  signed [31:0] coeffs_in_reg; // sfix32
  // Section 1   Processor Interface Signals 
  wire signed [31:0] coeff_scale1_assigned; // sfix32_En31
  wire signed [31:0] coeff_scale1_temp; // sfix32_En31
  reg  signed [31:0] coeff_scale1_reg; // sfix32_En31
  reg  signed [31:0] coeff_scale1_shadow_reg; // sfix32_En31
  wire signed [15:0] scale1; // sfix16_En15
  //wire signed [47:0] mul_temp; // sfix48_En46
  reg signed [47:0] mul_temp; // sfix48_En46
  wire signed [31:0] coeff_b1_section1_assigned; // sfix32_En29
  wire signed [31:0] coeff_b1_section1_temp; // sfix32_En29
  reg  signed [31:0] coeff_b1_section1_reg; // sfix32_En29
  reg  signed [31:0] coeff_b1_section1_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_b2_section1_assigned; // sfix32_En29
  wire signed [31:0] coeff_b2_section1_temp; // sfix32_En29
  reg  signed [31:0] coeff_b2_section1_reg; // sfix32_En29
  reg  signed [31:0] coeff_b2_section1_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_b3_section1_assigned; // sfix32_En29
  wire signed [31:0] coeff_b3_section1_temp; // sfix32_En29
  reg  signed [31:0] coeff_b3_section1_reg; // sfix32_En29
  reg  signed [31:0] coeff_b3_section1_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_a2_section1_assigned; // sfix32_En30
  wire signed [31:0] coeff_a2_section1_temp; // sfix32_En30
  reg  signed [31:0] coeff_a2_section1_reg; // sfix32_En30
  reg  signed [31:0] coeff_a2_section1_shadow_reg; // sfix32_En30
  wire signed [31:0] coeff_a3_section1_assigned; // sfix32_En30
  wire signed [31:0] coeff_a3_section1_temp; // sfix32_En30
  reg  signed [31:0] coeff_a3_section1_reg; // sfix32_En30
  reg  signed [31:0] coeff_a3_section1_shadow_reg; // sfix32_En30
  // Section 1 Signals 
  wire signed [48:0] ab1sum1; // sfix49_En44
  wire signed [48:0] ab2sum1; // sfix49_En44
  wire signed [48:0] ab3sum1; // sfix49_En44
  wire signed [48:0] b2sum1; // sfix49_En44
  reg  signed [15:0] delay1_section1; // sfix16_En14
  reg  signed [15:0] delay2_section1; // sfix16_En14
  wire signed [15:0] inputconv1; // sfix16_En15
  wire signed [15:0] feedback1; // sfix16_En14
  //wire signed [47:0] a2mul1; // sfix48_En44
  reg signed [47:0] a2mul1; // sfix48_En44
  //wire signed [47:0] a3mul1; // sfix48_En44
  reg signed [47:0] a3mul1; // sfix48_En44
  //wire signed [47:0] b1mul1; // sfix48_En44
  reg signed [47:0] b1mul1; // sfix48_En44
  //wire signed [47:0] b2mul1; // sfix48_En44
  reg signed [47:0] b2mul1; // sfix48_En44
  //wire signed [47:0] b3mul1; // sfix48_En44
  reg signed [47:0] b3mul1; // sfix48_En44
  wire signed [47:0] sub_signext; // sfix48_En44
  wire signed [47:0] sub_signext_1; // sfix48_En44
  wire signed [47:0] add_signext; // sfix48_En44
  wire signed [47:0] add_signext_1; // sfix48_En44
  wire signed [48:0] sub_signext_2; // sfix49_En44
  wire signed [48:0] sub_signext_3; // sfix49_En44
  wire signed [49:0] sub_temp; // sfix50_En44
  wire signed [47:0] add_signext_2; // sfix48_En44
  wire signed [47:0] add_signext_3; // sfix48_En44
  wire signed [15:0] delay1_typeconvert1; // sfix16_En14
  wire signed [15:0] delay2_typeconvert1; // sfix16_En14
  reg  signed [15:0] sos_pipeline1; // sfix16_En14
  // Section 2   Processor Interface Signals 
  wire signed [31:0] coeff_scale2_assigned; // sfix32_En31
  wire signed [31:0] coeff_scale2_temp; // sfix32_En31
  reg  signed [31:0] coeff_scale2_reg; // sfix32_En31
  reg  signed [31:0] coeff_scale2_shadow_reg; // sfix32_En31
  wire signed [15:0] scale2; // sfix16_En15
  //wire signed [47:0] mul_temp_1; // sfix48_En45
  reg signed [47:0] mul_temp_1; // sfix48_En45
  wire signed [31:0] coeff_b1_section2_assigned; // sfix32_En29
  wire signed [31:0] coeff_b1_section2_temp; // sfix32_En29
  reg  signed [31:0] coeff_b1_section2_reg; // sfix32_En29
  reg  signed [31:0] coeff_b1_section2_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_b2_section2_assigned; // sfix32_En29
  wire signed [31:0] coeff_b2_section2_temp; // sfix32_En29
  reg  signed [31:0] coeff_b2_section2_reg; // sfix32_En29
  reg  signed [31:0] coeff_b2_section2_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_b3_section2_assigned; // sfix32_En29
  wire signed [31:0] coeff_b3_section2_temp; // sfix32_En29
  reg  signed [31:0] coeff_b3_section2_reg; // sfix32_En29
  reg  signed [31:0] coeff_b3_section2_shadow_reg; // sfix32_En29
  wire signed [31:0] coeff_a2_section2_assigned; // sfix32_En30
  wire signed [31:0] coeff_a2_section2_temp; // sfix32_En30
  reg  signed [31:0] coeff_a2_section2_reg; // sfix32_En30
  reg  signed [31:0] coeff_a2_section2_shadow_reg; // sfix32_En30
  wire signed [31:0] coeff_a3_section2_assigned; // sfix32_En30
  wire signed [31:0] coeff_a3_section2_temp; // sfix32_En30
  reg  signed [31:0] coeff_a3_section2_reg; // sfix32_En30
  reg  signed [31:0] coeff_a3_section2_shadow_reg; // sfix32_En30
  // Section 2 Signals 
  wire signed [48:0] ab1sum2; // sfix49_En44
  wire signed [48:0] ab2sum2; // sfix49_En44
  wire signed [48:0] ab3sum2; // sfix49_En44
  wire signed [48:0] b2sum2; // sfix49_En44
  reg  signed [15:0] delay1_section2; // sfix16_En14
  reg  signed [15:0] delay2_section2; // sfix16_En14
  wire signed [15:0] inputconv2; // sfix16_En15
  wire signed [15:0] feedback2; // sfix16_En14
  //wire signed [47:0] a2mul2; // sfix48_En44
  reg signed [47:0] a2mul2; // sfix48_En44
  //wire signed [47:0] a3mul2; // sfix48_En44
  reg signed [47:0] a3mul2; // sfix48_En44
  //wire signed [47:0] b1mul2; // sfix48_En44
  reg signed [47:0] b1mul2; // sfix48_En44
  //wire signed [47:0] b2mul2; // sfix48_En44
  reg signed [47:0] b2mul2; // sfix48_En44
  //wire signed [47:0] b3mul2; // sfix48_En44
  reg signed [47:0] b3mul2; // sfix48_En44
  wire signed [47:0] sub_signext_4; // sfix48_En44
  wire signed [47:0] sub_signext_5; // sfix48_En44
  wire signed [47:0] add_signext_4; // sfix48_En44
  wire signed [47:0] add_signext_5; // sfix48_En44
  wire signed [48:0] sub_signext_6; // sfix49_En44
  wire signed [48:0] sub_signext_7; // sfix49_En44
  wire signed [49:0] sub_temp_1; // sfix50_En44
  wire signed [47:0] add_signext_6; // sfix48_En44
  wire signed [47:0] add_signext_7; // sfix48_En44
  wire signed [15:0] delay1_typeconvert2; // sfix16_En14
  wire signed [15:0] delay2_typeconvert2; // sfix16_En14
  // Last Section Value --   Processor Interface Signals 
  wire signed [31:0] coeff_scale3_assigned; // sfix32_En31
  wire signed [31:0] coeff_scale3_temp; // sfix32_En31
  reg  signed [31:0] coeff_scale3_reg; // sfix32_En31
  reg  signed [31:0] coeff_scale3_shadow_reg; // sfix32_En31
  wire signed [13:0] scale3; // sfix14_En12
  //wire signed [47:0] mul_temp_2; // sfix48_En45
  reg signed [47:0] mul_temp_2; // sfix48_En45
  wire signed [13:0] output_typeconvert; // sfix14_En12
  reg  signed [13:0] output_register; // sfix14_En12

  // Block Statements
  always @ ( posedge clk)
    begin: input_reg_process
      if (reset == 1'b1) begin
        input_register <= 0;
        write_enable_reg <= 1'b0;
        write_done_reg <= 1'b0;
        write_address_reg <= 0;
        coeffs_in_reg <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          input_register <= filter_in;
          write_enable_reg <= write_enable;
          write_done_reg <= write_done;
          write_address_reg <= write_address;
          coeffs_in_reg <= coeffs_in;
        end
      end
    end // input_reg_process
    
    //Shared Multiplier
    reg [4:0] ena;
    reg [15:0] A;
    reg [31:0] B;
    wire [47:0] P;
    
    mult_gen_0 mult1(.CLK(clk), .A(A), .B(B), .P(P));
    
    always @ ( posedge clk)begin
        if(reset == 1'b1)begin
            A <= 1'b0;
            B <= 1'b0;
            ena <= 4'b0;
            mul_temp <= 47'b0;
            a2mul1 <= 47'b0;
            a3mul1 <= 47'b0;
            b1mul1 <= 47'b0;
            b2mul1 <= 47'b0;
            b3mul1 <= 47'b0;
            mul_temp_1 <= 47'b0;
            a2mul2 <= 47'b0;
            a3mul2 <= 47'b0;
            b1mul2 <= 47'b0;
            b2mul2 <= 47'b0;
            b3mul2 <= 47'b0;
            mul_temp_2 <= 47'b0;
            sos_pipeline1 <= 16'b0;
        end
        else if(clk_enable == 1'b1)begin
            ena <= 4'b0;
        end
        else if(ena < 5'h10) begin
            ena <= ena + 1'b1;
        end
    end
    always @ ( negedge clk)begin
        if(ena == 5'h00)begin
            A <= input_register;
            B <= coeff_scale1_shadow_reg;
        end
        else if(ena == 5'h01)begin
            A <= inputconv1;
            B <= coeff_b3_section1_shadow_reg;
        end
        else if(ena == 5'h02)begin
            A <= feedback1;
            B <= coeff_a3_section1_shadow_reg;
        end
        else if(ena == 5'h03)begin
            A <= inputconv1;
            B <= coeff_b2_section1_shadow_reg;
        end
        else if(ena == 5'h04)begin//wait four cycles to grab mult output since mult has 4 pipeline stages
            mul_temp <= P;
            A <= feedback1;
            B <= coeff_a2_section1_shadow_reg;
        end
        else if(ena == 5'h05)begin
            sos_pipeline1 <= feedback1;
            b3mul1 <= P;
            A <= inputconv1;
            B <= coeff_b1_section1_shadow_reg;
        end
        else if(ena == 5'h06)begin
            a3mul1 <= P;
            A <= sos_pipeline1;
            B <= coeff_scale2_shadow_reg;
        end
        else if(ena == 5'h07)begin
            b2mul1 <= P;
            A <= inputconv2;
            B <= coeff_b3_section2_shadow_reg;
        end
        else if(ena == 5'h08)begin
            a2mul1 <= P;
            A <= feedback2;
            B <= coeff_a3_section2_shadow_reg;
        end
        else if(ena == 5'h09)begin
            b1mul1 <= P;
            A <= inputconv2;
            B <= coeff_b2_section2_shadow_reg;
        end
        else if(ena == 5'h0a)begin
            mul_temp_1 <= P;
            A <= feedback2;
            B <= coeff_a2_section2_shadow_reg;
        end
        else if(ena == 5'h0b)begin
            b3mul2 <= P;
            A <= inputconv2;
            B <= coeff_b1_section2_shadow_reg;
        end
        else if(ena == 5'h0c)begin
            a3mul2 <= P;
            A <= feedback2;
            B <= coeff_scale3_shadow_reg;
        end
        else if(ena == 5'h0d)begin
            b2mul2 <= P;
        end
        else if(ena == 5'h0e)begin
            a2mul2 <= P;
        end
        else if(ena == 5'h0f)begin
            b1mul2 <= P;
        end
        else if(ena == 5'h10)begin
            mul_temp_2 <= P;
        end
    end

  //   -------- Section 1 Processor Interface logic------------------

  //assign mul_temp = input_register * coeff_scale1_shadow_reg;
  assign scale1 = (mul_temp[46:0] + {mul_temp[31], {30{~mul_temp[31]}}})>>>31;

  assign coeff_scale1_assigned = (write_address_reg == 4'b0000) ? coeffs_in_reg :
                           coeff_scale1_reg;
  assign coeff_scale1_temp = (write_enable_reg == 1'b1) ? coeff_scale1_assigned :
                       coeff_scale1_reg;
  assign coeff_b1_section1_assigned = (write_address_reg == 4'b0001) ? coeffs_in_reg :
                                coeff_b1_section1_reg;
  assign coeff_b1_section1_temp = (write_enable_reg == 1'b1) ? coeff_b1_section1_assigned :
                            coeff_b1_section1_reg;
  assign coeff_b2_section1_assigned = (write_address_reg == 4'b0010) ? coeffs_in_reg :
                                coeff_b2_section1_reg;
  assign coeff_b2_section1_temp = (write_enable_reg == 1'b1) ? coeff_b2_section1_assigned :
                            coeff_b2_section1_reg;
  assign coeff_b3_section1_assigned = (write_address_reg == 4'b0011) ? coeffs_in_reg :
                                coeff_b3_section1_reg;
  assign coeff_b3_section1_temp = (write_enable_reg == 1'b1) ? coeff_b3_section1_assigned :
                            coeff_b3_section1_reg;
  assign coeff_a2_section1_assigned = (write_address_reg == 4'b0100) ? coeffs_in_reg :
                                coeff_a2_section1_reg;
  assign coeff_a2_section1_temp = (write_enable_reg == 1'b1) ? coeff_a2_section1_assigned :
                            coeff_a2_section1_reg;
  assign coeff_a3_section1_assigned = (write_address_reg == 4'b0101) ? coeffs_in_reg :
                                coeff_a3_section1_reg;
  assign coeff_a3_section1_temp = (write_enable_reg == 1'b1) ? coeff_a3_section1_assigned :
                            coeff_a3_section1_reg;
  always @ ( posedge clk)
    begin: coeff_reg_process_section1
      if (reset == 1'b1) begin
        coeff_scale1_reg <= 0;
        coeff_b1_section1_reg <= 0;
        coeff_b2_section1_reg <= 0;
        coeff_b3_section1_reg <= 0;
        coeff_a2_section1_reg <= 0;
        coeff_a3_section1_reg <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          coeff_scale1_reg <= coeff_scale1_temp;
          coeff_b1_section1_reg <= coeff_b1_section1_temp;
          coeff_b2_section1_reg <= coeff_b2_section1_temp;
          coeff_b3_section1_reg <= coeff_b3_section1_temp;
          coeff_a2_section1_reg <= coeff_a2_section1_temp;
          coeff_a3_section1_reg <= coeff_a3_section1_temp;
        end
      end
    end // coeff_reg_process_section1

  always @ ( posedge clk)
    begin: coeff_shadow_reg_process_section1
      if (reset == 1'b1) begin
        coeff_scale1_shadow_reg <= 0;
        coeff_b1_section1_shadow_reg <= 0;
        coeff_b2_section1_shadow_reg <= 0;
        coeff_b3_section1_shadow_reg <= 0;
        coeff_a2_section1_shadow_reg <= 0;
        coeff_a3_section1_shadow_reg <= 0;
      end
      else begin
        if (write_done_reg == 1'b1) begin
          coeff_scale1_shadow_reg <= coeff_scale1_reg;
          coeff_b1_section1_shadow_reg <= coeff_b1_section1_reg;
          coeff_b2_section1_shadow_reg <= coeff_b2_section1_reg;
          coeff_b3_section1_shadow_reg <= coeff_b3_section1_reg;
          coeff_a2_section1_shadow_reg <= coeff_a2_section1_reg;
          coeff_a3_section1_shadow_reg <= coeff_a3_section1_reg;
        end
      end
    end // coeff_shadow_reg_process_section1

  // ------------------ Section 1 ------------------

  assign inputconv1 = scale1;

//  assign a2mul1 = feedback1 * coeff_a2_section1_shadow_reg;

//  assign a3mul1 = feedback1 * coeff_a3_section1_shadow_reg;

//  assign b1mul1 = inputconv1 * coeff_b1_section1_shadow_reg;

//  assign b2mul1 = inputconv1 * coeff_b2_section1_shadow_reg;

//  assign b3mul1 = inputconv1 * coeff_b3_section1_shadow_reg;

  assign sub_signext = b3mul1;
  assign sub_signext_1 = a3mul1;
  assign ab3sum1 = sub_signext - sub_signext_1;

  assign add_signext = b2mul1;
  assign add_signext_1 = $signed({delay2_section1[15:0], 30'b000000000000000000000000000000});
  assign b2sum1 = add_signext + add_signext_1;

  assign sub_signext_2 = b2sum1;
  assign sub_signext_3 = $signed({{1{a2mul1[47]}}, a2mul1});
  assign sub_temp = sub_signext_2 - sub_signext_3;
  assign ab2sum1 = sub_temp[48:0];

  assign add_signext_2 = $signed({delay1_section1[15:0], 30'b000000000000000000000000000000});
  assign add_signext_3 = b1mul1;
  assign ab1sum1 = add_signext_2 + add_signext_3;

  assign delay1_typeconvert1 = (ab2sum1[45:0] + {ab2sum1[30], {29{~ab2sum1[30]}}})>>>30;

  assign delay2_typeconvert1 = (ab3sum1[45:0] + {ab3sum1[30], {29{~ab3sum1[30]}}})>>>30;

  always @ ( posedge clk)
    begin: delay_process_section1
      if (reset == 1'b1) begin
        delay1_section1 <= 0;
        delay2_section1 <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          delay1_section1 <= delay1_typeconvert1;
          delay2_section1 <= delay2_typeconvert1;
        end
      end
    end // delay_process_section1

  assign feedback1 = (ab1sum1[45:0] + {ab1sum1[30], {29{~ab1sum1[30]}}})>>>30;

//  always @ ( posedge clk)
//    begin: sos_pipeline_process_section1
//      if (reset == 1'b1) begin
//        sos_pipeline1 <= 0;
//      end
//      else begin
//        if (clk_enable == 1'b1) begin
//          sos_pipeline1 <= feedback1;
//        end
//      end
//    end // sos_pipeline_process_section1

  //   -------- Section 2 Processor Interface logic------------------

  //assign mul_temp_1 = sos_pipeline1 * coeff_scale2_shadow_reg;
  assign scale2 = (mul_temp_1[45:0] + {mul_temp_1[30], {29{~mul_temp_1[30]}}})>>>30;

  assign coeff_scale2_assigned = (write_address_reg == 4'b1000) ? coeffs_in_reg :
                           coeff_scale2_reg;
  assign coeff_scale2_temp = (write_enable_reg == 1'b1) ? coeff_scale2_assigned :
                       coeff_scale2_reg;
  assign coeff_b1_section2_assigned = (write_address_reg == 4'b1001) ? coeffs_in_reg :
                                coeff_b1_section2_reg;
  assign coeff_b1_section2_temp = (write_enable_reg == 1'b1) ? coeff_b1_section2_assigned :
                            coeff_b1_section2_reg;
  assign coeff_b2_section2_assigned = (write_address_reg == 4'b1010) ? coeffs_in_reg :
                                coeff_b2_section2_reg;
  assign coeff_b2_section2_temp = (write_enable_reg == 1'b1) ? coeff_b2_section2_assigned :
                            coeff_b2_section2_reg;
  assign coeff_b3_section2_assigned = (write_address_reg == 4'b1011) ? coeffs_in_reg :
                                coeff_b3_section2_reg;
  assign coeff_b3_section2_temp = (write_enable_reg == 1'b1) ? coeff_b3_section2_assigned :
                            coeff_b3_section2_reg;
  assign coeff_a2_section2_assigned = (write_address_reg == 4'b1100) ? coeffs_in_reg :
                                coeff_a2_section2_reg;
  assign coeff_a2_section2_temp = (write_enable_reg == 1'b1) ? coeff_a2_section2_assigned :
                            coeff_a2_section2_reg;
  assign coeff_a3_section2_assigned = (write_address_reg == 4'b1101) ? coeffs_in_reg :
                                coeff_a3_section2_reg;
  assign coeff_a3_section2_temp = (write_enable_reg == 1'b1) ? coeff_a3_section2_assigned :
                            coeff_a3_section2_reg;
  always @ ( posedge clk)
    begin: coeff_reg_process_section2
      if (reset == 1'b1) begin
        coeff_scale2_reg <= 0;
        coeff_b1_section2_reg <= 0;
        coeff_b2_section2_reg <= 0;
        coeff_b3_section2_reg <= 0;
        coeff_a2_section2_reg <= 0;
        coeff_a3_section2_reg <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          coeff_scale2_reg <= coeff_scale2_temp;
          coeff_b1_section2_reg <= coeff_b1_section2_temp;
          coeff_b2_section2_reg <= coeff_b2_section2_temp;
          coeff_b3_section2_reg <= coeff_b3_section2_temp;
          coeff_a2_section2_reg <= coeff_a2_section2_temp;
          coeff_a3_section2_reg <= coeff_a3_section2_temp;
        end
      end
    end // coeff_reg_process_section2

  always @ ( posedge clk)
    begin: coeff_shadow_reg_process_section2
      if (reset == 1'b1) begin
        coeff_scale2_shadow_reg <= 0;
        coeff_b1_section2_shadow_reg <= 0;
        coeff_b2_section2_shadow_reg <= 0;
        coeff_b3_section2_shadow_reg <= 0;
        coeff_a2_section2_shadow_reg <= 0;
        coeff_a3_section2_shadow_reg <= 0;
      end
      else begin
        if (write_done_reg == 1'b1) begin
          coeff_scale2_shadow_reg <= coeff_scale2_reg;
          coeff_b1_section2_shadow_reg <= coeff_b1_section2_reg;
          coeff_b2_section2_shadow_reg <= coeff_b2_section2_reg;
          coeff_b3_section2_shadow_reg <= coeff_b3_section2_reg;
          coeff_a2_section2_shadow_reg <= coeff_a2_section2_reg;
          coeff_a3_section2_shadow_reg <= coeff_a3_section2_reg;
        end
      end
    end // coeff_shadow_reg_process_section2

  // ------------------ Section 2 ------------------

  assign inputconv2 = scale2;

//  assign a2mul2 = feedback2 * coeff_a2_section2_shadow_reg;

//  assign a3mul2 = feedback2 * coeff_a3_section2_shadow_reg;

//  assign b1mul2 = inputconv2 * coeff_b1_section2_shadow_reg;

//  assign b2mul2 = inputconv2 * coeff_b2_section2_shadow_reg;

//  assign b3mul2 = inputconv2 * coeff_b3_section2_shadow_reg;

  assign sub_signext_4 = b3mul2;
  assign sub_signext_5 = a3mul2;
  assign ab3sum2 = sub_signext_4 - sub_signext_5;

  assign add_signext_4 = b2mul2;
  assign add_signext_5 = $signed({delay2_section2[15:0], 30'b000000000000000000000000000000});
  assign b2sum2 = add_signext_4 + add_signext_5;

  assign sub_signext_6 = b2sum2;
  assign sub_signext_7 = $signed({{1{a2mul2[47]}}, a2mul2});
  assign sub_temp_1 = sub_signext_6 - sub_signext_7;
  assign ab2sum2 = sub_temp_1[48:0];

  assign add_signext_6 = $signed({delay1_section2[15:0], 30'b000000000000000000000000000000});
  assign add_signext_7 = b1mul2;
  assign ab1sum2 = add_signext_6 + add_signext_7;

  assign delay1_typeconvert2 = (ab2sum2[45:0] + {ab2sum2[30], {29{~ab2sum2[30]}}})>>>30;

  assign delay2_typeconvert2 = (ab3sum2[45:0] + {ab3sum2[30], {29{~ab3sum2[30]}}})>>>30;

  always @ ( posedge clk)
    begin: delay_process_section2
      if (reset == 1'b1) begin
        delay1_section2 <= 0;
        delay2_section2 <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          delay1_section2 <= delay1_typeconvert2;
          delay2_section2 <= delay2_typeconvert2;
        end
      end
    end // delay_process_section2

  assign feedback2 = (ab1sum2[45:0] + {ab1sum2[30], {29{~ab1sum2[30]}}})>>>30;

  //   -------- Last Section Value -- Processor Interface logic------------------

  //assign mul_temp_2 = feedback2 * coeff_scale3_shadow_reg;
  assign scale3 = (mul_temp_2[46:0] + {mul_temp_2[33], {32{~mul_temp_2[33]}}})>>>33;

  assign coeff_scale3_assigned = (write_address_reg == 4'b0111) ? coeffs_in_reg :
                           coeff_scale3_reg;
  assign coeff_scale3_temp = (write_enable_reg == 1'b1) ? coeff_scale3_assigned :
                       coeff_scale3_reg;
  always @ ( posedge clk)
    begin: coeff_reg_process_Last_ScaleValue
      if (reset == 1'b1) begin
        coeff_scale3_reg <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          coeff_scale3_reg <= coeff_scale3_temp;
        end
      end
    end // coeff_reg_process_Last_ScaleValue

  always @ ( posedge clk)
    begin: coeff_shadow_reg_process_Last_ScaleValue
      if (reset == 1'b1) begin
        coeff_scale3_shadow_reg <= 0;
      end
      else begin
        if (write_done_reg == 1'b1) begin
          coeff_scale3_shadow_reg <= coeff_scale3_reg;
        end
      end
    end // coeff_shadow_reg_process_Last_ScaleValue

  assign output_typeconvert = scale3;

  always @ ( posedge clk)
    begin: Output_Register_process
      if (reset == 1'b1) begin
        output_register <= 0;
      end
      else begin
        if (clk_enable == 1'b1) begin
          output_register <= output_typeconvert;
        end
      end
    end // Output_Register_process

  // Assignment Statements
  assign filter_out = output_register;
endmodule  // Butter_pipelined

