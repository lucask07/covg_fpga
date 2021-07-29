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
//      5 - reset of adc7961_1_fifo
//      6 - reset of adc7961_2_fifo
//      7 - reset of adc7961_3_fifo
//
// WireOut 0x20
//  31:0 - wire to hold the value of the last word written to the ADS7952 FIFO (to help with debugging/observation)
//
// WireOut 0x21
//      0 - pll locked status signal
//
// TriggerOut 0x60
//      0 - status signal (bit 0) from ADS7952 FIFO telling the host that it is half full (time to read data)
//      1 - status signal telling host that AD7961_0 fifo is completely full
//      2 - status signal telling host that AD7961_0 fifo is half full
//      3 - status signal telling host that AD7961_0 fifo is empty
//      4 - status signal telling host that AD7961_1 fifo is completely full
//      5 - status signal telling host that AD7961_1 fifo is half full
//      6 - status signal telling host that AD7961_1 fifo is empty
//      7 - status signal telling host that AD7961_2 fifo is completely full
//      8 - status signal telling host that AD7961_2 fifo is half full
//      9 - status signal telling host that AD7961_2 fifo is empty
//      10 - status signal telling host that AD7961_3 fifo is completely full
//      11 - status signal telling host that AD7961_3 fifo is half full
//      12 - status signal telling host that AD7961_3 fifo is empty
//
// BTPipeOut - 0xA0
//      31:0 - pipeOut to transfer data in bulk from the ADS7952 FIFO
//
// PipeOut - 0xA1
//      31:0 - two 16 bit words of data from the AD7961[0]
// PipeOut - 0xA2
//      31:0 - two 16 bit words of data from the AD7961[1]
// PipeOut - 0xA3
//      31:0 - two 16 bit words of data from the AD7961[2]
// PipeOut - 0xA4
//      31:0 - two 16 bit words of data from the AD7961[3]
//
//
//
`include "ep_defines.v" 
//`default_nettype wire
localparam FADC_NUM = 1;

