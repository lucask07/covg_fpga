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
// FILE NAME : AD7961_timing.v   
// MODULE NAME : AD7961   
// original AUTHOR : atofan       
// original AUTHOR'S EMAIL : alexandru.tofan@analog.com
// modified by: Lucas Koerner
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// KEYWORDS : AD7961
// -----------------------------------------------------------------------------
// PURPOSE : Timing block for the AD7961, 16-Bit, 5 MSPS PulSAR Differential ADC
//           so that multiple AD7961s can be synchronized and the timing can be 
//           shared with other modules
// -----------------------------------------------------------------------------
// REUSE ISSUES        
// Reset Strategy      : Active low reset signal
// Other               : The driver is intended to be used for AD7961 ADCs configured
//                     : in Echoed Clock Mode
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
`timescale 1ns / 1ps
//------------------------------------------------------------------------------
//----------- Module Declaration -----------------------------------------------
//------------------------------------------------------------------------------
module AD7961_timing
    (
        input wire          m_clk_i,                    // 200 MHz timing clk (was 100 MHz Clock, used for timing)
        input wire          reset_n_i,                  // Reset signal, active low
        output reg [31:0] adc_tcyc_cnt,
        output reg [4:0] cycle_cnt
    );

//------------------------------------------------------------------------------
//----------- Local Parameters -------------------------------------------------
//------------------------------------------------------------------------------
// FPGA Clock Frequency
parameter real          FPGA_CLOCK_FREQ         = 200;
// Conversion signal generation
parameter real          TCYC                    = 0.200;
parameter       [31:0]  ADC_CYC_CNT             = FPGA_CLOCK_FREQ * TCYC - 1;
parameter       [4:0]   CYCLE_CNT = 9;
 

// Update conversion timing counters (this counter is then used by the AD7961 module)
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

// slower cycle counter 
always @(posedge m_clk_i)
begin
    if(reset_n_i == 1'b0) cycle_cnt <= CYCLE_CNT;
    else
    begin
        if(adc_tcyc_cnt == 32'd0)
        begin
            if (cycle_cnt != 5'd0) cycle_cnt <= cycle_cnt - 5'd1;
            else cycle_cnt <= CYCLE_CNT;
        end
    end
end

endmodule