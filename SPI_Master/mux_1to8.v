`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    13:37:04 01/20/2021 
// Design Name: 
// Module Name:    mux_8to1 
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
module mux_1to8(
    input wire [2:0] sel,
    input wire in,
	 input wire deflt,
    output reg [7:0] out
    );

always@(*)
	begin
		case(sel)
			3'b000: out = {{7{deflt}}, in};
			3'b001: out = {{6{deflt}}, in, {1{deflt}}};
			3'b010: out = {{5{deflt}}, in, {2{deflt}}};
			3'b011: out = {{4{deflt}}, in, {3{deflt}}};
			3'b100: out = {{3{deflt}}, in, {4{deflt}}};
			3'b101: out = {{2{deflt}}, in, {5{deflt}}};
			3'b110: out = {{1{deflt}}, in, {6{deflt}}};
			3'b111: out = {in, {7{deflt}}};
		default: out=8'd0;
		endcase
	end

endmodule
