`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Lucas Koerner
// 
// Create Date: 07/24/2021 01:12:04 PM
// Design Name: 
// Module Name: clock_divider
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
module clock_divider #(parameter ADDR = 0) (
    input wire clk,
    input wire okClk, // needed to synchronize to the register bridge data. Should reset divider after loading data.  
    input wire rst,
    output reg clk_out, //50% duty-cycle 
    output reg pulse, // single clk period pulse 
    input wire [31:0] addr,
    input wire [31:0] data_in, // must be multiple of 2 
    input wire write_in
    );
    
    reg [31:0] clk_div; // register to store 
    reg [31:0] cnt;
    
    always @ (posedge okClk) begin
         if(write_in) begin
              if(addr == ADDR) begin
                   clk_div <= data_in;
              end
         end
    end
    
    always @(posedge clk) begin
        if (rst) begin 
            cnt <= 32'd0;
            clk_out <= 1'b0;
            pulse <= 1'b0;
        end
        else if (cnt == ((clk_div >> 1)-1)) begin
            cnt <= cnt + 1'd1;
            clk_out <= 1'b1; 
            pulse <= 1'b0;
        end
        else if (cnt == ((clk_div)-1)) begin
            cnt <= 32'd0;
            clk_out <= 1'b0; 
            pulse <= 1'b1;
        end    
        else begin
            cnt <= cnt + 1'd1;
            pulse <= 1'b0;
        end 
    end 
endmodule
