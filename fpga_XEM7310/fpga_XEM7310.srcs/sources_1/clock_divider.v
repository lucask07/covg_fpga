`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Lucas Koerner
// 
// Create Date: 07/24/2021 01:12:04 PM
// Design Name: 
// Module Name: clock_divider
// Project Name: 
// Target Devices: XEM7310
// Tool Versions: Vivado (2018.2)
// Description: generate timing signals for SPI reading of ADS8686
//      TODO: allow for a pulse input so this is synchronized to the AD7961 reading. Add a mode bit. 
// Dependencies: ok RegisterBridge as input 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
module clock_divider #(parameter ADDR = 0) (
    input wire clk,
    input wire okClk, // needed to synchronize to the register bridge data. Should reset divider after loading data.  
    input wire rst, // reset of the clock divider. Allows synchronization.
    output reg clk_out, //50% duty-cycle (possibly not used)
    output reg pulse, // single clk period pulse 
    output reg convst,
    output reg [3:0] read_en,
    // input data to program frequency 
    input wire [31:0] addr,
    input wire [31:0] data_in, // dividing period. must be multiple of 2 
    input wire write_in
    );
    
    localparam CONV_WID = 10; // 50 ns with 200 MHz clock 
    localparam CONV_TIME = 114 - 2; // for the ADS8686: 570 ns (max) until busy falls. 
                                    // for oversampling ratio (OSR) of 0; would extend for greater OSRs
                                    // subtract 2 for two clock cycles to load SPI controller via wishbone
    reg [31:0] clk_div; // register to store clock divider. (nominal is 1000 for 200 kHz, could be up to 1 MSPS)
    reg [31:0] cnt;
    
    // from the OK register bridge. No benefit of reseting this. Just set be sure to set it. 
    //  by not reseting the memory then we can reset the clock divider to synchronize
    always @ (posedge okClk) begin
         if(write_in) begin
              if(addr == ADDR) begin
                   clk_div <= data_in;
              end
         end
    end
    // counter and 50% duty cycle divided clock
    always @(posedge clk) begin
        if (rst) begin 
            cnt <= 32'd0;
            clk_out <= 1'b0;
        end
        else if (cnt == ((clk_div >> 1)-1)) begin
            cnt <= cnt + 1'd1;
            clk_out <= 1'b1; 
        end
        else if (cnt == ((clk_div)-1)) begin
            cnt <= 32'd0;
            clk_out <= 1'b0; 
        end    
        else begin
            cnt <= cnt + 1'd1;
        end 
    end 
    // convert start signal -- specific to ADS8686 
    always @(posedge clk) begin
        if (rst)  convst <= 1'b0; 
        else if (cnt < CONV_WID) convst <= 1'b1;
        else convst <= 1'b0;
     end    
     // create the trigger pulse to the wishbone converter 
    always @(posedge clk) begin
        if (rst) pulse <= 1'b0;
        else if ( (cnt == CONV_TIME - 15) | (cnt == (CONV_TIME - 10)) | (cnt == (CONV_TIME - 5)) | (cnt == (CONV_TIME + 0)) )  pulse <= 1'b1; // trigger SPI wishbone transfer
        else pulse <= 1'b0;
     end     
     // create read enable for SPI data
     always @(posedge clk) begin
        if (rst) read_en <= 4'b0000;
        else if ( (cnt == CONV_TIME - 15 ) ) read_en <= 4'd1; 
        else if ( (cnt == CONV_TIME - 10 ) ) read_en <= 4'd2;  
        else if ( (cnt == CONV_TIME  -5  ) ) read_en <= 4'd3; 
        else if ( (cnt == CONV_TIME      ) ) read_en <= 4'd4;
        else read_en <= 4'b0;
     end     
endmodule
