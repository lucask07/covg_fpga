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
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
`timescale 1ns / 1ps
//------------------------------------------------------------------------------
//----------- Module Declaration -----------------------------------------------
//------------------------------------------------------------------------------
module AD7961
    (
        input wire          m_clk_i,                    // 100 MHz Clock, used for tiing
        input wire          fast_clk_i,                 // Maximum 300 MHz Clock, used for serial transfer
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
        output wire [15:0]  data_o                      // Read Data
    );

//------------------------------------------------------------------------------
//----------- Local Parameters -------------------------------------------------
//------------------------------------------------------------------------------
// FPGA Clock Frequency
parameter real          FPGA_CLOCK_FREQ         = 100;
// Conversion signal generation
parameter real          TCYC                    = 0.200;
parameter       [31:0]  ADC_CYC_CNT             = FPGA_CLOCK_FREQ * TCYC - 1;

// Serial Interface
parameter               SERIAL_IDLE_STATE       = 3'b001;
parameter               SERIAL_READ_STATE       = 3'b010;
parameter               SERIAL_DONE_STATE       = 3'b100; 
 
//------------------------------------------------------------------------------
//----------- Registers Declarations -------------------------------------------
//------------------------------------------------------------------------------ 
reg  [31:0]  adc_tcyc_cnt;
reg  [ 2:0]  serial_present_state;
reg  [ 2:0]  serial_next_state;
reg  [ 4:0]  sclk_cnt;
reg  [ 4:0]  sclk_echo_cnt;
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
assign clk_s            = ((serial_present_state == SERIAL_READ_STATE)&&(sclk_cnt > 5'd0)&&(buffer_reset_s != 1'b1)) ? 1'b1 : 1'b0;  
assign en_o             = en_i;
assign data_o           = serial_buffer;
assign data_rd_rdy_o    = ((serial_read_done_s == 1'b1) && (adc_tcyc_cnt == 32'd4)) ? 1'b1 : 1'b0; 
assign cnv_s            = (adc_tcyc_cnt > 32'd17) ? 1'b1 : 1'b0;
assign tmsb_done_s      = (adc_tcyc_cnt == 32'd18) ? 1'b1 : 1'b0;
assign buffer_reset_s   = (adc_tcyc_cnt == 32'd2) ? 1'b1 : 1'b0;

// Update conversion timing counters 
always @(posedge m_clk_i)
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

// State Switch Logic
always @(serial_present_state, tmsb_done_s, sclk_cnt, sclk_echo_cnt)
begin
    serial_next_state <= serial_present_state;
    case(serial_present_state)
        SERIAL_IDLE_STATE:
            begin
                if(tmsb_done_s == 1'b1)
                begin
                    serial_next_state <= SERIAL_READ_STATE;
                end
            end
        SERIAL_READ_STATE:
            begin
                if((sclk_echo_cnt == 5'd0)&&(sclk_cnt == 5'd0))
                begin
                    serial_next_state <= SERIAL_DONE_STATE;
                end
            end
        SERIAL_DONE_STATE:
            begin
                serial_next_state <= SERIAL_IDLE_STATE;
            end 
        default:
            begin
                serial_next_state <= SERIAL_IDLE_STATE;
            end
    endcase
end

// State Output Logic
always @(posedge fast_clk_i)
begin
    if(reset_n_i == 1'b0)
    begin
        serial_read_done_s      <= 1'b0;
        serial_present_state    <= SERIAL_IDLE_STATE;
    end
    else
    begin
        serial_present_state <= serial_next_state;
        case(serial_present_state)
            SERIAL_IDLE_STATE:
                begin
                    serial_read_done_s <= 1'b1;
                end
            SERIAL_READ_STATE:
                begin
                    serial_read_done_s <= 1'b0;
                end
            SERIAL_DONE_STATE:
                begin
                    serial_read_done_s <= 1'b1;
                end
            default: 
                begin   
                    serial_read_done_s <= 1'b0;
                end
        endcase
    end
end

// Count SCLK signals Out
always @(posedge fast_clk_i or posedge buffer_reset_s)
begin
    if(buffer_reset_s == 1'b1)
    begin  
        sclk_cnt <= 5'd16; 
    end
    else if ((sclk_cnt > 5'd0)&&(clk_s == 1'b1))
    begin
        sclk_cnt <= sclk_cnt - 5'd1;
    end
end

// Shift Data In
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

// Clock Out Single -> LVDS

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
OBUFDS 
    #(
        .IOSTANDARD("LVDS_33"),        // Specify the output I/O standard
        .SLEW("FAST")               // Specify the output slew rate
    ) 
    Clock_Out_OBUFDS 
    (
        .O(clk_pos_o),              // Diff_p output (connect directly to top-level port)
        .OB(clk_neg_o),             // Diff_n output (connect directly to top-level port)
        .I(fast_clk_i & clk_s)      // Buffer input 
    );    
`*/
endmodule
