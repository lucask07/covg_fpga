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
     input wire [15:0] adc_val_0,
     /*****Register Bridge and DDR Signals******/
     //input wire ep_read,
     input wire ep_write,
     input wire [31:0] ep_address,
     input wire [31:0] ep_dataout_coeff,
     //output wire [31:0] ep_datain,
     input wire [9:0] en_period,
     output wire clk_en_out,
     input wire clk_en_in,
     input wire ddr3_rst, // resets clock enable generator  
     input wire [13:0] ddr_dat_i,
     output wire rd_en_0,
     input wire regTrigger
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
    
     //General purpose clock divide - currently used as "helper" clocking module for reading form DDR3
     general_clock_divide MIG_DDR_FIFO_RD_EN(
         .clk(clk),  // input 
         .rst(ddr3_rst), // input 
         .en_period(en_period), // input [9:0]
         .clk_en(clk_en_out)  // output 
     );
	 
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
	 
	 wire [13:0] filter_out_modified;
	 
	 //State machine/controller for reading a FIFO with data and initiating SPI transfers to AD5453
	 read_fifo_to_spi_cmd #(.ADDR(ADDR)) data_converter_0(
	 .clk(clk), .okClk(fifoclk), .rst(rst), .int_o(int_o_0), .empty(1'b0), .adc_dat_i(/*ddr_dat_i*/filter_out_modified), 
	 .adr(adr_0), .cmd_stb(cmd_stb_0), .cmd_word(cmd_word_0),
	 .rd_en(rd_en_0), .data_rdy(/*dataready*/data_rdy_0), .regDataOut(ep_dataout_coeff[15:0]), 
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
	 
	 blk_mem_gen_0 realTime_LPF_coeff_BRAM(
	 .addra(ep_address[3:0] - (4'h4+ADDR)), .clka(fifoclk), .dina(ep_dataout_coeff), .ena(ep_write & ((ep_address>(ADDR + 8'h03)) & (ep_address<(ADDR + 8'h13)))), .wea(4'b1111),
	 .addrb({27'b0, read_address}), .clkb(clk), .doutb(coeff_bram_in), .enb(read_coeff)
	 );
	 
	 // Real-Time LPF
       Butterworth u_Butterworth_0
         (
         .clk(clk),
         .clk_enable(data_rdy_0 | write_enable | write_done),
         .reset(rst),
         .filter_in(adc_val_0),
         .write_enable(write_enable),
         .write_done(write_done),
         .write_address(write_address),
         .coeffs_in(coeffs_in),
         .filter_out(filter_out)
         );
         
     //wire [13:0] filter_out_modified;
     
     LPF_data_modify_fixpt u_dat_mod(
     .din(filter_out), .dout(filter_out_modified)
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
      .ss_pad_o(ss_0), .sclk_pad_o(sclk_0), .mosi_pad_o(mosi_0), .miso_pad_i() 
    );
    
endmodule
