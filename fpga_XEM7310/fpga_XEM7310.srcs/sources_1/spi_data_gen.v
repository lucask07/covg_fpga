`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/28/2021 09:16:03 AM
// Design Name: 
// Module Name: spi_data_gen
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

module spi_data_gen #(parameter ADDR = 8) (
    input wire clk,
    input wire okClk, // needed to synchronize to the register bridge data. Should reset divider after loading data.  
    input wire [3:0]read_en,
    // input data to program frequency 
    input wire [31:0] addr,
    input wire [31:0] data_in, // dividing period. must be multiple of 2 
    input wire write_in,
    // outputs 
    output reg [31:0] data_out
    );
    reg [31:0] data_reg[0:7];

    // from the OK register bridge. No benefit of reseting this. Just set be sure to set it. 
    //  by not reseting the memory then we can reset the clock divider to synchronize
    always @ (posedge okClk) begin
         if(write_in) begin
              if(addr == ADDR)  data_reg[0] <= data_in;
              else if(addr == (ADDR + 1))  data_reg[1] <= data_in;
              else if(addr == (ADDR + 2))  data_reg[2] <= data_in;
              else if(addr == (ADDR + 3))  data_reg[3] <= data_in;
         end
    end
    // condition ? if true : if false
    always @(posedge clk) begin
        if (read_en == 4'd1) data_out <= data_reg[0]; 
        else if (read_en == 4'd2) data_out <= data_reg[1]; 
        else if (read_en == 4'd3) data_out <= data_reg[2]; 
        else if (read_en == 4'd4) data_out <= data_reg[3]; 
    end
endmodule