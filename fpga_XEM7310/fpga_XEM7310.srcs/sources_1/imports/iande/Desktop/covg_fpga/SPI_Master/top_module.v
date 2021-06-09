//`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
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
	 input wire fifoclk,
     input wire rst,
     input wire [31:0] ep_dataout,
     input wire trigger,  
     output wire hostinterrupt, //interrupt signal from fifo to tell host computer that FIFO is half full
     input wire readFifo,
	 input wire rstFifo,
     output wire [31:0] dout,
	 output wire [31:0] lastWrite, //this signal will give the value of the last word written into the FIFO (for debugging)
	 output wire ep_ready, //this signal will tell the host that a block transfer is ready
	 /**/output wire mosi,
	 input wire miso,
	 output wire sclk,
	 output wire ss,//*/
	 output wire slow_pulse,
	 input wire data_rdy_0,
	 output wire ss_0,
     output wire sclk_0,
     output wire mosi_0,
     input wire [15:0] adc_val_0,
     input wire data_rdy_1,
     output wire ss_1,
     output wire sclk_1,
     output wire mosi_1,
     input wire [15:0] adc_val_1
     /*
     input wire data_rdy_2,
     output wire ss_2,
     output wire sclk_2,
     output wire mosi_2,
     input wire [15:0] adc_val_2,
     input wire data_rdy_3,
     output wire ss_3,
     output wire sclk_3,
     output wire mosi_3,
     input wire [15:0] adc_val_3
     */
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
        
      /*wire [7:0] ss;
      wire sclk;
      wire mosi;
      wire miso;//*/
        
      wire full;
      wire empty;
      wire writeFifo;//this signal and the one below are used to generate the write enable signal for the FIFO
      reg wr_en;//
		
    //syncronizer for the system rst (non-Fifo)
      reg s1, s2;
	  wire sync_rst;
	 
    always@(posedge rst or posedge clk)begin
		if(rst)begin
			s1<=1'b1;
			s2<=1'b1;
		end
		else begin
			s1<=1'b0;
			s2<=s1;
		end
    end
		
	 assign sync_rst = s2;
	 
	 //synchronizer for the FIFO reset
	 reg s3, s4;
	 wire sync_fifo_rst;
	 
    always@(posedge rstFifo or posedge fifoclk)begin
		if(rstFifo)begin
			s3<=1'b1;
			s4<=1'b1;
		end
		else begin
			s3<=1'b0;
			s4<=s3;
		end
    end
		
	 assign sync_fifo_rst = s4;
	 
	 /* ---------------- ADS7950 ----------------*/
    
    /*Wishbone Master module*/
    hbexec Wishbone_Master (
    .i_clk(clk), .i_reset(sync_rst), .i_cmd_stb(cmd_stb), .i_cmd_word(cmd_word), .o_cmd_busy(cmd_busy), .o_rsp_stb(rsp_stb),
    .o_rsp_word(wb_cmd_dataout), .o_wb_cyc(cyc), .o_wb_stb(stb),
    .o_wb_we(we), .o_wb_addr(adr), .o_wb_data(dat_o), .o_wb_sel(sel),        
    .i_wb_ack(ack), .i_wb_stall(1'b0), .i_wb_err(err), .i_wb_data(dat_i)
    );
    //*/
    
	 
	 //generating the write enable signal for the FIFO
	 always@(negedge clk)begin
		if(sync_rst)begin
			wr_en <= 1'b0;
		end
		else begin
			if(!wb_cmd_dataout[32] && !wb_cmd_dataout[33] && !rsp_stb)begin
				wr_en <= 1'b1;
			end
			else begin
				wr_en <= 1'b0;
			end
		end
	 end
    
	 assign writeFifo = wr_en;
  
    // SPI master core
    spi_top i_spi_top (
      .wb_clk_i(clk), .wb_rst_i(sync_rst), 
      .wb_adr_i(adr[4:0]), .wb_dat_i(dat_o), .wb_dat_o(dat_i), 
      .wb_sel_i(sel), .wb_we_i(we), .wb_stb_i(stb), 
      .wb_cyc_i(cyc), .wb_ack_o(ack), .wb_err_o(err), .wb_int_o(int_o),
      .ss_pad_o(ss), .sclk_pad_o(sclk), .mosi_pad_o(mosi), .miso_pad_i(miso) 
    );
  
    /* //SPI slave model
    spi_slave_model i_spi_slave (
      .rst(sync_rst), .ss(ss), .sclk(sclk), .mosi(mosi), .miso(miso)
    );//*/
    
	 //FIFO to hold data from the ADS7950
    fifo_generator_1 FIFO(
    .full(full), .din(wb_cmd_dataout[31:0]), .wr_en(writeFifo), .empty(empty), 
    .dout(dout), .rd_en(readFifo), .wr_clk(clk), .rd_clk(fifoclk), .rst(sync_fifo_rst), .prog_full(hostinterrupt)
    );
    
	 //module to take commands from the host and format them into commands that the Wishbone master will understand
    WbSignal_converter CONVERT(
    .clk(clk), .rst(sync_rst), .ep_dataout(ep_dataout), .trigger(trigger), .o_stb(cmd_stb), .cmd_word(cmd_word), .int_o(int_o)
    );
	 
	 //module to create a one second pulse on one of the LEDs (just to confirm the FPGA is working)
	 one_second_pulse out_pulse(
	 .clk(clk), .rst(sync_rst), .slow_pulse(slow_pulse)
	 );
	 
	 //capturing the value of the last word written to the FIFO
	 reg [31:0] lastFifoWrite;
	 
	 always@(posedge clk)begin
		if(sync_rst)begin
			lastFifoWrite <= 32'h0;
		end
		else begin
			if(writeFifo)begin
				lastFifoWrite <= wb_cmd_dataout[31:0];
			end
			else begin
				lastFifoWrite <= lastFifoWrite;
			end
		end
	 end
	 
	 assign lastWrite = lastFifoWrite;
	 
	 //creating a signal to serve as the EP_READY for the Block throttled Pipe out
	 reg blockready;
	 
	 always@(posedge fifoclk)begin
		if(sync_fifo_rst)begin
			blockready <= 1'b0;
		end
		else begin 
			if(hostinterrupt)begin
				blockready <= 1'b1;
			end
			else begin
				if(empty || !readFifo)begin
					blockready <= 1'b0;
				end
				else begin
					blockready <= blockready;
				end
			end
		end
	 end
	 
	 assign ep_ready = blockready;
	 
	 
	 
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
	 wire rd_en_0; //read enable for AD796x FIFO
	 
	 /*wire ss_0;
     wire sclk_0;
     wire mosi_0;*/
	 
	 //State machine/controller for reading data from AD796x FIFO and initiating SPI transfers to AD5453
	 read_AD796x_fifo_cmd data_converter_0(
	 .clk(clk), .rst(sync_rst), .int_o(int_o_0), .empty(1'b0), .adc_dat_i(/*adc_val_0*/16'h7fff), .adr(adr_0), .cmd_stb(cmd_stb_0), .cmd_word(cmd_word_0),
	 .rd_en(rd_en_0), .data_rdy(data_rdy_0)
	 );
	 
	 //Wishbone Master module for AD796x and AD5453
    hbexec Wishbone_Master_0 (
    .i_clk(clk), .i_reset(sync_rst), .i_cmd_stb(cmd_stb_0), .i_cmd_word(cmd_word_0), .o_cmd_busy(cmd_busy_0), .o_rsp_stb(rsp_stb_0),
    .o_rsp_word(wb_cmd_dataout_0), .o_wb_cyc(cyc_0), .o_wb_stb(stb_0),
    .o_wb_we(we_0), .o_wb_addr(), .o_wb_data(dat_o_0), .o_wb_sel(sel_0),        
    .i_wb_ack(ack_0), .i_wb_stall(1'b0), .i_wb_err(err_0), .i_wb_data(dat_i_0)
    );
    
    //SPI master core for AD796x and AD5453
    spi_top i_spi_top_0 (
      .wb_clk_i(clk), .wb_rst_i(sync_rst), 
      .wb_adr_i(adr_0[4:0]), .wb_dat_i(dat_o_0), .wb_dat_o(dat_i_0), 
      .wb_sel_i(sel_0), .wb_we_i(we_0), .wb_stb_i(stb_0), 
      .wb_cyc_i(cyc_0), .wb_ack_o(ack_0), .wb_err_o(err_0), .wb_int_o(int_o_0),
      .ss_pad_o(ss_0), .sclk_pad_o(sclk_0), .mosi_pad_o(mosi_0), .miso_pad_i() 
    );
    
    
    //instantiations and wires for AD796x and AD5453 SPI control
    wire cmd_stb_1;
    wire [33:0] cmd_word_1;
    wire cmd_busy_1;
    wire rsp_stb_1;
    wire [33:0] wb_cmd_dataout_1;
    wire [7:0] adr_1;
    wire [31:0] dat_i_1; 
    wire [31:0] dat_o_1;
    wire we_1;
    wire [3:0] sel_1;
    wire stb_1;
    wire cyc_1;
    wire ack_1;
    wire err_1;
    wire int_o_1;
    wire rd_en_1; //signaling data is being grabbed by stae machine/controller
     
     
    //State machine/controller for reading data from AD796x FIFO and initiating SPI transfers to AD5453
    read_AD796x_fifo_cmd data_converter_1(
    .clk(clk), .rst(sync_rst), .int_o(int_o_1), .empty(1'b0), .adc_dat_i(/*adc_val_1*/16'h7fff), .adr(adr_1), .cmd_stb(cmd_stb_1), .cmd_word(cmd_word_1),
    .rd_en(rd_en_1), .data_rdy(data_rdy_1)
    );
     
    //Wishbone Master module for AD796x and AD5453
    hbexec Wishbone_Master_1 (
    .i_clk(clk), .i_reset(sync_rst), .i_cmd_stb(cmd_stb_1), .i_cmd_word(cmd_word_1), .o_cmd_busy(cmd_busy_1), .o_rsp_stb(rsp_stb_1),
    .o_rsp_word(wb_cmd_dataout_1), .o_wb_cyc(cyc_1), .o_wb_stb(stb_1),
    .o_wb_we(we_1), .o_wb_addr(), .o_wb_data(dat_o_1), .o_wb_sel(sel_1),        
    .i_wb_ack(ack_1), .i_wb_stall(1'b0), .i_wb_err(err_1), .i_wb_data(dat_i_1)
    );
    
    //SPI master core for AD796x and AD5453
    spi_top i_spi_top_1 (
     .wb_clk_i(clk), .wb_rst_i(sync_rst), 
     .wb_adr_i(adr_1[4:0]), .wb_dat_i(dat_o_1), .wb_dat_o(dat_i_1), 
     .wb_sel_i(sel_1), .wb_we_i(we_1), .wb_stb_i(stb_1), 
     .wb_cyc_i(cyc_1), .wb_ack_o(ack_1), .wb_err_o(err_1), .wb_int_o(int_o_1),
     .ss_pad_o(ss_1), .sclk_pad_o(sclk_1), .mosi_pad_o(mosi_1), .miso_pad_i() 
    );
    /*
    //instantiations and wires for AD796x and AD5453 SPI control
    wire cmd_stb_2;
    wire [33:0] cmd_word_2;
    wire cmd_busy_2;
    wire rsp_stb_2;
    wire [33:0] wb_cmd_dataout_2;
    wire [7:0] adr_2;
    wire [31:0] dat_i_2; 
    wire [31:0] dat_o_2;
    wire we_2;
    wire [3:0] sel_2;
    wire stb_2;
    wire cyc_2;
    wire ack_2;
    wire err_2;
    wire int_o_2;
    wire rd_en_2; //signaling data is being grabbed by stae machine/controller
     
     
    //State machine/controller for reading data from AD796x FIFO and initiating SPI transfers to AD5453
    read_AD796x_fifo_cmd data_converter_2(
    .clk(clk), .rst(sync_rst), .int_o(int_o_2), .empty(1'b0), .adc_dat_i(adc_val_2), .adr(adr_2), .cmd_stb(cmd_stb_2), .cmd_word(cmd_word_2),
    .rd_en(rd_en_2), .data_rdy(data_rdy_2)
    );
     
    //Wishbone Master module for AD796x and AD5453
    hbexec Wishbone_Master_2 (
    .i_clk(clk), .i_reset(sync_rst), .i_cmd_stb(cmd_stb_2), .i_cmd_word(cmd_word_2), .o_cmd_busy(cmd_busy_2), .o_rsp_stb(rsp_stb_2),
    .o_rsp_word(wb_cmd_dataout_2), .o_wb_cyc(cyc_2), .o_wb_stb(stb_2),
    .o_wb_we(we_2), .o_wb_addr(), .o_wb_data(dat_o_2), .o_wb_sel(sel_2),        
    .i_wb_ack(ack_2), .i_wb_stall(1'b0), .i_wb_err(err_2), .i_wb_data(dat_i_2)
    );
    
    //SPI master core for AD796x and AD5453
    spi_top i_spi_top_2 (
     .wb_clk_i(clk), .wb_rst_i(sync_rst), 
     .wb_adr_i(adr_2[4:0]), .wb_dat_i(dat_o_2), .wb_dat_o(dat_i_2), 
     .wb_sel_i(sel_2), .wb_we_i(we_2), .wb_stb_i(stb_2), 
     .wb_cyc_i(cyc_2), .wb_ack_o(ack_2), .wb_err_o(err_2), .wb_int_o(int_o_2),
     .ss_pad_o(ss_2), .sclk_pad_o(sclk_2), .mosi_pad_o(mosi_2), .miso_pad_i() 
    );
    
    //instantiations and wires for AD796x and AD5453 SPI control
    wire cmd_stb_3;
    wire [33:0] cmd_word_3;
    wire cmd_busy_3;
    wire rsp_stb_3;
    wire [33:0] wb_cmd_dataout_3;
    wire [7:0] adr_3;
    wire [31:0] dat_i_3; 
    wire [31:0] dat_o_3;
    wire we_3;
    wire [3:0] sel_3;
    wire stb_3;
    wire cyc_3;
    wire ack_3;
    wire err_3;
    wire int_o_3;
    wire rd_en_3; //signaling data is being grabbed by stae machine/controller
     
     
    //State machine/controller for reading data from AD796x FIFO and initiating SPI transfers to AD5453
    read_AD796x_fifo_cmd data_converter_3(
    .clk(clk), .rst(sync_rst), .int_o(int_o_3), .empty(1'b0), .adc_dat_i(adc_val_3), .adr(adr_3), .cmd_stb(cmd_stb_3), .cmd_word(cmd_word_3),
    .rd_en(rd_en_3), .data_rdy(data_rdy_3)
    );
     
    //Wishbone Master module for AD796x and AD5453
    hbexec Wishbone_Master_3 (
    .i_clk(clk), .i_reset(sync_rst), .i_cmd_stb(cmd_stb_3), .i_cmd_word(cmd_word_3), .o_cmd_busy(cmd_busy_3), .o_rsp_stb(rsp_stb_3),
    .o_rsp_word(wb_cmd_dataout_3), .o_wb_cyc(cyc_3), .o_wb_stb(stb_3),
    .o_wb_we(we_3), .o_wb_addr(), .o_wb_data(dat_o_3), .o_wb_sel(sel_3),        
    .i_wb_ack(ack_3), .i_wb_stall(1'b0), .i_wb_err(err_3), .i_wb_data(dat_i_3)
    );
    
    //SPI master core for AD796x and AD5453
    spi_top i_spi_top_3 (
     .wb_clk_i(clk), .wb_rst_i(sync_rst), 
     .wb_adr_i(adr_3[4:0]), .wb_dat_i(dat_o_3), .wb_dat_o(dat_i_3), 
     .wb_sel_i(sel_3), .wb_we_i(we_3), .wb_stb_i(stb_3), 
     .wb_cyc_i(cyc_3), .wb_ack_o(ack_3), .wb_err_o(err_3), .wb_int_o(int_o_3),
     .ss_pad_o(ss_3), .sclk_pad_o(sclk_3), .mosi_pad_o(mosi_3), .miso_pad_i() 
    );
    
    */
    
    
endmodule
