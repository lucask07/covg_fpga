`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    16:11:47 01/13/2021 
// Design Name: 
// Module Name:    one_second_pulse 
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
//////////////////////////////////////////////////////////////////////////////////
module one_second_pulse(
    input wire clk,
    input wire rst,
    output wire slow_pulse
    );
	 
	 reg [31:0] cnt;
	 reg pulse;
	 
	 assign slow_pulse = pulse;
	 
	 //dividing the 100 MHz master clock by 100000000 to get the desired frequency of 1 Hz
    parameter halfof_divide_by = 31'd100000000;
    
    always @(posedge clk)begin
        //if reset goes high, slow_clk and cnt must reset
        if(rst == 1'b1)begin
            cnt <= 31'b0;
            pulse <= 1'b0;
        end
        else if(cnt == (halfof_divide_by - 1'b1))begin
        //when the count reaches half of the frequency of the master clock minus one, the slow clock toggles
            cnt <= 31'b0;
            pulse <= ~pulse;
        end
        else begin
        //if the cnt is not half of the master clock frequency, it simply counts up
            cnt <= cnt + 1'b1;
        end
    end


endmodule
