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

module tb_spi_wrapper;

	// Inputs
	reg clk;
	reg rst;
	reg [31:0] wire_in;
	reg trigger;
	reg miso;

	// Outputs
	wire [31:0] wire_out;
	wire ss, sclk, mosi;
	
	//
	integer i;
	//
		
    //syncronizer for the system rst (non-Fifo)
    reg s1, s2;
    wire sync_rst;
     
    always@(posedge rst or posedge clk)begin
        if(rst)begin
            s1<=1'b1;
            s2<=1'b1;
        end
        else begin
            s1<=1'b0;
            s2<=s1;
        end
    end
        
     assign sync_rst = s2;
		
		
	clock_divider #(.ADDR(3)) uut(
    .clk(clk),
    .okClk(okClk), // needed to synchronize to the register bridge data. Should reset divider after loading data.  
        input wire rst,
        output reg clk_out, //50% duty-cycle 
        output reg pulse, // single clk period pulse 
        input wire [31:0] addr,
        input wire [31:0] data_in, // must be multiple of 2 
        input wire write_in
        );
	
	// Generate clock
	always #2.5 clk = ~clk;//now 200 MHz sys clock
    always #5   okClk = ~okClk;
	initial begin
		// Initialize Inputs
		clk = 1'b0;
		rst = 1'b0;
		miso = 1'b1;
		trigger = 1'b0;
		wire_in = 32'h0;
		#15;
        rst = 1'b1;
		// Wait 100 ns for global reset to finish
		#100;
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
      trigger = 1'b1;
      wire_in = 32'h40000003;
      #10;
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
      wire_in = 32'h40003610;
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
      wire_in = 32'h40003710;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #905;
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
      wire_in = 32'h40003710;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #900;
      wire_in = 32'h40005238;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h80000041;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #40;
      wire_in = 32'h40003710;
      trigger = 1'b1;
      #5;
      trigger = 1'b0;
      #5000;
	end
      
endmodule

