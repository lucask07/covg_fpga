// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Wed Jun 15 08:43:13 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim {C:/Users/stro4149/OneDrive - University of St. Thomas/Research
//               Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v}
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
kmiSyHco2LvxP6BpZLlmQqsVkhO/fGndYFb9aABGCJDzOJqJO7X6F6eYxwFK3iw5cg4UBO3Ysbr0
7KMWoU3gbocCa5kiixeGDwh9XKTUQgOBxvLqVmwVEne/uaVIPlC9AWKFa4NbiQxtYvmNdvbqFDFe
PJ35eG35bvsrb0EYUtF2jkiMoVKnyz9x4dsU2s46lFVFy+iwioY/F33emvYad82gVDe8tTzGclpH
XWIlnyrTjjJeDqIDqKRN5025+kiCF1RGOXXsewWyjd5ytCCob7m1Urcn0C0dwIcp13t3uWYRbJZg
RPo8AfmXZIkGDd6OfHjvJCUqDGyTa1YhLLF9Qw==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
uZggwn09P+bF9+oRQ0JeEONu0NCvGdHm4WT55ITAv74wGFc4llARJbm9wfmxMWjBeDRkCbQ05S2y
1wIzH8vYyqgtLUnUMJ/GBUKMdZnLMLJh4pLCGF5deLJS58uRdagaQ6Zn6NqiYPQqY6q/e1eRDtNe
7ZKenqPbcUoLfww1YMPmIVwyHaX01iwNKqhnv8oa0mU8VNfZT6bNfa1TJ3texGv8zseK5zE2UCp3
jjJQh+LtrmON/IAhDjXhTNfuk770SxsLe6flaPOC7/AV5N35ZxkBSUdbvM7TLccXw6EDcJxWq71n
EEHLf2lCYVi2YjRcV52NT05czdRCfD9NShGJbw==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
oZrdOXUTznp9j2bjMJZNddev
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
