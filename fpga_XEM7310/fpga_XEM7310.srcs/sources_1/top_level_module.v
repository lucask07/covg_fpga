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

`default_nettype wire // depending on compile order this may be needed. OpalKelly says its not a problem.

`include "ep_defines.v" 
localparam FADC_NUM = 4;
localparam DAC80508_NUM = 2;
localparam AD5453_NUM = 6;
localparam I2C_DCARDS = 4;

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
    output wire [(FADC_NUM-1):0] a_en0_hv,          // Enable pins output (one for each ADC)
    output wire [2:0]a_en_hv,                       // Enable pins output (global); EN1, EN2, EN3
    
    input wire [(FADC_NUM-1):0]a_d_p,      // Data In, Positive Pair
    input wire [(FADC_NUM-1):0]a_d_n,      // Data In, Negative Pair
    input wire [(FADC_NUM-1):0]a_dco_p,    // Echoed Clock In, Positive Pair
    input wire [(FADC_NUM-1):0]a_dco_n,    // Echoed Clock In, Negative Pair
    
    output wire [(FADC_NUM-1):0]a_cnv_p,   // Convert Out, Positive Pair
    output wire [(FADC_NUM-1):0]a_cnv_n,   // Convert Out, Negative Pair
    output wire [(FADC_NUM-1):0]a_clk_p,   // Clock Out, Positive Pair
    output wire [(FADC_NUM-1):0]a_clk_n,   // Clock Out, Negative Pair
	
    // DAC80508 (ds for DAC slow)
    input wire  [(DAC80508_NUM-1):0]ds_sdo,    // DAC85058 input data is not necessary 
    output wire [(DAC80508_NUM-1):0]ds_sclk,
    output wire [(DAC80508_NUM-1):0]ds_csb,
    output wire [(DAC80508_NUM-1):0]ds_sdi,
    
    //AD5453 (SPI)
    output wire [(AD5453_NUM-1):0]d_sclk,
    output wire [(AD5453_NUM-1):0]d_csb,
    output wire [(AD5453_NUM-1):0]d_sdi,   
    
    //ADS8686
    output wire ads_csb,
    output wire ads_sclk,
    output wire ads_mosi,
    input  wire ads_sdoa,
    input  wire ads_sdob, // TODO: not yet connected 
    output wire ads_convst,
    output wire ads_resetb, //TODO: add to wireout (with ADC enables, DN/UP, etc.) 
    
    // GPIO (6+6+4+4+4 = 24 total signals)
    output wire [5:0]dn, // TODO: constraint generator prints [4:0]dn 
    output wire [5:0]up,
    output wire [3:0]gp_lvds_n, //TODO: need LVDS output driver
    output wire [3:0]gp_lvds_p,
    output wire [3:0]gpio, 

    //power supply regulatoor enable signals (5 total signals)
    output wire en_15v,
    output wire en_1v8,
    output wire en_3v3,
    output wire en_5v,
    output wire en_n15v,

    output wire [1:0]en_ipump, // (2 total signals)
    
    //DDR3 
    inout  wire [31:0]  ddr3_dq,
    output wire [14:0]  ddr3_addr,
    output wire [2 :0]  ddr3_ba,
    output wire [0 :0]  ddr3_ck_p,
    output wire [0 :0]  ddr3_ck_n,
    output wire [0 :0]  ddr3_cke,
    output wire         ddr3_cas_n,
    output wire         ddr3_ras_n,
    output wire         ddr3_we_n,
    output wire [0 :0]  ddr3_odt,
    output wire [3 :0]  ddr3_dm,
    inout  wire [3 :0]  ddr3_dqs_p,
    inout  wire [3 :0]  ddr3_dqs_n,
    output wire         ddr3_reset_n
    
	);
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
	.reset(ep40trig[`TI40_PLL_RST]), 
	.clk_out1(adc_clk), //out at 200 MHz
	.locked(adc_pll_locked)
	); 
	 //FrontPanel (HostInterface) wires	
	wire okClk;
	wire [112:0] okHE;
	wire [64:0] okEH;
	// Adjust size of okEHx to fit the number of outgoing endpoints in your design (n*65-1:0)
	//TODO: better way to keep track of these
	wire [16*65-1:0] okEHx;
	
	//Opal Kelly wires and triggers
	wire [31:0] ep00wire, ep01wire, ep02wire, ep40trig, ep41trig;
	
	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[`TI40_RST]); // TODO: TI40_RST is not found
	
	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(13)) wireOR (okEH, okEHx); //TODO
    
	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));
             
    /* ---------------- Ok Endpoints ----------------*/	
	//wire to hold the data/commands from the host this will be routed to the wishbone formatter/state machine for the ADS7952
	okWireIn wi0 (.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(8'h01), .ep_dataout(ep01wire));
    
    okWireIn wi2 (.okHE(okHE), .ep_addr(8'h02), 
      .ep_dataout(ep02wire));
      
     assign a_en0_hv = ep02wire[(`WI02_A_EN0+`WI02_A_EN0_LEN - 1):`WI02_A_EN0]; //1 for each channel
     assign a_en_hv = ep02wire[(`WI02_A_EN+`WI02_A_EN_LEN - 1):`WI02_A_EN];    // global

     wire [9:0] en_period;
     assign en_period = ep02wire[(`WI02_EN_PERIOD_LEN+`WI02_EN_PERIOD - 1):`WI02_EN_PERIOD];
      
     //power supply regulatoor enable signals (5 total signals)
     assign en_15v = ep02wire[`WI02_15V_EN];
     assign en_1v8 = ep02wire[`WI02_1V8_EN];
     assign en_3v3 = ep02wire[`WI02_3V3_EN];
     assign en_5v = ep02wire[`WI02_5V_EN];
     assign en_n15v = ep02wire[`WI02_N15V_EN];

     assign en_ipump = ep02wire[(`WI02_IPUMP_EN + `WI02_IPUMP_EN_LEN - 1):`WI02_IPUMP_EN]; // (2 total signals) 
      
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
	// ---------------------- END OpalKelly EndPoints (global) --------
    	
	// --------------------- Begin ADS8686 --------------------------
    okWireIn wi_ads (.okHE(okHE), .ep_addr(`ADS_WIRE_IN_ADDR), .ep_dataout(ads_wire_in));
    wire [31:0] ads_wire_in;
    wire [31:0] ads_data_out;
    wire ads_data_valid;
    spi_controller uut(
                       .clk(clk_sys),
                       .reset(sys_rst),
                       .divider_reset(ep40trig[`TI40_ADS_CLK_DIV]), 
                       .dac_val(ads_wire_in), 
                       .dac_convert_trigger(ep40trig[`TI40_ADS_WB]), // trigger wishbone transfers 
                       .host_fpgab(ep01wire[0]), // if 1 host driven commands; if 0 
                       // OKRegister bridge inputs 
                       .okClk(okClk),
                       .addr(regAddress),
                       .data_in(regDataOut),
                       .write_in(regWrite),
                       // outputs 
                       .dac_out(ads_data_out), // connect to FIFO
                       .data_valid(ads_data_valid), 
                       .ss(ads_csb),
                       .sclk(ads_sclk),
                       .mosi(ads_mosi),
                       .miso(ads_sdoa), //TODO: need to connect SDOB
                       .convst_out(ads_convst)
                       );
                                     	
   fifo_AD796x ads8686_fifo (//32 bit wide read and 16 bit wide write ports 
     .rst(ep40trig[`TI40_ADS8686_FIFO_RST]),
     .wr_clk(clk_sys),
     .rd_clk(okClk),
     .din(ads_data_out),         // Bus [15:0] (from ADC)
     .wr_en(ads_data_valid),    // from ADC 
     .rd_en(ads_pipe_read),      // from OKHost
     .dout(ads_fifo_data),     // Bus [31:0] (to OKHost)
     .full(ads_fifo_full),     // status 
     .empty(ads_fifo_empty),   // status 
     .prog_full(ads_fifo_halffull));//status
    	
    wire [31:0] ads_fifo_data;
    wire ads_pipe_read;
    //pipeOut to transfer data in bulk from the ADS8686 FIFO
   okPipeOut pipeOutADS86 (.okHE(okHE), .okEH(okEHx[2*65 +: 65]),
                      .ep_addr(`ADS_POUT_OFFSET),  .ep_read(ads_pipe_read),
                      .ep_datain(ads_fifo_data));  

   reg [31:0] ads_last_read;  
   always @(posedge clk_sys) begin 
        if (sys_rst) begin
             ads_last_read <=32'h0;
        end
        else if (ads_data_valid) begin  // 
            ads_last_read <= ads_data_out;
        end
    end
    okWireOut wo_ads (.okHE(okHE), .okEH(okEHx[11*65 +: 65 ]), .ep_addr(`ADS_WIRE_OUT_ADDR), .ep_datain(ads_last_read));

    // ------------ end ADS8686 -----------------------------------
	
	/* ---------------- AD796x 5 MSPS ADC  ----------------*/
    wire [(FADC_NUM-1):0] adc_reset; //asynchronous adc (AD796x resets)  

	wire [(FADC_NUM-1):0] adc_sync_rst;
    wire [31:0]adc_pipe_ep_datain[0:(FADC_NUM-1)];
	wire [(FADC_NUM-1):0]write_en_adc_o;
    wire [15:0] adc_val[0:(FADC_NUM-1)]; 
    wire [(FADC_NUM-1):0] adc_fifo_full;
    wire [(FADC_NUM-1):0] adc_fifo_halffull;
    wire [(FADC_NUM-1):0] adc_fifo_empty;
    wire [(FADC_NUM-1):0] adc_pipe_ep_read;
    wire [(FADC_NUM-1):0] adc_fifo_reset;

	genvar i;
    generate
    for (i=0; i<=(FADC_NUM-1); i=i+1) begin : ad7960_gen
        AD7961 adc7961(
        .m_clk_i(clk_sys),                // 200 MHz Clock, used for timing (only for 5 MSPS tracking)
        .fast_clk_i(adc_clk),           // Maximum 260 MHz Clock, used for serial transfer
        .reset_n_i(~ep40trig[`TI40_ADC_RST+i]),          // Reset signal, active low
        .en_i(),                // Enable pins input  LJK: assigned to en_o within module (serve no purpose)
        .d_pos_i(a_d_p[i]),                    // Data Ii, Positive Pair
        .d_neg_i(a_d_n[i]),                    // Data In, Negative Pair
        .dco_pos_i(a_dco_p[i]),                  // Echoed Clock In, Positive Pair
        .dco_neg_i(a_dco_n[i]),                  // Echoed Clock In, Negative Pair
        .en_o(),                              // Enable pins output
        .cnv_pos_o(a_cnv_p[i]),                  // Convert Out, Positive Pair
        .cnv_neg_o(a_cnv_n[i]),                  // Convert Out, Negative Pair
        .clk_pos_o(a_clk_p[i]),                  // Clock Out, Positive Pair
        .clk_neg_o(a_clk_n[i]),                  // Clock Out, Negative Pair
        .data_rd_rdy_o(write_en_adc_o[i]), // Signals that new data is available
        .data_o(adc_val[i])
        );
        
        //AD796x reset synchronizer 
        reset_sync_low sync_adc_rst_0 (.clk(clk_sys), .async_rst(adc_reset[i]), .sync_rst(adc_sync_rst[i]));

        fifo_AD796x adc7961_fifo (//32 bit wide read and 16 bit wide write ports 
          .rst(ep40trig[`TI40_ADC_FIFO_RST + i]),
          .wr_clk(clk_sys),
          .rd_clk(okClk),
          .din({adc_val[i]}),         // Bus [15:0] (from ADC)
          .wr_en(write_en_adc_o[i]),// from ADC 
          .rd_en(adc_pipe_ep_read[i]),      // from OKHost
          .dout(adc_pipe_ep_datain[i]),     // Bus [31:0] (to OKHost)
          .full(adc_fifo_full[i]),     // status 
          .empty(adc_fifo_empty[i]),   // status 
          .prog_full(adc_fifo_halffull[i]));//status
          
          //pipeOut for data from AD7961
          okPipeOut pipeOutA1(.okHE(okHE), .okEH(okEHx[(4+i)*65 +: 65]), 
                    .ep_addr(`AD796x_POUT_OFFSET + i), .ep_read(adc_pipe_ep_read[i]), 
                    .ep_datain(adc_pipe_ep_datain[i]));
     end
     endgenerate 

    /*---------------- DAC80508 -------------------*/
    wire [31:0]dac_wirein_data[(DAC80508_NUM-1):0];
    genvar j;
    generate
    for (j=0; j<=(DAC80508_NUM-1); j=j+1) begin : dac80508_gen     
        spi_controller dac_0 (
          .clk(clk), .reset(sys_rst), .dac_val(dac_wirein_data[j]), .dac_convert_trigger(ep40trig[`TI40_DAC805_WB+j]), .dac_out(dac_out_0),
          .ss(dac_ss_0), .sclk(dac_sclk_0), .mosi(dac_mosi_0), .miso(dac_miso_0)
        );
        okWireIn wi_dac_0 (.okHE(okHE), .ep_addr(`DS_WIRE_IN_OFFSET + j), .ep_dataout(dac_wirein_data[j]));
        //TODO (if needed) add WireOut to transfer data out
    end
    endgenerate 
    /*---------------- END DAC80508 -------------------*/ 
    
   //General purpose clock divide - currently used as "helper" clocking module for reading form DDR3
   wire dataready;
   //wire to capture clock enable period multiplier, and the clock enable itself
   wire clk_en;
   assign clk_en = dataready;
    general_clock_divide MIG_DDR_FIFO_RD_EN(
        .clk(clk),
        .rst(ddr3_rst),
        .en_period(en_period),
        .clk_en(dataready)
    );
    
    /* --------------- DDR3 ---------------------------*/
     ////////////////////////////*DDR3 INTERFACE INSTANTIATIONS*//////////////////////////////////////////////
     // OK RAMTest Parameters
     localparam BLOCK_SIZE = 128; // 512 bytes / 4 bytes per word, 
     localparam FIFO_SIZE = 1023; // note that Xilinx does not allow use of the full 1024 words
     localparam BUFFER_HEADROOM = 20; // headroom for the FIFO count to account for latency
     
     // Capability bitfield, used to indicate features supported by this bitfile:
     // [0] - Supports passing calibration status through FrontPanel
     localparam CAPABILITY = 16'h0001;
     
     wire          init_calib_complete;
     reg           rst_sys_ddr;
     
     wire [29 :0]  app_addr;
     wire [2  :0]  app_cmd;
     wire          app_en;
     wire          app_rdy;
     wire [255:0]  app_rd_data;
     wire          app_rd_data_end;
     wire          app_rd_data_valid;
     wire [255:0]  app_wdf_data;
     wire                       app_wdf_end;
     wire [31 :0]  app_wdf_mask;
     wire          app_wdf_rdy;
     wire          app_wdf_wren;
     
     wire          clk_ddr_ui;
     wire          rst_ddr_ui;
     
     wire [31:0]  ep03wire;
     
     wire         pipe_in_read;
     wire [255:0] pipe_in_data;
     wire [6:0]   pipe_in_rd_count;
     wire [9:0]   pipe_in_wr_count;
     wire         pipe_in_valid;
     wire         pipe_in_full;
     wire         pipe_in_empty;
     reg          pipe_in_ready;
     
     wire         pipe_out_write;
     wire [255:0] pipe_out_data;
     wire [9:0]   pipe_out_rd_count;
     wire [6:0]   pipe_out_wr_count;
     wire         pipe_out_full;
     wire         pipe_out_empty;
     reg          pipe_out_ready;
     
     // Pipe Fifos
     wire         pi0_ep_write;
     wire         po0_ep_read;
     wire [31:0]  pi0_ep_dataout;     
     wire [31:0] INDEX;
     wire          ddr3_rst;// MIG/DDR3 synchronous reset
     wire [31:0]  po0_ep_datain;// MIG/DDR3 data out
     wire rd_en_0;
     
     reset_synchronizer u_MIG_sync_rst(
     .clk(clk_sys),
     .async_rst(ep03wire[2]),
     .sync_rst(ddr3_rst)
     );
     
     //MIG Infrastructure Reset
     reg [31:0] rst_cnt;
     initial rst_cnt = 32'b0;
     always @(posedge okClk) begin
         if(rst_cnt < 32'h0800_0000) begin
             rst_cnt <= rst_cnt + 1;
             rst_sys_ddr <= 1'b1;
         end
         else begin
             rst_sys_ddr <= 1'b0;
         end
     end
     
     // MIG User Interface instantiation
     ddr3_256_32 u_ddr3_256_32 (
         // Memory interface ports
         .ddr3_addr                      (ddr3_addr),
         .ddr3_ba                        (ddr3_ba),
         .ddr3_cas_n                     (ddr3_cas_n),
         .ddr3_ck_n                      (ddr3_ck_n),
         .ddr3_ck_p                      (ddr3_ck_p),
         .ddr3_cke                       (ddr3_cke),
         .ddr3_ras_n                     (ddr3_ras_n),
         .ddr3_reset_n                   (ddr3_reset_n),
         .ddr3_we_n                      (ddr3_we_n),
         .ddr3_dq                        (ddr3_dq),
         .ddr3_dqs_n                     (ddr3_dqs_n),
         .ddr3_dqs_p                     (ddr3_dqs_p),
         .init_calib_complete            (init_calib_complete),
         
         .ddr3_dm                        (ddr3_dm),
         .ddr3_odt                       (ddr3_odt),
         // Application interface ports
         .app_addr                       (app_addr),
         .app_cmd                        (app_cmd),
         .app_en                         (app_en),
         .app_wdf_data                   (app_wdf_data),
         .app_wdf_end                    (app_wdf_end),
         .app_wdf_wren                   (app_wdf_wren),
         .app_rd_data                    (app_rd_data),
         .app_rd_data_end                (app_rd_data_end),
         .app_rd_data_valid              (app_rd_data_valid),
         .app_rdy                        (app_rdy),
         .app_wdf_rdy                    (app_wdf_rdy),
         .app_sr_req                     (1'b0),
         .app_sr_active                  (),
         .app_ref_req                    (1'b0),
         .app_ref_ack                    (),
         .app_zq_req                     (1'b0),
         .app_zq_ack                     (),
         .ui_clk                         (clk_ddr_ui), // output from Mig
         .ui_clk_sync_rst                (rst_ddr_ui),
         
         .app_wdf_mask                   (app_wdf_mask),
         
         .sys_clk_i(clk_sys),
         .sys_rst                        (rst_sys_ddr)
         );
         
     // OK MIG DDR3 Testbench Instatiation
     ddr3_test ddr3_tb (
         .clk                (clk_ddr_ui), // from the DDR3 MIG "ui_clk"
         .INDEX              (INDEX),
         .reset              (ep03wire[2] | rst_ddr_ui),
         .reads_en           (ep03wire[0]),
         .writes_en          (ep03wire[1]),
         .calib_done         (init_calib_complete),
     
         .ib_re              (pipe_in_read),
         .ib_data            (pipe_in_data),
         .ib_count           (pipe_in_rd_count),
         .ib_valid           (pipe_in_valid),
         .ib_empty           (pipe_in_empty),
         
         .ob_we              (pipe_out_write),
         .ob_data            (pipe_out_data),
         .ob_count           (pipe_out_wr_count),
         .ob_full            (pipe_out_full),
         
         .app_rdy            (app_rdy),
         .app_en             (app_en),
         .app_cmd            (app_cmd),
         .app_addr           (app_addr),
         
         .app_rd_data        (app_rd_data),
         .app_rd_data_end    (app_rd_data_end),
         .app_rd_data_valid  (app_rd_data_valid),
         
         .app_wdf_rdy        (app_wdf_rdy),
         .app_wdf_wren       (app_wdf_wren),
         .app_wdf_data       (app_wdf_data),
         .app_wdf_end        (app_wdf_end),
         .app_wdf_mask       (app_wdf_mask)
         );
     
     //Block Throttle
     always @(posedge okClk) begin
         // Check for enough space in input FIFO to pipe in another block
         // The count is compared against a reduced size to account for delays in
         // FIFO count updates.
         if(pipe_in_wr_count <= (FIFO_SIZE-BUFFER_HEADROOM-BLOCK_SIZE) ) begin
             pipe_in_ready <= 1'b1;
         end
         else begin
             pipe_in_ready <= 1'b0;
         end    
         // Check for enough space in output FIFO to pipe out another block
         if(pipe_out_rd_count >= BLOCK_SIZE) begin
             pipe_out_ready <= 1'b1;
         end
         else begin
             pipe_out_ready <= 1'b0;
         end
     end
     
     okWireIn       wi03 (.okHE(okHE),                             .ep_addr(8'h03), .ep_dataout(ep03wire));
     okWireIn       wi04 (.okHE(okHE),                             .ep_addr(8'h04), .ep_dataout(INDEX));
     okWireOut      wo02 (.okHE(okHE), .okEH(okEHx[ 14*65 +: 65 ]), .ep_addr(8'h22), .ep_datain({31'h00, init_calib_complete}));
     okWireOut      wo03 (.okHE(okHE), .okEH(okEHx[ 15*65 +: 65 ]), .ep_addr(8'h3e), .ep_datain(po0_ep_datain/*CAPABILITY*/));
     okBTPipeIn     pi0  (.okHE(okHE), .okEH(okEHx[ 12*65 +: 65 ]), .ep_addr(8'h80), .ep_write(pi0_ep_write), .ep_blockstrobe(), .ep_dataout(pi0_ep_dataout), .ep_ready(pipe_in_ready));
     okBTPipeOut    po0  (.okHE(okHE), .okEH(okEHx[ 13*65 +: 65 ]), .ep_addr(8'ha5), .ep_read(po0_ep_read),   .ep_blockstrobe(), .ep_datain(po0_ep_datain),   .ep_ready(pipe_out_ready));
     
     fifo_w32_1024_r256_128 okPipeIn_fifo (
         .rst(ep03wire[2]),
         .wr_clk(okClk),
         .rd_clk(clk),
         .din(pi0_ep_dataout), // Bus [31 : 0]
         .wr_en(pi0_ep_write),
         .rd_en(pipe_in_read),
         .dout(pipe_in_data), // Bus [256 : 0]
         .full(pipe_in_full),
         .empty(pipe_in_empty),
         .valid(pipe_in_valid),
         .rd_data_count(pipe_in_rd_count), // Bus [6 : 0]
         .wr_data_count(pipe_in_wr_count)); // Bus [9 : 0]
     
     fifo_w256_128_r32_1024 okPipeOut_fifo (
         .rst(ep03wire[2]),
         .wr_clk(clk),
         .rd_clk(clk_sys/*okClk*/),
         .din(pipe_out_data), // Bus [256 : 0]
         .wr_en(pipe_out_write),
         .rd_en(/*clk_en*/rd_en_0 & ep03wire[0]/*po0_ep_read*/),
         .dout(po0_ep_datain), // Bus [31 : 0]
         .full(pipe_out_full),
         .empty(pipe_out_empty),
         .valid(),
         .rd_data_count(pipe_out_rd_count), // Bus [9 : 0]
         .wr_data_count(pipe_out_wr_count)); // Bus [6 : 0]
    
    /* ------------------ END DDR3 ------------------- */
    
    /* ------------------ AD5453 SPI ------------------- */
    genvar k;
    generate
    for (k=0; k<=(AD5453_NUM-1); k=k+1) begin : dac_ad5453_gen
    // instantiate old top-level (but only for the AD5453 SPI) 
    spi_fifo_driven spi_fifo0 (.clk(clk_sys), .fifoclk(okClk), .rst(sys_rst), 
             .ss_0(d_csb), .mosi_0(d_sdi), .sclk_0(d_sclk), .data_rdy_0(), .adc_val_0(), //not yet used
             // register bridge 
             .ep_read(regRead), .ep_write(regWrite), .ep_address(regAddress), .ep_dataout_coeff(regDataOut), .ep_datain(regDataIn),
             // ddr 
             .en_period(en_period), .clk_en(clk_en), .ddr3_rst(ddr3_rst), .ddr_dat_i(po0_ep_datain[13:0]), .rd_en_0(rd_en_0), .regTrigger(ep40trig[`TI40_AD5453_WB]));
    end
    endgenerate        
    /* ----------------- END AD5453 ------------------------------------ */
    
	 //module to create a one second pulse on one of the LEDs (keepAlive test)
	 one_second_pulse out_pulse(
	 .clk(clk), .rst(sys_rst), .slow_pulse(led[0])
	 );
endmodule
