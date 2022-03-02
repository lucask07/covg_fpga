// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Tue Mar  1 14:13:35 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
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
ZAko1UjkxML6kVPNkqPRlOvvIyFrDTYPZq/jkzMBEJK4wnmVSMNoolP3YYxe1rUhkwGhBHV74ZAF
9PknTqKFVEOtfZhxikh8Lbl9mo+ykGjmRkeayLU1vTO2jYEqewB5Bgub/ET45ls5zG1ExJWYTFnX
Af6R/NFTdlx1cLAxIZRNQ0YP9oe0Mlxm1bOEBXuXrR68Q5YrcOF4IWpd0LvXvoLnVStN+dNUXLo3
pBH39Eb08Cb4in0ib9UgWhjpPN120GFGgbmBAvotPXTQQUmx9D+sBIO0wEIRgzSCIaoMldSfvIYp
nTMy418uwIyIj8C7JkaaPUJyNlb6MCS9LbVsWw==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
ICk2dgWg+v3nBkgJQ1hD8Ap7fi06RBRZGBSZhP2EmiJ5X/h92ELA2WrB1TKbAWw8Urbc6W5CEBUy
Gp1JqTRDyTijDjw5W4bjBPqo/cHXHFbqo4la3+vVIFzoSIpv0jAixAxG5LmbmopD/QwytVHOzqEs
HYH5H62AlDKYfIpFHvkVcvUX/Df10oSMEKrqQTGM1C389rpNjpw44MHwqXwP7gA3aPuOCRJvOpqJ
ki6AQD/Pj0bKDr6Nne5xOLlcVvU4VwS+HcRHZd5GrTsOgtlTzNFNaetYXkH+FXYzocpjkIRwvuip
8kOe2LXYgYhfDcJ59GPUdZFeLgR2+UhWImGllg==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
rJa1L16DQgg=
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
