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

// LJK - modified to be 4:1 and use 16-bit wide busses 

`default_nettype wire
module mux_4to1_16wide (
	input  wire [15:0] datain_0,
	input  wire [15:0] datain_1,
	input  wire [15:0] datain_2,
	input  wire [15:0] datain_3,
	input  wire [1:0] sel,
	output reg  [15:0] dataout
	);
	
always @(*) begin
	if (sel == 3'b11)      dataout = datain_3;
	else if (sel == 3'b10) dataout = datain_2;
	else if (sel == 3'b01) dataout = datain_1;
	else                   dataout = datain_0;
end

endmodule