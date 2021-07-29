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

module tb_clock_divider;

	// Inputs to DUT
	reg clk;
	reg okClk;
	reg rst;
	reg [31:0] addr;
	reg [31:0] data_in;
	reg write_in;

	// Outputs from DUT
	wire clk_out, pulse, convst, read_en_data, read_en_creg;
	// Outputs from DUT2 
	wire [31:0] data_out;

clock_divider #(.ADDR(32'ha)) dut(
    .clk(clk),
    .okClk(okClk), // needed to synchronize to the register bridge data. Should reset divider after loading data.  
    .rst(rst),
    .clk_out(clk_out), //50% duty-cycle 
    .pulse(pulse), // single clk period pulse 
    .convst(convst),
    .read_en_data(read_en_data),
    .read_en_creg(read_en_creg),    
    .addr(addr),     // input data to program frequency 
    .data_in(data_in), // must be multiple of 2 
    .write_in(write_in)
    );
	
spi_data_gen #(.ADDR(32'd8)) dut2 (
        .clk(clk),
        .okClk(okClk), // needed to synchronize to the register bridge data. Should reset divider after loading data.  
        .read_en_data(read_en_data),
        .read_en_creg(read_en_creg),
        // input data to program frequency 
        .addr(addr),
        .data_in(data_in), 
        .write_in(write_in),
        .data_out(data_out)
        );
	
	// Generate clock
	always #2.5 clk = ~clk;//now 200 MHz sys clock
	always #5.05 okClk = ~okClk;//now 200 MHz sys clock
    
	initial begin
		// Initialize Inputs
		clk = 1'b0;
		okClk = 1'b0;
		rst = 1'b0;
		addr = 32'h0;
		data_in = 32'd0;
		write_in = 1'b0;
		#15;
        rst = 1'b1;
		// Wait 5 ns (one clock) for global reset to finish
		#5;
		rst = 1'b0;
        
      // Program divider 
      #5;
      addr = 32'ha; 
      data_in = 32'd200;
      write_in = 1'b1;
      #25;
      // program SPI creg data 
      addr = 32'h8; 
      data_in = 32'h5555;
      write_in = 1'b1;
      #25;
      // program SPI tx data 
      addr = 32'h9; 
      data_in = 32'haaaa;
      write_in = 1'b1;
      #25;
      
      
      #5;

      write_in = 1'b0;
	  #100000;

	end    
endmodule
