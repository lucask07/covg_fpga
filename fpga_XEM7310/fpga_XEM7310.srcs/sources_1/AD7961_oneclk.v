`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/24/2021 03:28:13 PM
// Design Name: 
// Module Name: AD7961_oneclk
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
// -----------------------------------------------------------------------------
//
// Copyright 2011(c) Analog Devices, Inc.
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//  - Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//  - Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in
//    the documentation and/or other materials provided with the
//    distribution.
//  - Neither the name of Analog Devices, Inc. nor the names of its
//    contributors may be used to endorse or promote products derived
//    from this software without specific prior written permission.
//  - The use of this software may or may not infringe the patent rights
//    of one or more patent holders.  This license does not release you
//    from the requirement that you obtain separate licenses from these
//    patent holders to use this software.
//  - Use of the software either in source or binary form, must be run
//    on or directly connected to an Analog Devices Inc. component.
//
// THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED
// WARRANTIES, INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY
// AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
// IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// INTELLECTUAL PROPERTY RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// -----------------------------------------------------------------------------
// FILE NAME : AD7961.v
// MODULE NAME : AD7961
// AUTHOR : atofan
// AUTHOR'S EMAIL : alexandru.tofan@analog.com
// -----------------------------------------------------------------------------
// SVN REVISION: 468
// -----------------------------------------------------------------------------
// KEYWORDS : AD7961
// -----------------------------------------------------------------------------
// PURPOSE : Driver for the AD7961, 16-Bit, 5 MSPS PulSAR Differential ADC
// -----------------------------------------------------------------------------
// REUSE ISSUES
// Reset Strategy      : Active low reset signal
// Clock Domains       : 2 clocks - the system clock that drives the internal logic
//                     : and a clock for ADC serial interface
// Critical Timing     : N/A
// Test Features       : N/A
// Asynchronous I/F    : N/A
// Instantiations      : N/A
// Synthesizable (y/n) : Y
// Target Device       : AD7961
// Other               : The driver is intended to be used for AD7961 ADCs configured
//                     : in Echoed Clock Mode
//                     : LJK - edited to use only a single clock due to challenges with timing
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
`timescale 1ns / 1ps
//------------------------------------------------------------------------------
//----------- Module Declaration -----------------------------------------------
//------------------------------------------------------------------------------
module AD7961_oneclk
    (
        input wire          m_clk_i,                    // 100 MHz Clock, used for tiing
        input wire          fast_clk_i,                 // 250 MHz Clock, used for serial transfer
        input wire          reset_n_i,                  // Reset signal, active low
        input wire  [ 3:0]  en_i,                       // Enable pins input
        input wire          d_pos_i,                    // Data In, Positive Pair
        input wire          d_neg_i,                    // Data In, Negative Pair
        input wire          dco_pos_i,                  // Echoed Clock In, Positive Pair
        input wire          dco_neg_i,                  // Echoed Clock In, Negative Pair
        output wire  [ 3:0]  en_o,                       // Enable pins output
        output wire         cnv_pos_o,                  // Convert Out, Positive Pair
        output wire         cnv_neg_o,                  // Convert Out, Negative Pair
        output wire         clk_pos_o,                  // Clock Out, Positive Pair
        output wire         clk_neg_o,                  // Clock Out, Negative Pair
        output wire         data_rd_rdy_o,              // Signals that new data is available
        output wire [15:0]  data_o,                      // Read Data
        output wire conv,   // debug signals
        output wire dco,    // debug signals
        output wire adc_serial_data
    );

//------------------------------------------------------------------------------
//----------- Local Parameters -------------------------------------------------
//------------------------------------------------------------------------------
// FPGA Clock Frequency
parameter real          FPGA_CLOCK_FREQ         = 250;
// Conversion signal generation
parameter real          TCYC                    = 0.200; // in microseconds
parameter       [5:0]  ADC_CYC_CNT             = FPGA_CLOCK_FREQ * TCYC - 1; // 49 for 250 MHz and 5 MSPS

// Serial Interface
parameter               SERIAL_IDLE_STATE       = 8'b0000_0001;
parameter               SERIAL_CONV1_STATE      = 8'b0000_0010;
parameter               SERIAL_CONV2_STATE      = 8'b0000_0100; 
parameter               SERIAL_READ_STATE       = 8'b0000_1000;
parameter               SERIAL_READDONE_STATE   = 8'b0001_0000; 
parameter               SERIAL_DATADONE_STATE   = 8'b0010_0000;
parameter               SERIAL_CLEAR_STATE      = 8'b0100_0000; 
parameter               SERIAL_DONE_STATE       = 8'b1000_0000; 

