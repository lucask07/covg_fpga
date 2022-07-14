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
// 
//  To-do: The DAC ddr data is read from a clock divider (e.g. 2.5 MSPS) 
//   but we need to synchronize to the AD7961 
//   the AD7961 uses a slower clock (100 MHz for timing) -- how does this impact synchronization?  -- valid out is from the fast_clk 250 MHz 
//          can this be switched to the 200 MHz clock? 
//   find the thread about the poor AD7961 design 
//////////////////////////////////////////////////////////////////////////////////
// Clocks:
//    clk_sys  - 200 MHz system clock
//    okClk    - 100.8 MHz host-interface clock provided by okHost
//    adc_clk  - 250 MHz clock for AD7961.v
//
//

`default_nettype wire // depending on compile order this may be needed. OpalKelly says its not a problem.

`include "ep_defines.v"
localparam FADC_NUM = 4;
localparam DAC80508_NUM = 2;
localparam AD5453_NUM = 6;
localparam I2C_DCARDS_NUM = 4;
localparam NUM_OK_EPS = 34;

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
    input  wire ads_sdob, 
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

    output wire [1:0]sma,

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
	.clk_out1(adc_clk), //out at 250 MHz
	.locked(adc_pll_locked)
	);

	wire adc_sync_rst;
    wire [31:0]adc_pipe_ep_datain[0:(FADC_NUM-1)];
    wire [(FADC_NUM-1):0]write_en_adc_o;
    wire [15:0] adc_val[0:(FADC_NUM-1)];
    
    wire [(FADC_NUM-1):0] adc_fifo_full;
    wire [(FADC_NUM-1):0] adc_fifo_halffull;
    wire [(FADC_NUM-1):0] adc_fifo_empty;
    wire [(FADC_NUM-1):0] adc_pipe_ep_read;
    wire [(FADC_NUM-1):0] adc_fifo_reset;
	
	assign led[1] = ~adc_pll_locked;
	assign led[2] = ~adc_fifo_empty[0]; // LEDs light when low
	assign led[3] = ~adc_fifo_halffull[1];
	assign led[4] = ~adc_fifo_full[1];
	assign led[5] = ~ep40trig[`AD7961_PLL_RESET];
	assign led[6] = ~(ep40trig[`AD7961_RESET_GEN_BIT+i] | adc_sync_rst);
    assign led[7] = 1'b0;

    // WireIn 0 configures MUX for logic analyzer debug. CSB signals 
    mux_8to1 (
	   .datain({d_csb[4:0], ds_csb[1], ds_csb[0], ads_csb}), // 7:0
	   .sel(ep00wire[(`GPIO_CSB_DEBUG_LEN + `GPIO_CSB_DEBUG - 1) :(`GPIO_CSB_DEBUG)]),
	   .dataout(gpio[0])
	);

    mux_8to1 (
       .datain({d_sclk[4:0], ds_sclk[1], ds_sclk[0], ads_sclk}), // 7:0
       .sel(ep00wire[(`GPIO_SCLK_DEBUG_LEN + `GPIO_SCLK_DEBUG - 1) :(`GPIO_SCLK_DEBUG)]),
       .dataout(gpio[1])
    );

    mux_8to1 (
       .datain({d_sdi[4:0], ds_sdi[1], ds_sdi[0], ads_sdi}), // 7:0
       .sel(ep00wire[(`GPIO_SDI_DEBUG_LEN + `GPIO_SDI_DEBUG - 1) :(`GPIO_SDI_DEBUG)]),
       .dataout(gpio[2])
    );

    mux_8to1 (
       .datain({4'b0100, ads_busy, ads_convst, ads_sdob, ads_sdoa}), // 7:0
       .sel(ep00wire[(`GPIO_ADS_CONVST_DEBUG_LEN + `GPIO_ADS_CONVST_DEBUG - 1) :(`GPIO_ADS_CONVST_DEBUG)]),
       .dataout(gpio[3])
    );

    //debug AD7961 
    wire [(FADC_NUM-1):0] conv;
    wire [(FADC_NUM-1):0] dco;
    wire [(FADC_NUM-1):0] adc_serial_data;
    

	//Opal Kelly wires and triggers bussess
	wire [31:0] ep00wire;
	wire [31:0] ep01wire;
	wire [31:0] ep02wire;
	wire [31:0] ep40trig;
	wire [31:0] ep41trig;
	wire [31:0] ep42trig;

	//wire used to OR the triggerIn reset with the pushbutton reset (so that any of the two can reset the FPGA)
	wire sys_rst;
	assign sys_rst = (pushreset | ep40trig[`GP_SYSTEM_RESET]); 

    //FrontPanel (HostInterface) wires
    wire okClk;
    wire [112:0] okHE;
    wire [64:0] okEH;
    // Adjust size of okEHx to fit the number of outgoing endpoints in your design (n*65-1:0)
    wire [NUM_OK_EPS*65-1:0] okEHx;
	// Adjust N to fit the number of outgoing endpoints in your design (.N(n))
	okWireOR # (.N(NUM_OK_EPS)) wireOR (okEH, okEHx); 
	//okHost instantiation
	okHost okHI (.okUH(okUH), .okHU(okHU), .okUHU(okUHU), .okAA(okAA),
             .okClk(okClk), .okHE(okHE), .okEH(okEH));

    /* ---------------- Ok Endpoints ----------------*/
	//wire to hold the data/commands from the host this will be routed to the wishbone formatter/state machine for the ADS7952
	okWireIn wi0 (.okHE(okHE), .ep_addr(`GPIO_DEBUG_WIRE_IN), .ep_dataout(ep00wire));
	// Wire in to select what slave the SPI data is routed to
	okWireIn wi1 (.okHE(okHE), .ep_addr(`GP_HOST_FPGAB_GPIO_WIRE_IN), .ep_dataout(ep01wire));
    wire host_fpgab;
    assign host_fpgab = ep01wire[`ADS8686_HOST_FPGA];
    
    //assign up = ep01wire[(`GPIO_UP_WIRE_IN+`GPIO_UP_WIRE_IN_LEN - 1):`GPIO_UP_WIRE_IN]; //TODO: up is being used for other debug. 
    assign dn = ep01wire[(`GPIO_DOWN_WIRE_IN+`GPIO_DOWN_WIRE_IN_LEN - 1):`GPIO_DOWN_WIRE_IN];
        
    // GPIO is used with the SPI debug mux so this is commented out.
    //assign gpio = ep01wire[(`GPIO_3V3_WIRE_IN+`GPIO_3V3_WIRE_IN_LEN - 1):`GPIO_3V3_WIRE_IN];  
    
    // LVDS output 
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
     // 4:1
     assign a_en0_hv = ep02wire[(`AD7961_ENABLE_GEN_BIT+`AD7961_ENABLE_LEN - 1):`AD7961_ENABLE_GEN_BIT]; //1 for each channel
     // 17:15
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

      wire [31:0]  ep03wire;
      okWireIn       wi03 (.okHE(okHE),                             .ep_addr(`DDR3_RESET_READ_WRITE_ENABLE), .ep_dataout(ep03wire));
     
      wire [31:0] ep_wire_filtsel;  //also includes DDR FIFO reset signals
      okWireIn wi_filt_sel (.okHE(okHE), .ep_addr(`FILTER_SEL_WIRE_IN), .ep_dataout(ep_wire_filtsel));
     
       wire [31:0] ep20wire;
       okWireOut      wo20 (.okHE(okHE), .okEH(okEHx[ 11*65 +: 65 ]), .ep_addr(`DDR3_INIT_CALIB_COMPLETE), .ep_datain(ep20wire));
       assign ep20wire[`DDR3_INIT_COMPLETE] = init_calib_complete;
       assign ep20wire[`DDR3_IN1_FULL] = pipe_in_full;
       assign ep20wire[`DDR3_IN1_EMPTY] = pipe_in_empty;
       assign ep20wire[`DDR3_IN2_FULL] = pipe_in2_full;
       assign ep20wire[`DDR3_IN2_EMPTY] = pipe_in2_empty;
       assign ep20wire[`DDR3_OUT1_FULL] = pipe_out_full;
       assign ep20wire[`DDR3_OUT1_EMPTY] = pipe_out_empty;
       assign ep20wire[`DDR3_OUT2_FULL] = pipe_out2_full;
       assign ep20wire[`DDR3_OUT2_EMPTY] = pipe_out2_empty;
       assign ep20wire[`DDR3_ADC_DATA_COUNT] = adc_data_cnt;

	okTriggerIn trigIn40 (.okHE(okHE),
                      .ep_addr(`GP_RST_VALID_TRIG_IN), .ep_clk(clk_sys), .ep_trigger(ep40trig));

    okTriggerIn trigIn41 (.okHE(okHE),
                                    .ep_addr(`I2C_TRIG_IN), .ep_clk(clk_sys), .ep_trigger(ep41trig));

    okTriggerIn trigIn42 (.okHE(okHE),
                                .ep_addr(`ADC_TIMING_TRIG_IN), .ep_clk(clk_sys), .ep_trigger(ep42trig)); 
	//wire to hold the value of the last word written to the FIFO (to help with debugging/observation)
	// okWireOut wo0 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(lastWrite));

    //wire to hold general status output to host
    // The +: syntax is explained here: https://stackoverflow.com/questions/18067571/indexing-vectors-and-arrays-with  
    okWireOut wo1 (.okHE(okHE), .okEH(okEHx[0*65 +: 65 ]), .ep_addr(`AD7961_PLL_LOCKED_WIRE_OUT), .ep_datain({30'b0, adc_timing_pll_locked, adc_pll_locked}));
	//TODO: reorganize triggerout
	wire [(I2C_DCARDS_NUM-1):0] i2c_done;
	wire [1:0] i2c_aux_done;
	wire [2:0] debug_fifo_status;
	okTriggerOut trigOut60 (.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(`GP_FIFO_FLAG_I2C_DONE_TRIG_OUT), .ep_clk(clk_sys),
                           .ep_trigger({7'b0,
                                                     debug_fifo_status,        // 3 bits wide: 24-22 empty (MSB), halffull, full
													 i2c_aux_done,      // 2 bits wide: 21-20
													 i2c_done,          // 4 bits wide: 19-16
                                                     ads_fifo_empty,    // bit 15
													 ads_fifo_halffull, // bit 14
													 ads_fifo_full,     // bit 13
                                                     adc_fifo_empty,    // 4 bits wide: 12-9
													 adc_fifo_halffull, // 4 bits wide: 8-5
													 adc_fifo_full,     // 4 bits wide: 4-1
													 hostinterrupt}));  // bit 0 -- not used

       //register bridge for writing filter coefficients to BRAM and to the spi_controller
       wire regWrite;
       wire regRead;
       wire [31:0] regAddress;
       wire [31:0] regDataOut;
       wire [31:0] regDataIn; // Was reg, gave error in Vivado synthesis
       assign regDataIn = 32'haaaa;  // TODO: unused

       okRegisterBridge regBridge (
           .okHE(okHE),
           .okEH(okEHx[2*65 +: 65]),
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
                       .divider_reset(ep42trig[`AD7961_RESET_GEN_BIT]), //NOTE: to synchronize to the AD7961_timing module share reset signal. TODO: check the phase alignment remains consistent
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
                       .miso(ads_sdoa), 
                       .miso_b(ads_sdob),
                       .convst_out(ads_convst)
                       );
                       
   wire [31:0] ads_fifo_data;
   wire ads_pipe_read;

    // ADS8686 convert start counter so that we can know what sequence in the sequencer we are in 
   // Wireout of ADS8686 data for host driven SPI reads 
   
    // detect rising-edge of convert start
    reg conv_start_pulse;
    reg conv_start_reg;
    always @(posedge clk_sys) begin
        conv_start_reg <= ads_convst;
    end
    
    // single clock widge pulse 
    always @(posedge clk_sys) begin
        conv_start_pulse <= (ads_convst & ~conv_start_reg);
    end
    
    reg [4:0] ads_sequence_count; //max of 31
    always @(posedge clk_sys) begin
         if (ads_resetb==1'b0) begin
              ads_sequence_count <=32'h0;
         end
         else if (conv_start_pulse==1'b1) begin 
             if (ads_sequence_count == 5'd23) ads_sequence_count <= 5'd0; //24 allows for sequencer lengths of 1,2,3,4,6,8,12
             else ads_sequence_count <= ads_sequence_count + 5'd1;        
         end             
     end    
    

   fifo_ADS8686 ads8686_fifo ( //32 bit wide read and 32 bit wide write ports, 2048 deep
     .rst(ep40trig[`ADS8686_FIFO_RESET]),
     .wr_clk(clk_sys),
     .rd_clk(okClk),
     .din(ads_data_out),             // Bus [31:0] (from ADC)
     .wr_en(ads_data_valid),         // from ADC
     .rd_en(ads_pipe_read),          // from OKHost
     .dout(ads_fifo_data),           // Bus [31:0] (to OKHost)
     .full(ads_fifo_full),           // status
     .empty(ads_fifo_empty),         // status
     .prog_full(ads_fifo_halffull)); // status (flags at 1024 full) 

    //pipeOut to transfer data in bulk from the ADS8686 FIFO
   okPipeOut pipeOutADS86 (.okHE(okHE), .okEH(okEHx[3*65 +: 65]),
                      .ep_addr(`ADS8686_PIPE_OUT_GEN_ADDR),  .ep_read(ads_pipe_read),
                      .ep_datain(ads_fifo_data));

   // Wireout of ADS8686 data for host driven SPI reads 
   reg [31:0] ads_last_read;
   always @(posedge clk_sys) begin
        if (sys_rst) begin
             ads_last_read <=32'h0;
        end
        else if (ads_data_valid) begin 
            ads_last_read <= ads_data_out;
        end
    end
    okWireOut wo_ads (.okHE(okHE), .okEH(okEHx[4*65 +: 65 ]), .ep_addr(`ADS8686_OUT), .ep_datain(ads_last_read));

  // ------------ end ADS8686 -----------------------------------

	/* ---------------- AD796x 5 MSPS ADC  ----------------*/
    reg adc_valid_cnt[0:(FADC_NUM-1)];
    reg adc_valid_pulse[0:(FADC_NUM-1)];
    reg [15:0] adc_val_reg[0:(FADC_NUM-1)];
    wire [31:0] adc_tcyc_cnt; // timing counter (clocked at 200 MHz)
    wire [4:0] cycle_cnt;     // counter (9 - 0) for what data goes into DDR

    sync_reset ad7961_sync_reset(
        .clk(clk_sys),
        .async_reset(ep01wire[`AD7961_WIRE_RESET_GEN_BIT]),
        .sync_reset(adc_sync_rst)
        );
	
	wire adc_rd_en_emulator;
	
	global_timing Timing (
	    .clk_sys(clk_sys),                    // 200 MHz timing clk (was 100 MHz Clock, used for timing)
        .reset_n_i(~(ep42trig[`AD7961_RESET_GEN_BIT+0] | adc_sync_rst)),                  // Reset signal, active low
        .adc_tcyc_cnt(adc_tcyc_cnt),
        .cycle_cnt(cycle_cnt),
        .adc_rd_en_emulator(adc_rd_en_emulator)
	);
	
	genvar i;
    generate
    for (i=0; i<=(FADC_NUM-1); i=i+1) begin : ad7961_gen

        AD7961 adc7961 (
        .adc_tcyc_cnt(adc_tcyc_cnt),    // 200 MHz counter used for timing
        .fast_clk_i(adc_clk),           // Maximum 260 MHz Clock, used for serial transfer
        // Must reset all synchronously so that all data can go into the same FIFO
        .reset_n_i(~(ep42trig[`AD7961_RESET_GEN_BIT+0] | adc_sync_rst)),// Reset signal active low: both Python signals are active high due to inversion
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
        .data_o(adc_val[i]),
        .conv(conv[i]),
        .dco(dco[i]),
        .adc_serial_data(adc_serial_data[i])        
        );

          //pipeOut for data from AD7961
          okPipeOut pipeOutA1(.okHE(okHE), .okEH(okEHx[(5+i)*65 +: 65]),
                    .ep_addr(`AD7961_PIPE_OUT_GEN_ADDR + i), .ep_read(adc_pipe_ep_read[i]),
                    .ep_datain(adc_pipe_ep_datain[i])); 
     end
     endgenerate

    assign sma[0] = dco[0]; //J17, MC2-77
    assign sma[1] = write_en_adc_o[0]; //J16
    
    /* --------------- SPI clock generator ----------- */
    reg ddr_dac_rd_en;
    reg ads_rd_en;
    wire ddr_data_valid; 

    // pulse at 2.5 MHz for reading DAC ddr data. Syncrhonize to the 7961_timing module
    always @(posedge clk_sys) begin
        if (cycle_cnt[0] == 1'b0) begin // even value 
            if (adc_tcyc_cnt == 32'd20) ddr_dac_rd_en <= 1'b1;  //TODO is 18 best (sync'd with adc_wr_en optimal?); this is one #more behind due to the register
            else ddr_dac_rd_en <= 1'b0;
        end
        else ddr_dac_rd_en <= 1'b0;
    end

    /* --------------- DDR3 ---------------------------*/
    wire [31:0] ep43trig;
    wire          clk_ddr_ui;

    okTriggerIn trigIn43 (.okHE(okHE),
                            .ep_addr(`DDR_RESET_ADDR_TRIG), .ep_clk(clk_ddr_ui), .ep_trigger(ep43trig));

     ////////////////////////////*DDR3 INTERFACE INSTANTIATIONS*//////////////////////////////////////////////
     // OK RAMTest Parameters
     localparam BLOCK_SIZE = 512; // 512 bytes / 4 bytes per word. LJK update from 128 to 512. 
     localparam FIFO_SIZE = 1023; // note that Xilinx does not allow use of the full 1024 words
     localparam BUFFER_HEADROOM = 20; // headroom for the FIFO count to account for latency

     // Capability bitfield, used to indicate features supported by this bitfile:
     // [0] - Supports passing calibration status through FrontPanel
     localparam CAPABILITY = 16'h0001;

     wire          init_calib_complete;
     reg           rst_sys_ddr; // reset at startup for a certain number of clock cycles 

     wire [29 :0]  app_addr;
     wire [2  :0]  app_cmd;
     wire          app_en;
     wire          app_rdy;
     wire [255:0]  app_rd_data;
     wire          app_rd_data_end;
     wire          app_rd_data_valid;
     wire [255:0]  app_wdf_data;
     wire          app_wdf_end;
     wire [31 :0]  app_wdf_mask;
     wire          app_wdf_rdy;
     wire          app_wdf_wren;

     wire          rst_ddr_ui;

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
     wire [7:0]   pipe_out_rd_count;
     wire [7:0]   pipe_out_wr_count;
     wire         pipe_out_full;
     wire         pipe_out_empty;
     reg          pipe_out_ready;

     wire         pipe_in2_read;
     wire [255:0] pipe_in2_data;
     wire [7:0]   pipe_in2_rd_count;
     wire [7:0]   pipe_in2_wr_count;
     wire         pipe_in2_valid;
     wire         pipe_in2_full;
     wire         pipe_in2_empty;
     reg          pipe_in2_ready;

     wire         pipe_out2_write;
     wire [255:0] pipe_out2_data;
     wire [9:0]   pipe_out2_rd_count;
     wire [6:0]   pipe_out2_wr_count;
     wire         pipe_out2_full;
     wire         pipe_out2_empty;
     reg          pipe_out2_ready;

     // Pipe Fifos
     wire         pi0_ep_write;
     wire         po0_ep_read;
     wire [31:0]  pi0_ep_dataout;
     wire [31:0] INDEX;
     wire [31:0] INDEX2;
     
     wire [127:0]  po0_ep_datain;// MIG/DDR3 FIFO data out to DACs 
     
     wire         po2_ep_read;
     wire [31:0]  po2_ep_datain;// MIG/DDR3 ADC FIFO data out
     wire [31:0]  adc_data_cnt; // count of ADC words in DDR

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

    // --------- The DDR section is derived from OpalKelly ramtest.v provided in the FrontPanelAPI
    // this is intended to be used on OpalKelly devices only
    // -----------------------------------------  
     // This sample is included for reference only.  No guarantees, either
     // expressed or implied, are to be drawn.
     //------------------------------------------------------------------------
     // Copyright (c) 2005-2016 Opal Kelly Incorporated
     
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

     // OK MIG DDR3 User interface
     ddr3_test ddr3_ui_0 (
         .clk                (clk_ddr_ui), // from the DDR3 MIG "ui_clk"
         .reset              (ep43trig[`DDR3_UI_RESET]),
         .write1_en          (ep03wire[`DDR3_DAC_WRITE_ENABLE]),
         .read1_en           (ep03wire[`DDR3_DAC_READ_ENABLE]),
         .write2_en          (ep03wire[`DDR3_ADC_WRITE_ENABLE]),
         .read2_en           (ep03wire[`DDR3_ADC_TRANSFER_ENABLE]),
         .calib_done         (init_calib_complete),
         
         .adc_addr_reset (ep43trig[`DDR3_ADC_ADDR_RESET]),
         .adc_addr_restart (ep03wire[`DDR3_ADC_ADDR_SET]),

         .ib_re              (pipe_in_read),
         .ib_data            (pipe_in_data),
         .ib_count           (pipe_in_rd_count),
         .ib_valid           (pipe_in_valid),
         .ib_empty           (pipe_in_empty),

         .ob_we              (pipe_out_write),
         .ob_data            (pipe_out_data),
         .ob_count           (pipe_out_wr_count),
         .ob_full            (pipe_out_full),
         
         .ib2_re              (pipe_in2_read),
         .ib2_data            (pipe_in2_data),
         .ib2_count           (pipe_in2_rd_count),
         .ib2_valid           (pipe_in2_valid),
         .ib2_empty           (pipe_in2_empty),

         .ob2_we              (pipe_out2_write),
         .ob2_data            (pipe_out2_data),
         .ob2_count           (pipe_out2_wr_count),
         .ob2_full            (pipe_out2_full),
         
         .adc_data_count        (adc_data_cnt),

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

     //Block Throttle OK interfaces: check for enough space or enough data
     always @(posedge okClk) begin
         // Check for enough space in input FIFO to pipe in another block
         // The count is compared against a reduced size to account for delays in FIFO count updates.
         if(pipe_in_wr_count <= (FIFO_SIZE-BUFFER_HEADROOM-BLOCK_SIZE) ) begin
             pipe_in_ready <= 1'b1;
         end
         else begin
             pipe_in_ready <= 1'b0;
         end
         // Check for enough data in FIFO to pipe out another block -- this is to DACs -- reading from pipeOut is not optimized
         if(pipe_out_rd_count >= BLOCK_SIZE) begin  // size is in 4 bytes so block size is 512*4 = 2048 bytes 
             pipe_out_ready <= 1'b1;
         end
         else begin
             pipe_out_ready <= 1'b0;
         end
        // Check for enough space in ADC output FIFO to pipe out another block
         if(pipe_out2_rd_count >= BLOCK_SIZE) begin // size is in 4 bytes so block size is 512*4 = 2048 bytes 
             pipe_out2_ready <= 1'b1;
         end
         else begin
             pipe_out2_ready <= 1'b0;
         end
     end

     // DDR debug signals
     assign up[0] = pipe_out2_write; // pipe_out2_full; //pipe_in_ready;
     assign up[1] = pipe_out2_data[0]; // pipe_out2_empty; // pipe_out_ready;
     assign up[2] = pipe_out2_data[15]; //pipe_in2_full;
     assign up[3] = pipe_out2_data[255]; //pipe_in2_full; // po0_ep_read;
     assign up[4] = ddr_dac_rd_en;
     assign up[5] = ddr_data_valid;
      
      okWireOut      wo03 (.okHE(okHE), .okEH(okEHx[ 12*65 +: 65 ]), .ep_addr(`DDR3_ADC_DATA_CNT), .ep_datain(adc_data_cnt));
      okBTPipeIn     pi0  (.okHE(okHE), .okEH(okEHx[ 13*65 +: 65 ]), .ep_addr(`DDR3_BLOCK_PIPE_IN), .ep_write(pi0_ep_write), .ep_blockstrobe(), .ep_dataout(pi0_ep_dataout), .ep_ready(pipe_in_ready));
      //PipeOuts
      //     EP_READ    Output    Active-high read signal.  Data must be provided in the cycle following as assertion of this signal.
      //     EP_BLOCKSTROBE    Output    Active-high block strobe.  This is asserted for one cycle just before a block of data is read.
      //     EP_READY    Input    Active-high ready signal.  Logic should assert this signal when it is prepared to transmit a full block of data.     
      okBTPipeOut    po0  (.okHE(okHE), .okEH(okEHx[ 14*65 +: 65 ]), .ep_addr(`DDR3_BLOCK_PIPE_OUT_FG), .ep_read(po0_ep_read),   .ep_blockstrobe(), .ep_datain(po0_ep_datain[31:0]),   .ep_ready(pipe_out_ready));
      okBTPipeOut    po2  (.okHE(okHE), .okEH(okEHx[ 22*65 +: 65 ]), .ep_addr(`DDR3_BLOCK_PIPE_OUT), .ep_read(po2_ep_read),   .ep_blockstrobe(), .ep_datain(po2_ep_datain[31:0]),   .ep_ready(pipe_out2_ready));
 
      fifo_w32_1024_r256_128 fg_pipein_fifo (  // Function generator data from the host via pi0 
          .rst(ep_wire_filtsel[`DDR3_FIFO_DAC_IN_RST]),
          .wr_clk(okClk),
          .rd_clk(clk_ddr_ui),
          .din(pi0_ep_dataout), // Bus [31 : 0]
          .wr_en(pi0_ep_write),
          .rd_en(pipe_in_read),
          .dout(pipe_in_data), // Bus [255 : 0] -- to DDR 
          .full(pipe_in_full),
          .empty(pipe_in_empty),
          .valid(pipe_in_valid),
          .rd_data_count(pipe_in_rd_count), // Bus [6 : 0]  //128 available for reading (by DDR)
          .wr_data_count(pipe_in_wr_count)); // Bus [9 : 0] //1024 available for writing 

    reg [15:0] adc_debug_cnt; 
    always @(posedge clk_sys or posedge sys_rst) begin 
        if (sys_rst == 1'b1) adc_debug_cnt <= 16'b0;
        else if (ddr_data_valid == 1'b1) adc_debug_cnt <= adc_debug_cnt + 1'b1;
    end
    
    reg [47:0] timestamp;
    always @(posedge clk_sys) begin
        if (sys_rst == 1'b1) timestamp <= 48'b0;
        else timestamp <= timestamp + 1'b1;  //32 bit is 21.7 seconds; 48 bits is 16.23 days
    end

    reg [47:0] timestamp_snapshot;
    always @(posedge clk_sys) begin
        if (sys_rst == 1'b1) timestamp_snapshot <= 48'b0;
        else if (adc_ddr_wr_en == 1'b1 & ((cycle_cnt == 4'd5) | (cycle_cnt == 4'd0)) ) timestamp_snapshot <= timestamp;
    end

    reg [127:0] adc_ddr_data;
    reg adc_ddr_wr_en;
    
    wire [23:0] dac_val_out[0:(AD5453_NUM-1)]; //for AD5453 data 
    wire dac_val_out_ready[0:(AD5453_NUM-1)]; //for AD5453 data 

    always @(*) begin 
        if (ep03wire[`DDR3_ADC_DEBUG] == 1'b0) begin 
            case (cycle_cnt)
                4'd9:    adc_ddr_data = {ads_last_read[15:0],       timestamp_snapshot[15:0],  dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd8:    adc_ddr_data = {ads_last_read[31:16],      timestamp_snapshot[31:16], dac_val_out[3][15:0], dac_val_out[1][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd7:    adc_ddr_data = {timestamp_snapshot[47:32], dac_val_out[4][15:0],      dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd6:    adc_ddr_data = {16'haa55,                  dac_val_out[5][15:0],      dac_val_out[3][15:0], dac_val_out[1][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd5:    adc_ddr_data = {{11'h28b, ads_sequence_count},                  dac_val_out[4][15:0],      dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};

                4'd4:    adc_ddr_data = {ads_last_read[15:0],       timestamp_snapshot[15:0],  dac_val_out[3][15:0], dac_val_out[1][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd3:    adc_ddr_data = {ads_last_read[31:16],      timestamp_snapshot[31:16], dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd2:    adc_ddr_data = {timestamp_snapshot[47:32], dac_val_out[5][15:0],      dac_val_out[3][15:0], dac_val_out[1][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd1:    adc_ddr_data = {16'h77bb,                  dac_val_out[4][15:0],      dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                4'd0:    adc_ddr_data = { {11'h28c, ads_sequence_count},                  dac_val_out[5][15:0],      dac_val_out[3][15:0], dac_val_out[1][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
                
                default: adc_ddr_data = {ads_last_read[15:0],       timestamp_snapshot[15:0],  dac_val_out[2][15:0], dac_val_out[0][15:0], adc_val[3][15:0], adc_val[2][15:0], adc_val[1][15:0], adc_val[0][15:0]};
            endcase 
            if (ep03wire[`DDR3_USE_ADC_READY] == 1'b1) adc_ddr_wr_en = write_en_adc_o[0]; // Pulse to use to synchronize DACs and the ADS8686
            else adc_ddr_wr_en = adc_rd_en_emulator;
        end
        else begin
            adc_ddr_data = {po0_ep_datain[47:0], adc_debug_cnt[15:0]};
            adc_ddr_wr_en = ddr_data_valid;
        end
    end

    // synchronize the OpalKelly wire in DDR3_READ_ENABLE signals with the cycle count so data always starts at cycle cnt of 9
    reg adc_ddr_wr_en_slow;    
    always @(posedge clk_sys) begin
        if (ep_wire_filtsel[`DDR3_FIFO_ADC_IN_RST] == 1'b1) adc_ddr_wr_en_slow <= 1'b0;
        else if ((adc_ddr_wr_en == 1'b1) & (cycle_cnt == 4'd0)) adc_ddr_wr_en_slow <= ep03wire[`DDR3_ADC_WRITE_ENABLE];
    end
    
    // TODO: timing may change so that adc_ddr_wr_en is not the starting pulse
    reg dac_ddr_read_en_slow;    
    always @(posedge clk_sys) begin
        if (ep_wire_filtsel[`DDR3_FIFO_DAC_READ_RST] == 1'b1) dac_ddr_read_en_slow <= 1'b0;
        else if ((adc_ddr_wr_en == 1'b1) & (cycle_cnt == 4'd0)) dac_ddr_read_en_slow <= ep03wire[`DDR3_DAC_READ_ENABLE];
    end
    
     fifo_w128_512_r256_256 adc_to_ddr_fifo (  //ADC data input, output to DDR
         .rst(ep_wire_filtsel[`DDR3_FIFO_ADC_IN_RST]), // supports asynchronous reset -- asserted for at least three clock cycles of slowest clock
         .wr_clk(clk_sys),
         .rd_clk(clk_ddr_ui),
         .din(adc_ddr_data),
         .wr_en(adc_ddr_wr_en & adc_ddr_wr_en_slow), //
         .rd_en(pipe_in2_read),
         .dout(pipe_in2_data), // Bus [255 : 0] - to DDR 
         .full(pipe_in2_full),
         .empty(pipe_in2_empty),
         .valid(pipe_in2_valid),  //output 
         .rd_data_count(pipe_in2_rd_count), // Bus [6 : 0]  //128 available for reading (by DDR)
         .wr_data_count(pipe_in2_wr_count)); // Bus [7 : 0] //256 available for writing 

    // DDR: read from DDR and 1) output data to DACs and 2) output data to host through BTPipeOut

     fifo_w256_256_r128_512 ddr_to_dac_fifo_ddr ( //Data in from DDR -> Output to DACs 
         .rst(ep_wire_filtsel[`DDR3_FIFO_DAC_READ_RST]), // supports asynchronous reset 
         .wr_clk(clk_ddr_ui),
         .rd_clk(clk_sys),
         .din(pipe_out_data), // Bus [255 : 0] -- from DDR 
         .wr_en(pipe_out_write),
         .rd_en(ddr_dac_rd_en & dac_ddr_read_en_slow),
         .dout(po0_ep_datain), // Bus [127 : 0]
         .full(pipe_out_full),
         .empty(pipe_out_empty),
         .valid(ddr_data_valid), //output 
         .rd_data_count(pipe_out_rd_count), // Bus [7 : 0]
         .wr_data_count(pipe_out_wr_count)); // Bus [6 : 0]

     fifo_w256_128_r32_1024 okPipeOut_fifo_ddr2 (  // Output ADC data from DDR to PipeOut (does not need to be syncrhonized with cycle cnt)
         .rst(ep_wire_filtsel[`DDR3_FIFO_ADC_TRANSFER_RST]), // supports asynchronous reset 
         .wr_clk(clk_ddr_ui),
         .rd_clk(okClk),
         .din(pipe_out2_data), // Bus [255 : 0] -- from DDR 
         .wr_en(pipe_out2_write),
         .rd_en(po2_ep_read),
         .dout(po2_ep_datain), // Bus [31 : 0]
         .full(pipe_out2_full),
         .empty(pipe_out2_empty),
         .valid(),  //output
         .rd_data_count(pipe_out2_rd_count), // Bus [9 : 0]
         .wr_data_count(pipe_out2_wr_count)); // Bus [6 : 0]
    /* ------------------ END DDR3 ------------------- */
    
    /*---------------- DAC80508 -------------------*/
    wire [31:0] ds_spi_data[0:(DAC80508_NUM - 1)];
    wire [31:0] ds_host_spi_data[0:(DAC80508_NUM - 1)];
    wire [(DAC80508_NUM - 1):0] rd_en_ds;
    wire [(DAC80508_NUM - 1):0] data_ready_ds;
    wire [(DAC80508_NUM - 1):0] spi_host_trigger_ds; 
    
    genvar k;
    generate
    for (k=0; k<=(DAC80508_NUM-1); k=k+1) begin : dac80508_gen
    
        okWireIn wi_ddr_spi (.okHE(okHE), .ep_addr(`DAC80508_HOST_WIRE_IN_GEN_ADDR + k), .ep_dataout(ds_host_spi_data[k]));
        assign spi_host_trigger_ds[k] = ep41trig[`DAC80508_HOST_TRIG_GEN_BIT + k];
        
        mux8to1_32wide spi_mux_bus( // lower 24 bits are data, most-significant bit is the data_ready signal 
            .datain_0({ddr_data_valid, 11'b0, 1'b1, po0_ep_datain[ (k*2*16 + 14) +:2], po0_ep_datain[((k*2 + 1)*16 + 14) +:1], po0_ep_datain[(AD5453_NUM*16 + k*16) +:16]}),
            //                            [15:14] for k=0                 [30:30] for k =0        ,              [111:96] for k  = 0
            // Leading 1 to complete OUT channel address on chip (for DAC0 - DAC7 always 1),
            // last 2 bits of an AD5453 16-bit group for addressing,
            // 15th bit of the next AD5453 group to complete the address,
            // 16 bits data from DAC80508 group
            .datain_1({spi_host_trigger_ds[k], 7'b0, ds_host_spi_data[k][23:0]}), // TODO: determine size for this, I believe it should be 24 bits of SPI message that the host must determine because the spi_fifo_driven is expecting 24 bits
            .datain_2({ads_data_valid, 11'b0, 1'b1, ds_host_spi_data[k][2:0], ads_data_out[15:0]}),  // data from ADS8686
            .datain_3({ads_data_valid, 11'b0, 1'b1, ds_host_spi_data[k][2:0], ads_data_out[31:16]}), // Default to output channel DAC0
            .datain_4({adc_valid_pulse[0], 11'b0, 1'b1, ds_host_spi_data[k][2:0], adc_val_reg[0][15:0]}), // data from AD7961, channel is selected by input wire 
            .datain_5({adc_valid_pulse[1], 11'b0, 1'b1, ds_host_spi_data[k][2:0], adc_val_reg[1][15:0]}), // data from AD7961, channel is selected by input wire 
            .datain_6({adc_valid_pulse[2], 11'b0, 1'b1, ds_host_spi_data[k][2:0], adc_val_reg[2][15:0]}), // data from AD7961, channel is selected by input wire 
            .datain_7({adc_valid_pulse[3], 11'b0, 1'b1, ds_host_spi_data[k][2:0], adc_val_reg[3][15:0]}), // data from AD7961, channel is selected by input wire 
            .sel(ep03wire[(`DAC80508_DATA_SEL_GEN_BIT + k*`DAC80508_DATA_SEL_GEN_BIT_LEN) +: `DAC80508_DATA_SEL_GEN_BIT_LEN]),
            .dataout({ds_spi_data[k]})
        );
        
        assign data_ready_ds[k] = ds_spi_data[k][31];
            
        spi_fifo_driven #(.ADDR(`DAC80508_REGBRIDGE_OFFSET_GEN_ADDR + k*20))spi_fifo1 (
                 .clk(clk_sys), .fifoclk(okClk), .rst(sys_rst),
                 .ss_0(ds_csb[k]), .mosi_0(ds_sdi[k]), .sclk_0(ds_sclk[k]), 
                 .data_rdy_0(data_ready_ds[k]), 
                 .data_i(ds_spi_data[k][23:0]), 
                 // register bridge 
                 .ep_write(regWrite),           //input wire 
                 .ep_address(regAddress),       //input wire [31:0] 
                 .ep_dataout_coeff(regDataOut), //input wire [31:0] (TODO: name is confusing}. Output from OKRegisterBridge

                 // All DAC80508 output channels have the form {0b1, number_output_channel}
                 .rd_en_0(rd_en_ds[k]),   //out: debug of state machine
                 .regTrigger(ep40trig[`DAC80508_REG_TRIG_GEN_BIT + k]), //input: state machine to init after SPI clock divider is re-programmed
                 .filter_sel(ep_wire_filtsel[(`DAC80508_FILTER_SEL_GEN_BIT + k*`DAC80508_FILTER_SEL_GEN_BIT_LEN) +: 1]),
                 .dac_val_out(),
                 .data_out_ready()
                 );
        assign ds_sdo[k] = 1'b1; // sdo for the DAC80508C is connected to CLRB -- force to logic high
        end
    endgenerate
    /*---------------- END DAC80508 -------------------*/
    
    /* ------------------ AD5453 SPI ------------------- */
    wire [(AD5453_NUM-1):0] rd_en_fast_dac;
    wire [(AD5453_NUM-1):0] data_ready_fast_dac;
    wire [(AD5453_NUM-1):0] filter_data_ready_fast_dac;
   
    wire [31:0] spi_data[0:(AD5453_NUM-1)];
    wire [31:0] filter_spi_data[0:(AD5453_NUM-1)];
    wire [31:0] host_spi_data[0:(AD5453_NUM-1)];
    wire [(AD5453_NUM-1):0] spi_host_trigger_fast_dac; 

    wire [31:0] coeff_debug_out1[0:(AD5453_NUM-1)];
    wire [31:0] coeff_debug_out2[0:(AD5453_NUM-1)];
    
    reg [13:0] last_ddr_read[0:(AD5453_NUM-1)];
    reg ddr_data_valid_norepeat[0:(AD5453_NUM-1)]; // Skip DAC update if the value is the same. Reduces digital switching noise. 
    
    wire [31:0] ep_wire_filtdata;
    okWireIn wi_ad5453_filtdata (.okHE(okHE), .ep_addr(`AD5453_SERIES_RES_WIRE_IN), .ep_dataout(ep_wire_filtdata));
    
    genvar p;
    generate
    for (p=0; p<=(AD5453_NUM-1); p=p+1) begin : dac_ad5453_gen
        okWireIn wi_ddr_spi (.okHE(okHE), .ep_addr(`AD5453_HOST_WIRE_IN_GEN_ADDR + p), .ep_dataout(host_spi_data[p]));
        
        assign spi_host_trigger_fast_dac[p] = ep41trig[`AD5453_HOST_TRIG_GEN_BIT + p];
        
        // Skip DAC update DDR SPI if the values don't change (adds one clock cycle of latency -- 5 ns)
        always @(posedge clk_sys) begin
            if (ddr_data_valid==1'b1) last_ddr_read[p] <= po0_ep_datain[(p*16) +:14];
        end        
        always @(posedge clk_sys) begin
            if (last_ddr_read[p] == po0_ep_datain[(p*16) +:14]) ddr_data_valid_norepeat[p] <= 1'b0;
            else ddr_data_valid_norepeat[p] <= ddr_data_valid;
        end
                
        mux8to1_32wide spi_mux_bus_fast_dac( // lower 24 bits are data, most-significant bit (bit 31) is the data_ready signal 
            .datain_0({ddr_data_valid, 17'b0, po0_ep_datain[(p*16) +:14]}),
            .datain_1({spi_host_trigger_fast_dac[p], 7'b0, host_spi_data[p][23:0]}), 
            .datain_2({ads_data_valid, 15'b0, ads_data_out[15:0]}), // 
            .datain_3({ddr_data_valid_norepeat[p], 17'b0, last_ddr_read[p]}), // 
            .datain_4({write_en_adc_o[0], 15'b0, adc_val[0][15:0]}), // data from AD7961  
            .datain_5({write_en_adc_o[1], 15'b0, adc_val[1][15:0]}), // data from AD7961
            .datain_6({write_en_adc_o[2], 15'b0, adc_val[2][15:0]}), // data from AD7961
            .datain_7({write_en_adc_o[3], 15'b0, adc_val[3][15:0]}), // data from AD7961
            .sel(ep03wire[(`AD5453_DATA_SEL_GEN_BIT + p*`AD5453_DATA_SEL_GEN_BIT_LEN) +: `AD5453_DATA_SEL_GEN_BIT_LEN]),
            .dataout({spi_data[p]})
        );
        
        assign data_ready_fast_dac[p] = spi_data[p][31]; // assign MUX output MSB to the data_ready signal. 
        
        mux8to1_32wide filter_spi_mux_bus_fast_dac( // lower 24 bits are data, most-significant bit (bit 31) is the data_ready signal 
            .datain_0({ddr_data_valid, 17'b0, po0_ep_datain[(p*16) +:14]}),
            .datain_1({spi_host_trigger_fast_dac[p], 7'b0, host_spi_data[p][23:0]}), 
            .datain_2({ads_data_valid, 15'b0, ads_data_out[15:0]}), // 
            .datain_3({ddr_data_valid_norepeat[p], 17'b0, last_ddr_read[p]}), // 
            .datain_4({write_en_adc_o[0], 15'b0, adc_val[0][15:0]}), // data from AD7961  
            .datain_5({write_en_adc_o[1], 15'b0, adc_val[1][15:0]}), // data from AD7961
            .datain_6({write_en_adc_o[2], 15'b0, adc_val[2][15:0]}), // data from AD7961
            .datain_7({write_en_adc_o[3], 15'b0, adc_val[3][15:0]}), // data from AD7961
            .sel(ep_wire_filtdata[(`AD5453_FILTER_DATA_SEL_GEN_BIT + p*`AD5453_FILTER_DATA_SEL_GEN_BIT_LEN) +: `AD5453_FILTER_DATA_SEL_GEN_BIT_LEN]),
            .dataout({filter_spi_data[p]})
        );
        
        assign filter_data_ready_fast_dac[p] = filter_spi_data[p][31]; // assign MUX output MSB to the data_ready signal. 
            
        spi_fifo_driven #(.ADDR(`AD5453_REGBRIDGE_OFFSET_GEN_ADDR + p*20))spi_fifo0 (
                 .clk(clk_sys), .fifoclk(okClk), .rst(sys_rst),
                 .ss_0(d_csb[p]), .mosi_0(d_sdi[p]), .sclk_0(d_sclk[p]), 
                 .data_rdy_0(data_ready_fast_dac[p]), 
                 .data_i(spi_data[p]),
                 // register bridge 
                 .ep_write(regWrite),           //input wire 
                 .ep_address(regAddress),       //input wire [31:0] 
                 .ep_dataout_coeff(regDataOut), //input wire [31:0] (TODO: name is confusing}. Output from OKRegisterBridge

                 .rd_en_0(rd_en_fast_dac[p]),   //out: debug only 
                 .regTrigger(ep40trig[`AD5453_REG_TRIG_GEN_BIT + p]), //input  -- sends state machine to init. Use for after updates via register bridge.
                 .filter_sel(ep_wire_filtsel[`AD5453_FILTER_SEL_GEN_BIT + p]),
                 .coeff_debug_out1(coeff_debug_out1[p]),
                 .coeff_debug_out2(coeff_debug_out2[p]),
                 .dac_val_out(dac_val_out[p]),
                 .data_out_ready(dac_val_out_ready[p]),
                 .filter_data_i(filter_spi_data[p]),
                 .data_rdy_0_filt(filter_data_ready_fast_dac[p]),
                 .downsample_en(ep_wire_filtdata[`AD5453_DOWNSAMPLE_ENABLE_GEN_BIT + p]),
                 .sum_en(ep_wire_filtdata[`AD5453_SUMMATION_ENABLE_GEN_BIT + p])
                 );
        end
    endgenerate

    // Four wire outs for debug of filter loading. TODO: generally unecessary now. 
     okWireOut      wo06 (.okHE(okHE), .okEH(okEHx[ 18*65 +: 65 ]), .ep_addr(`AD5453_COEFF_DEBUG_0), .ep_datain(ep_wire_filtsel));
     okWireOut      wo07 (.okHE(okHE), .okEH(okEHx[ 19*65 +: 65 ]), .ep_addr(`AD5453_COEFF_DEBUG_1), .ep_datain(coeff_debug_out2[0]));
     okWireOut      wo08 (.okHE(okHE), .okEH(okEHx[ 20*65 +: 65 ]), .ep_addr(`AD5453_COEFF_DEBUG_2), .ep_datain(coeff_debug_out1[1]));
     okWireOut      wo09 (.okHE(okHE), .okEH(okEHx[ 21*65 +: 65 ]), .ep_addr(`AD5453_COEFF_DEBUG_3), .ep_datain(coeff_debug_out2[1]));

    /* ----------------- END AD5453 ------------------------------------ */

    /*---------------- I2C -------------------*/
    /*---------------- daughercard I2C -------------------*/
    wire [15:0] i2c_memdin[0:(I2C_DCARDS_NUM-1)];
    wire [7:0] i2c_memdout[0:(I2C_DCARDS_NUM-1)];

    generate
        for (i = 0; i < (I2C_DCARDS_NUM / 2); i = i + 1) begin : i2c_dc_wire_gen
            okWireIn wi_i2c_dc0 (.okHE(okHE), .ep_addr(`I2CDC_WIRE_IN + i), .ep_dataout({i2c_memdin[(i * 2) + 1], i2c_memdin[i * 2]}));
        end
    endgenerate

    generate
        for (i = 0; i < (I2C_DCARDS_NUM / 4); i = i + 1) begin
            okWireOut wo_i2c_dc (.okHE(okHE), .okEH(okEHx[ (15 + i)*65 +: 65 ]), .ep_addr(`I2CDC_WIRE_OUT_GEN_ADDR + i),
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

    wire [15:0] i2c_aux_memdin[0:1];
    wire [7:0] i2c_aux_memdout[0:1];

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
        .i2c_sdat (ls_sda),        // inout
        .i2c_sclk_pull_up (i2c_test_sclk_pull_up),
        .i2c_sdat_pull_up (i2c_test_sdat_pull_up)
    );

    wire i2c_qw_po_re;
    wire [31:0] fifo_i2c_data;

	 okPipeOut i2c_qw_po (.okHE(okHE), .okEH(okEHx[ 28*65 +: 65 ]), .ep_addr(`I2CDAQ_PIPE_OUT_GEN_ADDR+1), 
	                           .ep_read(i2c_qw_po_re), .ep_datain(fifo_i2c_data));

    // The FIFO rst signal needs to be at least 3 (slowest) clock cycles wide
    wire i2c_fifo_reset;
    reg [3:0] i2c_fifo_reset_cnt;    
    // stretch the reset signal 
    always @(posedge clk_sys) begin         
        if (ep41trig[`I2CDAQ_FIFO_RESET_GEN_BIT+1] == 1'b1) i2c_fifo_reset_cnt = 4'b0;
        else if (i2c_fifo_reset_cnt < 4'd15) i2c_fifo_reset_cnt = i2c_fifo_reset_cnt + 1'b1;        
    end // reset_cnt will idle at 15 
    
    assign i2c_fifo_reset = (i2c_fifo_reset_cnt < 4'd15);

	// QW 3.3v I2C bus (used for auxiliary I2C. e.g. TOF controller)
    i2cController_wPipe i2c_controller_5 (
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
        .i2c_sdat (qw_sda),        // inout
        
        // additional for FIFO output pipe
        .ok_clk(okClk),
        .fifo_rst(i2c_fifo_reset),
        .fifo_rd_en(i2c_qw_po_re),
        .fifo_empty(),
        .fifo_data(fifo_i2c_data)
    );
    /*---------------- End I2C -------------------*/

	 //module to create a one second pulse on one of the LEDs (keepAlive test)
	 one_second_pulse out_pulse(
	 .clk(clk_sys), .rst(sys_rst), .slow_pulse(led[0])
	 );
	 
	 /*---------------- FPGA test -------------------*/
	 // Set up Endpoints
	 reg [31:0] fpga_test_static_wo;
	 okWireOut fpga_test_wo_0 (.okHE(okHE), .okEH(okEHx[ 23*65 +: 65 ]), .ep_addr(`FPGATEST_STATIC_READ_WO), .ep_datain(fpga_test_static_wo));
	 
	 reg [127:0] fpga_test_static_po = 128'd1234567890987654321;
     reg [31:0] fpga_test_static_po_data;
	 wire fpga_test_static_po_read;
	 okPipeOut fpga_test_po_0 (.okHE(okHE), .okEH(okEHx[ 24*65 +: 65 ]), .ep_addr(`FPGATEST_STATIC_READ_PO), .ep_read(fpga_test_static_po_read), .ep_datain(fpga_test_static_po_data));
	 
	 wire [31:0] fpga_test_looped_wi;
     wire [31:0] fpga_test_looped_wo;
     okWireIn fpga_test_wi_0 (.okHE(okHE), .ep_addr(`FPGATEST_LOOPED_WI), .ep_dataout(fpga_test_looped_wi));
     okWireOut fpga_test_wo_1 (.okHE(okHE), .okEH(okEHx[ 25*65 +: 65 ]), .ep_addr(`FPGATEST_LOOPED_WO), .ep_datain(fpga_test_looped_wo));
     
     wire [31:0] fpga_test_ti;
     reg fpga_test_ti_confirm;
     okTriggerIn fpga_test_ti_0 (.okHE(okHE), .ep_addr(`FPGATEST_TI_ADDR), .ep_clk(okClk), .ep_trigger(fpga_test_ti[`FPGATEST_TI]));
     okWireOut fpga_test_wo_2 (.okHE(okHE), .okEH(okEHx[ 26*65 +: 65 ]), .ep_addr(`FPGATEST_TI_CONFIRM), .ep_datain(fpga_test_ti_confirm));
     
     wire [31:0] fpga_test_to;
     okTriggerOut fpga_test_to_0 (.okHE(okHE), .okEH(okEHx[ 27*65 +: 65 ]), .ep_addr(`FPGATEST_TO_ADDR), .ep_clk(clk_sys), .ep_trigger(fpga_test_to[`FPGATEST_TO]));  // bit 0 -- not used
	 
	 // Assign values for static reads
	 always @(*) begin
	   fpga_test_static_wo = 32'd123456789;
     end

    reg [1:0] fpga_test_po_state;
    reg [1:0] fpga_test_po_nextstate;
     always @(posedge okClk) begin
         if (fpga_test_static_po_read) begin
           fpga_test_po_state <= fpga_test_po_nextstate;
           case(fpga_test_po_state)
               0 : fpga_test_static_po_data <= fpga_test_static_po[31:0];
               1 : fpga_test_static_po_data <= fpga_test_static_po[63:32];
               2 : fpga_test_static_po_data <= fpga_test_static_po[95:64];
               3 : fpga_test_static_po_data <= fpga_test_static_po[127:96];
               default : fpga_test_static_po_data <= fpga_test_static_po[31:0];
            endcase
       end
     end

    always @(*) begin
         case(fpga_test_po_state)
            0 : fpga_test_po_nextstate = 1;
            1 : fpga_test_po_nextstate = 2;
            2 : fpga_test_po_nextstate = 3;
            3 : fpga_test_po_nextstate = 0;
            default : fpga_test_po_nextstate = 0;
         endcase
     end
     
     // Connect looped WireIn, WireOut
     assign fpga_test_looped_wi = fpga_test_looped_wo;
     
     // Set up input trigger confirm
     always @(posedge fpga_test_ti) fpga_test_ti_confirm = 1;
     
     // Set up continuous TriggerOut pulses
     assign fpga_test_to = 1;
     /*---------------- End FPGA test -------------------*/
     
     /*---------------- I2C test -------------------*/
     // Set up Endpoints
     reg [63:0] i2c_test_message;
     okWireOut i2c_test_message_0 (.okHE(okHE), .okEH(okEHx[ 31*65 +: 65 ]), .ep_addr(`I2CTEST_MESSAGE_0), .ep_datain(i2c_test_message[31:0]));
     okWireOut i2c_test_message_1 (.okHE(okHE), .okEH(okEHx[ 32*65 +: 65 ]), .ep_addr(`I2CTEST_MESSAGE_1), .ep_datain(i2c_test_message[63:32]));
     
     // SCL and SDA pulled from tri-state version of SCL, SDA of level shifted bus (i2c_controller_4)
     // i2c_test_sclk_pull_up;
     // i2c_test_sdat_pull_up;
         
     // Set up message output
     // Shift register to store transmission from the controller and read it on a WireOut
     // No reset because we can just read the newest N bits based on how many bits we sent with the last transmission
     // i2c_read_long reads 2 bytes, has register byte, 2 slave bytes -> max 5 bytes = 40 bits
     always @(posedge i2c_test_sclk_pull_up) begin
         i2c_test_message[63:1] <= i2c_test_message[62:0];
         i2c_test_message[0] <= i2c_test_sdat_pull_up;
     end
     /*---------------- End I2C test -------------------*/

endmodule
