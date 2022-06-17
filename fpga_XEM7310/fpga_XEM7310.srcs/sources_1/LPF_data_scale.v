`timescale 1ns / 1ps

////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
//
// Create Date:   9:43:18 6/8/2022
// Design Name:   top_module
// Module Name:   C:\Users\iande\covg_fpga_project\covg_fpga\fpga_XEM7310\fpga_XEM7310.srcs\sources_\LPF_data_scale.v
// Project Name:  fpga_XEM7310
// Target Device:  
// Tool versions:  
// Description: 
//
// Module to apply additional scaling to 4th order butterworth filter for series resistance compensation purposes
//
// Dependencies:
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
////////////////////////////////////////////////////////////////////////////////

module LPF_data_scale #(parameter ADDR = 0) (
    input wire clk,
    input wire reset,
    //Register Bridge Signals
    input wire ep_write,
    input wire [31:0] ep_address,
    input wire [31:0] regDataOut,
    //Latest Filter Output (after signed to unsigned conversion) and data ready signal 
    input wire [13:0] filter_data_in,
    input wire filter_in_ready,
    //Sum and downsample enable signals
    input wire downsample_en,
    input wire sum_en,
    //Cmd signal and data ready signal
    input wire [13:0] cmd_data_in,
    input wire cmd_in_ready,
    //new data ready signal and output after scaling
    output wire [13:0] filter_data_out,
    output reg data_rdy
    );

    reg [13:0] coeff_scale;
    reg [13:0] coeff_offset;
    reg [13:0] A;
    reg [13:0] B;
    wire [27:0] P;
    reg [13:0] filter_data_out_temp_0;
    reg [13:0] filter_data_out_temp_1;
    reg [13:0] filter_data_out_temp_2;
    reg [13:0] filter_data_out_temp_3;
    reg [13:0] filter_data_out_reg;
    reg [3:0] ena;
    reg temp_data_rdy;
    
    assign filter_data_out = filter_data_out_reg;

    //Xilinx Multiplier IP instantiation
    mult_gen_1 mult1(.CLK(clk), .A(A), .B(B), .P(P));

    //scaling coeff assignment process
    always @ (posedge clk) begin
        if (reset == 1'b1) begin
            coeff_scale <= 14'b0;
            coeff_offset <= 14'b0;
        end
        else if (ep_write && (ep_address == (ADDR + 32'h13))) begin
            coeff_scale <= regDataOut[13:0];
            coeff_offset <= regDataOut[27:14];
        end
    end

    //Multiplication process
    always @ (posedge clk) begin
        if (reset == 1'b1) begin
            A <= 14'b0;
            B <= 14'b0;
            ena <= 3'b0;
            filter_data_out_temp_0 <= 14'b0;
            filter_data_out_temp_1 <= 14'b0;
            filter_data_out_temp_2 <= 14'b0;
        end
        else if (filter_in_ready == 1'b1) begin
            ena <= 3'b0;
        end
        else if(ena < 4'd9) begin
            ena <= ena + 1'b1;
        end
        else begin
            ena <= ena;
        end
        case(ena)
            0: begin
                A <= 14'b0;
                B <= 14'b0;
            end
            1: begin
                A <= coeff_scale;
                B <= filter_data_in;
            end
            5: begin
                filter_data_out_temp_0 <= P[26:13];
            end
            6: begin
                if(filter_data_out_temp_0[13] == 1'b1)begin
                    filter_data_out_temp_1 <= (filter_data_out_temp_0<<1) - 14'h2000;
                end
                else begin
                    filter_data_out_temp_1 <= (filter_data_out_temp_0<<1) + 14'h1fff;
                end
            end
            7: begin
                filter_data_out_temp_2 <= filter_data_out_temp_1 + coeff_offset;
            end
            default: begin
                A <= 14'b0;
                B <= 14'b0;
            end
        endcase
    end
    
    reg [13:0] cmd_data_in_reg;
    reg cmd_sum_rdy;
    reg filter_sum_rdy;
    reg filter_data_read_en;
    
    //grabbing cmd signal and producing data ready signal
    always @ (posedge clk) begin
        if (reset == 1'b1) begin
            cmd_data_in_reg <= 14'b0;
            cmd_sum_rdy <= 1'b0;
        end
        else if (cmd_in_ready == 1'b1) begin
            cmd_data_in_reg <= cmd_data_in;
            cmd_sum_rdy <= 1'b1;
        end
        else begin
            cmd_sum_rdy <= 1'b0;
            cmd_data_in_reg <= cmd_data_in_reg;
        end
    end
    
    //grabbing scaled and offsetted filter data with optional downsampling and producing data ready signal
    always @ (posedge clk) begin
        if (reset == 1'b1) begin
            filter_data_out_temp_3 <= 14'b0;
            filter_data_read_en <= 1'b1;
            filter_sum_rdy <= 1'b0;
        end
        else if (temp_data_rdy == 1'b1) begin
            if (downsample_en == 1'b1 && filter_data_read_en == 1'b0) begin
                filter_data_read_en <= 1'b1;
                filter_sum_rdy <= 1'b0;
                filter_data_out_temp_3 <= filter_data_out_temp_3;
            end
            else begin
                filter_data_read_en <= 1'b0;
                filter_data_out_temp_3 <= filter_data_out_temp_2;
                filter_sum_rdy <= 1'b1;
            end
        end
        else begin
            filter_data_out_temp_3 <= filter_data_out_temp_3;
            filter_sum_rdy <= 1'b0;
            filter_data_read_en <= filter_data_read_en;
        end
    end
    
    //optional summing process and data ready process
    reg data_rdy_delay;
    
    always @ (posedge clk) begin
        if(reset == 1'b1)begin
            filter_data_out_reg <= 14'b0;
            data_rdy <= 1'b0;
            //data_rdy_delay <= 1'b0;
        end
        else if (filter_sum_rdy == 1'b1) begin
            if(sum_en == 1'b1)begin
                if (filter_data_out_temp_3 >= 14'h1fff) begin
                    filter_data_out_reg <= (filter_data_out_temp_3 - 14'h1fff) + cmd_data_in_reg;
                end
                else begin
                    filter_data_out_reg <= cmd_data_in_reg - (14'h1fff - filter_data_out_temp_3);
                end
                data_rdy <= 1'b1;
            end
            else begin
                filter_data_out_reg <= filter_data_out_temp_3;
                data_rdy <= 1'b1;
            end
        end
        else begin
            data_rdy <= 1'b0;
            //data_rdy <= data_rdy_delay;
        end
    end

    //temp data ready process
    always @ (posedge clk) begin
        if (reset == 1'b1) begin
            temp_data_rdy <= 1'b0;
        end
        else if (ena == 4'd8) begin
            temp_data_rdy <= 1'b1;
        end
        else begin
            temp_data_rdy <= 1'b0;
        end
    end

endmodule