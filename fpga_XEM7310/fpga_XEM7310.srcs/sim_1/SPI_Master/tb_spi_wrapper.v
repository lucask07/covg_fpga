`timescale 1ns / 1ps

////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer:
//
// Create Date:   Aug 2021
// Design Name:   tb_spi_wrapper  tests spi_controller for the ADS8686 
// Module Name:   
// Project Name:  
// Target Device:  Opal Kelly XEM7310; Virtex; 200 MHz system clock 
// Tool versions:  
// Description: 
//
// Dependencies:
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
////////////////////////////////////////////////////////////////////////////////

module tb_spi_wrapper;
	// Inputs
	reg clk;
	reg rst, divider_rst;
	reg [31:0] wire_in;
	reg trigger;
	reg miso;
	reg host_fpgab;
    reg okClk;
    reg [31:0]addr;
    reg [31:0]data_in;
    reg write_in;

	// Outputs
	wire [31:0] wire_out;
	wire data_valid;
	wire ss, sclk, mosi, convst;

	spi_controller uut(
        .clk(clk),
        .reset(rst),
        .divider_reset(divider_rst),
        .dac_val(wire_in),
        .dac_convert_trigger(trigger),
        .host_fpgab(host_fpgab),
        // OKRegister bridge inputs 
        .okClk(okClk),
        .addr(addr),
        .data_in(data_in),
        .write_in(write_in),
        // outputs 
        .dac_out(wire_out),
        .data_valid(data_valid),
        .ss(ss),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .convst_out(convst)
        );
	
	// Generate clock
	always #2.5 clk = ~clk;//now 200 MHz sys clock
    always #5.05 okClk = ~okClk; 
    
	initial begin
		// Initialize Inputs
		clk = 1'b0;
		rst = 1'b0;
		divider_rst = 1'b0;
		miso = 1'b1;
		trigger = 1'b0;
		wire_in = 32'h0;
		host_fpgab = 1'b1; //host controlled SPI writes 
		// OK register bridge
        okClk = 1'b0;
        addr = 32'h0;
        data_in = 32'd0;
        write_in = 1'b0;
		
		#15;
        rst = 1'b1;
		// Wait 5 ns (one clock) for global reset to finish
		#5;
		rst = 1'b0;
        
      // Add stimulus here
      #17.5;
      trigger = 1'b0;
      wire_in = 32'h00000000; 
      #10;
      wire_in = 32'h80000051;//divide register address
	  #10;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h40000008;
      #5
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000001;//tx register 1 address
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      trigger = 1'b1;
      wire_in = 32'h40008aa5;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000041;//ctrl register address
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      //wire_in = 32'h40003610;
      wire_in = 32'h40003618;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000061;//ss register address
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h40000001;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000041;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      //wire_in = 32'h40003710; // set ths go bit 
      wire_in = 32'h40003718;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #1905;
    /**/
    wire_in = 32'hc0000000;
    trigger = 1'b1;
    #5;
    trigger = 1'b0;
    #40;
    //*/
      wire_in = 32'h40005a01;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000041;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      //wire_in = 32'h40003710;
      wire_in = 32'h40003718;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #1900;
      wire_in = 32'h40ffffff; //why don't we need to switch to the Tx register? 
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000041;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      //wire_in = 32'h40003710;
      wire_in = 32'h40003718;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #1000;
      
      // end host driven tests 
      // Program divider 
      #5;
      addr = 32'h0; 
      data_in = 32'd400;  // T = 5ns * 400 = 2000 ns => 500 kHz
      write_in = 1'b1;
      #25;
      // program SPI data
      addr = 32'h1; 
      data_in = 32'h80000001;
      write_in = 1'b1;
      #25;
      addr = 32'h2; 
      data_in = 32'h40000000;
      write_in = 1'b1;
      #25;
      addr = 32'h3; 
      data_in = 32'h80000041;
      write_in = 1'b1;
      #25;
      // program go bit to Tx 
      addr = 32'h4; 
      data_in = 32'h40003710;
      write_in = 1'b1;
      #5;
      write_in = 1'b0;
      #25;
      divider_rst = 1'b1; //don't reset the wishbone and SPI top, only the clock divider
      #10
      divider_rst = 1'b0;
      #10
      host_fpgab = 1'b0; // FPGA driven controlled SPI writes 
   
	end
      
endmodule

