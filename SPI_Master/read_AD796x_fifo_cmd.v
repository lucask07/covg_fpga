`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    16:33:24 01/25/2021 
// Design Name: 
// Module Name:    read_AD796x_fifo_cmd 
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
module read_AD796x_fifo_cmd(clk, rst, int_o, empty, adc_dat_i, adr, cmd_stb, cmd_word, rd_en
    );
	 input wire clk, rst, int_o, empty;
	 input wire [15:0] adc_dat_i;
	 output reg [7:0] adr;
	 output reg [33:0] cmd_word;
	 output reg cmd_stb;
	 output reg rd_en; //pulse to mark the points in time where the state machine is grabbing AD796x datan(for simulation purposes)
	 
	 reg [13:0] converted_dat; //reg to hold the converted value to be sent to the AD5453
	 wire [15:0] converted_cmd_dat = {2'b0, converted_dat}; //reg to hold the converted value plus command bits for AD5453
	 
	 parameter conversion_offset = 14'h2000; //offset to convert AD796x data before sending to AD5453
	 
	 //this always block will do the data conversion
	 //the data is constantly being converted, but the state machine only samples the converted data every 400 ns
	 always@(posedge clk)begin
		if(rst)begin
			converted_dat = 14'b0;
		end
		else begin
			if(adc_dat_i[15])begin
				converted_dat = (adc_dat_i[15:2] - conversion_offset);
			end
			else begin
				converted_dat = (adc_dat_i[15:2] + conversion_offset);
			end
		end
	 end
	 
	 //states
	 reg [4:0] state, nextstate;
	 //state encoding
	 parameter INIT_0 = 5'b00000; //states to initialize the SPI master registers
	 parameter INIT_1 = 5'b00001;
	 parameter INIT_2 = 5'b00010;
	 parameter INIT_3 = 5'b00011;
	 parameter INIT_4 = 5'b00100;
	 parameter INIT_5 = 5'b00101;
	 parameter INIT_6 = 5'b00110;
	 parameter INIT_7 = 5'b00111;
	 parameter INIT_8 = 5'b01000;
	 parameter Convert_0 = 5'b01001; //states that will take care the first read from the AD796x FIFO
	 parameter Convert_1 = 5'b01010;
	 parameter Convert_2 = 5'b01011;
	 parameter Transfer_0 = 5'b01100; //states to initiate SPI transfer
	 parameter Transfer_1 = 5'b01101;
	 parameter Transfer_2 = 5'b01110;
	 parameter IDLE_0 = 5'b10001; //states to take advantage of "idle" time during SPI transfer, reading the next word from AD796x FIFO
	 
	 
	 //state register
	 always@(posedge clk)begin
		if(rst)begin
			state <= INIT_0;
		end
		else begin
			state <= nextstate;
		end
	 end
	 
	 //nextstate logic
	 always@(*)begin
			case(state)
				INIT_0: begin
					nextstate = INIT_1;
				end
				INIT_1: begin
					nextstate = INIT_2;
				end
				INIT_2: begin
					nextstate = INIT_3;
				end
				INIT_3: begin
					nextstate = INIT_4;
				end
				INIT_4: begin
					nextstate = INIT_5;
				end
				INIT_5: begin
					nextstate = INIT_6;
				end
				INIT_6: begin
					nextstate = INIT_7;
				end
				INIT_7: begin
					nextstate = INIT_8;
				end
				INIT_8: begin
						nextstate = Convert_0;
				end
				Convert_0: begin
					nextstate = Convert_1;
				end
				Convert_1: begin
					nextstate = Convert_2;
				end
				Convert_2: begin
					nextstate = Transfer_0;
				end
				Transfer_0: begin
					nextstate = Transfer_1;
				end
				Transfer_1: begin
					nextstate = Transfer_2;
				end
				Transfer_2: begin
					nextstate = IDLE_0;
				end
				IDLE_0: begin
					if(int_o)begin
						nextstate = Convert_1;
					end
					else begin
						nextstate = IDLE_0;
					end
				end
				default: nextstate = INIT_0;
			endcase
	 end
	 
	 //output logic
	 always@(*)begin
			case(state)
				INIT_0: begin //programming DIVIDE register: starts here
					rd_en = 1'b0;
					adr = 8'h14;
					cmd_word = 34'h100000000;
					cmd_stb = 1'b0;
				end
				INIT_1: begin
					rd_en = 1'b0;
					adr = 8'h14;
					cmd_word = 34'h100000000;
					cmd_stb = 1'b1;	
				end
				INIT_2: begin
					rd_en = 1'b0;
					adr = 8'h14;
					cmd_word = 34'h100000000;
					cmd_stb = 1'b1;
				end
				INIT_3: begin //programming CTRL register: starts here
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = 34'h100003010;
					cmd_stb = 1'b0;
				end
				INIT_4: begin
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = 34'h100003010;
					cmd_stb = 1'b1;
				end
				INIT_5: begin
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = 34'h100003010;
					cmd_stb = 1'b1;
				end
				INIT_6: begin //programming SS register: starts here
					rd_en = 1'b0;
					adr = 8'h18;
					cmd_word = 34'h100000001;
					cmd_stb = 1'b0;
				end
				INIT_7: begin
					rd_en = 1'b0;
					adr = 8'h18;
					cmd_word = 34'h100000001;
					cmd_stb = 1'b1;
				end
				INIT_8: begin
					rd_en = 1'b0;
					adr = 8'h18;
					cmd_word = 34'h100000001;
					cmd_stb = 1'b1;
				end
				Convert_0: begin //reading data entry from AD796x FIFO
					rd_en = 1'b1;
					adr = 8'h0;
					cmd_word = {18'h10000, converted_cmd_dat};
					cmd_stb = 1'b0;
				end
				Convert_1: begin
					rd_en = 1'b0;
					adr = 8'h0;
					cmd_word = cmd_word;
					cmd_stb = 1'b1;
				end
				Convert_2: begin
					rd_en = 1'b0;
					adr = 8'h0;
					cmd_word = cmd_word;
					cmd_stb = 1'b1;
				end
				Transfer_0: begin //starting SPI transfer
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = 34'h100003110;
					cmd_stb = 1'b0;
				end
				Transfer_1: begin
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = cmd_word;
					cmd_stb = 1'b1;
				end
				Transfer_2: begin
					rd_en = 1'b0;
					adr = 8'h10;
					cmd_word = cmd_word;
					cmd_stb = 1'b1;
				end
				IDLE_0: begin //idling while SPI transfers are in progress
					if(int_o)begin//as soon as SPI transfer is complete, read in the next converted word
						rd_en = 1'b1;
						adr = 8'h0;
						cmd_word = {18'h10000, converted_cmd_dat};
						cmd_stb = 1'b0;
					end
					else begin
						rd_en = 1'b0;
						adr = 8'h0;
						cmd_word = cmd_word;
						cmd_stb = 1'b0;
					end
				end
				default: begin
					rd_en = 1'b0;
					adr = 8'h0;
					cmd_word = 34'h0;
					cmd_stb = 1'b0;
				end
			endcase
	 end
endmodule
