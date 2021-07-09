`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/06/2021 01:18:28 PM
// Design Name: 
// Module Name: realTimeLPF_readwrite_coeff
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


module realTimeLPF_readwrite_coeff(clk, rst, wr_en, coeff_out, wr_adr, wr_done, read_enable, ep_write, rd_adr, bram_in
);
    input wire clk, rst, ep_write;
    input wire [31:0] bram_in;
    output reg wr_en, wr_done;
    output wire read_enable;
    output reg [4:0] wr_adr;
    output reg [31:0] coeff_out;
    output reg [4:0] rd_adr;
    
    reg rd_en;
    assign read_enable = {rd_en & ~ep_write};
    
    //states
    reg [4:0] state, nextstate;
    
    parameter S1 = 5'b00000;
    parameter S2 = 5'b00001;
    parameter S3 = 5'b00010;
    parameter S4 = 5'b00011;
    parameter S5 = 5'b00100;
    parameter S6 = 5'b00101;
    parameter S7 = 5'b00111;
    parameter S8 = 5'b01000;
    parameter S9 = 5'b01001;
    parameter S10 = 5'b01010;
    parameter S11 = 5'b01011;
    parameter S12 = 5'b01100;
    parameter S13 = 5'b01101;
    parameter S14 = 5'b01111;
    parameter S15 = 5'b10000;
    parameter S16 = 5'b10001;
    parameter S17 = 5'b10100;
    parameter S18 = 5'b10101;
    parameter INIT = 5'b10010;
    parameter CHECK = 5'b10011;
    
    //state register
     always@(posedge clk)begin
        if(rst)begin
            state <= INIT;
        end
        else begin
             state <= nextstate;
        end
     end
     
     //nextstate logic
     always@(*)begin
        case(state)
            INIT: nextstate = CHECK;
            CHECK: begin //wait for coefficient writes to BRAM to finish, otherwise, write coefficients in BRAM to the filter
                if(ep_write)begin
                    nextstate = CHECK;
                end
                else begin
                    nextstate = S1;
                end
            end
            S1: nextstate = S2;
            S2: nextstate = S3;
            S3: nextstate = S4;
            S4: nextstate = S5;
            S5: nextstate = S6;
            S6: nextstate = S7;
            S7: nextstate = S8;
            S8: nextstate = S9;
            S9: nextstate = S10;
            S10: nextstate = S11;
            S11: nextstate = S12;
            S12: nextstate = S13;
            S13: nextstate = S14;
            S14: nextstate = S15;
            S15: nextstate = S16;
            S16: nextstate = S17;
            S17: begin //once coefficients have been written to the filter, idle until new coefficients are written to BRAM
                if(ep_write)begin
                    nextstate = CHECK;
                end
                else begin
                    nextstate = S17;
                end
            end
            default: nextstate = INIT;
        endcase
     end
     
     //output
     always@(*)begin
        case(state)
            INIT: begin
                wr_en = 1'b0;
                rd_en = 1'b0;
                wr_adr = 4'b0;
                rd_adr = 4'h0;
                wr_done = 1'b0;
                coeff_out = 16'b0;
            end
            CHECK: begin
                wr_en = 1'b0;
                rd_en = 1'b0;
                wr_adr = 4'b0;
                rd_adr = 4'h0;
                wr_done = 1'b0;
                coeff_out = 16'b0;
            end
            S1: begin
                wr_en = 1'b0;
                rd_en = 1'b1;
                wr_adr = 4'b0;
                rd_adr = 4'h0;
                wr_done = 1'b0;
                coeff_out = 16'b0;
            end
            S2: begin
                wr_en = 1'b0;
                rd_en = 1'b1;
                coeff_out = 32'h0;
                wr_done = 1'b0;
                wr_adr = 4'h0;
                rd_adr = 4'h1;
            end
            S3: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h0;
                rd_adr = 4'h2;
            end
            S4: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h1;
                rd_adr = 4'h3;
            end
            S5: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h2;
                rd_adr = 4'h4;
            end
            S6: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h3;
                rd_adr = 4'h5;
            end
            S7: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h4;
                rd_adr = 4'h8;
            end
            S8: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h5;
                rd_adr = 4'h9;
            end
            S9: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h8;
                rd_adr = 4'ha;
            end
            S10: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h9;
                rd_adr = 4'hb;
            end
            S11: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'ha;
                rd_adr = 4'hc;
            end
            S12: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'hb;
                rd_adr = 4'hd;
            end
            S13: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'hc;
                rd_adr = 4'h7;
            end
            S14: begin
                wr_en = 1'b1;
                rd_en = 1'b1;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'hd;
                rd_adr = 4'h0;
            end
            S15: begin
                wr_en = 1'b1;
                rd_en = 1'b0;
                coeff_out = bram_in;
                wr_done = 1'b0;
                wr_adr = 4'h7;
                rd_adr = 4'h0;
            end
            S16: begin
                wr_en = 1'b0;
                rd_en = 1'b0;
                coeff_out = 32'h0;
                wr_done = 1'b1;
                wr_adr = 1'b0;
                rd_adr = 4'h0;
            end
            S17: begin
                wr_en = 1'b0;
                rd_en = 1'b0;
                coeff_out = 16'h0;
                wr_done = 1'b0;
                wr_adr = 1'b0;
                rd_adr = 4'h0;
            end
            default: begin
                wr_en = 1'b0;
                rd_en = 1'b0;
                coeff_out = 16'h0;
                wr_done = 1'b0;
                wr_adr = 1'b0;
                rd_adr = 4'h0;
            end
        endcase
     end
endmodule
