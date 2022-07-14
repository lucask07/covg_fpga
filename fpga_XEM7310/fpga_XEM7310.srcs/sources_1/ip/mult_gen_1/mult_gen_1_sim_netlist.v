// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Thu Jul 14 10:51:15 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
// Design      : mult_gen_1
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a75tfgg484-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "mult_gen_1,mult_gen_v12_0_14,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "mult_gen_v12_0_14,Vivado 2018.2" *) 
(* NotValidForBitStream *)
module mult_gen_1
   (CLK,
    A,
    B,
    P);
  (* x_interface_info = "xilinx.com:signal:clock:1.0 clk_intf CLK" *) (* x_interface_parameter = "XIL_INTERFACENAME clk_intf, ASSOCIATED_BUSIF p_intf:b_intf:a_intf, ASSOCIATED_RESET sclr, ASSOCIATED_CLKEN ce, FREQ_HZ 10000000, PHASE 0.000" *) input CLK;
  (* x_interface_info = "xilinx.com:signal:data:1.0 a_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME a_intf, LAYERED_METADATA undef" *) input [13:0]A;
  (* x_interface_info = "xilinx.com:signal:data:1.0 b_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME b_intf, LAYERED_METADATA undef" *) input [13:0]B;
  (* x_interface_info = "xilinx.com:signal:data:1.0 p_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME p_intf, LAYERED_METADATA undef" *) output [27:0]P;

  wire [13:0]A;
  wire [13:0]B;
  wire CLK;
  wire [27:0]P;
  wire [47:0]NLW_U0_PCASC_UNCONNECTED;
  wire [1:0]NLW_U0_ZERO_DETECT_UNCONNECTED;

  (* C_A_TYPE = "1" *) 
  (* C_A_WIDTH = "14" *) 
  (* C_B_TYPE = "0" *) 
  (* C_B_VALUE = "10000001" *) 
  (* C_B_WIDTH = "14" *) 
  (* C_CCM_IMP = "0" *) 
  (* C_CE_OVERRIDES_SCLR = "0" *) 
  (* C_HAS_CE = "0" *) 
  (* C_HAS_SCLR = "0" *) 
  (* C_HAS_ZERO_DETECT = "0" *) 
  (* C_LATENCY = "3" *) 
  (* C_MODEL_TYPE = "0" *) 
  (* C_MULT_TYPE = "1" *) 
  (* C_OPTIMIZE_GOAL = "1" *) 
  (* C_OUT_HIGH = "27" *) 
  (* C_OUT_LOW = "0" *) 
  (* C_ROUND_OUTPUT = "0" *) 
  (* C_ROUND_PT = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  mult_gen_1_mult_gen_v12_0_14 U0
       (.A(A),
        .B(B),
        .CE(1'b1),
        .CLK(CLK),
        .P(P),
        .PCASC(NLW_U0_PCASC_UNCONNECTED[47:0]),
        .SCLR(1'b0),
        .ZERO_DETECT(NLW_U0_ZERO_DETECT_UNCONNECTED[1:0]));
endmodule

(* C_A_TYPE = "1" *) (* C_A_WIDTH = "14" *) (* C_B_TYPE = "0" *) 
(* C_B_VALUE = "10000001" *) (* C_B_WIDTH = "14" *) (* C_CCM_IMP = "0" *) 
(* C_CE_OVERRIDES_SCLR = "0" *) (* C_HAS_CE = "0" *) (* C_HAS_SCLR = "0" *) 
(* C_HAS_ZERO_DETECT = "0" *) (* C_LATENCY = "3" *) (* C_MODEL_TYPE = "0" *) 
(* C_MULT_TYPE = "1" *) (* C_OPTIMIZE_GOAL = "1" *) (* C_OUT_HIGH = "27" *) 
(* C_OUT_LOW = "0" *) (* C_ROUND_OUTPUT = "0" *) (* C_ROUND_PT = "0" *) 
(* C_VERBOSITY = "0" *) (* C_XDEVICEFAMILY = "artix7" *) (* ORIG_REF_NAME = "mult_gen_v12_0_14" *) 
(* downgradeipidentifiedwarnings = "yes" *) 
module mult_gen_1_mult_gen_v12_0_14
   (CLK,
    A,
    B,
    CE,
    SCLR,
    ZERO_DETECT,
    P,
    PCASC);
  input CLK;
  input [13:0]A;
  input [13:0]B;
  input CE;
  input SCLR;
  output [1:0]ZERO_DETECT;
  output [27:0]P;
  output [47:0]PCASC;

  wire \<const0> ;
  wire [13:0]A;
  wire [13:0]B;
  wire CLK;
  wire [27:0]P;
  wire [47:0]NLW_i_mult_PCASC_UNCONNECTED;
  wire [1:0]NLW_i_mult_ZERO_DETECT_UNCONNECTED;

  assign PCASC[47] = \<const0> ;
  assign PCASC[46] = \<const0> ;
  assign PCASC[45] = \<const0> ;
  assign PCASC[44] = \<const0> ;
  assign PCASC[43] = \<const0> ;
  assign PCASC[42] = \<const0> ;
  assign PCASC[41] = \<const0> ;
  assign PCASC[40] = \<const0> ;
  assign PCASC[39] = \<const0> ;
  assign PCASC[38] = \<const0> ;
  assign PCASC[37] = \<const0> ;
  assign PCASC[36] = \<const0> ;
  assign PCASC[35] = \<const0> ;
  assign PCASC[34] = \<const0> ;
  assign PCASC[33] = \<const0> ;
  assign PCASC[32] = \<const0> ;
  assign PCASC[31] = \<const0> ;
  assign PCASC[30] = \<const0> ;
  assign PCASC[29] = \<const0> ;
  assign PCASC[28] = \<const0> ;
  assign PCASC[27] = \<const0> ;
  assign PCASC[26] = \<const0> ;
  assign PCASC[25] = \<const0> ;
  assign PCASC[24] = \<const0> ;
  assign PCASC[23] = \<const0> ;
  assign PCASC[22] = \<const0> ;
  assign PCASC[21] = \<const0> ;
  assign PCASC[20] = \<const0> ;
  assign PCASC[19] = \<const0> ;
  assign PCASC[18] = \<const0> ;
  assign PCASC[17] = \<const0> ;
  assign PCASC[16] = \<const0> ;
  assign PCASC[15] = \<const0> ;
  assign PCASC[14] = \<const0> ;
  assign PCASC[13] = \<const0> ;
  assign PCASC[12] = \<const0> ;
  assign PCASC[11] = \<const0> ;
  assign PCASC[10] = \<const0> ;
  assign PCASC[9] = \<const0> ;
  assign PCASC[8] = \<const0> ;
  assign PCASC[7] = \<const0> ;
  assign PCASC[6] = \<const0> ;
  assign PCASC[5] = \<const0> ;
  assign PCASC[4] = \<const0> ;
  assign PCASC[3] = \<const0> ;
  assign PCASC[2] = \<const0> ;
  assign PCASC[1] = \<const0> ;
  assign PCASC[0] = \<const0> ;
  assign ZERO_DETECT[1] = \<const0> ;
  assign ZERO_DETECT[0] = \<const0> ;
  GND GND
       (.G(\<const0> ));
  (* C_A_TYPE = "1" *) 
  (* C_A_WIDTH = "14" *) 
  (* C_B_TYPE = "0" *) 
  (* C_B_VALUE = "10000001" *) 
  (* C_B_WIDTH = "14" *) 
  (* C_CCM_IMP = "0" *) 
  (* C_CE_OVERRIDES_SCLR = "0" *) 
  (* C_HAS_CE = "0" *) 
  (* C_HAS_SCLR = "0" *) 
  (* C_HAS_ZERO_DETECT = "0" *) 
  (* C_LATENCY = "3" *) 
  (* C_MODEL_TYPE = "0" *) 
  (* C_MULT_TYPE = "1" *) 
  (* C_OPTIMIZE_GOAL = "1" *) 
  (* C_OUT_HIGH = "27" *) 
  (* C_OUT_LOW = "0" *) 
  (* C_ROUND_OUTPUT = "0" *) 
  (* C_ROUND_PT = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  mult_gen_1_mult_gen_v12_0_14_viv i_mult
       (.A(A),
        .B(B),
        .CE(1'b0),
        .CLK(CLK),
        .P(P),
        .PCASC(NLW_i_mult_PCASC_UNCONNECTED[47:0]),
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
oMtpbkVksmYVYN6zQweKzW/KHdbcWQz6KOYgZSqBe9+b+yU2S+PyuCUBCDTGGqDbF1Xx2BE072o6
1Gt5nGNOVweyjfT+iZeR5KrKM/Xkd7d7zT1R4PdlYEb+y8TKXQ7MGGYeZUcP80GfJF42KOuxCKBc
CN3tcF6R4GPTSgRfGrqQ/rCYt7SKOAdnHm0Rq05h5Ut0We3ZdYPcDQd2JV78Z1+GZIfMJrowZ/vK
/nNIt5FZE1tRfeQqYCpYt11rpKD/svwaEc4QxVEBWpZuWX8JH/aRuAL41Zsi+tZi0YwdaNlyWdj6
k1cxVtzFSwODbQg03HApdKgnD4rNGDfzXsVnwg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
w1TOgfWCZYcZ+QoVn8EuCe0KjSsKNkunfnRBoSSOP3BgZ4MoWV5j6C933S3CIpX6yfSOlZTxSp+E
XaCmL1gd3HwvBW7i/B/IQIyIoGWpAfFYWlqT5+wDg5mNer2Lx6Id37s6VEQxU2UdeuOFp8x0w/ed
lmawpeswKRUEl2m6zIW4A6uM65ZTre6j2XLxPSnU6uWYbarTIAZACpmmLnm5meTWWpNUR/CKBdvc
9/HNxGI9m47TxDy4/qL78z3T8G1Xt/pXWvsVf6LY7vYucR6RjtsOns9imaxOu95o7LMSDsnMHL3i
I48pqZAdG8anMQHBlfsaiN4GPE9Cj338fZi7dA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
LgQSTsmXFJnzixq3txtIgsMW
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
