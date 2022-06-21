// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Jun 17 11:19:51 2022
// Host        : FDC212-05 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
// Design      : mult_gen_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a75tfgg484-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "mult_gen_0,mult_gen_v12_0_14,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "mult_gen_v12_0_14,Vivado 2018.2" *) 
(* NotValidForBitStream *)
module mult_gen_0
   (CLK,
    A,
    B,
    P);
  (* x_interface_info = "xilinx.com:signal:clock:1.0 clk_intf CLK" *) (* x_interface_parameter = "XIL_INTERFACENAME clk_intf, ASSOCIATED_BUSIF p_intf:b_intf:a_intf, ASSOCIATED_RESET sclr, ASSOCIATED_CLKEN ce, FREQ_HZ 10000000, PHASE 0.000" *) input CLK;
  (* x_interface_info = "xilinx.com:signal:data:1.0 a_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME a_intf, LAYERED_METADATA undef" *) input [15:0]A;
  (* x_interface_info = "xilinx.com:signal:data:1.0 b_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME b_intf, LAYERED_METADATA undef" *) input [31:0]B;
  (* x_interface_info = "xilinx.com:signal:data:1.0 p_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME p_intf, LAYERED_METADATA undef" *) output [47:0]P;

  wire [15:0]A;
  wire [31:0]B;
  wire CLK;
  wire [47:0]P;
  wire [47:0]NLW_U0_PCASC_UNCONNECTED;
  wire [1:0]NLW_U0_ZERO_DETECT_UNCONNECTED;

  (* C_A_TYPE = "0" *) 
  (* C_A_WIDTH = "16" *) 
  (* C_B_TYPE = "0" *) 
  (* C_B_VALUE = "10000001" *) 
  (* C_B_WIDTH = "32" *) 
  (* C_CCM_IMP = "0" *) 
  (* C_CE_OVERRIDES_SCLR = "0" *) 
  (* C_HAS_CE = "0" *) 
  (* C_HAS_SCLR = "0" *) 
  (* C_HAS_ZERO_DETECT = "0" *) 
  (* C_LATENCY = "4" *) 
  (* C_MODEL_TYPE = "0" *) 
  (* C_MULT_TYPE = "1" *) 
  (* C_OPTIMIZE_GOAL = "1" *) 
  (* C_OUT_HIGH = "47" *) 
  (* C_OUT_LOW = "0" *) 
  (* C_ROUND_OUTPUT = "0" *) 
  (* C_ROUND_PT = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  mult_gen_0_mult_gen_v12_0_14 U0
       (.A(A),
        .B(B),
        .CE(1'b1),
        .CLK(CLK),
        .P(P),
        .PCASC(NLW_U0_PCASC_UNCONNECTED[47:0]),
        .SCLR(1'b0),
        .ZERO_DETECT(NLW_U0_ZERO_DETECT_UNCONNECTED[1:0]));
endmodule

(* C_A_TYPE = "0" *) (* C_A_WIDTH = "16" *) (* C_B_TYPE = "0" *) 
(* C_B_VALUE = "10000001" *) (* C_B_WIDTH = "32" *) (* C_CCM_IMP = "0" *) 
(* C_CE_OVERRIDES_SCLR = "0" *) (* C_HAS_CE = "0" *) (* C_HAS_SCLR = "0" *) 
(* C_HAS_ZERO_DETECT = "0" *) (* C_LATENCY = "4" *) (* C_MODEL_TYPE = "0" *) 
(* C_MULT_TYPE = "1" *) (* C_OPTIMIZE_GOAL = "1" *) (* C_OUT_HIGH = "47" *) 
(* C_OUT_LOW = "0" *) (* C_ROUND_OUTPUT = "0" *) (* C_ROUND_PT = "0" *) 
(* C_VERBOSITY = "0" *) (* C_XDEVICEFAMILY = "artix7" *) (* ORIG_REF_NAME = "mult_gen_v12_0_14" *) 
(* downgradeipidentifiedwarnings = "yes" *) 
module mult_gen_0_mult_gen_v12_0_14
   (CLK,
    A,
    B,
    CE,
    SCLR,
    ZERO_DETECT,
    P,
    PCASC);
  input CLK;
  input [15:0]A;
  input [31:0]B;
  input CE;
  input SCLR;
  output [1:0]ZERO_DETECT;
  output [47:0]P;
  output [47:0]PCASC;

  wire \<const0> ;
  wire [15:0]A;
  wire [31:0]B;
  wire CLK;
  wire [47:0]P;
  wire [47:0]PCASC;
  wire [1:0]NLW_i_mult_ZERO_DETECT_UNCONNECTED;

  assign ZERO_DETECT[1] = \<const0> ;
  assign ZERO_DETECT[0] = \<const0> ;
  GND GND
       (.G(\<const0> ));
  (* C_A_TYPE = "0" *) 
  (* C_A_WIDTH = "16" *) 
  (* C_B_TYPE = "0" *) 
  (* C_B_VALUE = "10000001" *) 
  (* C_B_WIDTH = "32" *) 
  (* C_CCM_IMP = "0" *) 
  (* C_CE_OVERRIDES_SCLR = "0" *) 
  (* C_HAS_CE = "0" *) 
  (* C_HAS_SCLR = "0" *) 
  (* C_HAS_ZERO_DETECT = "0" *) 
  (* C_LATENCY = "4" *) 
  (* C_MODEL_TYPE = "0" *) 
  (* C_MULT_TYPE = "1" *) 
  (* C_OPTIMIZE_GOAL = "1" *) 
  (* C_OUT_HIGH = "47" *) 
  (* C_OUT_LOW = "0" *) 
  (* C_ROUND_OUTPUT = "0" *) 
  (* C_ROUND_PT = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  mult_gen_0_mult_gen_v12_0_14_viv i_mult
       (.A(A),
        .B(B),
        .CE(1'b0),
        .CLK(CLK),
        .P(P),
        .PCASC(PCASC),
        .SCLR(1'b0),
        .ZERO_DETECT(NLW_i_mult_ZERO_DETECT_UNCONNECTED[1:0]));
endmodule
`pragma protect begin_protected
`pragma protect version = 1
`pragma protect encrypt_agent = "XILINX"
`pragma protect encrypt_agent_info = "Xilinx Encryption Tool 2015"
`pragma protect key_keyowner="Cadence Design Systems.", key_keyname="cds_rsa_key", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=64)
`pragma protect key_block
Xy0rQtyFjlVkbWfeQXwuqraA3MiYyL0eFNjbY4iEa+s0Iy4tsgQeJeqb8F2nyNFI15QQro+xjbie
m+gt7LRqSA==

`pragma protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
ket885wFwjDLqC97HI68cpTwpD1hGBIJdkMh+rsfw+vPf59MdHJNNbcLh5jkiDAOhjCAn8l7Pljd
OAdA4DPaB1th3EEcK28Uhm8xkCE8u1JeKM+cTawL1ZqM7f5vFJDMTdaQdo2ODraPwf63iOc4O7I1
Jp0iW8w4eq4dmJxUtLQ=

`pragma protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
0sLRbF/nd38eurlUzps5D+y+9REEleMhJud3+B55Wgm1hYo1ntzC4vdMFNHAcAq1l46fEiE/D85o
eYPC/WuBoZraAAbt+2vzvO+6NgUIpKKrii5bWkc7zSRBw4OUgkdgOToRQnup7uEq7pNL5gER2W2q
jpbl57Ks7667W7TbtoCx+55cY2wmHeQ+Fi9eAhxvopt9UQ7JhiAITU32QV0QOUo0C5DuMrCOfUPt
Q4mY/sCujPAsGwpHpQOH6JmVeTJ9/9FBANFdHkzv6F+8T8a1pEE2+YcJXysHrFHMtW27J1ZZCZGA
hChjmCakAGz4Jve6Njfz9RKNiLrrvv0gHwgvEw==

`pragma protect key_keyowner="ATRENTA", key_keyname="ATR-SG-2015-RSA-3", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
Z45gwqdZGpYP0Kv2lPvhL9t/dewTJD5ANS61F5BSLbdhMd8PVbRummT3J9CrH0Xrbuzjih6sOpQw
kP9SCPfkWk0LECt8HjobCatSEoRRONU79HyCEoDk93VT8CY8JL1BVS13wUngEWn6CIfitTyUUXR/
CxyxtdDZQFDUfHXEX4XQ0Yn12IXvHzgVAVLyG8UmGQWtQl4u7U/ZvMszHbCI4hHi6FW2kYvzBYlf
e14GZYOKCoOlqFp/3u2vs2rSSE9ciWV/SYIJDbOxsQCcBEM+UYYOzWikcZxKJAlJhndq92g1JKTL
sQcp7SBbbJ1O6Xynuz0MZ47Dfl+F87qkHSjwDQ==

`pragma protect key_keyowner="Xilinx", key_keyname="xilinxt_2017_05", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
AeZ3V4sxDArImz8Q4W0bdOLintyw5zFj71qsxS4fYZUiRz8fNjC87lJzQ+YnUM13/42C5tAz/W5B
5De7uFmIgyIiHZ7Y1Ljeaa49Hank9rJJwKCFDSSNL8oJL51I1jWnn7YQnA7UX2zo1TTkepqKq7HW
QLVQHxdIfz7XQJ1KYPLfGQXcsGEecPlraNmNXeykJAgtAFm5XnR8iyVOGbjm9W9BUx0070wOpVoK
DNLr58vy3yAgTwtSBr+RexJEsBPZIUDyrA9NgYHy91GC6l4e/tQMTkA5GUgHnQd/YiVINSR358nO
A3j+0MMXq+Hrg0TJtfXsqD7mdjD7gjs4pqa1Vw==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
BTz6m4RfoEciTWA22aqSQ7leYhQBT580p+3gUMnEkDKrl8y/O8yBG9prYh9eaBfxpy/1/zsYPTfE
O0sD3klOHeyC81JjLy2AWCWL1sk9/7n5I9vvSHXaQP4PHYRjAzqZC2XENPD0SKyVkobaEQpad+o8
VjB8RI608B9GgMaZvYA=

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
D7Hbf96be8hL6h8aH9GXSy4IzBK9xG0ri9cVSVfA+REat+znGl+3rKoWJP3Y8xVsMkc1boG+wuph
DvXt9Y8VIRQAHNgamdZlVmWFc7YNNoioXwxsiPQUGQ033qF9EQryRyyXiVxfPqJOSfqv7PrbvgOT
5UDZUXtmOWGVrgoDlz45TFPs5v+lO6i3RYt0nujylzKTS8VLhLp7chpkjrCdjQc8hZGNDkUI5WPz
T16PgMtr8+aqlEn030MgQ09L5vJki+2qisAmejQVoQ30QbY0N/13XTb4LdaYF1u53Ib59hKf/1nP
//1d/wsq1f4QJoIkaVIa2ngZqWphjv4BhaOjtw==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-PREC-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
cJujn1Ocw7mSGcswsnXaMqSlsOeIw8ehFrcxDdUjG8BPBCZBawpHkYD36kGF07ZiZIEe+WDEcPXM
Ltn6ML3u0LpIOJC14mQPS0S4m1fJcEtrg6DhgweNJfHbpv6cf+/gl2rQJKH1xrgpAhXi6mQCYd9K
OtW+i4EhYD7EL3gP4RIc/NbmVNj80g8fv4A9NQZhUU2/hv2P7+SbDn+idKLihy/WR7O+9YJMOMy9
fbhkEoYOmbupiCBkT22Gb073e9BOKzVRl7eewXb8eNkqQozT0GCBz4D1yaJv5ttt4YDyKciHgzU5
NyVtJ7/XA+viwccOmJkTlSjupxwLE6pK55palg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
Eh5rC4iS7D2+vFuoEWB4Om1mBYs7w6uRrIlyGIDeLizCnRFL7eZm02fsbTFKWjZm06ox39aMna+m
1zuZQn+5/dlR0rKlQV+mfKbqY0N0cWDh6ByVKEWDcXy4bmraA5myWv7E1slq+SGIlzFGSB3kMXwW
ri0vu8SXi3kGIZOccbEALuVf6NHxLHOMfDputlx4D+p3IJOq169rh8quwPiQRkw7jYdq1EVeTUor
5Qec7BTgzqUW3JtL9+eHSHPpVbPBio7qreUu1YkTwz4z3VfuS9/BB8i/ebA3sTzbIc+cU0a/+CBn
sk0GYt5ctvyILVdqUCYf0ZjJkOTt/BrpSqZ/Yg==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
0qzYvRbmh8k=
`pragma protect end_protected
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

endmodule
`endif
