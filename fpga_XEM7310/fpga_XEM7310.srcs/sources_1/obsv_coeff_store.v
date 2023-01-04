//`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UST
// Engineer: Ian Delgadillo Bonequi
// 
// Create Date:   13:52:51 1/4/2023 
// Design Name: 
// Module Name:    obsv_coeff_store
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
//////////////////////////////////////////////////////////////////////////////////`include "timescale.v"
`include "timescale.v"

module obsv_coeff_store #(parameter ADDR = 0) (
    input wire okClk,
    input wire ep_write,
    input wire [31:0] ep_address,
    input wire [31:0] ep_dataout,
    output wire [31:0] L_0, // 32 bit buses for L matrix coefficients
    output wire [31:0] L_1, // 32 bit buses for L matrix coefficients
    output wire [31:0] L_2, // 32 bit buses for L matrix coefficients
    output wire [31:0] L_3, // 32 bit buses for L matrix coefficients
    output wire [31:0] A_0, // 32 bit buses for A matrix coefficients
    output wire [31:0] A_1, // 32 bit buses for A matrix coefficients
    output wire [31:0] A_2, // 32 bit buses for A matrix coefficients
    output wire [31:0] A_3, // 32 bit buses for A matrix coefficients
    output wire [31:0] B_0, // 32 bit buses for B matrix coefficients
    output wire [31:0] B_1 // 32 bit buses for B matrix coefficients
);

    reg [31:0] L_matrix_coeff [3:0]; // 32 bit buses for L matrix coefficients
    reg [31:0] A_matrix_coeff [3:0]; // 32 bit buses for A matrix coefficients
    reg [31:0] B_matrix_coeff [1:0]; // 32 bit buses for B matrix coefficients

    //scaling coeff assignment process
    always @ (posedge okClk) begin
        if (ep_write && (ep_address == (ADDR + 8'h0))) begin
            L_matrix_coeff[0] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h1))) begin
            L_matrix_coeff[1] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h2))) begin
            L_matrix_coeff[2] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h3))) begin
            L_matrix_coeff[3] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h4))) begin
            A_matrix_coeff[0] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h5))) begin
            A_matrix_coeff[1] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h6))) begin
            A_matrix_coeff[2] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h7))) begin
            A_matrix_coeff[3] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h8))) begin
            B_matrix_coeff[0] <= ep_dataout;
        end
        else if (ep_write && (ep_address == (ADDR + 8'h9))) begin
            B_matrix_coeff[1] <= ep_dataout;
        end
    end

    assign L_0 = L_matrix_coeff[0];
    assign L_1 = L_matrix_coeff[1];
    assign L_2 = L_matrix_coeff[2];
    assign L_3 = L_matrix_coeff[3];
    assign A_0 = A_matrix_coeff[0];
    assign A_1 = A_matrix_coeff[1];
    assign A_2 = A_matrix_coeff[2];
    assign A_3 = A_matrix_coeff[3];
    assign B_0 = B_matrix_coeff[0];
    assign B_1 = B_matrix_coeff[1];

endmodule