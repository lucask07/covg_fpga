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

	//ep40trig[0] will be used to trigger the Wishbone formatter/state machine, telling the state machine that wi0 is valid
	//ep40trig[1] will be used as the master reset for the rest of the design
	//ep40trig[2] will be used as the reset for the ADS7952 FIFO
	//ep40trig[3] will be used as the reset for the "fast" clock pll
	//ep40trig[4] is the reset for adc7961_0_fifo
	//ep40trig[5] is the reset for adc7961_1_fifo
	//ep40trig[6] is the reset for adc7961_2_fifo
	//ep40trig[7] is the reset for adc7961_3_fifo
	//ep40trig[8] will be used to trigger the Wishbone formatter/state machine for dac_0, telling the state machine that wi0 is valid
	//ep40trig[9] will be used to trigger the Wishbone formatter/state machine for dac_1, telling the state machine that wi0 is valid
	//ep40trig[10] reset the programmable clock divider for the ADS8686 spi 
	//ep40trig[11] trigger the ADS8686 SPI wishbone when in host driven mode 
	

// trigger in at 0x40
// `define TI40_ 0
`define TI40_RST 1 // sys reset
// `define TI40_ 2 // not used 
`define TI40_RST 1 // sys reset
`define TI40_PLL_RST 3 //AD796x PLL reset 
`define TI40_ADC_FIFO_RST 4 // 4,5,6,7 by generate loop.
`define TI40_AD5453_WB 8 // 8,9,10,11,12,13
`define TI40_ADS_CLK_DIV 14
`define TI40_ADS_WB 15
`define TI40_ADC_RST 16
`define TI40_DAC805_WB 17 //17, 18

// TODO set this up! 
`define NUM_OUTGOING_EPS 13