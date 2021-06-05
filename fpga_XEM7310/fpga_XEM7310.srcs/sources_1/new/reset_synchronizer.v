`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
// 
// Create Date: 06/02/2021 12:41:30 PM
// Design Name: 
// Module Name: reset_synchronizer
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


module reset_synchronizer(
    input wire clk,
    input wire async_rst,
    output wire sync_rst
    );
    reg s1, s2;
         
    always@(posedge async_rst or posedge clk)begin
        if(async_rst)begin
            s1<=1'b1;
            s2<=1'b1;
        end
        else begin
            s1<=1'b0;
            s2<=s1;
        end
    end
    
    assign sync_rst = s2;
endmodule
