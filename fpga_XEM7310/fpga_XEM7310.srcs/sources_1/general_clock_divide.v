`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/12/2021 09:46:52 AM
// Design Name: 
// Module Name: general_clock_divide
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


module general_clock_divide(en_period, clk_en, clk, rst
    );
    input wire [9:0] en_period;
    input wire clk, rst;
    output reg clk_en;
    
    reg [9:0] count;
    
    always@(posedge clk)begin
        if(rst)begin
            count <= 10'b0;
            clk_en <= 1'b0;
        end
        else if(count == (en_period - 1'b1))begin
            count <= 10'b0;
            clk_en <= 1'b1;        
        end
        else begin
            count <= count + 1'b1;
            clk_en <= 1'b0;
        end    
    end
    
endmodule