//------------------------------------------------------------------------------
//----------- Registers Declarations -------------------------------------------
//------------------------------------------------------------------------------
reg  [5:0]  adc_tcyc_cnt;
reg  [ 7:0]  serial_present_state;
reg  [ 7:0]  serial_next_state;
reg  [ 4:0]  sclk_cnt;
reg  [ 4:0]  sclk_echo_cnt; // max is 16
reg  [15:0]  serial_buffer;
reg          serial_read_done_s;

//------------------------------------------------------------------------------
//----------- Wires Declarations -----------------------------------------------
//------------------------------------------------------------------------------
wire         cnv_s;
wire         tmsb_done_s;
wire         buffer_reset_s;
wire         clk_s;
wire         sclk_s;
wire         sdi_s;

//------------------------------------------------------------------------------
//----------- Assign/Always Blocks ---------------------------------------------
//------------------------------------------------------------------------------
assign en_o             = en_i; // not used 
assign data_o           = serial_buffer; // just a rename
assign clk_s            = ((serial_present_state == SERIAL_CONV2_STATE) || (serial_present_state == SERIAL_READ_STATE)) ? 1'b1 : 1'b0;
assign data_rd_rdy_o    = (serial_present_state == SERIAL_DATADONE_STATE) ? 1'b1 : 1'b0;
assign cnv_s            = ((serial_present_state == SERIAL_CONV1_STATE) || (serial_present_state == SERIAL_CONV2_STATE))  ? 1'b1 : 1'b0;
assign buffer_reset_s   = ((serial_present_state == SERIAL_CLEAR_STATE) || (serial_present_state == SERIAL_IDLE_STATE)) ? 1'b1 : 1'b0;

// State machine sequence:
// 1) convert start  [high for 8 clock cycles]
// 2) wait
// 3) un-gate serial clk, send 16 clock pulses; use DDR primitive [needs 16 of the 50 clock cycles]
// 4) shift register of incoming data, clocked with DCO
// 5) after cnt of 16 DCO clocks assert data ready (stretch this pulse + FIFO clk if necessay?)
// 6) data is captured by FIFO using fast clk on write side
// 7) serial data buffer is reset
// 8) wait and then return to convert start

