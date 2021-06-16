`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
// 
// Create Date:    18:09:30 01/05/2021 
// Design Name: 
// Module Name:    top_level_module 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module top_level_module(
	input wire [4:0] okUH,
	output wire[2:0] okHU,
	inout wire[31:0] okUHU,
	inout wire okAA,
   input wire sys_clkn,
	input wire sys_clkp,
	
	/*
	output wire mosi,/////////
	input wire miso, 
	output wire ss,
	output wire sclk,/////////
	*/ 
	
	// ADS7952
	output wire adcs_sdi,/////////
	input wire adcs_sdo,  /*these spi signals are for the ADS7950*/
	output wire adcs_sclk,
	output wire adcs_csb,/////////
	
	//Fast DAC AD5453
	output wire d0_sdi,
	output wire d0_csb,
	output wire d0_sclk,

	output wire d1_sdi,
	output wire d1_csb,
	output wire d1_sclk,

	output wire d2_sdi,
	output wire d2_csb,
	output wire d2_sclk,

	output wire d3_sdi,
	output wire d3_csb,
	output wire d3_sclk,	
	
	input wire pushreset,//pushbutton reset
	output wire [7:0] led, //LEDs on OpalKelly device; bit 0 will pulse every one second to indicate the FPGA is working
	
	// output wire [3:0] gp
	output wire gp_mosi,
	input wire gp_miso,
	output wire gp_ss,
	output wire gp_sclk
	);
	
	wire mosi;
	wire miso;
	wire ss;
	wire sclk;
	
	// connect SPI signals to the general purpose outputs for debug
	//assign gp[0] = mosi;
	assign gp_mosi = mosi; 
	//assign gp[1] = miso; // gp[1] is input for ADS8686 bring-up. do not echo
	
	//assign gp[2] = ss;
	assign gp_ss = ss;
	
	//assign gp[3] = sclk;
	assign gp_sclk = sclk;	
	
	// MUX for routing the SPI master  [select mosi default, outputs]
	mux_1to8 mux_sdi (ep01wire[2:0], mosi, 1'b0, {d3_sdi, d2_sdi, d1_sdi, d0_sdi, adcs_sdi});
	// MUX for routing the SPI master  [select ss default, outputs]
	mux_1to8 mux_csb (ep01wire[2:0], ss, 1'b1, {d3_csb, d2_csb, d1_csb, d0_csb, adcs_csb});
	// MUX for routing the SPI master  [select sclk default, outputs]
	mux_1to8 mux_sclk (ep01wire[2:0], sclk, 1'b0, {d3_sclk, d2_sclk, d1_sclk, d0_sclk, adcs_sclk});

	// no mux needed since DACs do not output data
	
	// LJK -- ADS8686 bringup ---------
	// assign miso = adcs_sdo;
	assign miso = gp_miso;
	 
	//System Clock from input differential pair 
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
	
	//Opal Kelly wires and triggers
	wire [31:0] ep00wire, ep01wire;
	wire [31:0] ep40trig;
	
	//wires to capture output from the user HDL
	wire [31:0] lastWrite;
	wire hostinterrupt;
	wire ep_ready;
	
	//output data from the FIFO via top user HDL module
	wire [31:0] dout;
	
	//wires to capture output from BTPipeOut (initiating block reads from FIFO)
	wire readFifo;
	wire pipestrobe;
	
	//wire to capture slave select signal from the SPI master
	wire slaveselect;
	assign ss = slaveselect;//slave select signal for ADS7950
	
	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[1]);
	
	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(3)) wireOR (okEH, okEHx);

	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));
				 
	//wire to hold the data/commands from the host – this will be routed to the wishbone formatter/state machine
	okWireIn wi0 (.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
	
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(8'h01), .ep_dataout(ep01wire));

	
	//trigger to tell the wishbone signal converter/state machine that the input command is valid
	//ep40trig[0] will be used to trigger the Wishbone formatter/state machine, telling the state machine that wi0 is valid
	//ep40trig[1] will be used as the master reset for the rest of the design
	//ep40trig[2] will be used as the reset for the FIFO
	okTriggerIn trigIn40 (.okHE(okHE),
                      .ep_addr(8'h40), .ep_clk(clk_sys), .ep_trigger(ep40trig));
	
	//wire to hold the value of the last word written to the FIFO (to help with debugging/observation)
	okWireOut wo0 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(lastWrite));
	
	//status signal (bit 0) from FIFO telling the host that it is half full (time to read data)
	okTriggerOut trigOut60 (.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h60), .ep_clk(okClk), .ep_trigger({31'b0, hostinterrupt}));
	
	//pipeOut to transfer data in bulk from the FIFO
	okBTPipeOut pipeOutA0 (.okHE(okHE), .okEH(okEHx[2*65 +: 65]),
                       .ep_addr(8'hA0), .ep_datain(dout), .ep_read(readFifo),
                       .ep_blockstrobe(pipestrobe), .ep_ready(ep_ready));
	
	//instantiation of lower level "top module" to connect the okHost and OpalKelly Endpoints to the rest of the design
	top_module top (.clk(clk_sys), .fifoclk(okClk), .rst(sys_rst), .ep_dataout(ep00wire), .trigger(ep40trig[0]), 
				 .hostinterrupt(hostinterrupt), .readFifo(readFifo), .rstFifo(ep40trig[2]), .dout(dout), .lastWrite(lastWrite),
				 .ep_ready(ep_ready), .mosi(mosi), .miso(miso), .sclk(sclk), .ss(slaveselect), .slow_pulse(led[0]));
	

endmodule
