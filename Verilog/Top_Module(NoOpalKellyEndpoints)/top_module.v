`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    16:58:51 12/28/2020 
// Design Name: 
// Module Name:    top_module 
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

module top_module(
    input wire clk,
    input wire rst,
    input wire [31:0] ep_dataout,
    input wire trigger,  
    output wire hostinterrupt, //interrupt signal from fifo to tell host computer that FIFO is half full
    input wire readFifo,
    output wire [31:0] dout
    );
    
      wire cmd_stb;
      wire [33:0] cmd_word;
      wire cmd_busy;
      wire rsp_stb;
      wire [33:0] wb_cmd_dataout;
      wire [31:0] adr;
      wire [31:0] dat_i; 
      wire [31:0] dat_o;
      wire we;
      wire [3:0] sel;
      wire stb;
      wire cyc;
      wire ack;
      wire err;
      wire int_o;
        
      wire [7:0] ss;
      wire sclk;
      wire mosi;
      wire miso;
        
      wire full;
      wire empty;
      wire writeFifo;
    
  /*Wishbone Master module*/
    hbexec Wishbone_Master (
    .i_clk(clk), .i_reset(rst), .i_cmd_stb(cmd_stb), .i_cmd_word(cmd_word), .o_cmd_busy(cmd_busy), .o_rsp_stb(rsp_stb),
    .o_rsp_word(wb_cmd_dataout), .o_wb_cyc(cyc), .o_wb_stb(stb),
    .o_wb_we(we), .o_wb_addr(adr), .o_wb_data(dat_o), .o_wb_sel(sel),        
    .i_wb_ack(ack), .i_wb_stall(1'b0), .i_wb_err(err), .i_wb_data(dat_i)
    );
    //*/
    
    assign writeFifo = (!wb_cmd_dataout[32] & !wb_cmd_dataout[33] & rsp_stb);//only write to FIFO when rsp word status bits say that a value was read from the SPI
  
    // SPI master core
    spi_top i_spi_top (
      .wb_clk_i(clk), .wb_rst_i(rst), 
      .wb_adr_i(adr[4:0]), .wb_dat_i(dat_o), .wb_dat_o(dat_i), 
      .wb_sel_i(sel), .wb_we_i(we), .wb_stb_i(stb), 
      .wb_cyc_i(cyc), .wb_ack_o(ack), .wb_err_o(err), .wb_int_o(int_o),
      .ss_pad_o(ss), .sclk_pad_o(sclk), .mosi_pad_o(mosi), .miso_pad_i(miso) 
    );
  
    // SPI slave model
    spi_slave_model i_spi_slave (
      .rst(rst), .ss(ss[0]), .sclk(sclk), .mosi(mosi), .miso(miso)
    );
    
    fifo_generator_0 FIFO(
    .full(full), .din(wb_cmd_dataout[31:0]), .wr_en(writeFifo), .empty(empty), 
    .dout(dout), .rd_en(readFifo), .clk(clk), .rst(rst), .prog_full(hostinterrupt)
    );
    
    WbSignal_converter CONVERT(
    .clk(clk), .rst(rst), .ep_dataout(ep_dataout), .trigger(trigger), .o_stb(cmd_stb), .cmd_word(cmd_word), .int_o(int_o)
    );
    
endmodule
