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
localparam I2C_DCARDS_NUM = 4;

module top_level_module(
	input wire [4:0] okUH,
	output wire[2:0] okHU,
	inout wire[31:0] okUHU,
	inout wire okAA,
    input wire sys_clkn,
	input wire sys_clkp,

	input wire pushreset,//pushbutton reset
	output wire [7:0] led, //LEDs on OpalKelly device; bit 0 will pulse every one second to indicate the FPGA is working
	                       //TODO: connect other signals to led

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
    output wire  [(DAC80508_NUM-1):0]ds_sdo,    // DAC85058; daq_v2 build has DAC85058ZC which means SDO is CLRB; will tie to logic high.
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
    output wire ads_sdi,
    input  wire ads_sdoa,
    input  wire ads_sdob, // TODO: not yet connected
    output wire ads_convst,
    output wire ads_resetb,
    input wire ads_busy,  // TODO: not yet connected

    // GPIO (6+6+4+4+4 = 24 total signals)
    output wire [5:0]dn, // TODO: constraint generator prints [4:0]dn
    output wire [5:0]up,
    output wire [3:0]gp_lvds_n, //TODO: need LVDS output driver (for now leave unconnected)
    output wire [3:0]gp_lvds_p,
    output wire [3:0]gpio,

    //power supply regulator enable signals (5 total signals)
    output wire en_15v,
    output wire en_1v8,
    output wire en_3v3,
    output wire en_5v,
    output wire en_n15v,

    output wire [1:0]en_ipump, // (2 total signals)

    inout [(I2C_DCARDS_NUM-1):0]dc_scl,
    inout [(I2C_DCARDS_NUM-1):0]dc_sda,

    inout ls_scl,
    inout ls_sda,
    inout qw_scl,
    inout qw_sda,

    input wire [1:0]sma,

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
	.reset(ep40trig[`AD7961_PLL_RESET]),
	.clk_out1(adc_clk), //out at 200 MHz
	.locked(adc_pll_locked)
	);
	 //FrontPanel (HostInterface) wires
	wire okClk;
	wire [112:0] okHE;
	wire [64:0] okEH;
	// Adjust size of okEHx to fit the number of outgoing endpoints in your design (n*65-1:0)
	//TODO: better way to keep track of these
	wire [17*65-1:0] okEHx;

	//Opal Kelly wires and triggers
	wire [31:0] ep00wire, ep01wire, ep02wire, ep40trig, ep41trig;

	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[`GP_SYSTEM_RESET]); // TODO: GP_SYSTEM_RESET is not found

	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(17)) wireOR (okEH, okEHx); //TODO

	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));

    /* ---------------- Ok Endpoints ----------------*/
	//wire to hold the data/commands from the host this will be routed to the wishbone formatter/state machine for the ADS7952
	okWireIn wi0 (.okHE(okHE), .ep_addr(`GP_UNCONNECTED_WIRE_IN), .ep_dataout(ep00wire));
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(`GP_HOST_FPGAB_GPIO_WIRE_IN), .ep_dataout(ep01wire));
    wire host_fpgab;
    assign host_fpgab = ep01wire[`ADS8686_HOST_FPGA_BIT];
    assign up = ep01wire[(`GPIO_UP_WIRE_IN+`GPIO_UP_WIRE_IN_LEN - 1):`GPIO_UP_WIRE_IN];
    assign dn = ep01wire[(`GPIO_DOWN_WIRE_IN+`GPIO_DOWN_WIRE_IN_LEN - 1):`GPIO_DOWN_WIRE_IN];
    assign gpio = ep01wire[(`GPIO_3V3_WIRE_IN+`GPIO_3V3_WIRE_IN_LEN - 1):`GPIO_3V3_WIRE_IN];
    wire [3:0]gp_lvds_se;
    assign gp_lvds_se = ep01wire[(`GPIO_LVDS_WIRE_IN+`GPIO_LVDS_WIRE_IN_LEN - 1):`GPIO_LVDS_WIRE_IN];

    genvar m;
    generate
    for (m=0; m<=3; m=m+1) begin : lvds_obuf

    // Single-Ended -> LVDS
    OBUFDS
        #(
            .IOSTANDARD("LVDS_25"),        // Specify the output I/O standard
            .SLEW("FAST")                  // Specify the output slew rate
        )
        Cnv_Out_OBUFDS
        (
            .O(gp_lvds_p[m]),              // Diff_p output (connect directly to top-level port)
            .OB(gp_lvds_n[m]),             // Diff_n output (connect directly to top-level port)
            .I(gp_lvds_se[m])              // Buffer input
        );
    end
    endgenerate

    /* ---------------- WI02 ---------------------- */
    okWireIn wi2 (.okHE(okHE), .ep_addr(`GP_PWR_REG_ADC_EN_WIRE_IN),
      .ep_dataout(ep02wire));

     assign a_en0_hv = ep02wire[(`AD7961_ENABLE_GEN_BIT+`AD7961_ENABLE_LEN - 1):`AD7961_ENABLE_GEN_BIT]; //1 for each channel
     assign a_en_hv = ep02wire[(`AD7961_GLOBAL_ENABLE+`AD7961_GLOBAL_ENABLE_LEN - 1):`AD7961_GLOBAL_ENABLE];    // global

     wire [9:0] en_period; //TODO: different for each channel?
     assign en_period = ep02wire[(`AD5453_PERIOD_ENABLE_LEN+`AD5453_PERIOD_ENABLE - 1):`AD5453_PERIOD_ENABLE];

     //power supply regulatoor enable signals (5 total signals)
     assign en_15v = ep02wire[`POWER_15V_ENABLE];
     assign en_1v8 = ep02wire[`POWER_1V8_ENABLE];
     assign en_3v3 = ep02wire[`POWER_3V3_ENABLE];
     assign en_5v = ep02wire[`POWER_5V_ENABLE];
     assign en_n15v = ep02wire[`POWER_N15V_ENABLE];

     assign en_ipump = ep02wire[(`GP_CURRENT_PUMP_ENABLE + `GP_CURRENT_PUMP_ENABLE_LEN - 1):`GP_CURRENT_PUMP_ENABLE]; // (2 total signals)

     assign ads_resetb = ep02wire[`ADS8686_RESET];

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
                      .ep_addr(`GP_RST_VALID_TRIG_IN), .ep_clk(clk_sys), .ep_trigger(ep40trig));

    okTriggerIn trigIn41 (.okHE(okHE),
                                    .ep_addr(`I2C_TRIG_IN), .ep_clk(clk_sys), .ep_trigger(ep41trig));
	//wire to hold the value of the last word written to the FIFO (to help with debugging/observation)
	// okWireOut wo0 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(lastWrite));

    //wire to hold general status output to host
    okWireOut wo1 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(`AD7961_PLL_LOCKED), .ep_datain({31'b0, adc_pll_locked}));

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

	//TODO: reorganize triggerout
	wire [(I2C_DCARDS_NUM-1):0] i2c_done;
	wire [1:0] i2c_aux_done;
	okTriggerOut trigOut60 (.okHE(okHE), .okEH(okEHx[ 3*65 +: 65 ]), .ep_addr(`GP_FIFO_FLAG_I2C_DONE_TRIG_OUT), .ep_clk(clk_sys),
                           .ep_trigger({10'b0,
													 i2c_aux_done,      // 2 bits wide: 21-20
													 i2c_done,          // 4 bits wide: 19-16
                           ads_fifo_empty,    // bit 15
													 ads_fifo_halffull, // bit 14
													 ads_fifo_full,     // bit 13
                           adc_fifo_empty,    // 4 bits wide: 12-6
													 adc_fifo_halffull, // 4 bits wide: 8-5
													 adc_fifo_full,     // 4 bits wide: 4-1
													 hostinterrupt}));  // bit 0

       //register bridge for writing filter coefficients to BRAM and to the spi_controller
       wire regWrite;
       wire regRead;
       wire [31:0] regAddress;
       wire [31:0] regDataOut;
       wire [31:0] regDataIn; // Was reg, gave error in Vivado synthesis

       okRegisterBridge regBridge (
           .okHE(okHE),
           .okEH(okEHx[4*65 +: 65]),
           .ep_write(regWrite),
           .ep_read(regRead),
           .ep_address(regAddress),
           .ep_dataout(regDataOut),
           .ep_datain(regDataIn)
       );
	// ---------------------- END OpalKelly EndPoints (global) --------

	// --------------------- Begin ADS8686 --------------------------
    wire [31:0] ads_wire_in;
    wire [31:0] ads_data_out;
    wire ads_data_valid;

    okWireIn wi_ads (.okHE(okHE), .ep_addr(`ADS8686_WB_IN), .ep_dataout(ads_wire_in));
    spi_controller #(.ADDR(`ADS8686_REGBRIDGE_OFFSET)) uut(
                       .clk(clk_sys),
                       .reset(sys_rst),
                       .divider_reset(ep40trig[`ADS8686_CLK_DIV_RESET]),
                       .dac_val(ads_wire_in),
                       .dac_convert_trigger(ep40trig[`ADS8686_WB_CONVERT]), // trigger wishbone transfers
                       .host_fpgab(host_fpgab), // if 1 host driven commands; if 0
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
                       .mosi(ads_sdi),
                       .miso(ads_sdoa), //TODO: need to connect SDOB
                       .convst_out(ads_convst)
                       );

   wire [31:0] ads_fifo_data;
   wire ads_pipe_read;

   fifo_AD796x ads8686_fifo ( //32 bit wide read and 16 bit wide write ports
     .rst(ep40trig[`ADS8686_FIFO_RESET]),
     .wr_clk(clk_sys),
     .rd_clk(okClk),
     .din(ads_data_out),         // Bus [15:0] (from ADC)
     .wr_en(ads_data_valid),    // from ADC
     .rd_en(ads_pipe_read),      // from OKHost
     .dout(ads_fifo_data),     // Bus [31:0] (to OKHost)
     .full(ads_fifo_full),     // status
     .empty(ads_fifo_empty),   // status
     .prog_full(ads_fifo_halffull));//status

    //pipeOut to transfer data in bulk from the ADS8686 FIFO
   okPipeOut pipeOutADS86 (.okHE(okHE), .okEH(okEHx[5*65 +: 65]),
                      .ep_addr(`ADS8686_PIPE_OUT_GEN_ADDR),  .ep_read(ads_pipe_read),
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
    okWireOut wo_ads (.okHE(okHE), .okEH(okEHx[6*65 +: 65 ]), .ep_addr(`ADS8686_OUT), .ep_datain(ads_last_read));

  // ------------ end ADS8686 -----------------------------------

	/* ---------------- AD796x 5 MSPS ADC  ----------------*/
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
    
        sync_reset ad7961_sync_reset(
            clk_sys,
            ep01wire[`AD7961_WIRE_RESET_GEN_BIT+i],
            adc_sync_rst[i]);
        
        AD7961 adc7961(
        .m_clk_i(clk_sys),                // 200 MHz Clock, used for timing (only for 5 MSPS tracking)
        .fast_clk_i(adc_clk),           // Maximum 260 MHz Clock, used for serial transfer
        .reset_n_i(~(ep40trig[`AD7961_RESET_GEN_BIT+i] | adc_sync_rst[i])),// Reset signal active low: both Python signals are active high due to inversion
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

        fifo_AD796x adc7961_fifo (//32 bit wide read and 16 bit wide write ports
          .rst(ep40trig[`AD7961_FIFO_RESET_GEN_BIT + i]),
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
          okPipeOut pipeOutA1(.okHE(okHE), .okEH(okEHx[(7+i)*65 +: 65]),
                    .ep_addr(`AD7961_PIPE_OUT_GEN_ADDR + i), .ep_read(adc_pipe_ep_read[i]),
                    .ep_datain(adc_pipe_ep_datain[i]));
     end
     endgenerate

    /*---------------- DAC80508 -------------------*/
    wire [31:0]dac_wirein_data[(DAC80508_NUM-1):0];
    wire [31:0]dac_data_out[(DAC80508_NUM-1):0];

    genvar j;
    generate
    for (j=0; j<=(DAC80508_NUM-1); j=j+1) begin : dac80508_gen
        spi_controller dac_0 (
          .clk(clk_sys), .reset(sys_rst), .dac_val(dac_wirein_data[j]), .dac_convert_trigger(ep40trig[`DAC80508_WB_CONVERT_GEN_BIT+j]), .dac_out(dac_data_out[j]),
          .ss(ds_csb[j]), .sclk(ds_sclk[j]), .mosi(ds_sdi[j]), .miso(ds_sdo[j]), .okClk(okClk), .addr(regAddress), .data_in(regDataOut), .write_in(regWrite)
        );
        okWireIn wi_dac_0 (.okHE(okHE), .ep_addr(`DAC80508_WB_IN_GEN_ADDR + j), .ep_dataout(dac_wirein_data[j]));
        // TODO: wireout is not needed (nor supported with the Clear version of the DAC80508)
        okWireOut wo_dac_0 (.okHE(okHE), .okEH(okEHx[(j + 1)*65 +: 65 ]), .ep_addr(`DAC80508_OUT_GEN_ADDR), .ep_datain(dac_data_out[j]));

    end
    endgenerate
    /*---------------- END DAC80508 -------------------*/

   //General purpose clock divide - currently used as "helper" clocking module for reading form DDR3
   //TODO: was a clk_en that was assigned to dataready
   wire dataready;
   //wire to capture clock enable period multiplier, and the clock enable itself
    general_clock_divide MIG_DDR_FIFO_RD_EN(
        .clk(clk_sys),
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

     reset_synchronizer u_MIG_sync_rst( //TODO: move this to a trigger in
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

         .sys_clk_i                      (clk_sys),
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

     okWireIn       wi03 (.okHE(okHE),                             .ep_addr(`DDR3_RESET_READ_WRITE_ENABLE), .ep_dataout(ep03wire));
     okWireIn       wi04 (.okHE(okHE),                             .ep_addr(`DDR3_INDEX), .ep_dataout(INDEX));
     okWireOut      wo02 (.okHE(okHE), .okEH(okEHx[ 11*65 +: 65 ]), .ep_addr(`DDR3_INIT_CALIB_COMPLETE), .ep_datain({31'h00, init_calib_complete}));
     okWireOut      wo03 (.okHE(okHE), .okEH(okEHx[ 12*65 +: 65 ]), .ep_addr(`DDR3_WIRE_OUT), .ep_datain(po0_ep_datain/*CAPABILITY*/));
     okBTPipeIn     pi0  (.okHE(okHE), .okEH(okEHx[ 13*65 +: 65 ]), .ep_addr(`DDR3_BLOCK_PIPE_IN), .ep_write(pi0_ep_write), .ep_blockstrobe(), .ep_dataout(pi0_ep_dataout), .ep_ready(pipe_in_ready));
     okBTPipeOut    po0  (.okHE(okHE), .okEH(okEHx[ 14*65 +: 65 ]), .ep_addr(`DDR3_BLOCK_PIPE_OUT), .ep_read(po0_ep_read),   .ep_blockstrobe(), .ep_datain(po0_ep_datain),   .ep_ready(pipe_out_ready));

     fifo_w32_1024_r256_128 okPipeIn_fifo (
         .rst(ep03wire[2]),
         .wr_clk(okClk),
         .rd_clk(clk_ddr_ui),
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
         .wr_clk(clk_ddr_ui),
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

    wire [(AD5453_NUM-1):0] rd_en_fast_dac;
    wire [(AD5453_NUM-1):0] clk_en_fast_dac;

    genvar k;
    generate
    for (k=0; k<=(AD5453_NUM-1); k=k+1) begin : dac_ad5453_gen
    // instantiate old top-level (but only for the AD5453 SPI)
    spi_fifo_driven spi_fifo0 (.clk(clk_sys), .fifoclk(okClk), .rst(sys_rst),
             .ss_0(d_csb[k]), .mosi_0(d_sdi[k]), .sclk_0(d_sclk[k]), .data_rdy_0(), .adc_val_0(), //not yet used
             // register bridge //TODO: add address increment based on generate k
             /*.ep_read(regRead),*/ .ep_write(regWrite), .ep_address(regAddress), .ep_dataout_coeff(regDataOut), /*.ep_datain(regDataIn),*/
             // DDR
             .en_period(en_period),//in,
             .clk_en(clk_en_fast_dac[k]),//out
             .ddr3_rst(ddr3_rst),//in
             .ddr_dat_i(po0_ep_datain[13:0]), //in
             .rd_en_0(rd_en_fast_dac[k]), //out
             .regTrigger(ep40trig[`AD5453_REG_TRIG_GEN_BIT]) //input
             );
    end
    endgenerate

    assign rd_en_0 = rd_en_fast_dac[0];
    assign clk_en = clk_en_fast_dac[0];

    /* ----------------- END AD5453 ------------------------------------ */

    /*---------------- I2C -------------------*/
    /*---------------- daughercard I2C -------------------*/
    wire [15:0] i2c_memdin[(I2C_DCARDS_NUM-1):0];
    wire [7:0] i2c_memdout[(I2C_DCARDS_NUM-1):0];

    generate
        for (i = 0; i < (I2C_DCARDS_NUM / 2); i = i + 1) begin : i2c_dc_wire_gen
            okWireIn wi_i2c_dc0 (.okHE(okHE), .ep_addr(`I2CDC_WIRE_IN_GEN_ADDR + i), .ep_dataout({i2c_memdin[(i * 2) + 1], i2c_memdin[i * 2]}));
        end
    endgenerate

    generate
        for (i = 0; i < (I2C_DCARDS_NUM / 4); i = i + 1) begin
            okWireOut wo_i2c_dc (.okHE(okHE), .okEH(okEHx[ (15 + i)*65 +: 65 ]), .ep_addr(`I2CDC_WIRE_OUT + i),
                            .ep_datain({i2c_memdout[i + 3], i2c_memdout[i + 2], i2c_memdout[i + 1], i2c_memdout[i + 0]}));
        end
    endgenerate

    genvar l;
    generate
    for (l=0; l<=(I2C_DCARDS_NUM-1); l=l+1) begin : i2c_dc_gen
    // generate for the 4 daughtercards... then hand create for the other two
    i2cController i2c_controller_0 (
        .clk (clk_sys),
        .reset (ep40trig[`I2CDC_RESET_GEN_BIT + l]),
        .start (ep40trig[`I2CDC_START_GEN_BIT + l]), //trigger in
        .done (i2c_done[l]),   // trigger out
        .memclk (clk_sys),  //the triggers are synchronized to clk_sys
        .memstart (ep41trig[`I2CDC_MEMSTART_GEN_BIT + l]), //trigger in
        .memwrite (ep41trig[`I2CDC_MEMWRITE_GEN_BIT + l]), // trigger in
        .memread (ep41trig[`I2CDC_MEMREAD_GEN_BIT + l]),   // trigger in
        .memdin (i2c_memdin[l]),     //wire in
        .memdout (i2c_memdout[l]),   //wire out
        .i2c_sclk (dc_scl[l]),       // inout
        .i2c_sdat (dc_sda[l])        // inout
    );
    end
    endgenerate
    /*---------------- END daughercard I2C -------------------*/

    wire [15:0] i2c_aux_memdin[1:0];
    wire [7:0] i2c_aux_memdout[1:0];

    okWireIn wi_i2c_aux (.okHE(okHE), .ep_addr(`I2CDAQ_WIRE_IN_GEN_ADDR), .ep_dataout({i2c_aux_memdin[1], i2c_aux_memdin[0]}));
    okWireOut wo_i2c_aux (.okHE(okHE), .okEH(okEHx[ 16*65 +: 65 ]), .ep_addr(`I2CDAQ_WIRE_OUT_GEN_ADDR),
                    .ep_datain({i2c_aux_memdout[1], i2c_aux_memdout[0]}));

		// level shifted I2C bus
    i2cController i2c_controller_4 (
        .clk (clk_sys),
        .reset (ep41trig[`I2CDAQ_RESET_GEN_BIT + 0]),
        .start (ep41trig[`I2CDAQ_START_GEN_BIT + 0]), //trigger in
        .done (i2c_aux_done[0]),   // trigger out
        .memclk (clk_sys),  //the triggers are synchronized to clk_sys
        .memstart (ep41trig[`I2CDAQ_MEMSTART_GEN_BIT + 0]), //trigger in
        .memwrite (ep41trig[`I2CDAQ_MEMWRITE_GEN_BIT + 0]), // trigger in
        .memread (ep41trig[`I2CDAQ_MEMREAD_GEN_BIT + 0]),   // trigger in
        .memdin (i2c_aux_memdin[0]),     //wire in
        .memdout (i2c_aux_memdout[0]),   //wire out
        .i2c_sclk (ls_scl),       // inout
        .i2c_sdat (ls_sda)        // inout
    );

		// QW 3.3v I2C bus
    i2cController i2c_controller_5 (
        .clk (clk_sys),
        .reset (ep41trig[`I2CDAQ_RESET_GEN_BIT + 1]),
        .start (ep41trig[`I2CDAQ_START_GEN_BIT + 1]), //trigger in
        .done (i2c_aux_done[1]),   // trigger out
        .memclk (clk_sys),  //the triggers are synchronized to clk_sys
        .memstart (ep41trig[`I2CDAQ_MEMSTART_GEN_BIT + 1]), //trigger in
        .memwrite (ep41trig[`I2CDAQ_MEMWRITE_GEN_BIT + 1]), // trigger in
        .memread (ep41trig[`I2CDAQ_MEMREAD_GEN_BIT + 1]),   // trigger in
        .memdin (i2c_aux_memdin[1]),     //wire in
        .memdout (i2c_aux_memdout[1]),   //wire out
        .i2c_sclk (qw_scl),       // inout
        .i2c_sdat (qw_sda)        // inout
    );
    /*---------------- End I2C -------------------*/

	 //module to create a one second pulse on one of the LEDs (keepAlive test)
	 one_second_pulse out_pulse(
	 .clk(clk_sys), .rst(sys_rst), .slow_pulse(led[0])
	 );
endmodule
