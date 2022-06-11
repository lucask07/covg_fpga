//`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
// 
// Create Date:    16:58:51 12/28/2020 
// Design Name: 
// Module Name:    spi_fifo_driven 
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
//////////////////////////////////////////////////////////////////////////////////`include "timescale.v"
`include "timescale.v"

module spi_fifo_driven #(parameter ADDR = 0) (
     input wire clk,
	 input wire fifoclk,
     input wire rst,
	 /*****AD796x signals*****/
	 input wire data_rdy_0,
	 output wire ss_0,
     output wire sclk_0,
     output wire mosi_0,
     input wire [23:0] data_i,
     /*****Register Bridge and DDR Signals******/
     //input wire ep_read,
     input wire ep_write,
     input wire [31:0] ep_address,
     input wire [31:0] ep_dataout_coeff,
     //output wire [31:0] ep_datain,
     output wire rd_en_0,
     input wire regTrigger,
     input wire filter_sel,  // if high SPI data is from the filter. 
     output wire [31:0] coeff_debug_out1,
     output wire [31:0] coeff_debug_out2,
     output reg [23:0] dac_val_out,
     output reg data_out_ready,
     output wire [13:0] filter_out_modified
    );
    
      wire cmd_stb;
      wire [33:0] cmd_word;
      wire cmd_busy;
      wire rsp_stb;
      wire [33:0] wb_cmd_dataout;
      wire [29:0] adr; //was 32 bits wide
      wire [31:0] dat_i; 
      wire [31:0] dat_o;
      wire we;
      wire [3:0] sel;
      wire stb;
      wire cyc;
      wire ack;
      wire err;
      wire int_o;
        
      wire full;
      //wire empty;
      wire writeFifo;//this signal and the one below are used to generate the write enable signal for the FIFO
      reg wr_en;//
	 
	 /* ---------------- ADC796x & AD5453 control ----------------*/
	 
	 //instantiations and wires for AD796x and AD5453 SPI control
	 wire cmd_stb_0;
	 wire [33:0] cmd_word_0;
	 wire cmd_busy_0;
	 wire rsp_stb_0;
	 wire [33:0] wb_cmd_dataout_0;
	 wire [7:0] adr_0;
	 wire [31:0] dat_i_0; 
	 wire [31:0] dat_o_0;
	 wire we_0;
	 wire [3:0] sel_0;
	 wire stb_0;
	 wire cyc_0;
	 wire ack_0;
	 wire err_0;
	 wire int_o_0;
	 
	 //wire [13:0] filter_out_modified;
	 
	 reg [23:0] spi_data; 
	 reg data_ready_mux;

     always @(*) begin
         if (filter_sel == 1'b1) spi_data = {11'b0, filter_out_modified};
         else spi_data = data_i;
     end
	 
//	 reg [15:0] filter_data_rdy; // filter output data is registered when clk_enable is =1. Need a one-cycle delay for the data to be stable before input to the SPI command generator
//	 always @(posedge clk) begin
//	   filter_data_rdy[15] <= data_rdy_0;
//	   filter_data_rdy[14:0] <= filter_data_rdy[15:1];
//	 end
	 
	 wire filter_data_rdy;
     always @(*) begin
         if (filter_sel == 1'b1) data_ready_mux = filter_data_rdy;
         else data_ready_mux = data_rdy_0;
     end
	 
	 always @(posedge clk) begin
	    if (rst == 1'b1) dac_val_out <= 24'd0;
        else if (data_ready_mux == 1'b1) dac_val_out <= spi_data;
	 end
	 
     always @(posedge clk) begin
        if (rst == 1'b1) data_out_ready <= 1'b0;
        else if (data_ready_mux == 1'b1) data_out_ready <= 1'b1;
        else data_out_ready <= 1'b0;
     end
	 
	 //State machine/controller for reading a FIFO with data and initiating SPI transfers to AD5453
	 read_fifo_to_spi_cmd #(.ADDR(ADDR)) data_converter_0(
	 .clk(clk), .okClk(fifoclk), .rst(rst), .int_o(int_o_0), .empty(1'b0), .adc_dat_i(spi_data), 
	 .adr(adr_0), .cmd_stb(cmd_stb_0), .cmd_word(cmd_word_0),
	 .rd_en(rd_en_0), .data_rdy(data_ready_mux), .regDataOut(ep_dataout_coeff[15:0]), 
	 .regWrite(ep_write), .regAddress(ep_address[7:0]), .regTrigger(regTrigger)
	 );
	 
	 //Real-Time LPF coefficient reader
     wire write_enable, write_done, read_coeff;
     wire [4:0] write_address;
     wire [31:0] coeffs_in;
     wire [13:0] filter_out;
     wire [4:0] read_address;
     wire [31:0] coeff_bram_in;
	 
	 realTimeLPF_readwrite_coeff coeff_rd_0(
	 .clk(clk), .rst(rst), .wr_en(write_enable), .wr_done(write_done), .wr_adr(write_address),
	 .coeff_out(coeffs_in), .ep_write(ep_write & ((ep_address>(ADDR + 8'h03)) & (ep_address<(ADDR + 8'h13)))), .read_enable(read_coeff), .rd_adr(read_address),
	 .bram_in(coeff_bram_in)
	 );
	 
	 wire [31:0] addra_subtract;
	 assign addra_subtract = ep_address - (32'h4+ADDR);
	 
	 blk_mem_gen_0 realTime_LPF_coeff_BRAM(
	 .addra(addra_subtract[3:0]), .clka(fifoclk), .dina(ep_dataout_coeff), 
	 .ena(ep_write & ((ep_address>(ADDR + 8'h03)) & (ep_address<(ADDR + 8'h13)))), .wea(4'b1111),
	 .addrb({27'b0, read_address}), .clkb(clk), .doutb(coeff_bram_in), .enb(read_coeff)
	 );
	 
	 wire [13:0] filter_out_scaled;
     wire filter_out_ready;
	 
	 // Real-Time LPF
       Butter_pipelined u_Butterworth_0
         (
         .clk(clk),
         .clk_enable(data_rdy_0 | write_enable | write_done),  // input data is registered when clk_enable is high 
         .reset(rst),
         .filter_in(data_i[15:0]), 
         .write_enable(write_enable),
         .write_done(write_done),
         .write_address(write_address[3:0]),
         .coeffs_in(coeffs_in),
         .filter_out(filter_out),
         .data_ready(filter_out_ready)
         //.coeff_debug_out1(coeff_debug_out1),
         //.coeff_debug_out2(coeff_debug_out2)
         );
              
//     LPF_data_modify_fixpt u_dat_mod(  // combinatorial -- not pipeline delay
//     .din(filter_out_scaled), .dout(filter_out_modified)
//     );
     
     LPF_data_scale #(.ADDR(ADDR)) u_dat_scale(
     .clk(clk), .reset(rst), .ep_write(ep_write), .ep_address(ep_address), .regDataOut(ep_dataout_coeff),
     .filter_data_in(filter_out), .filter_out_ready(filter_out_ready), .filter_data_out(filter_out_modified), .data_rdy(filter_data_rdy)
     );
	 
	 //Wishbone Master module for AD796x and AD5453
    hbexec Wishbone_Master_0 (
    .i_clk(clk), .i_reset(rst), .i_cmd_stb(cmd_stb_0), .i_cmd_word(cmd_word_0), .o_cmd_busy(cmd_busy_0), .o_rsp_stb(rsp_stb_0),
    .o_rsp_word(wb_cmd_dataout_0), .o_wb_cyc(cyc_0), .o_wb_stb(stb_0),
    .o_wb_we(we_0), .o_wb_addr(), .o_wb_data(dat_o_0), .o_wb_sel(sel_0),        
    .i_wb_ack(ack_0), .i_wb_stall(1'b0), .i_wb_err(err_0), .i_wb_data(dat_i_0)
    );
    
    //SPI master core for AD796x and AD5453
    spi_top i_spi_top_0 (
      .wb_clk_i(clk), .wb_rst_i(rst), 
      .wb_adr_i(adr_0[4:0]), .wb_dat_i(dat_o_0), .wb_dat_o(dat_i_0), 
      .wb_sel_i(sel_0), .wb_we_i(we_0), .wb_stb_i(stb_0), 
      .wb_cyc_i(cyc_0), .wb_ack_o(ack_0), .wb_err_o(err_0), .wb_int_o(int_o_0),
      .ss_pad_o(ss_0), .sclk_pad_o(sclk_0), .mosi_pad_o(mosi_0), .miso_pad_i(1'b0), .miso_b_pad_i(1'b0)
    );
     
endmodule
