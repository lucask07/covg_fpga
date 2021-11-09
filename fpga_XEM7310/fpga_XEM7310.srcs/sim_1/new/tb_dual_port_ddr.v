`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/08/2021 03:06:30 PM
// Design Name: 
// Module Name: tb_dual_port_ddr
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_dual_port_ddr;

`timescale 1ns / 1ps
//------------------------------------------------------------------------------
//----------- Module Declaration -----------------------------------------------
//------------------------------------------------------------------------------
reg clk_sys;
reg clk_ddr_ui; 
reg ddr_reset;
    /* --------------- DDR3 ---------------------------*/
     ////////////////////////////*DDR3 INTERFACE INSTANTIATIONS*//////////////////////////////////////////////
     // OK RAMTest Parameters

 /*
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

     wire          clk_ddr_ui;
     wire          rst_ddr_ui;

     wire [31:0]  ep03wire;



     
     wire          ddr3_rst;// MIG/DDR3 synchronous reset


/*
     reset_synchronizer u_MIG_sync_rst( //TODO: move this to a trigger in
     .clk(clk_sys),
     .async_rst(ep03wire[`DDR3_RESET]),
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
         .INDEX2              (INDEX2),

         .reset              (ddr3_rst | rst_ddr_ui),
         .reads_en           (ep03wire[`DDR3_READ_ENABLE]),
         .writes_en          (ep03wire[`DDR3_WRITE_ENABLE]),
         .fg_reads_en        (ep03wire[`DDR3_FG_READ_ENABLE]),
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
*/

     //wire         pipe_in_read;
     //wire [255:0] pipe_in_data;
     //wire [6:0]   pipe_in_rd_count;
     //wire [9:0]   pipe_in_wr_count;
     //wire         pipe_in_valid;
     //wire         pipe_in_full;
     //wire         pipe_in_empty;
     //reg          pipe_in_ready;

     //wire         pipe_out_write;
     //wire [255:0] pipe_out_data;
     wire [8:0]   pipe_out_rd_count; //LJK to change
     wire [6:0]   pipe_out_wr_count;
     wire         pipe_out_full;
     wire         pipe_out_empty;
     reg          pipe_out_ready;

     //wire         pipe_in2_read;
     //wire [255:0] pipe_in2_data;
     wire [6:0]   pipe_in2_rd_count;
     wire [8:0]   pipe_in2_wr_count;  //LJK to change 
     //wire         pipe_in2_valid;
     //wire         pipe_in2_full;
     //wire         pipe_in2_empty;
     //reg          pipe_in2_ready;

     //wire         pipe_out2_write;
     //wire [255:0] pipe_out2_data;
     //wire [9:0]   pipe_out2_rd_count;
     //wire [6:0]   pipe_out2_wr_count;
     //wire         pipe_out2_full;
     //wire         pipe_out2_empty;
     //reg          pipe_out2_ready;

     wire [127:0]  po0_ep_datain;// MIG/DDR3 FIFO data out to DACs 
     
     //wire         po2_ep_read;
     //wire [31:0]  po2_ep_datain;// MIG/DDR3 ADC FIFO data out
     //wire [15:0] adc_data_cnt; // count of ADC words in DDR
     
     // Pipe Fifos
     //wire         pi0_ep_write;
     //wire         po0_ep_read;
     //wire [31:0]  pi0_ep_dataout;
     //wire [31:0] INDEX;
     //wire [31:0] INDEX2;

     reg[7:0] five_msps_adc_pulse = 8'd0;
     reg adc_emulator_valid;
     always @(posedge clk_ddr_ui) begin
        if (five_msps_adc_pulse == 8'b0) begin
            five_msps_adc_pulse <= 8'd39;
            adc_emulator_valid <= 1'b1;
        end
        else begin
            five_msps_adc_pulse <= five_msps_adc_pulse - 8'b1;
            adc_emulator_valid <= 1'b0;
        end
    end

reg [255:0]dac_ddr_data;
wire ad5453_clk_en;
assign ad5453_clk_en = adc_emulator_valid;

     fifo_w64_512_r256_128_1 adc_ddr_fifo (  //ADC data input, output to DDR
         .rst(ddr_reset),
         //.wr_clk(adc_timing_clk),
         .wr_clk(clk_sys),
         .rd_clk(clk_ddr_ui),
         //.din(adc_ddr_debug_cnt), // Bus [63 : 0]
         .din(po0_ep_datain[63:0]),
         //.wr_en(write_en_adc_o[0]),
         .wr_en(ad5453_clk_en),
         .rd_en(1'b1),
         .dout(pipe_in2_data), // Bus [255 : 0] - to DDR 
         .full(pipe_in2_full),
         .empty(pipe_in2_empty),
         .valid(pipe_in2_valid),  //output 
         .rd_data_count(pipe_in2_rd_count), // Bus [6 : 0]  //128 available for reading (by DDR)
         .wr_data_count(pipe_in2_wr_count)); // Bus [9 : 0] //1024 available for writing 

    // DDR: read from DDR and 1) output data to DACs and 2) output data to host through BTPipeOut

     fifo_w256_128_r128_256_1 okPipeOut_fifo_ddr ( //Data in from DDR -> Output to DACs 
         .rst(ddr_reset), // supports asynchronous reset 
         .wr_clk(clk_ddr_ui),
         .rd_clk(clk_sys),
         .din(dac_ddr_data), // Bus [255 : 0] -- from DDR 
         .wr_en(1'b1),
         .rd_en(ad5453_clk_en),
         .dout(po0_ep_datain), // Bus [127 : 0]
         .full(pipe_out_full),
         .empty(pipe_out_empty),
         .valid(dac_data_valid), //output 
         .rd_data_count(pipe_out_rd_count), // Bus [9 : 0]
         .wr_data_count(pipe_out_wr_count)); // Bus [6 : 0]
 
always @(posedge clk_ddr_ui) begin
    if(ddr_reset == 1'b1) dac_ddr_data <=0;
    else dac_ddr_data <= dac_ddr_data + 1'b1;
end
 
// Generate clock
 initial 
    clk_sys = 1'b0;
 always 
    #5 clk_sys = ~clk_sys; //now 200 MHz sys clock

 initial 
    clk_ddr_ui = 1'b0;
 always 
    #5 clk_ddr_ui = ~clk_ddr_ui; //now 200 MHz sys clock
 
initial begin
    // Initialize Inputs
    #5;
    ddr_reset = 1'b0;
    #200;
    ddr_reset = 1'b1;
    #200;
    ddr_reset = 1'b0;
    #20000;
end
 
 
endmodule
