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
// Clocks:
//    clk_sys  - 200 MHz system clock
//    okClk    - 100.8 MHz host-interface clock provided by okHost
//    fast_clk - 200 MHz (for now) clock for AD7961.v
//
//
// Host Interface registers:
//
// WireIn 0x00
//     31:0 - data/commands to Wishbone interface -> SPI master for ADS7952
//
// WireIn 0x01
//   Wire in to select what slave the SPI data is routed to
//
// WireIn 0x02
//      3:0 - AD796x resets (async)
//      7:4 - AD796x enables (individual)
//      8 - AD796x enables (global)
//
// TriggerIn 0x40
//      0 - used to trigger the Wishbone formatter/state machine, telling the state machine that wi0 is valid
//      1 - used as the master reset for the rest of the design
//      2 - used as the reset for the ADS7952 FIFO
//      3 - reset for "fast" clock pll
//      4 - reset of adc7961_0_fifo
//
// WireOut 0x20
//  31:0 - wire to hold the value of the last word written to the ADS7952 FIFO (to help with debugging/observation)
//
// WireOut 0x20
//      0 - pll locked status signal
//
// TriggerOut 0x60
//      0 - status signal (bit 0) from ADS7952 FIFO telling the host that it is half full (time to read data)
//      1 - status signal telling host that AD7961_0 fifo is completely full
//      2 - status signal telling host that AD7961_0 fifo is half full
//      3 - status signal telling host that AD7961_0 fifo is empty
//
// BTPipeOut - 0xA0
//      31:0 - pipeOut to transfer data in bulk from the ADS7950 FIF2
//
//
//
`default_nettype wire

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
	output wire [6:0] gp,
	
	
	//AD796x (sufficient for only one channel/instantiation of AD7961–more to be added)
    output wire [3:0] adc_en0,          // Enable pins output
    output wire adc_en2,                // Enable pins output
    
    input wire A0_D_P,                // Data In, Positive Pair
    input wire A0_D_N,                    // Data In, Negative Pair
    input wire A0_DCO_P,                  // Echoed Clock In, Positive Pair
    input wire A0_DCO_N,                  // Echoed Clock In, Negative Pair
    
    output wire A0_CNV_P,                 // Convert Out, Positive Pair
    output wire A0_CNV_N,                 // Convert Out, Negative Pair
    output wire A0_CLK_P,                 // Clock Out, Positive Pair
    output wire A0_CLK_N                 // Clock Out, Negative Pair
	
	
	);
	
	
	wire mosi;
	wire miso;
	wire ss;
	wire sclk;
	
	wire mosi_0;
    wire ss_0;
    wire sclk_0;
	
	// connect SPI signals to the general purpose outputs for debug
	assign gp[0] = mosi;
	assign gp[1] = miso;
	assign gp[2] = ss;
	assign gp[3] = sclk;
	
	// SPI signals to AD5453 also connected to gp outputs
	assign gp[4] = mosi_0;
    assign gp[5] = ss_0;
    assign gp[6] = sclk_0;
	 
	// MUX for routing the SPI master  [select mosi default, outputs]
	mux_1to8 mux_sdi (ep01wire[2:0], mosi, 1'b0, {d3_sdi, d2_sdi, d1_sdi, d0_sdi, adcs_sdi});
	// MUX for routing the SPI master  [select ss default, outputs]
	mux_1to8 mux_csb (ep01wire[2:0], ss, 1'b1, {d3_csb, d2_csb, d1_csb, d0_csb, adcs_csb});
	// MUX for routing the SPI master  [select sclk default, outputs]
	mux_1to8 mux_sclk (ep01wire[2:0], sclk, 1'b0, {d3_sclk, d2_sclk, d1_sclk, d0_sclk, adcs_sclk});

	// no mux needed since DACs do not output data
	assign miso = adcs_sdo;
	 
	//System Clock from input differential pair 
	wire clk_sys;
	IBUFGDS osc_clk(
		  .O(clk_sys),
		  .I(sys_clkp),
		  .IB(sys_clkn)
	);
	
	//pll generating "Fast" clock for Ad796x.v
	wire adc_clk;
	//wire adc_pll_rst;
	wire adc_pll_locked;
	
	clk_wiz_0 adc_pll(
	.clk_in1(clk_sys), //in at 200 MHz
	.reset(ep40trig[3]), 
	.clk_out1(adc_clk), //out at 200 MHz
	.locked(adc_pll_locked)
	);
	 
	 //FrontPanel (HostInterface) wires	
	wire okClk;
	wire [112:0] okHE;
	wire [64:0] okEH;
	
	// Adjust size of okEHx to fit the number of outgoing endpoints in your design (n*65-1:0)
	wire [5*65-1:0] okEHx;
	
	//Opal Kelly wires and triggers
	wire [31:0] ep00wire, ep01wire;
	wire [31:0] ep40trig;
	
	//wires to capture output from the HDL regarding last data written to ADS7952 Fifo and when the data is ready
	wire [31:0] lastWrite;
	wire hostinterrupt;
	wire ep_ready;
	
	//output data from the ADS7952 FIFO
	wire [31:0] dout;
	
	//wires to capture output from BTPipeOut (initiating block reads from ADS7952 FIFO)
	wire readFifo;
	wire pipestrobe;
	
	//wire to capture slave select signal from the SPI master
	wire slaveselect;
	assign ss = slaveselect;//slave select signal for ADS7950
	
	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[1]);
	
	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(5)) wireOR (okEH, okEHx);
    
	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));
             
    /* ---------------- Ok Endpoints ----------------*/
				 
	//wire to hold the data/commands from the host – this will be routed to the wishbone formatter/state machine for the ADS7952
	okWireIn wi0 (.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
	
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(8'h01), .ep_dataout(ep01wire));
	
	wire [3:0] adc_reset; //asynchronous adc (AD796x resets)  

    okWireIn wi2 (.okHE(okHE), .ep_addr(8'h02), 
      .ep_dataout({26'b0, adc_en2, adc_en0, adc_reset}));
	
	//trigger to tell the wishbone signal converter/state machine that the input command is valid
	//ep40trig[0] will be used to trigger the Wishbone formatter/state machine, telling the state machine that wi0 is valid
	//ep40trig[1] will be used as the master reset for the rest of the design
	//ep40trig[2] will be used as the reset for the ADS7952 FIFO
	//ep40trig[3] will be used as the reset for the "fast" clock pll
	//ep40trig[4] is the reset for adc7961_0_fifo
	okTriggerIn trigIn40 (.okHE(okHE),
                      .ep_addr(8'h40), .ep_clk(clk_sys), .ep_trigger(ep40trig));
	
	//wire to hold the value of the last word written to the FIFO (to help with debugging/observation)
	okWireOut wo0 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(lastWrite));
	
	//status signal (bit 0) from ADS7952 FIFO telling the host that it is half full (time to read data)
	//bit 1 is status signal telling host that AD7961_0 fifo is completely full
	//bit 2 is status signal telling host that AD7961_0 fifo is half full
	//bit 3 is status signal telling host that AD7961_0 fifo is empty
	okTriggerOut trigOut60 (.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h60), .ep_clk(okClk), 
	                   .ep_trigger({28'b0, adc_fifo_empty[0], adc_fifo_halffull[0], adc_fifo_full[0], hostinterrupt}));
	
	//pipeOut to transfer data in bulk from the ADS7952 FIFO
	okBTPipeOut pipeOutA0 (.okHE(okHE), .okEH(okEHx[2*65 +: 65]),
                       .ep_addr(8'hA0), .ep_datain(dout), .ep_read(readFifo),
                       .ep_blockstrobe(pipestrobe), .ep_ready(ep_ready));  
                       
    //wire to hold general status output to host
    okWireOut wo1 (.okHE(okHE), .okEH(okEHx[3*65 +: 65 ]), .ep_addr(8'h21), .ep_datain({31'b0, adc_pll_locked}));
    
    //pipeOut for data from AD7961_0
    wire [31:0]adc_pipe_ep_datain[0:3];
    okPipeOut pipeOutA1(.okHE(okHE), .okEH(okEHx[4*65 +: 65]), 
              .ep_addr(8'hA1), .ep_read(adc_pipe_ep_read[0]), 
              .ep_datain(adc_pipe_ep_datain[0])); 
	
	//instantiation of lower level "top module" to connect the okHost and OpalKelly Endpoints to the rest of the design
	top_module top (.clk(clk_sys), .fifoclk(okClk), .rst(sys_rst), .ep_dataout(ep00wire), .trigger(ep40trig[0]), 
				 .hostinterrupt(hostinterrupt), .readFifo(readFifo), .rstFifo(ep40trig[2]), .dout(dout), .lastWrite(lastWrite),
				 .ep_ready(ep_ready), .mosi(mosi), .miso(miso), .sclk(sclk), .ss(slaveselect), .slow_pulse(led/*[0]*/), 
				 .ss_0(ss_0), .mosi_0(mosi_0), .sclk_0(sclk_0), .data_rdy_0(pipe_out_write_adc[0]), .adc_val_0(adc_val[0]));
	
	/* ---------------- ADC796x ----------------*/
	wire [3:0] adc_sync_rst;
	reset_synchronizer sync_adc_rst_0 (.clk(clk_sys), .async_rst(adc_reset[0]), .sync_rst(adc_sync_rst[0]));
	
	
	
	wire [3:0]pipe_out_write_adc;
    wire [15:0] adc_val[0:3]; 
    
    wire [3:0] adc_fifo_full;
    wire [3:0] adc_fifo_halffull;
    wire [3:0] adc_fifo_empty;
    
    //wire [9:0] pipe_out_rd_count[0:3];
    //wire [9:0] pipe_out_wr_count[0:3];
    wire [3:0] adc_pipe_ep_read;
	
	
	AD7961 adc7961_0(
    .m_clk_i(clk_sys),                // 200 MHz Clock, used for timing (only for 5 MSPS tracking)
    .fast_clk_i(adc_clk),           // Maximum 260 MHz Clock, used for serial transfer
    .reset_n_i(adc_sync_rst[0]),          // Reset signal, active low
    .en_i({1'b0, adc_en2, 1'b0, adc_en0[0]}),                // Enable pins input  LJK: assigned to en_o within module (all that's done)
    .d_pos_i(A0_D_P),                    // Data In, Positive Pair
    .d_neg_i(A0_D_N),                    // Data In, Negative Pair
    .dco_pos_i(A0_DCO_P),                  // Echoed Clock In, Positive Pair
    .dco_neg_i(A0_DCO_N),                  // Echoed Clock In, Negative Pair
    .en_o(),                              // Enable pins output
    .cnv_pos_o(A0_CNV_P),                  // Convert Out, Positive Pair
    .cnv_neg_o(A0_CNV_N),                  // Convert Out, Negative Pair
    .clk_pos_o(A0_CLK_P),                  // Clock Out, Positive Pair
    .clk_neg_o(A0_CLK_N),                  // Clock Out, Negative Pair
    .data_rd_rdy_o(pipe_out_write_adc[0]), // Signals that new data is available
    .data_o(adc_val[0])
    );
    
    //sychronized AD796x fifo resets
    wire [3:0] adc_fifo_reset;
    reset_synchronizer sync_adc_fifo_rst_0 (.clk(clk_sys), .async_rst(ep40trig[4]), .sync_rst(adc_fifo_reset[0]));
    
    
    fifo_AD796x adc7961_0_fifo (//32 bit wide read and write ports 
      .rst(adc_fifo_reset[0]),
      .wr_clk(clk_sys),
      .rd_clk(okClk),
      .din({adc_val[0]}),         // Bus [15:0] (from ADC)
      .wr_en(pipe_out_write_adc[0]),// from ADC 
      .rd_en(adc_pipe_ep_read[0]),      // from OKHost
      .dout(adc_pipe_ep_datain[0]),     // Bus [31:0] (to OKHost)
      .full(adc_fifo_full[0]),     // status 
      .empty(adc_fifo_empty[0]),   // status 
      .prog_full(adc_fifo_halffull[0]));//status
	
endmodule
