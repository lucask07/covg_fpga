`timescale 1ns / 1ps
`default_nettype wire
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Abe Stroschein
// 
// Create Date:    12:09:23 07/12/2021
// Design Name: 
// Module Name:    spi_controller
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: module for general SPU control including the Wishbone signal converter, the Wishbone master,
// and the SPI master used for the chip. This module is meant to be instantiated in the top level for each
// SPI chip in use on the FPGA.
//
// Dependencies: WbSignal_converter, hbexec, spi_top
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
    
module spi_controller #(ADDR = 0)(
    input wire clk,
    input wire reset,
    input wire divider_reset,
    input wire [31:0] dac_val,
    input wire dac_convert_trigger,
    input wire host_fpgab,
    
    // OkRegister bridge 
    input wire okClk, // needed to synchronize to the register bridge data. Should reset divider after loading data.  
    input wire [31:0] addr,
    input wire [31:0] data_in, // dividing period. must be multiple of 2     
    input wire write_in,
    
    output wire [31:0] dac_out,
    output wire data_valid,
    output wire ss,
    output wire sclk,
    output wire mosi,
    input wire miso,
    input wire miso_b,
    // for ADS8686
    output wire convst_out
    );

    //instantiations and wires for DAC80508
    wire cmd_stb;
    wire [33:0] cmd_word;
    wire cmd_busy;
    wire rsp_stb;
    wire [33:0] wb_cmd_dataout;
    wire [29:0] adr;
    wire [31:0] dat_i; 
    wire [31:0] dat_o;
    wire we;
    wire [3:0] sel;
    wire stb;
    wire cyc;
    wire ack;
    wire err;
    wire int_o;
    wire rd_en; //signaling data is being grabbed by stae machine/controller

    wire pulse;
    wire [3:0]read_en;
    wire [31:0] data_out;

    // generates pulses to the wishbone converter (4 per clock cycle) and the convst signal needed by the ADS8686
    clock_divider #(.ADDR(ADDR)) dut(
        .clk(clk),
        .okClk(okClk), // needed to synchronize to the register bridge data. Should reset divider after loading data.  
        .rst(divider_reset),
        .clk_out(), //50% duty-cycle 
        .pulse(pulse), // single clk period pulse (programmable frequency)
        .convst(convst),
        .read_en(read_en),    
        .addr(addr),     // input data to program frequency 
        .data_in(data_in), // must be multiple of 2 
        .write_in(write_in)
        );
        
    assign convst_out = convst & (~host_fpgab); // force convst output to zero if doing host driven reads. 
        
    spi_data_gen #(.ADDR(ADDR + 1)) dut2 (
            .clk(clk),
            .okClk(okClk), // needed to synchronize to the register bridge data. Should reset divider after loading data.  
            .read_en(read_en),
            // input data to program frequency 
            .addr(addr),
            .data_in(data_in), 
            .write_in(write_in),
            .data_out(data_out)
            );

    wire wb_trigger;
    assign wb_trigger = host_fpgab ? dac_convert_trigger : pulse; 
    
    wire [31:0] wb_conv_data; // data to the wishbone converter 
    assign wb_conv_data = host_fpgab ? dac_val : data_out; 

    assign data_valid = (!wb_cmd_dataout[32] && !wb_cmd_dataout[33] && !rsp_stb);

    //module to take commands from the host and format them into commands that the Wishbone master will understand
    WbSignal_converter CONVERT(
    .clk(clk), .rst(reset), .ep_dataout(wb_conv_data), .trigger(wb_trigger), 
    .o_stb(cmd_stb), .cmd_word(cmd_word), .int_o(int_o)
    );

    //Wishbone Master module
    hbexec Wishbone_Master (
    .i_clk(clk), .i_reset(reset), .i_cmd_stb(cmd_stb), .i_cmd_word(cmd_word), 
    .o_cmd_busy(cmd_busy), .o_rsp_stb(rsp_stb),
    .o_rsp_word(wb_cmd_dataout), .o_wb_cyc(cyc), .o_wb_stb(stb),
    .o_wb_we(we), .o_wb_addr(adr), .o_wb_data(dat_o), .o_wb_sel(sel),        
    .i_wb_ack(ack), .i_wb_stall(1'b0), .i_wb_err(err), .i_wb_data(dat_i)
    );

    assign dac_out = wb_cmd_dataout[31:0];
    
    //SPI master core 
    spi_top i_spi_top (
     .wb_clk_i(clk), .wb_rst_i(reset), 
     .wb_adr_i(adr[4:0]), .wb_dat_i(dat_o), .wb_dat_o(dat_i), 
     .wb_sel_i(sel), .wb_we_i(we), .wb_stb_i(stb), 
     .wb_cyc_i(cyc), .wb_ack_o(ack), .wb_err_o(err), .wb_int_o(int_o),
     .ss_pad_o(ss), .sclk_pad_o(sclk), .mosi_pad_o(mosi), .miso_pad_i(miso),
     .miso_b_pad_i(miso_b)    
     );
endmodule