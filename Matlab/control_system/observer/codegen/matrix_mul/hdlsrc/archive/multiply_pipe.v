`timescale 1 ns / 1 ns

module multiply_pipe
          (clk,
           reset,
           a,
           b,
           out);

  input   clk;
  input reset; 
  input   signed [15:0] a; // coeff
  input   signed [15:0] b;
  output  reg signed [31:0] out;  // 14 + 14 = 28

  reg signed [31:0] out_store [0:2]; 

  always @(posedge clk) 
    begin
        if (reset == 1'b1) begin
            out_store[0] <= 31'sd0;
            out_store[1] <= 31'sd0;
            out_store[2] <= 31'sd0;
            out <= 31'sd0;
        end
        else begin
            out_store[0] <= a*b;
            out_store[1] <= out_store[0];
            out_store[2] <= out_store[1];
            out <= out_store[2];
        end
    end

endmodule