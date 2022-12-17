// -------------------------------------------------------------
// 
// File Name: /Users/koer2434/My Drive/UST/research/covg/manuscripts/control_system/secord_memos/obersver_nov_update/codegen/matrix_mul_fixedpt/hdlsrc/matrix_mul_fixedpt_fixpt_tb.v
// Created: 2022-12-13 08:06:06
// 
// Generated by MATLAB 9.12, MATLAB Coder 5.4 and HDL Coder 3.20
// 
// 
// 
// -- -------------------------------------------------------------
// -- Rate and Clocking Details
// -- -------------------------------------------------------------
// Model base rate: 0.025
// Target subsystem base rate: 0.025
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
// out_0                         ce_out        1
// out_1                         ce_out        1
// -- -------------------------------------------------------------
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: matrix_mul_fixedpt_fixpt_tb
// Source Path: 
// Hierarchy Level: 0
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns
`define directory "C:/Users/koer2434/Documents/covg/covg_fpga/Matlab/control_system/observer/matrix_mul/codegen/matrix_mul/hdlsrc/"

module matrix_mul_fixpt_folded_tb;



  reg  clk;
  reg  reset;
  wire enb_1_40_0;
  wire out_0_done;  // ufix1
  wire ce_out;
  wire out_0_done_enb;  // ufix1
  reg [6:0] out_0_addr;  // ufix7
  wire out_0_active;  // ufix1
  wire [6:0] B_addr_delay;  // ufix7
  wire tb_enb;
  wire phase_1;
  reg signed [31:0] fp_B_1;  // sfix32
  reg signed [15:0] rawData_B_1;  // sfix16_En15
  reg signed [31:0] status_B_1;  // sfix32
  reg signed [15:0] holdData_B_1;  // sfix16_En15
  reg signed [15:0] B_1_offset;  // sfix16_En15
  wire signed [15:0] B_1;  // sfix16_En15
  reg [6:0] A_addr;  // ufix7
  reg signed [31:0] fp_B_0;  // sfix32
  reg signed [15:0] rawData_B_0;  // sfix16_En15
  reg signed [31:0] status_B_0;  // sfix32
  reg signed [15:0] holdData_B_0;  // sfix16_En15
  reg signed [15:0] B_0_offset;  // sfix16_En15
  wire signed [15:0] B_0;  // sfix16_En15
  wire [6:0] A_addr_delay;  // ufix7
  reg signed [31:0] fp_A_3;  // sfix32
  reg signed [15:0] rawData_A_3;  // sfix16_En15
  reg signed [31:0] status_A_3;  // sfix32
  reg signed [15:0] holdData_A_3;  // sfix16_En15
  reg signed [15:0] A_3_offset;  // sfix16_En15
  wire signed [15:0] A_3;  // sfix16_En15
  reg signed [31:0] fp_A_2;  // sfix32
  reg signed [15:0] rawData_A_2;  // sfix16_En15
  reg signed [31:0] status_A_2;  // sfix32
  reg signed [15:0] holdData_A_2;  // sfix16_En15
  reg signed [15:0] A_2_offset;  // sfix16_En15
  wire signed [15:0] A_2;  // sfix16_En15
  reg signed [31:0] fp_A_1;  // sfix32
  reg signed [15:0] rawData_A_1;  // sfix16_En15
  reg signed [31:0] status_A_1;  // sfix32
  reg signed [15:0] holdData_A_1;  // sfix16_En15
  reg signed [15:0] A_1_offset;  // sfix16_En15
  wire signed [15:0] A_1;  // sfix16_En15
  wire A_active;  // ufix1
  wire A_enb;  // ufix1
  reg signed [31:0] fp_A_0;  // sfix32
  reg signed [15:0] rawData_A_0;  // sfix16_En15
  reg signed [31:0] status_A_0;  // sfix32
  reg signed [15:0] holdData_A_0;  // sfix16_En15
  reg signed [15:0] A_0_offset;  // sfix16_En15
  wire signed [15:0] A_0;  // sfix16_En15
  reg  check1_done;  // ufix1
  wire snkDonen;
  wire resetn;
  wire tb_enb_delay;
  reg [5:0] counter;  // ufix6
  wire phasesel_1_relop1;
  wire notDone;
  wire signed [32:0] out_0;  // sfix33_En30
  wire signed [32:0] out_1;  // sfix33_En30
  wire out_0_enb;  // ufix1
  wire out_0_lastAddr;  // ufix1
  wire [6:0] out_0_addr_delay_1;  // ufix7
  reg signed [31:0] fp_out_0_0_expected;  // sfix32
  reg signed [32:0] out_0_0_expected;  // sfix33_En30
  reg signed [31:0] status_out_0_0_expected;  // sfix32
  reg signed [32:0] out_0_ref_hold;  // sfix33_En30
  wire signed [32:0] out_0_refTmp;  // sfix33_En30
  wire signed [32:0] out_0_ref;  // sfix33_En30
  reg  out_0_testFailure;  // ufix1
  reg signed [31:0] fp_out_0_1_expected;  // sfix32
  reg signed [32:0] out_0_1_expected;  // sfix33_En30
  reg signed [31:0] status_out_0_1_expected;  // sfix32
  reg signed [32:0] out_1_ref_hold;  // sfix33_En30
  wire signed [32:0] out_1_refTmp;  // sfix33_En30
  wire signed [32:0] out_1_ref;  // sfix33_En30
  reg  out_1_testFailure;  // ufix1
  wire testFailure;  // ufix1


  assign out_0_done_enb = out_0_done & ce_out;



  assign out_0_active = out_0_addr != 7'b1100011;



  // Data source for B_1
  initial
    begin : B_1_fileread
      fp_B_1 =$fopen({`directory,"B_1.dat"}, "r");
      status_B_1 = $rewind(fp_B_1);
    end

  always @(B_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_B_1 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_B_1 = $fscanf(fp_B_1, "%h", rawData_B_1);
      end
    end

  // holdData reg for B
  always @(posedge clk or posedge reset)
    begin : stimuli_B
      if (reset) begin
        holdData_B_1 <= 16'bx;
      end
      else begin
        holdData_B_1 <= rawData_B_1;
      end
    end

  always @(rawData_B_1 or phase_1)
    begin : stimuli_B_1
      if (phase_1 == 1'b0) begin
        B_1_offset <= holdData_B_1;
      end
      else begin
        B_1_offset <= rawData_B_1;
      end
    end

  assign #2 B_1 = B_1_offset;

  assign #1 B_addr_delay = A_addr;

  // Data source for B_0
  initial
    begin : B_0_fileread
      fp_B_0 =$fopen({`directory,"B_0.dat"}, "r");
      status_B_0 = $rewind(fp_B_0);
    end

  always @(B_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_B_0 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_B_0 = $fscanf(fp_B_0, "%h", rawData_B_0);
      end
    end

  // holdData reg for B
  always @(posedge clk or posedge reset)
    begin : stimuli_B_2
      if (reset) begin
        holdData_B_0 <= 16'bx;
      end
      else begin
        holdData_B_0 <= rawData_B_0;
      end
    end

  always @(rawData_B_0 or phase_1)
    begin : stimuli_B_3
      if (phase_1 == 1'b0) begin
        B_0_offset <= holdData_B_0;
      end
      else begin
        B_0_offset <= rawData_B_0;
      end
    end

  assign #2 B_0 = B_0_offset;

  // Data source for A_3
  initial
    begin : A_3_fileread
      fp_A_3 =$fopen({`directory,"A_3.dat"}, "r");
      status_A_3 = $rewind(fp_A_3);
    end

  always @(A_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_A_3 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_A_3 = $fscanf(fp_A_3, "%h", rawData_A_3);
      end
    end

  // holdData reg for A
  always @(posedge clk or posedge reset)
    begin : stimuli_A
      if (reset) begin
        holdData_A_3 <= 16'bx;
      end
      else begin
        holdData_A_3 <= rawData_A_3;
      end
    end

  always @(rawData_A_3 or phase_1)
    begin : stimuli_A_1
      if (phase_1 == 1'b0) begin
        A_3_offset <= holdData_A_3;
      end
      else begin
        A_3_offset <= rawData_A_3;
      end
    end

  assign #2 A_3 = A_3_offset;

  // Data source for A_2
  initial
    begin : A_2_fileread
      fp_A_2 =$fopen({`directory,"A_2.dat"}, "r");
      status_A_2 = $rewind(fp_A_2);
    end

  always @(A_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_A_2 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_A_2 = $fscanf(fp_A_2, "%h", rawData_A_2);
      end
    end

  // holdData reg for A
  always @(posedge clk or posedge reset)
    begin : stimuli_A_2
      if (reset) begin
        holdData_A_2 <= 16'bx;
      end
      else begin
        holdData_A_2 <= rawData_A_2;
      end
    end

  always @(rawData_A_2 or phase_1)
    begin : stimuli_A_3
      if (phase_1 == 1'b0) begin
        A_2_offset <= holdData_A_2;
      end
      else begin
        A_2_offset <= rawData_A_2;
      end
    end

  assign #2 A_2 = A_2_offset;

  // Data source for A_1
  initial
    begin : A_1_fileread
      fp_A_1 =$fopen({`directory,"A_1.dat"}, "r");
      status_A_1 = $rewind(fp_A_1);
    end

  always @(A_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_A_1 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_A_1 = $fscanf(fp_A_1, "%h", rawData_A_1);
      end
    end

  // holdData reg for A
  always @(posedge clk or posedge reset)
    begin : stimuli_A_4
      if (reset) begin
        holdData_A_1 <= 16'bx;
      end
      else begin
        holdData_A_1 <= rawData_A_1;
      end
    end

  always @(rawData_A_1 or phase_1)
    begin : stimuli_A_5
      if (phase_1 == 1'b0) begin
        A_1_offset <= holdData_A_1;
      end
      else begin
        A_1_offset <= rawData_A_1;
      end
    end

  assign #2 A_1 = A_1_offset;

  assign A_active = A_addr != 7'b1100011;



  assign A_enb = A_active & (phase_1 & tb_enb);



  // Count limited, Unsigned Counter
  //  initial value   = 0
  //  step value      = 1
  //  count to value  = 99
  always @(posedge clk or posedge reset)
    begin : A_process
      if (reset == 1'b1) begin
        A_addr <= 7'b0000000;
      end
      else begin
        if (A_enb) begin
          if (A_addr >= 7'b1100011) begin
            A_addr <= 7'b0000000;
          end
          else begin
            A_addr <= A_addr + 7'b0000001;
          end
        end
      end
    end



  assign #1 A_addr_delay = A_addr;

  // Data source for A_0
  initial
    begin : A_0_fileread
      fp_A_0 =$fopen({`directory,"A_0.dat"}, "r");
      status_A_0 = $rewind(fp_A_0);
    end

  always @(A_addr_delay, phase_1, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_A_0 <= 16'bx;
      end
      else if (phase_1 == 1) begin
        status_A_0 = $fscanf(fp_A_0, "%h", rawData_A_0);
      end
    end

  // holdData reg for A
  always @(posedge clk or posedge reset)
    begin : stimuli_A_6
      if (reset) begin
        holdData_A_0 <= 16'bx;
      end
      else begin
        holdData_A_0 <= rawData_A_0;
      end
    end

  always @(rawData_A_0 or phase_1)
    begin : stimuli_A_7
      if (phase_1 == 1'b0) begin
        A_0_offset <= holdData_A_0;
      end
      else begin
        A_0_offset <= rawData_A_0;
      end
    end

  assign #2 A_0 = A_0_offset;

  assign snkDonen =  ~ check1_done;



  assign resetn =  ~ reset;



  assign tb_enb = resetn & snkDonen;



  assign tb_enb_delay = tb_enb;

  // Count limited, Unsigned Counter
  //  initial value   = 1
  //  step value      = 1
  //  count to value  = 39
  always @(posedge clk or posedge reset)
    begin : slow_clock_enable_process
      if (reset == 1'b1) begin
        counter <= 6'b000001;
      end
      else begin
        if (tb_enb_delay) begin
          if (counter >= 6'b100111) begin
            counter <= 6'b000000;
          end
          else begin
            counter <= counter + 6'b000001;
          end
        end
      end
    end



  assign phasesel_1_relop1 = counter == 6'b000001;



  assign phase_1 = phasesel_1_relop1 & tb_enb;



  assign notDone = phase_1 & snkDonen;



  assign #2 enb_1_40_0 = notDone;

  initial
    begin : reset_gen
      reset <= 1'b1;
      # (20);
      @ (posedge clk)
      # (2);
      reset <= 1'b0;
    end

  always 
    begin : clk_gen
      clk <= 1'b1;
      # (5);
      clk <= 1'b0;
      # (5);
      if (check1_done == 1'b1) begin
        clk <= 1'b1;
        # (5);
        clk <= 1'b0;
        # (5);
        $stop;
      end
    end

  matrix_mul_fixpt_folded u_matrix_mul_fixpt (.clk(clk),
                                                       .reset(reset),
                                                       .clk_enable(enb_1_40_0),
                                                       .A_0(A_0),  // sfix16_En15 0,0
                                                       .A_1(A_1),  // sfix16_En15 1,0
                                                       .A_2(A_2),  // sfix16_En15 0,1
                                                       .A_3(A_3),  // sfix16_En15 1,1
                                                       .B_0(B_0),  // sfix16_En15
                                                       .B_1(B_1),  // sfix16_En15
                                                       .ce_out(ce_out),
                                                       .out_0(out_0),  // sfix33_En30
                                                       .out_1(out_1)  // sfix33_En30
                                                       );

  assign out_0_enb = ce_out & out_0_active;



  // Count limited, Unsigned Counter
  //  initial value   = 0
  //  step value      = 1
  //  count to value  = 99
  always @(posedge clk or posedge reset)
    begin : out_process
      if (reset == 1'b1) begin
        out_0_addr <= 7'b0000000;
      end
      else begin
        if (out_0_enb) begin
          if (out_0_addr >= 7'b1100011) begin
            out_0_addr <= 7'b0000000;
          end
          else begin
            out_0_addr <= out_0_addr + 7'b0000001;
          end
        end
      end
    end



  assign out_0_lastAddr = out_0_addr >= 7'b1100011;



  assign out_0_done = out_0_lastAddr & resetn;



  // Delay to allow last sim cycle to complete
  always @(posedge clk or posedge reset)
    begin : checkDone_1
      if (reset) begin
        check1_done <= 0;
      end
      else begin
        if (out_0_done_enb) begin
          check1_done <= out_0_done;
        end
      end
    end

  assign #1 out_0_addr_delay_1 = out_0_addr;

  // Data source for out_0_0_expected
  initial
    begin : out_0_0_expected_fileread
      fp_out_0_0_expected =$fopen({`directory, "out_0_0_expected.dat"}, "r");
      status_out_0_0_expected = $rewind(fp_out_0_0_expected);
    end

  always @(out_0_addr_delay_1,  tb_enb)
    begin
      if (tb_enb == 0) begin
        out_0_0_expected <= 33'bx;
      end
      else  begin
        status_out_0_0_expected = $fscanf(fp_out_0_0_expected, "%h", out_0_0_expected);
      end
    end

  // Bypass register to hold out_0_ref
  always @(posedge clk or posedge reset)
    begin : DataHold_out_0_ref
      if (reset) begin
        out_0_ref_hold <= 0;
      end
      else begin
        if (ce_out) begin
          out_0_ref_hold <= out_0_0_expected;
        end
      end
    end

  assign out_0_refTmp = out_0_0_expected;

  assign out_0_ref = (ce_out == 1'b0 ? out_0_ref_hold :
              out_0_refTmp);



  always @(posedge clk or posedge reset)
    begin : out_0_checker
      if (reset == 1'b1) begin
        out_0_testFailure <= 1'b0;
      end
      else begin
        if (ce_out == 1'b1 && out_0 !== out_0_ref) begin
          out_0_testFailure <= 1'b1;
          $display("ERROR in out_0 at time %t : Expected '%h' Actual '%h'", $time, out_0_ref, out_0);
        end
      end
    end

  // Data source for out_0_1_expected
  initial
    begin : out_0_1_expected_fileread
      fp_out_0_1_expected =$fopen({`directory, "out_0_1_expected.dat"}, "r");
      status_out_0_1_expected = $rewind(fp_out_0_1_expected);
    end

  always @(out_0_addr_delay_1,  tb_enb)
    begin
      if (tb_enb == 0) begin
        out_0_1_expected <= 33'bx;
      end
      else  begin
        status_out_0_1_expected = $fscanf(fp_out_0_1_expected, "%h", out_0_1_expected);
      end
    end

  // Bypass register to hold out_1_ref
  always @(posedge clk or posedge reset)
    begin : DataHold_out_1_ref
      if (reset) begin
        out_1_ref_hold <= 0;
      end
      else begin
        if (ce_out) begin
          out_1_ref_hold <= out_0_1_expected;
        end
      end
    end

  assign out_1_refTmp = out_0_1_expected;

  assign out_1_ref = (ce_out == 1'b0 ? out_1_ref_hold :
              out_1_refTmp);



  always @(posedge clk or posedge reset)
    begin : out_1_checker
      if (reset == 1'b1) begin
        out_1_testFailure <= 1'b0;
      end
      else begin
        if (ce_out == 1'b1 && out_1 !== out_1_ref) begin
          out_1_testFailure <= 1'b1;
          $display("ERROR in out_1 at time %t : Expected '%h' Actual '%h'", $time, out_1_ref, out_1);
        end
      end
    end

  assign testFailure = out_0_testFailure | out_1_testFailure;



  always @(posedge clk)
    begin : completed_msg
      if (check1_done == 1'b1) begin
        if (testFailure == 1'b0) begin
          $display("**************TEST COMPLETED (PASSED)**************");
        end
        else begin
          $display("**************TEST COMPLETED (FAILED)**************");
        end
      end
    end

endmodule  // matrix_mul_fixedpt_fixpt_tb

