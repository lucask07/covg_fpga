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


module realTimeLPF_readwrite_coeff(clk, rst, wr_en, coeff_out, wr_adr, wr_done
);
    input wire clk, rst;
    output reg wr_en, wr_done;
    output reg [4:0] wr_adr;
    output reg [31:0] coeff_out;
    
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
    
    //state register
     always@(posedge clk)begin
        if(rst)begin
            state <= S1;
        end
        else begin
             state <= nextstate;
        end
     end
     
     //nextstate logic
     always@(*)begin
        case(state)
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
            S16: nextstate = S16;
            default: state = S1;
        endcase
     end
     
     //output
     always@(*)begin
        case(state)
            S1: begin
                wr_en = 1'b0;
                wr_adr = 4'b0;
                wr_done = 1'b0;
                coeff_out = 16'b0;
            end
            S2: begin
                wr_en = 1'b1;
                coeff_out = 32'h009e1586;
                wr_done = 1'b0;
                wr_adr = 4'h0;
            end
            S3: begin
                wr_en = 1'b1;
                coeff_out = 32'h20000000;
                wr_done = 1'b0;
                wr_adr = 4'h1;
            end
            S4: begin
                wr_en = 1'b1;
                coeff_out = 32'h40000000;
                wr_done = 1'b0;
                wr_adr = 4'h2;
            end
            S5: begin
                wr_en = 1'b1;
                coeff_out = 32'h20000000;
                wr_done = 1'b0;
                wr_adr = 4'h3;
            end
            S6: begin
                wr_en = 1'b1;
                coeff_out = 32'hbce3be9a;
                wr_done = 1'b0;
                wr_adr = 4'h4;
            end
            S7: begin
                wr_en = 1'b1;
                coeff_out = 32'h12f3f6b0;
                wr_done = 1'b0;
                wr_adr = 4'h5;
            end
            S8: begin
                wr_en = 1'b1;
                coeff_out = 32'h7fffffff;
                wr_done = 1'b0;
                wr_adr = 4'h8;
            end
            S9: begin
                wr_en = 1'b1;
                coeff_out = 32'h20000000;
                wr_done = 1'b0;
                wr_adr = 4'h9;
            end
            S10: begin
                wr_en = 1'b1;
                coeff_out = 32'h40000000;
                wr_done = 1'b0;
                wr_adr = 4'ha;
            end
            S11: begin
                wr_en = 1'b1;
                coeff_out = 32'h20000000;
                wr_done = 1'b0;
                wr_adr = 4'hb;
            end
            S12: begin
                wr_en = 1'b1;
                coeff_out = 32'hab762783;
                wr_done = 1'b0;
                wr_adr = 4'hc;
            end
            S13: begin
                wr_en = 1'b1;
                coeff_out = 32'h287ecada;
                wr_done = 1'b0;
                wr_adr = 4'hd;
            end
            S14: begin
                wr_en = 1'b1;
                coeff_out = 32'h7fffffff;
                wr_done = 1'b0;
                wr_adr = 4'h7;
            end
            S15: begin
                wr_en = 1'b0;
                coeff_out = 16'h0;
                wr_done = 1'b1;
                wr_adr = 1'b0;
            end
            S16: begin
                wr_en = 1'b0;
                coeff_out = 16'h0;
                wr_done = 1'b0;
                wr_adr = 1'b0;
            end
            default: begin
                wr_en = 1'b0;
                coeff_out = 16'h0;
                wr_done = 1'b0;
                wr_adr = 1'b0;
            end
        endcase
     end
endmodule
