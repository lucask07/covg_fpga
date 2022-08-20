// 8-to-1 33-bit MUX
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

// LJK - modified to be 8:1 and use 32-bit wide busses 
// IDB - modified to be 8:1 and use 33-bit wide busses

`default_nettype wire
module mux8to1_33wide (
	input  wire [32:0] datain_0,
	input  wire [32:0] datain_1,
	input  wire [32:0] datain_2,
	input  wire [32:0] datain_3,
    input  wire [32:0] datain_4,
    input  wire [32:0] datain_5,    
    input  wire [32:0] datain_6,
    input  wire [32:0] datain_7,
	input  wire [2:0] sel,
	output reg  [32:0] dataout
	);
	
always @(*) begin
	if (sel == 3'b111)      dataout = datain_7;
	else if (sel == 3'b110) dataout = datain_6;
    else if (sel == 3'b101) dataout = datain_5;
	else if (sel == 3'b100) dataout = datain_4;
    else if (sel == 3'b011) dataout = datain_3;
	else if (sel == 3'b010) dataout = datain_2;
	else if (sel == 3'b001) dataout = datain_1;
	else                   dataout = datain_0;
end

endmodule