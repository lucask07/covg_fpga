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
reg dco_p_2;
reg dco_n_2;

wire cnv_p;
wire cnv_n;
wire clk_p;
wire clk_n;

wire cnv_p_2;
wire cnv_n_2;
wire clk_p_2;
wire clk_n_2;

wire data_rd;
wire [15:0] data;
wire data_rd_2;
wire [15:0] data_2;

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
 
 /*
 AD7961_oneclk adc2
        (
            .m_clk_i(),
            .fast_clk_i(adc_clk),                 // Maximum 300 MHz Clock, used for serial transfer
            .reset_n_i(reset_n),                  // Reset signal, active low
            .en_i(),
            .d_pos_i(d_p),                    // Data In, Positive Pair
            .d_neg_i(d_n),                    // Data In, Negative Pair
            .dco_pos_i(dco_p_2),                  // Echoed Clock In, Positive Pair
            .dco_neg_i(dco_n_2),                  // Echoed Clock In, Negative Pair
            .en_o(),
            .cnv_pos_o(cnv_p_2),                  // Convert Out, Positive Pair
            .cnv_neg_o(cnv_n_2),                  // Convert Out, Negative Pair
            .clk_pos_o(clk_p_2),                  // Clock Out, Positive Pair
            .clk_neg_o(clk_n_2),                  // Clock Out, Negative Pair
            .data_rd_rdy_o(data_rd_2),              // Signals that new data is available
            .data_o(data_2)                      // Read Data
        );
*/

	// Generate clock
	initial 
	   sys_clk = 1'b0;
	always 
	   #2.5 sys_clk = ~sys_clk; //now 200 MHz sys clock
	
	// Generate adc_clk
	initial 
	   adc_clk = 1'b0;
	always 
	   #2 adc_clk = ~adc_clk;
	   
	always @(clk_p) dco_p <= #15 clk_p;
    always @(clk_n) dco_n <= #15 clk_n;
	//dco_p_2 = clk_p_2;
	//dco_n_2 = clk_n_2;

	initial begin
		// Initialize Inputs
		#5;
		reset_n = 1'b0;
		#200;
		reset_n = 1'b1;
		d_p = 1'b1;
		d_n = 1'b0;
		#200;
    end

endmodule
