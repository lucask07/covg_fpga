// -------------------------------------------------------------
// 
// File Name: C:\Users\iande\Desktop\covg_fpga_project\covg_fpga\Matlab\DSPfilterFunctions\CMDFilters\codegen\sumGain\hdlsrc\sumGain_fixpt_tb.v
// Created: 2021-08-13 09:30:14
// 
// Generated by MATLAB 9.9, MATLAB Coder 5.1 and HDL Coder 3.17
// 
// 
// 
// -- -------------------------------------------------------------
// -- Rate and Clocking Details
// -- -------------------------------------------------------------
// Model base rate: 1
// Target subsystem base rate: 1
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: sumGain_fixpt_tb
// Source Path: 
// Hierarchy Level: 0
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module sumGain_fixpt_tb;



  reg  clk;
  reg  reset;
  wire enb;
  wire y_done;  // ufix1
  wire rdEnb;
  wire y_done_enb;  // ufix1
  reg [7:0] y_addr;  // ufix8
  wire y_active;  // ufix1
  reg  check1_done;  // ufix1
  wire snkDonen;
  wire resetn;
  wire tb_enb;
  wire ce_out;
  wire y_enb;  // ufix1
  wire y_lastAddr;  // ufix1
  reg [7:0] in1_addr;  // ufix8
  wire in1_active;  // ufix1
  wire in1_enb;  // ufix1
  wire [7:0] in1_addr_delay_1;  // ufix8
  reg signed [31:0] fp_in1;  // sfix32
  reg signed [13:0] rawData_in1;  // sfix14_En13
  reg signed [31:0] status_in1;  // sfix32
  reg signed [13:0] holdData_in1;  // sfix14_En13
  wire [7:0] in2_addr_delay_1;  // ufix8
  reg signed [31:0] fp_in2;  // sfix32
  reg signed [13:0] rawData_in2;  // sfix14_En13
  reg signed [31:0] status_in2;  // sfix32
  reg signed [13:0] holdData_in2;  // sfix14_En13
  wire [7:0] in3_addr_delay_1;  // ufix8
  reg signed [31:0] fp_in3;  // sfix32
  reg signed [13:0] rawData_in3;  // sfix14_En13
  reg signed [31:0] status_in3;  // sfix32
  reg signed [13:0] holdData_in3;  // sfix14_En13
  wire [7:0] rawData_g1;  // uint8
  reg [7:0] holdData_g1;  // uint8
  wire [7:0] rawData_g2;  // uint8
  reg [7:0] holdData_g2;  // uint8
  wire [7:0] rawData_g3;  // uint8
  reg [7:0] holdData_g3;  // uint8
  wire [7:0] rawData_scaleVal;  // uint8
  reg [7:0] holdData_scaleVal;  // uint8
  reg signed [13:0] in1_offset;  // sfix14_En13
  wire signed [13:0] in1_1;  // sfix14_En13
  reg signed [13:0] in2_offset;  // sfix14_En13
  wire signed [13:0] in2;  // sfix14_En13
  reg signed [13:0] in3_offset;  // sfix14_En13
  wire signed [13:0] in3;  // sfix14_En13
  reg [7:0] g1_offset;  // uint8
  wire [7:0] g1_1;  // uint8
  reg [7:0] g2_offset;  // uint8
  wire [7:0] g2_1;  // uint8
  reg [7:0] g3_offset;  // uint8
  wire [7:0] g3_1;  // uint8
  reg [7:0] scaleVal_offset;  // uint8
  wire [7:0] scaleVal_1;  // uint8
  wire signed [13:0] y_1;  // sfix14_En13
  wire [7:0] y_addr_delay_1;  // ufix8
  reg signed [31:0] fp_y_expected;  // sfix32
  reg signed [13:0] y_expected;  // sfix14_En13
  reg signed [31:0] status_y_expected;  // sfix32
  wire signed [13:0] y_ref;  // sfix14_En13
  reg  y_testFailure;  // ufix1
  wire testFailure;  // ufix1


  assign y_done_enb = y_done & rdEnb;



  assign y_active = y_addr != 8'b11111011;



  assign #2 enb = rdEnb;

  assign snkDonen =  ~ check1_done;



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

  initial
    begin : reset_gen
      reset <= 1'b1;
      # (20);
      @ (posedge clk)
      # (2);
      reset <= 1'b0;
    end

  assign resetn =  ~ reset;



  assign tb_enb = resetn & snkDonen;



  assign rdEnb = (check1_done == 1'b0 ? tb_enb :
              1'b0);



  assign ce_out = enb & (rdEnb & tb_enb);



  assign y_enb = ce_out & y_active;



  // Count limited, Unsigned Counter
  //  initial value   = 0
  //  step value      = 1
  //  count to value  = 251
  always @(posedge clk)
    begin : y_process
      if (reset == 1'b1) begin
        y_addr <= 8'b00000000;
      end
      else begin
        if (y_enb) begin
          if (y_addr >= 8'b11111011) begin
            y_addr <= 8'b00000000;
          end
          else begin
            y_addr <= y_addr + 8'b00000001;
          end
        end
      end
    end



  assign y_lastAddr = y_addr >= 8'b11111011;



  assign y_done = y_lastAddr & resetn;



  // Delay to allow last sim cycle to complete
  always @(posedge clk)
    begin : checkDone_1
      if (reset) begin
        check1_done <= 0;
      end
      else begin
        if (y_done_enb) begin
          check1_done <= y_done;
        end
      end
    end

  assign in1_active = in1_addr != 8'b11111011;



  assign in1_enb = in1_active & (rdEnb & tb_enb);



  // Count limited, Unsigned Counter
  //  initial value   = 0
  //  step value      = 1
  //  count to value  = 251
  always @(posedge clk)
    begin : in1_process
      if (reset == 1'b1) begin
        in1_addr <= 8'b00000000;
      end
      else begin
        if (in1_enb) begin
          if (in1_addr >= 8'b11111011) begin
            in1_addr <= 8'b00000000;
          end
          else begin
            in1_addr <= in1_addr + 8'b00000001;
          end
        end
      end
    end



  assign #1 in1_addr_delay_1 = in1_addr;

  // Data source for in1
  initial
    begin : in1_fileread
      fp_in1 = $fopen("in1.dat", "r");
      status_in1 = $rewind(fp_in1);
    end

  always @(in1_addr_delay_1, rdEnb, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_in1 <= 14'bx;
      end
      else if (rdEnb == 1) begin
        status_in1 = $fscanf(fp_in1, "%h", rawData_in1);
      end
    end

  // holdData reg for in1
  always @(posedge clk)
    begin : stimuli_in1
      if (reset) begin
        holdData_in1 <= 14'bx;
      end
      else begin
        holdData_in1 <= rawData_in1;
      end
    end

  assign #1 in2_addr_delay_1 = in1_addr;

  // Data source for in2
  initial
    begin : in2_fileread
      fp_in2 = $fopen("in2.dat", "r");
      status_in2 = $rewind(fp_in2);
    end

  always @(in2_addr_delay_1, rdEnb, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_in2 <= 14'bx;
      end
      else if (rdEnb == 1) begin
        status_in2 = $fscanf(fp_in2, "%h", rawData_in2);
      end
    end

  // holdData reg for in2
  always @(posedge clk)
    begin : stimuli_in2
      if (reset) begin
        holdData_in2 <= 14'bx;
      end
      else begin
        holdData_in2 <= rawData_in2;
      end
    end

  assign #1 in3_addr_delay_1 = in1_addr;

  // Data source for in3
  initial
    begin : in3_fileread
      fp_in3 = $fopen("in3.dat", "r");
      status_in3 = $rewind(fp_in3);
    end

  always @(in3_addr_delay_1, rdEnb, tb_enb)
    begin
      if (tb_enb == 0) begin
        rawData_in3 <= 14'bx;
      end
      else if (rdEnb == 1) begin
        status_in3 = $fscanf(fp_in3, "%h", rawData_in3);
      end
    end

  // holdData reg for in3
  always @(posedge clk)
    begin : stimuli_in3
      if (reset) begin
        holdData_in3 <= 14'bx;
      end
      else begin
        holdData_in3 <= rawData_in3;
      end
    end

  // Data source for g1
  assign rawData_g1 = 8'b00000001;



  // holdData reg for g1
  always @(posedge clk)
    begin : stimuli_g1
      if (reset) begin
        holdData_g1 <= 8'bx;
      end
      else begin
        holdData_g1 <= rawData_g1;
      end
    end

  // Data source for g2
  assign rawData_g2 = 8'b00000001;



  // holdData reg for g2
  always @(posedge clk)
    begin : stimuli_g2
      if (reset) begin
        holdData_g2 <= 8'bx;
      end
      else begin
        holdData_g2 <= rawData_g2;
      end
    end

  // Data source for g3
  assign rawData_g3 = 8'b00000001;



  // holdData reg for g3
  always @(posedge clk)
    begin : stimuli_g3
      if (reset) begin
        holdData_g3 <= 8'bx;
      end
      else begin
        holdData_g3 <= rawData_g3;
      end
    end

  // Data source for scaleVal
  assign rawData_scaleVal = 8'b00000001;



  // holdData reg for scaleVal
  always @(posedge clk)
    begin : stimuli_scaleVal
      if (reset) begin
        holdData_scaleVal <= 8'bx;
      end
      else begin
        holdData_scaleVal <= rawData_scaleVal;
      end
    end

  always @(rawData_in1 or rdEnb)
    begin : stimuli_in1_1
      if (rdEnb == 1'b0) begin
        in1_offset <= holdData_in1;
      end
      else begin
        in1_offset <= rawData_in1;
      end
    end

  assign #2 in1_1 = in1_offset;

  always @(rawData_in2 or rdEnb)
    begin : stimuli_in2_1
      if (rdEnb == 1'b0) begin
        in2_offset <= holdData_in2;
      end
      else begin
        in2_offset <= rawData_in2;
      end
    end

  assign #2 in2 = in2_offset;

  always @(rawData_in3 or rdEnb)
    begin : stimuli_in3_1
      if (rdEnb == 1'b0) begin
        in3_offset <= holdData_in3;
      end
      else begin
        in3_offset <= rawData_in3;
      end
    end

  assign #2 in3 = in3_offset;

  always @(rawData_g1 or rdEnb)
    begin : stimuli_g1_1
      if (rdEnb == 1'b0) begin
        g1_offset <= holdData_g1;
      end
      else begin
        g1_offset <= rawData_g1;
      end
    end

  assign #2 g1_1 = g1_offset;

  always @(rawData_g2 or rdEnb)
    begin : stimuli_g2_1
      if (rdEnb == 1'b0) begin
        g2_offset <= holdData_g2;
      end
      else begin
        g2_offset <= rawData_g2;
      end
    end

  assign #2 g2_1 = g2_offset;

  always @(rawData_g3 or rdEnb)
    begin : stimuli_g3_1
      if (rdEnb == 1'b0) begin
        g3_offset <= holdData_g3;
      end
      else begin
        g3_offset <= rawData_g3;
      end
    end

  assign #2 g3_1 = g3_offset;

  always @(rawData_scaleVal or rdEnb)
    begin : stimuli_scaleVal_1
      if (rdEnb == 1'b0) begin
        scaleVal_offset <= holdData_scaleVal;
      end
      else begin
        scaleVal_offset <= rawData_scaleVal;
      end
    end

  assign #2 scaleVal_1 = scaleVal_offset;

  sumGain_fixpt u_sumGain_fixpt (.in1(in1_1),  // sfix14_En13
                                 .in2(in2),  // sfix14_En13
                                 .in3(in3),  // sfix14_En13
                                 .g1(g1_1),  // uint8
                                 .g2(g2_1),  // uint8
                                 .g3(g3_1),  // uint8
                                 .scaleVal(scaleVal_1),  // uint8
                                 .y(y_1)  // sfix14_En13
                                 );

  assign #1 y_addr_delay_1 = y_addr;

  // Data source for y_expected
  initial
    begin : y_expected_fileread
      fp_y_expected = $fopen("y_expected.dat", "r");
      status_y_expected = $rewind(fp_y_expected);
    end

  always @(y_addr_delay_1, rdEnb, tb_enb)
    begin
      if (tb_enb == 0) begin
        y_expected <= 14'bx;
      end
      else if (rdEnb == 1) begin
        status_y_expected = $fscanf(fp_y_expected, "%h", y_expected);
      end
    end

  assign y_ref = y_expected;

  always @(posedge clk)
    begin : y_1_checker
      if (reset == 1'b1) begin
        y_testFailure <= 1'b0;
      end
      else begin
        if (ce_out == 1'b1 && y_1 !== y_ref) begin
          y_testFailure <= 1'b1;
          $display("ERROR in y_1 at time %t : Expected '%h' Actual '%h'", $time, y_ref, y_1);
        end
      end
    end

  assign testFailure = y_testFailure;

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

endmodule  // sumGain_fixpt_tb
