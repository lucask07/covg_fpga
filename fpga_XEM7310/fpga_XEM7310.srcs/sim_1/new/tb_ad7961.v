`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/25/2021 10:29:41 AM
// Design Name: 
// Module Name: tb_ad7961
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

module tb_ad7961;

`timescale 1ns / 1ps
//------------------------------------------------------------------------------
//----------- Module Declaration -----------------------------------------------
//------------------------------------------------------------------------------

reg sys_clk;
reg adc_clk; 
reg reset_n;

reg d_p;
reg d_n;
reg dco_p;
reg dco_n;

wire cnv_p;
wire cnv_n;
wire clk_p;
wire clk_n;

wire data_rd;
wire [15:0] data;

AD7961 adc0
    (
        .m_clk_i(sys_clk),                    // 100 MHz Clock, used for tiing
        .fast_clk_i(adc_clk),                 // Maximum 300 MHz Clock, used for serial transfer
        .reset_n_i(reset_n),                  // Reset signal, active low
        .en_i(),                       // Enable pins input
        .d_pos_i(d_p),                    // Data In, Positive Pair
        .d_neg_i(d_n),                    // Data In, Negative Pair
        .dco_pos_i(dco_p),                  // Echoed Clock In, Positive Pair
        .dco_neg_i(dco_n),                  // Echoed Clock In, Negative Pair
        .en_o(),                       // Enable pins output
        .cnv_pos_o(cnv_p),                  // Convert Out, Positive Pair
        .cnv_neg_o(cnv_n),                  // Convert Out, Negative Pair
        .clk_pos_o(clk_p),                  // Clock Out, Positive Pair
        .clk_neg_o(clk_n),                  // Clock Out, Negative Pair
        .data_rd_rdy_o(data_rd),              // Signals that new data is available
        .data_o(data)                      // Read Data
    );

	// Generate clock
	initial 
	   sys_clk = 1'b0;
	always 
	   #5 sys_clk = ~sys_clk; //now 200 MHz sys clock
	
	// Generate adc_clk
	initial 
	   adc_clk = 1'b0;
	always 
	   #2 adc_clk = ~adc_clk;
	   
	always @(*) begin
	   #1;
	   dco_p = clk_p;
	   dco_n = clk_n;
   end

	initial begin
		// Initialize Inputs
		#5;
		reset_n = 1'b0;
		#20;
		reset_n = 1'b1;
		d_p = 1'b1;
		d_n = 1'b0;
		#200;
    end

endmodule
