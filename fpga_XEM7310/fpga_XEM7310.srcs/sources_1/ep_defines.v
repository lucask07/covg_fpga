//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/28/2021 01:22:20 PM
// Design Name: 
// Module Name: ep_defines 
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

// establish the addresses of all OpalKelly endpoints here. This will ease keeping tracking between the 
//  Verilog code and the API easier. 

`define AD796x_POUT_OFFSET 8'hA1 
`define ADS_POUT_OFFSET 8'hA5
`define ADS_WIRE_IN_ADDR 8'h05
`define ADS_WIRE_OUT_ADDR 8'h24 
`define DS_WIRE_IN_OFFSET 8'h05
`define DS_TRIG_OFFSET 32'h08  // bit 8 



`define NUM_OUTGOING_EPS 13