// Update conversion timing counters (LJK: based on fast_clk_i)
always @(posedge fast_clk_i)
begin
    if(reset_n_i == 1'b0)
    begin
        adc_tcyc_cnt <= ADC_CYC_CNT;
    end
    else
    begin
        if(adc_tcyc_cnt != 32'd0)
        begin
            adc_tcyc_cnt <= adc_tcyc_cnt - 32'd1;
        end
        else
        begin
            adc_tcyc_cnt <= ADC_CYC_CNT;
        end
    end
end

always @(adc_tcyc_cnt) begin
  if(reset_n_i == 1'b0)
  begin
      serial_present_state <= SERIAL_IDLE_STATE;
  end
  else begin
      serial_present_state <= serial_next_state;
  end
end

// State Switch Logic
always @(*) begin
    case(serial_present_state)
        SERIAL_IDLE_STATE:
            begin
              if (adc_tcyc_cnt == (ADC_CYC_CNT - 5'd1)) begin
                  serial_next_state <= SERIAL_CONV1_STATE;
              end
              else begin
                  serial_next_state <= SERIAL_IDLE_STATE;
              end
            end
          SERIAL_CONV1_STATE: // conv high but no reading yet
                begin
                  if (adc_tcyc_cnt < (ADC_CYC_CNT - 5'd4)) begin
                    serial_next_state <= SERIAL_CONV2_STATE;
                  end
                  else begin
                    serial_next_state <= SERIAL_CONV1_STATE;
                  end
                end
          SERIAL_CONV2_STATE: // conv high and data reading begins
            begin
                if((adc_tcyc_cnt < (ADC_CYC_CNT - 5'd8))) begin
                    serial_next_state <= SERIAL_READ_STATE;
                end
                else begin
                  serial_next_state <= SERIAL_CONV2_STATE;
                end
            end
          SERIAL_READ_STATE:
            begin
              if ((sclk_echo_cnt == 5'd0)&&(sclk_cnt == 5'd0)) begin
                serial_next_state <= SERIAL_DATADONE_STATE;
              end
              else if (sclk_cnt == 5'd0) begin
                serial_next_state <= SERIAL_READDONE_STATE;
              end
              else begin
                serial_next_state <= SERIAL_READ_STATE;
              end
            end
          SERIAL_READDONE_STATE: //TODO -- how to do this?
          begin
            if (sclk_echo_cnt == 5'd0) begin
              serial_next_state <= SERIAL_DATADONE_STATE;
            end
            else begin
              serial_next_state <= SERIAL_READDONE_STATE;
            end
          end
        SERIAL_DATADONE_STATE:
          begin
              serial_next_state <= SERIAL_CLEAR_STATE;
          end
          SERIAL_CLEAR_STATE:
            begin
              serial_next_state <= SERIAL_IDLE_STATE;
            end
        default:
            begin
                serial_next_state <= SERIAL_IDLE_STATE;
            end
    endcase
end

// Count SCLK signals Out (LJK -- this can remain)
always @(posedge fast_clk_i or posedge buffer_reset_s)
begin
    if(buffer_reset_s == 1'b1)
    begin
        sclk_cnt <= 5'd15; // LJK -- changes since states are registered 
    end
    else if ((sclk_cnt > 5'd0)&&(clk_s == 1'b1))
    begin
        sclk_cnt <= sclk_cnt - 5'd1;
    end
end

// Shift Data In (LJK - this can remain)
always @(posedge sclk_s or posedge buffer_reset_s)
begin
    if(buffer_reset_s == 1'b1)
    begin
        serial_buffer <= 16'd0;
        sclk_echo_cnt <= 5'd16;
    end
    else if(sclk_echo_cnt > 5'd0)
    begin
        sclk_echo_cnt <= sclk_echo_cnt - 5'd1;
        serial_buffer <= {serial_buffer[14:0], sdi_s};
    end
end

// Data In LVDS -> Single
IBUFDS
    #(
        .DIFF_TERM("TRUE"),         // Differential Termination
        .IBUF_LOW_PWR("FALSE"),     // Low power="TRUE", Highest performance="FALSE"
        .IOSTANDARD("LVDS_25")         // Specify the input I/O standard
    )
    Data_In_IBUFDS
    (
        .O(sdi_s),                  // Buffer output
        .I(d_pos_i),                // Diff_p buffer input (connect directly to top-level port)
        .IB(d_neg_i)                // Diff_n buffer input (connect directly to top-level port)
    );

assign adc_serial_data = sdi_s;

// Serial Clock In LVDS -> Single
IBUFDS
    #(
        .DIFF_TERM("TRUE"),         // Differential Termination
        .IBUF_LOW_PWR("FALSE"),     // Low power="TRUE", Highest performance="FALSE"
        .IOSTANDARD("LVDS_25")         // Specify the input I/O standard
    )
    Serial_Clock_In_IBUFDS
    (
        .O(sclk_s),                 // Buffer output
        .I(dco_pos_i),              // Diff_p buffer input (connect directly to top-level port)
        .IB(dco_neg_i)              // Diff_n buffer input (connect directly to top-level port)
    );

// Conversion Out Single -> LVDS
assign conv = cnv_s;

OBUFDS
    #(
        .IOSTANDARD("LVDS_25"),        // Specify the output I/O standard
        .SLEW("FAST")               // Specify the output slew rate
    )
    Cnv_Out_OBUFDS
    (
        .O(cnv_pos_o),              // Diff_p output (connect directly to top-level port)
        .OB(cnv_neg_o),             // Diff_n output (connect directly to top-level port)
        .I(cnv_s)                   // Buffer input
    );

// Clock Out Single -> LVDS using a ODDR2
wire fast_clk_s;

ODDR2
    #(
        .INIT (1'b0)
     )
Clock_Out_ODDR
    (
        .CE (1'b1),
        .R (1'b0),
        .S (1'b0),
        .C0 (fast_clk_i),
        .C1 (~fast_clk_i),
        .D0 (clk_s),
        .D1 (1'b0),
        .Q (fast_clk_s)
    );

OBUFDS
    #(
        .IOSTANDARD("LVDS_25"),     // Specify the output I/O standard
        .SLEW("FAST")               // Specify the output slew rate
    )
    Clock_Out_OBUFDS
    (
        .O(clk_pos_o),              // Diff_p output (connect directly to top-level port)
        .OB(clk_neg_o),             // Diff_n output (connect directly to top-level port)
        .I(fast_clk_s)              // Buffer input
    );

/*
assign dco = fast_clk_i & clk_s; // for debug

OBUFDS
    #(
        .IOSTANDARD("LVDS_25"),        // Specify the output I/O standard
        .SLEW("FAST")               // Specify the output slew rate
    )
    Clock_Out_OBUFDS
    (
        .O(clk_pos_o),              // Diff_p output (connect directly to top-level port)
        .OB(clk_neg_o),             // Diff_n output (connect directly to top-level port)
        .I(fast_clk_i & clk_s)      // Buffer input
    );
*/
endmodule