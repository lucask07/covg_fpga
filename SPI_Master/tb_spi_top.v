`timescale 1ns / 1ps

////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer:
//
// Create Date:   20:37:51 12/28/2020
// Design Name:   top_module
// Module Name:   C:/Users/iande/OneDrive - University of St. Thomas/Research SPI core files/SPI_Master/tb_spi_top.v
// Project Name:  SPI_Master
// Target Device:  
// Tool versions:  
// Description: 
//
// Verilog Test Fixture created by ISE for module: top_module
//
// Dependencies:
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
////////////////////////////////////////////////////////////////////////////////

module tb_spi_top;

	// Inputs
	reg clk;
	reg fifoclk;
	reg rst;
	reg [31:0] ep_dataout;
	reg trigger;
	reg readFifo;
	reg rstFifo;

	// Outputs
	wire hostinterrupt;
	wire [31:0] dout;
	wire [31:0] lastWrite;
	wire ep_ready;
	wire slow_pulse;
	
	//
	integer i;

	// Instantiate the Unit Under Test (UUT)
	top_module uut (
		.clk(clk),
		.fifoclk(fifoclk),
		.rst(rst), 
		.ep_dataout(ep_dataout), 
		.trigger(trigger), 
		.hostinterrupt(hostinterrupt), 
		.readFifo(readFifo),
		.rstFifo(rstFifo),
		.dout(dout),
		.lastWrite(lastWrite),
		.ep_ready(ep_ready),
		.slow_pulse(slow_pulse)
	);
	
	// Generate clock
	always #5 clk = ~clk;
	
	// Generate fifoclk
	always #4.96 fifoclk = ~fifoclk;

	initial begin
		// Initialize Inputs
		clk = 1'b0;
		fifoclk = 1'b0;
		rst = 1'b0;
		rstFifo = 1'b0;
		trigger = 1'b0;
		/*ep_dataout = 0;
		trigger = 0;*/
		readFifo = 1'b0;
		#15;
		rst = 1'b1;
		rstFifo = 1'b1;

		// Wait 100 ns for global reset to finish
		#100;
		rst = 1'b0;
		rstFifo = 1'b0;
        
		// Add stimulus here
		#20;
      trigger = 1'b0;
      #5;
      ep_dataout = 32'h80000051;
		#10//
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      trigger = 1'b1;
      ep_dataout = 32'h40000001;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000001;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      trigger = 1'b1;
      ep_dataout = 32'h40008aa5;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000041;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40003610;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000061;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40000001;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000041;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40003710;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #900;
		/**/
		ep_dataout = 32'hc0000000;
		trigger = 1'b1;
		#10;
		trigger = 1'b0;
		#40;
		//*/
      ep_dataout = 32'h40005a01;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000041;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40003710;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #900;
      ep_dataout = 32'h40005238;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000041;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40003710;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #900;
      #40;
      readFifo = 1'b1;
      #10;
      readFifo = 1'b0;
      #40;
      readFifo = 1'b1;
      #10;
      readFifo = 1'b0;
      #40;
      readFifo = 1'b1;
      #10;
      readFifo = 1'b0;
		#40;
		rstFifo = 1'b1;
		#10;
		rstFifo = 1'b0;
		#100;
		for (i=0; i<128; i=i+1) begin
          ep_dataout = 32'h40005238 + (i);
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#40;
				ep_dataout = 32'h80000041;
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#40;
				ep_dataout = 32'h40003710;
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#900;
      end
		readFifo = 1'b1;
		#/*1500*/70;
		readFifo = 1'b0;
		#20
		for (i=0; i<7; i=i+1) begin
          ep_dataout = 32'h40005238 + (i);
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#40;
				ep_dataout = 32'h80000041;
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#40;
				ep_dataout = 32'h40003710;
				trigger = 1'b1;
				#10;
				trigger = 1'b0;
				#900;
      end
		readFifo = 1'b1;
		#1350;
		readFifo = 1'b0;
		#20;
	end
      
endmodule

