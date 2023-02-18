// 8-to-1 1-bit MUX
// 
//------------------------------------------------------------------------
// Copyright (c) 2005-2017 Opal Kelly Incorporated
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//------------------------------------------------------------------------

// LJK - modified to be 8:1 and use 32-bit wide busses and to be synchronous to reduce considerable fanouts 

`default_nettype wire
module mux8to1_32wide_clocked (
    input wire clk,
	input  wire [31:0] datain_0,
	input  wire [31:0] datain_1,
	input  wire [31:0] datain_2,
	input  wire [31:0] datain_3,
    input  wire [31:0] datain_4,
    input  wire [31:0] datain_5,    
    input  wire [31:0] datain_6,
    input  wire [31:0] datain_7,
	input  wire [2:0] sel,
	output reg  [31:0] dataout
	);
	
reg [31:0] dataout_tmp;
always @(*) begin
	if (sel == 3'b111)      dataout_tmp = datain_7;
	else if (sel == 3'b110) dataout_tmp = datain_6;
    else if (sel == 3'b101) dataout_tmp = datain_5;
	else if (sel == 3'b100) dataout_tmp = datain_4;
    else if (sel == 3'b011) dataout_tmp = datain_3;
	else if (sel == 3'b010) dataout_tmp = datain_2;
	else if (sel == 3'b001) dataout_tmp = datain_1;
	else                   dataout_tmp = datain_0;
end

always @(posedge clk) dataout <= dataout_tmp;

endmodule