module top_level_module(
	input wire [4:0] okUH,
	output wire[2:0] okHU,
	inout wire[31:0] okUHU,
	inout wire okAA,
    input wire sys_clkn,
	input wire sys_clkp,
	
	input wire pushreset,//pushbutton reset
	output wire [7:0] led, //LEDs on OpalKelly device; bit 0 will pulse every one second to indicate the FPGA is working

	//AD796x
	/*
    output wire [(FADC_NUM-1):0] adc_en0,          // Enable pins output
    output wire adc_en2,                // Enable pins output
    
    input wire [(FADC_NUM-1):0]adc_d_p,      // Data In, Positive Pair
    input wire [(FADC_NUM-1):0]adc_d_n,      // Data In, Negative Pair
    input wire [(FADC_NUM-1):0]adc_dco_p,    // Echoed Clock In, Positive Pair
    input wire [(FADC_NUM-1):0]adc_dco_n,    // Echoed Clock In, Negative Pair
    
    output wire [(FADC_NUM-1):0]adc_cnv_p,   // Convert Out, Positive Pair
    output wire [(FADC_NUM-1):0]adc_cnv_n,   // Convert Out, Negative Pair
    output wire [(FADC_NUM-1):0]adc_clk_p,   // Clock Out, Positive Pair
    output wire [(FADC_NUM-1):0]adc_clk_n,   // Clock Out, Negative Pair
	*/
	
    // DAC80508
    input wire ds1_sdo,
    output wire ds1_sclk,
    output wire ds1_csb,
    output wire ds1_sdi,

    input wire ds2_sdo,
    output wire ds2_sclk,
    output wire ds2_csb,
    output wire ds2_sdi ,
    
    //ADS8686
    output wire ss_ads,
    output wire sclk_ads,
    output wire mosi_ads,
    input wire miso_ads,
    output wire convst
    
	);
		    
    /* ---------------- DAC80508 ----------------*/
    // Input Values to Wishbones
    wire [31:0] dac_val_0;
    wire [31:0] dac_val_1;
    
    wire [(FADC_NUM-1):0] adc_reset; //asynchronous adc (AD796x resets)  

	//System Clock from input differential pair 
	wire clk_sys;
	IBUFGDS osc_clk(
		  .O(clk_sys),
		  .I(sys_clkp),
		  .IB(sys_clkn)
	);
	
	//pll generating "Fast" clock for Ad796x.v
	wire adc_clk;
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
	//TODO: better way to keep track of these
	wire [12*65-1:0] okEHx;
	
	//Opal Kelly wires and triggers
	wire [31:0] ep00wire, ep01wire, ep40trig;
	
	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[1]);
	
	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(11)) wireOR (okEH, okEHx);
    
	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));
             
    /* ---------------- Ok Endpoints ----------------*/
				 
	//wire to hold the data/commands from the host this will be routed to the wishbone formatter/state machine for the ADS7952
	okWireIn wi0 (.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(8'h01), .ep_dataout(ep01wire));
    okWireIn wi2 (.okHE(okHE), .ep_addr(8'h02), 
      .ep_dataout({26'b0, adc_en2, adc_en0, adc_reset}));

    okWireIn wi_dac_0 (.okHE(okHE), .ep_addr(8'h03), .ep_dataout(dac_val_0));
    okWireIn wi_dac_1 (.okHE(okHE), .ep_addr(8'h04), .ep_dataout(dac_val_1));
	
	//trigger to tell the wishbone signal converter/state machine that the input command is valid
	//ep40trig[0] will be used to trigger the Wishbone formatter/state machine, telling the state machine that wi0 is valid
	//ep40trig[1] will be used as the master reset for the rest of the design
	//ep40trig[2] will be used as the reset for the ADS7952 FIFO
	//ep40trig[3] will be used as the reset for the "fast" clock pll
	//ep40trig[4] is the reset for adc7961_0_fifo
	//ep40trig[5] is the reset for adc7961_1_fifo
	//ep40trig[6] is the reset for adc7961_2_fifo
	//ep40trig[7] is the reset for adc7961_3_fifo
	//ep40trig[8] will be used to trigger the Wishbone formatter/state machine for dac_0, telling the state machine that wi0 is valid
	//ep40trig[9] will be used to trigger the Wishbone formatter/state machine for dac_1, telling the state machine that wi0 is valid
	//ep40trig[10] reset the programmable clock divider for the ADS8686 spi 
	//ep40trig[11] trigger the ADS8686 SPI wishbone when in host driven mode 
	
	okTriggerIn trigIn40 (.okHE(okHE),
                      .ep_addr(8'h40), .ep_clk(clk_sys), .ep_trigger(ep40trig));
    
    wire [31:0]ep41trig;
    okTriggerIn trigIn41 (.okHE(okHE),
                                    .ep_addr(8'h41), .ep_clk(clk_sys_fast), .ep_trigger(ep41trig));
	//wire to hold the value of the last word written to the FIFO (to help with debugging/observation)
	// okWireOut wo0 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(lastWrite));

    //wire to hold general status output to host
    okWireOut wo1 (.okHE(okHE), .okEH(okEHx[3*65 +: 65 ]), .ep_addr(8'h21), .ep_datain({31'b0, adc_pll_locked}));
    okWireOut wo_dac_0 (.okHE(okHE), .okEH(okEHx[9*65 +: 65 ]), .ep_addr(8'h22), .ep_datain(dac_out_0));
    okWireOut wo_dac_1 (.okHE(okHE), .okEH(okEHx[10*65 +: 65 ]), .ep_addr(8'h23), .ep_datain(dac_out_1));
	//status signal (bit 0) from ADS7952 FIFO telling the host that it is half full (time to read data)
	//bit 1 is status signal telling host that AD7961_0 fifo is completely full
	//bit 2 is status signal telling host that AD7961_0 fifo is half full
	//bit 3 is status signal telling host that AD7961_0 fifo is empty
	//bit 4 is status signal telling host that AD7961_1 fifo is completely full
    //bit 5 is status signal telling host that AD7961_1 fifo is half full
    //bit 6 is status signal telling host that AD7961_1 fifo is empty
    //bit 7 is status signal telling host that AD7961_2 fifo is completely full
    //bit 8 is status signal telling host that AD7961_2 fifo is half full
    //bit 9 is status signal telling host that AD7961_2 fifo is empty
    //bit 10 is status signal telling host that AD7961_3 fifo is completely full
    //bit 11 is status signal telling host that AD7961_3 fifo is half full
    //bit 12 is status signal telling host that AD7961_3 fifo is empty
    //bit 13 is status signal telling host that AD7S8686 fifo is completely full
    //bit 14 is status signal telling host that AD7S8686 fifo is half full
    //bit 15 is status signal telling host that AD7S8686 fifo is empty    
	okTriggerOut trigOut60 (.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h60), .ep_clk(okClk), 
                           .ep_trigger({16'b0, 
                           ads_fifo_empty, ads_fifo_halffull, ads_fifo_full,
                           adc_fifo_empty[3], adc_fifo_halffull[3], adc_fifo_full[3],
                           adc_fifo_empty[2], adc_fifo_halffull[2], adc_fifo_full[2],
                           adc_fifo_empty[1], adc_fifo_halffull[1], adc_fifo_full[1],
                           adc_fifo_empty[0], adc_fifo_halffull[0], adc_fifo_full[0], hostinterrupt}));
       //register bridge for writing filter coefficients to BRAM and to the spi_controller 
       wire regWrite;
       wire regRead;
       wire [31:0] regAddress;
       wire [31:0] regDataOut;
       wire [31:0] regDataIn; // Was reg, gave error in Vivado synthesis
       
       okRegisterBridge regBridge (
           .okHE(okHE),
           .okEH(okEHx[8*65 +: 65]),
           .ep_write(regWrite),
           .ep_read(regRead),
           .ep_address(regAddress),
           .ep_dataout(regDataOut),
           .ep_datain(regDataIn)
       );
	
	// --------------------- for the ADS8686 --------------------------
    okWireIn wi_ads (.okHE(okHE), .ep_addr(ADS_WIRE_IN_ADDR), .ep_dataout(ads_wire_in));
    wire [31:0] ads_wire_in;
    wire [31:0] ads_data_out;
    wire ads_data_valid;
    spi_controller uut(
                       .clk(clk),
                       .reset(sys_rst),
                       .divider_reset(ep40trig[10]), //TODO: to trigger 
                       .dac_val(ads_wire_in), 
                       .dac_convert_trigger(ep40trig[11]), // trigger wishbone transfers 
                       .host_fpgab(ep01wire[0]), // if 1 host driven commands; if 0 
                       // OKRegister bridge inputs 
                       .okClk(okClk),
                       .addr(regAddress),
                       .data_in(regDataOut),
                       .write_in(regWrite),
                       // outputs 
                       .dac_out(ads_data_out), // connect to FIFO
                       .data_valid(ads_data_valid), 
                       .ss(ss_ads),
                       .sclk(sclk_ads),
                       .mosi(mosi_ads),
                       .miso(miso_ads),
                       .convst_out(convst)
                       );
                                     	
   fifo_AD796x ads8686_fifo (//32 bit wide read and 16 bit wide write ports 
     .rst(ads_fifo_reset),
     .wr_clk(clk_sys),
     .rd_clk(okClk),
     .din(ads_data_out),         // Bus [15:0] (from ADC)
     .wr_en(ads_data_valid),// from ADC 
     .rd_en(ads_pipe_read),      // from OKHost
     .dout(ads_fifo_data),     // Bus [31:0] (to OKHost)
     .full(ads_fifo_full),     // status 
     .empty(ads_fifo_empty),   // status 
     .prog_full(ads_fifo_halffull));//status
    	
    wire [31:0] ads_fifo_data;
    wire ads_pipe_read;
    //pipeOut to transfer data in bulk from the ADS8686 FIFO
   okPipeOut pipeOutADS86 (.okHE(okHE), .okEH(okEHx[2*65 +: 65]),
                      .ep_addr(ADS_POUT_OFFSET),  .ep_read(ads_pipe_read),
                      .ep_datain(ads_fifo_data));  

   reg [31:0] ads_last_read;  
   always @(posedge clk_sys) begin 
        if (sys_rst) begin
             ads_last_read <=32'h0;
        end
        else if (ads_pipe_read) begin
            ads_last_read <= ads_data_out;
        end
    end
    okWireOut wo_ads (.okHE(okHE), .okEH(okEHx[11*65 +: 65 ]), .ep_addr(ADS_WIRE_OUT_ADDR), .ep_datain(ads_last_read));

    // ------------ end ADS8686 -----------------------------------
    	
    	
	//instantiation of lower level "top module" to connect the okHost and OpalKelly Endpoints to the rest of the design
	top_module top (.clk(clk_sys), .fifoclk(okClk), .rst(sys_rst), .ep_dataout(ep00wire), .trigger(ep40trig[0]), 
				 .hostinterrupt(hostinterrupt), .readFifo(readFifo), .rstFifo(ep40trig[2]), .dout(dout), .lastWrite(lastWrite),
				 .ep_ready(ep_ready), .mosi(mosi), .miso(miso), .sclk(sclk), .ss(slaveselect), .slow_pulse(led[0]), 
				 .ss_0(ss_0), .mosi_0(mosi_0), .sclk_0(sclk_0), .data_rdy_0(pipe_out_write_adc[0]), .adc_val_0(adc_val[0]),
				 .ss_1(ss_1), .mosi_1(mosi_1), .sclk_1(sclk_1), .data_rdy_1(pipe_out_write_adc[1]), .adc_val_1(adc_val[1]),
				 .ss_2(ss_2), .mosi_2(mosi_2), .sclk_2(sclk_2), .data_rdy_2(pipe_out_write_adc[2]), .adc_val_2(adc_val[2]),
				 .ss_3(ss_3), .mosi_3(mosi_3), .sclk_3(sclk_3), .data_rdy_3(pipe_out_write_adc[3]), .adc_val_3(adc_val[3]),
                 .dac_val_0(dac_val_0), .dac_convert_trigger_0(ep40trig[8]), .dac_out_0(dac_out_0), .dac_ss_0(ds1_csb), .dac_sclk_0(ds1_sclk), .dac_mosi_0(ds1_sdi), .dac_miso_0(sd1_sdi),
                 .dac_val_1(dac_val_1), .dac_convert_trigger_1(ep40trig[9]), .dac_out_1(dac_out_1), .dac_ss_1(ds2_csb), .dac_sclk_1(ds2_sclk), .dac_mosi_1(ds2_sdo), .dac_miso_1(ds2_sdi), 
				 .ep_read(regRead), .ep_write(regWrite), .ep_address(regAddress), .ep_dataout_coeff(regDataOut), .ep_datain(regDataIn));
	
	/* ---------------- ADC796x ----------------*/
	wire [(FADC_NUM-1):0] adc_sync_rst;
    wire [31:0]adc_pipe_ep_datain[0:(FADC_NUM-1)];
	wire [(FADC_NUM-1):0]pipe_out_write_adc;
    wire [15:0] adc_val[0:(FADC_NUM-1)]; 
    wire [(FADC_NUM-1):0] adc_fifo_full;
    wire [(FADC_NUM-1):0] adc_fifo_halffull;
    wire [(FADC_NUM-1):0] adc_fifo_empty;
    wire [(FADC_NUM-1):0] adc_pipe_ep_read;
    wire [(FADC_NUM-1):0] adc_fifo_reset;
	/*
	genvar i;
    generate
    for (i=0; i<=(FADC_NUM-1); i=i+1) begin : ad7960_gen
	
        AD7961 adc7961(
        .m_clk_i(clk_sys),                // 200 MHz Clock, used for timing (only for 5 MSPS tracking)
        .fast_clk_i(adc_clk),           // Maximum 260 MHz Clock, used for serial transfer
        .reset_n_i(adc_sync_rst[i]),          // Reset signal, active low
        .en_i(),                // Enable pins input  LJK: assigned to en_o within module (serve no purpose)
        .d_pos_i(adc_d_p[i]),                    // Data Ii, Positive Pair
        .d_neg_i(adc_d_n[i]),                    // Data In, Negative Pair
        .dco_pos_i(adc_dco_p[i]),                  // Echoed Clock In, Positive Pair
        .dco_neg_i(adc_dco_n[i]),                  // Echoed Clock In, Negative Pair
        .en_o(),                              // Enable pins output
        .cnv_pos_o(adc_cnv_p[i]),                  // Convert Out, Positive Pair
        .cnv_neg_o(adc_cnv_n[i]),                  // Convert Out, Negative Pair
        .clk_pos_o(adc_clk_p[i]),                  // Clock Out, Positive Pair
        .clk_neg_o(adc_clk_n[i]),                  // Clock Out, Negative Pair
        .data_rd_rdy_o(pipe_out_write_adc[i]), // Signals that new data is available
        .data_o(adc_val[i])
        );
        
        //AD796x reset synchronizer 
        reset_sync_low sync_adc_rst_0 (.clk(clk_sys), .async_rst(adc_reset[i]), .sync_rst(adc_sync_rst[i]));
        //sychronized AD796x fifo resets
        reset_synchronizer sync_adc_fifo_rst_0 (.clk(clk_sys), .async_rst(ep40trig[4 + i]), .sync_rst(adc_fifo_reset[i]));
            
        fifo_AD796x adc7961_fifo (//32 bit wide read and 16 bit wide write ports 
          .rst(adc_fifo_reset[i]),
          .wr_clk(clk_sys),
          .rd_clk(okClk),
          .din({adc_val[i]}),         // Bus [15:0] (from ADC)
          .wr_en(pipe_out_write_adc[i]),// from ADC 
          .rd_en(adc_pipe_ep_read[i]),      // from OKHost
          .dout(adc_pipe_ep_datain[i]),     // Bus [31:0] (to OKHost)
          .full(adc_fifo_full[i]),     // status 
          .empty(adc_fifo_empty[i]),   // status 
          .prog_full(adc_fifo_halffull[i]));//status
          
          //pipeOut for data from AD7961
          okPipeOut pipeOutA1(.okHE(okHE), .okEH(okEHx[(4+i)*65 +: 65]), 
                    .ep_addr(AD796x_POUT_OFFSET + i), .ep_read(adc_pipe_ep_read[i]), 
                    .ep_datain(adc_pipe_ep_datain[i]));
     end
     endgenerate 
     */	
endmodule
