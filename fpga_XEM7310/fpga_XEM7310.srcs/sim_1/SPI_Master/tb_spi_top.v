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
	reg ep_write;
	reg [31:0] ep_address;
	reg [31:0] ep_dataout_coeff;
	reg [9:0] en_period;
	reg ddr3_rst;
	reg regTrigger;
	wire filter_sel;

	// Outputs
	wire hostinterrupt;
	wire [31:0] dout;
	wire [31:0] lastWrite;
	wire ep_ready;
	wire slow_pulse;
	wire clk_en;
	wire [13:0] filter_out_modified;
	//
//	wire clk_en;
//	general_clock_divide divide(
//	.clk(clk),
//	.rst(rst),
//	.en_period(32'd40),
//	.clk_en(clk_en)
//	);
	//
	integer i;
	//
	reg data_rdy = 1'b0;
	reg [23:0] filter_in; // expand data length

	// Instantiate the Unit Under Test (UUT)
	spi_fifo_driven #(.ADDR(8'h15)) uut (
		.clk(clk),
		.fifoclk(fifoclk),
		.rst(rst), 
		//.ep_dataout(ep_dataout), 
		//.trigger(trigger), 
		//.hostinterrupt(hostinterrupt), 
		//.readFifo(readFifo),
		//.rstFifo(rstFifo),
		//.dout(dout),
		//.lastWrite(lastWrite),
		//.ep_ready(ep_ready),
		//.slow_pulse(slow_pulse),
		.data_rdy_0(data_rdy),
		.data_i(filter_in),
		.ep_write(ep_write),
		.ep_address(ep_address),
		.ep_dataout_coeff(ep_dataout_coeff),
		.filter_sel(1'b1),  //LJK: enable filter select
		//.en_period(en_period),
		//.ddr3_rst(ddr3_rst),
		//.clk_en(clk_en),
		.regTrigger(regTrigger),
		.filter_out_modified(filter_out_modified)
	);
	
	// Generate clock
	always #2.5 clk = ~clk;//now 200 MHz sys clock
	
	// Generate fifoclk
	always #4.96 fifoclk = ~fifoclk;
	
	//simulating data ready from ad796x.v
	reg [7:0] count_enable = 8'b0;
    reg [7:0] count = 8'b0;	
	
	//reg data_rdy = 1'b0;
    always@(posedge clk)begin
        if(count_enable == 8'd39)begin
            data_rdy = 1'b1;
            count_enable = 5'b0;
        end
        else begin
            data_rdy = 1'b0;
            count_enable = count_enable + 1'b1;
        end
    end
    
    integer FileID, file;
//     Data source for filter_in
      initial begin
          FileID = $fopen("filter_in.dat", "r");
      end
    
    always@(posedge data_rdy)begin
        $display("%d", filter_out_modified);
        if(count > 10'd49)begin
            count = count + 1'b1;
            //filter_in = 16'h7fff;
            //filter_in = 16'h4000;
            //filter_in = 16'hc000;
            file = $fscanf(FileID, "%h\n", filter_in);
        end
        else begin
            file = $fscanf(FileID, "%h\n", filter_in);
            //filter_in = 16'h0000;
            //filter_in = 16'hc000;
            count = count + 1'b1;
        end
    end
    
	initial begin
		// Initialize Inputs
		clk = 1'b0;
		fifoclk = 1'b0;
		rst = 1'b0;
		ddr3_rst = 1'b0;
		rstFifo = 1'b0;
		trigger = 1'b0;
		regTrigger = 1'b0;
		filter_in = 16'h0;
		ep_write = 1'b0;
		ep_address = 32'h0;
		ep_dataout_coeff = 32'h0;
		en_period = 10'd80;
		/*ep_dataout = 0;
		trigger = 0;*/
		readFifo = 1'b0;
		#15;
		rst = 1'b1;
		ddr3_rst = 1'b1;
		rstFifo = 1'b1;

		// Wait 100 ns for global reset to finish
		#100;
		rst = 1'b0;
		ddr3_rst = 1'b0;
		rstFifo = 1'b0;
        
		// Add stimulus here
		#25;
      trigger = 1'b0;
      ep_write = 1'b1;
      ep_address = 32'h00000000 + 8'h19;
      ep_dataout_coeff = 32'h009e1586;
      //ep_dataout_coeff = 32'h7fff_ffff;
      #10;
      ep_address = 32'h00000001 + 8'h19;
      ep_dataout_coeff = 32'h20000000;
      #10;
      ep_address = 32'h00000002 + 8'h19;
      ep_dataout_coeff = 32'h40000000;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h00000003 + 8'h19;
      ep_dataout_coeff = 32'h20000000;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h00000004 + 8'h19;
      ep_dataout_coeff = 32'hbce3be9a;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h00000005 + 8'h19;
      ep_dataout_coeff = 32'h12f3f6b0;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h00000008 + 8'h19;
      ep_dataout_coeff = 32'h7fffffff;
      #10;
      ep_address = 32'h00000009 + 8'h19;
      ep_dataout_coeff = 32'h20000000;
      #10;
      ep_address = 32'h0000000a + 8'h19;
      ep_dataout_coeff = 32'h40000000;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h0000000b + 8'h19;
      ep_dataout_coeff = 32'h20000000;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h0000000c + 8'h19;
      ep_dataout_coeff = 32'hab762783;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h0000000d + 8'h19;
      ep_dataout_coeff = 32'h287ecada;
      //ep_dataout_coeff = 32'h00000000;
      #10;
      ep_address = 32'h00000007 + 8'h19;
      ep_dataout_coeff = 32'h7fffffff;
      #10;
      ep_write = 1'b0;
      #5;
      ep_dataout = 32'h80000051;//divide register address
	  #10;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      trigger = 1'b1;
      ep_dataout = 32'h40000003;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000001;//tx register 1 address
      trigger = 1'b1;
      #10;
      ep_write = 1'b1;
      ep_address = 32'h80000010;
      ep_dataout_coeff = 32'h00003410;
      trigger = 1'b0;
      #10;
      ep_write = 1'b0;
      regTrigger = 1'b1;
      #5;
      regTrigger = 1'b0;
      #25;
      trigger = 1'b1;
      ep_dataout = 32'h40008aa5;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000041;//ctrl register address
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h40003610;
      trigger = 1'b1;
      #10;
      trigger = 1'b0;
      #40;
      ep_dataout = 32'h80000061;//ss register address
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
      #905;
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
		$fclose(FileID);
	end
endmodule

