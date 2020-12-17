//------------------------------------------------------------------------
// example.v - Top-level instantiation of I2C Controller with FrontPanel
//
// Clocks:
//    CLK_SYS    - 100 MHz single-ended input clock
//    CLK_TI     - 48 MHz host-interface clock provided by okHost
//    CLK0       - Memory interface clock provided by MEM_IF
//    CLK_PIX    - 96 MHz single-ended input clock from image sensor
//
//
// Host Interface registers:
// WireIn 0x00
//     0 - Asynchronous reset
// WireIn 0x10
//   7:0 - I2C input data
//
// WireOut 0x30
//  15:0 - I2C data output
//
// TriggerIn 0x50
//     0 - I2C start
//     1 - I2C memory start
//     2 - I2C memory write
//     3 - I2C memory read
// TriggerOut 0x70  (i2c_clk)
//     0 - I2C done
//
//
// This sample is included for reference only.  No guarantees, either 
// expressed or implied, are to be drawn.
//------------------------------------------------------------------------
// Copyright (c) 2005-2017 Opal Kelly Incorporated
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//------------------------------------------------------------------------
`timescale 1ns/1ps
`default_nettype none

module top_level(
		  input wire [4:0] okUH,
		  output wire[2:0] okHU,
		  inout wire[31:0] okUHU,
		  inout wire okAA,
		  input wire sys_clkn,
		  input wire sys_clkp,
		  input wire reset,  //TODO: This reset is not used 
		  // Your signals here
		  output wire [7:0]  led,
		  inout wire        scl,
		  inout wire       sda,
		  //output wire [7:0] sine,
		  output wire [7:0] i2c_debug,
		  output wire [4:0] trig_debug,
		  output reg period_signal,
		  output reg dly_a_out,
		  output reg dly_b_out
		);
  
