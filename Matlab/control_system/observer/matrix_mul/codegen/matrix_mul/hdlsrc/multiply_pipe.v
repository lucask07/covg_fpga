`timescale 1 ns / 1 ns



module multiply_pipe
#(
parameter A_wid = 'd16,
parameter B_wid = 'd16)
          (clk,
           reset,
           a,
           b,
           out);

  input   clk;
  input reset; 
  input   signed [(A_wid-1):0] a; // coeff
  input   signed [(B_wid-1):0] b;
  output  reg signed [(A_wid + B_wid -1):0] out;  // 14 + 14 = 28

  reg signed [(A_wid + B_wid -1):0] out_store [0:2]; 

  always @(posedge clk) 
    begin
        if (reset == 1'b1) begin
            out_store[0] <= {(A_wid + B_wid){1'b0}};
            out_store[1] <= {(A_wid + B_wid){1'b0}};
            out_store[2] <= {(A_wid + B_wid){1'b0}};
            out <= {(A_wid + B_wid){1'b0}};
        end
        else begin
            out_store[0] <= a*b;
            out_store[1] <= out_store[0];
            out_store[2] <= out_store[1];
            out <= out_store[2];
        end
    end

endmodule