assign trig_debug[0] = ti50_clkti[0];
assign trig_debug[1] = to70_clkti[0];
assign trig_debug[2] = ti50_clkti[1];
assign trig_debug[3] = ti50_clkti[2];
assign trig_debug[4] = ti50_clkti[3];
  
	// System Clock from input differential pair 
	wire clk_sys;
	IBUFGDS osc_clk(
		  .O(clk_sys),
		  .I(sys_clkp),
		  .IB(sys_clkn)
	);

	//FrontPanel (HostInterface) wires	
	wire okClk;
	wire [112:0] okHE;
	wire [64:0] okEH;
	// Adjust size of okEHx to fit the number of outgoing endpoints in your design (n*65-1:0)
	wire [3*65-1:0] okEHx;
	wire [31:0] ep00wire, ep10wire, dly_period, dly_width, dly_delay, dly_pulses;
	wire [31:0] i2c_rep_rate;
	wire [31:0] to70_clkti; 
	wire [31:0] ti50_clkti; 
	
	// FIFO and pipe-out
	wire fifo_rd_en;

	okHost hostIF (
		  .okUH(okUH),
		  .okHU(okHU),
		  .okUHU(okUHU),
		  .okClk(okClk),
		  .okAA(okAA),
		  .okHE(okHE),
		  .okEH(okEH)
	);

	okWireIn wi0 (.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire)); // FPGA control register: resets, LEDs 
	okWireIn wi1 (.okHE(okHE), .ep_addr(8'h01), .ep_dataout(memdin));
	// okWireIn wi2 (.okHE(okHE), .ep_addr(8'h02), .ep_dataout(s_axis_config_tdata));
	// counter for I2C 
	okWireIn wi3 (.okHE(okHE), .ep_addr(8'h03), .ep_dataout(i2c_rep_rate));
	
	// delay generator wire inputs
	okWireIn wi4 (.okHE(okHE), .ep_addr(8'h04), .ep_dataout(dly_period));
	okWireIn wi5 (.okHE(okHE), .ep_addr(8'h05), .ep_dataout(dly_width));
	okWireIn wi6 (.okHE(okHE), .ep_addr(8'h06), .ep_dataout(dly_delay));
	okWireIn wi7 (.okHE(okHE), .ep_addr(8'h07), .ep_dataout(dly_pulses));
	
	okTriggerOut trig_out (.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h70), .ep_clk(okClk), .ep_trigger(to70_clkti));
	okTriggerIn trig_in (.okHE(okHE), .ep_addr(8'h50), .ep_clk(okClk), .ep_trigger(ti50_clkti));
	okWireOut wo0 (.okHE(okHE), .okEH(okEHx[1*65 +: 65 ]), .ep_addr(8'h30), .ep_datain({24'b0, memdout}	));	  
	okPipeOut pipeA0(.okHE(okHE), .okEH(okEHx[2*65 +: 65]), .ep_addr(8'hA0), .ep_read(fifo_rd_en), .ep_datain({24'b0, memdout}));

	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(3)) wireOR (okEH, okEHx);
 
	//integer led_offset = 8; //TODO: Check if this offset is working 
	assign led[0] = ep00wire[8 + 0];
	assign led[1] = ep00wire[8 + 1];
	assign led[2] = ep00wire[8 + 2];
	assign led[3] = ep00wire[8 + 3];
	assign led[4] = ep00wire[8 + 4];
	assign led[5] = ep00wire[8 + 5];
	assign led[6] = ep00wire[8 + 6];
	assign led[7] = ep00wire[8 + 7];
 
	// Reset Chain
	wire reset_syspll;
	wire reset_pixdcm;
	wire reset_async_i2c;
	wire reset_async_dds;
	wire reset_clkpix;
	wire reset_clk_ti;
	wire reset_clk_sys;

	assign reset_async_i2c         =  ep00wire[0];	
	// assign reset_async_dds 			 =  ep00wire[1];
	
	// Create RESETs that deassert synchronous to specific clock domains
	// 	Reset for the I2C controller
	sync_reset sync_reset_ti (.clk(okClk),     .async_reset(reset_async_i2c),  .sync_reset(reset_clk_ti));
	//sync_reset sync_reset_sys (.clk(clk_sys),   .async_reset(reset_async_dds),  .sync_reset(reset_clk_sys));

	wire [15:0] memdin;  //from OKWireIn
	wire [7:0]  memdout; //to OKWireOUT
	wire [15:0] i2c_read_num;
	assign i2c_read_num = ep00wire[31:16];

	// trigger signals: start, memstart, memwrite, memread 
	// goal: memstart can come from host or from FPGA counter 
	// counter can go multiple times 
	reg [31:0] rep_cnt; // timer 
	reg [15:0] read_cnt;  //number of transactions 
	reg rep_cnt_trig;

	always @(posedge okClk or posedge ti50_clkti[0]) begin 
		if (ti50_clkti[0] | rep_cnt == 32'b0)
			rep_cnt <= i2c_rep_rate;
	       	else if (rep_cnt !=32'b0 & read_cnt != 16'b0)	
			rep_cnt <= rep_cnt - 1'b1;
	end

	always @(posedge okClk) begin 
		if (rep_cnt == 32'b0)
			rep_cnt_trig <= 1'b1;
	       	else
			rep_cnt_trig <= 1'b0;
	end
	
	always @(posedge okClk or posedge ti50_clkti[0]) begin 
		if (ti50_clkti[0])
			read_cnt <= i2c_read_num;
	       	else if ( (read_cnt != 16'b0) & (rep_cnt_trig) )	
			read_cnt <= read_cnt - 1'b1;
	end

	wire cnt_start; 
	assign cnt_start = ti50_clkti[0] | rep_cnt_trig; 

	wire i2c_start; 
	assign i2c_start = ep00wire[2] ? ti50_clkti[0] : cnt_start;

	reg mult_read_done;
	reg mult_read_done_dly;	
	// create a trigger to indicate end of multiple reads 
	always @(posedge okClk) begin
		mult_read_done <= (read_cnt == 16'b0);
		mult_read_done_dly <= (mult_read_done);
	end
	assign to70_clkti[1] = mult_read_done & (~mult_read_done_dly);

	wire [11:0] fifo_data_cnt; 
	reg data_cnt;
	reg data_cnt_dly;	
	// create a trigger to indicate end of multiple reads 
	always @(posedge okClk) begin
		data_cnt <= (fifo_data_cnt > 12'h800);
		data_cnt_dly <= (data_cnt);
	end
	assign to70_clkti[2] = data_cnt & (~data_cnt_dly);

	wire [3:0] cmd_ram_sel; 
	
	assign cmd_ram_sel[0] = ep00wire[4] | (ep00wire[3] & (read_cnt[0] == 1'b0));
	assign cmd_ram_sel[1] = ep00wire[5] | (ep00wire[3] & (read_cnt[0] == 1'b1));
	assign cmd_ram_sel[2] = ep00wire[6] & 1'b0;
	assign cmd_ram_sel[3] = ep00wire[7] & 1'b0;
	
	i2cController # (
		.CLOCK_STRETCH_SUPPORT  (1),
		.CLOCK_DIVIDER          (16'd62) ) //this has to be a constant
	i2c_ctrl0 (
		.clk          (okClk),
		.reset        (reset_clk_ti),
		.start        (i2c_start),
		.done         (to70_clkti[0]),
		.memclk       (okClk),
		.memstart     (ti50_clkti[1]),
		.memwrite     (ti50_clkti[2]),
		.memread      (ti50_clkti[3]),
		.memdin       (memdin[7:0]),
		.memdout      (memdout[7:0]),
		.i2c_sclk     (scl), 
		.i2c_sdat     (sda),
		.i2c_debug    (i2c_debug),
		.fifo_rd_en(fifo_rd_en),
		.fifo_cnt(fifo_data_cnt),
		.cmd_ram_sel(cmd_ram_sel)
	);
  
reg [31:0] dly_period_cnt;

/* Delay generator */ 
// free running period generator with a reset  
always @(posedge okClk) begin   
	if (~ep00wire[1])
		dly_period_cnt <= 32'b0;
	else begin
	if (dly_period_cnt == 32'b0) begin
		dly_period_cnt <= dly_period;
		period_signal <= ~period_signal;
	end
	else
		dly_period_cnt <= dly_period_cnt - 1;
	end
end  
  
reg period_signal_dly, period_pulse, period_pulse_b, period_pulse_b_dly, period_pulse_b_gate;
// pulse from the period generator to start the width counter 
always @(posedge okClk) begin
	period_pulse <= (period_signal & ~period_signal_dly);
	period_signal_dly <= period_signal;
end	

reg [31:0] dly_width_a_cnt, dly_width_b_cnt, delay_dly_cnt;

always @(posedge okClk) begin
	if(period_pulse) begin // load the counter 
		dly_width_a_cnt <= dly_width;
	end
	else begin
		if (dly_width_a_cnt == 32'b0) 
			dly_a_out <= 'b0;
		else begin
			dly_width_a_cnt <= dly_width_a_cnt - 1'b1;
			dly_a_out <= 'b1;
		end
	end
end

always @(posedge okClk) begin
	if(period_pulse) begin // load the counter 
		delay_dly_cnt <= dly_delay;
	end
	else begin
		if (delay_dly_cnt == 32'b0) 
			period_pulse_b_gate <= 'b1;
		else begin
			delay_dly_cnt <= delay_dly_cnt - 1'b1;
			period_pulse_b_gate <= 'b0;
		end
	end
end

always @(posedge okClk) begin
	period_pulse_b <= (period_pulse_b_gate & ~period_pulse_b_dly);
	period_pulse_b_dly <= period_pulse_b_gate;
end	


always @(posedge okClk) begin
	if(period_pulse_b) begin // load the counter 
		dly_width_b_cnt <= dly_width;
	end
	else begin
		if (dly_width_b_cnt == 32'b0) 
			dly_b_out <= 'b0;
		else begin
			dly_width_b_cnt <= dly_width_b_cnt - 1'b1;
			dly_b_out <= 'b1;
		end
	end
end

/*   
wire [31:0] s_axis_config_tdata; // wire in for DDS phase increment 
wire [7:0] cosine;
wire [15:0] extra;

dds dds1 (
  .aclk(clk_sys), 				// input aclk
  .aclken(1'b1), 					// input aclken
  .aresetn(~reset_clk_sys), 	// input aresetn     TODO: since this is resetn does the deassert synch logic need to change?
  .s_axis_config_tvalid(1'b1), 	// input s_axis_config_tvalid
  .s_axis_config_tdata(s_axis_config_tdata), 			// input [31 : 0] s_axis_config_tdata
  .m_axis_data_tvalid(), 										// output m_axis_data_tvalid
  .m_axis_data_tdata({extra[15:0], sine[7:0], cosine[7:0]}), 			// output [31 : 0] m_axis_data_tdata [cos is sine extended to nearest byte boundary]
  .m_axis_phase_tvalid(), 			// output m_axis_phase_tvalid
  .m_axis_phase_tdata() 			// output [31 : 0] m_axis_phase_tdata
);
*/
  
// comparator and counter for number of sinusoid periods (trigger fires at each period)
// auto-increment of phase: start phase, stop phase, index of current phase, bit that indicates done
// state machine for DDS control: reset, start, running, stop 
// output scaling (/2^n or more fine grained options?)

endmodule
