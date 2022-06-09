// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Wed Jun  8 20:23:06 2022
// Host        : DESKTOP-EPIAN0I running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               c:/Users/iande/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
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
mD9jWNw5i0k6Q3tuPbq8/XIn+eY79hIYqN7FIQMR5Km+AwFUOB18nhlcMkIOaE+J4kDVlw/rqVAV
neyVy7ejLhwjYZ32JJhsLwEUO4l2S9hts+cE38JMQzr/kGu6Fr5jcKzlQ2DYUKE8VKsQs3AEY9W9
9A5su1W06tS93mfo8Pukfc7kyqDItWF0FuzmNL/eZt52xiUSetBPZxOW/5Zj28bYfFGP0f71+JKX
bgLPh0ZOfdBkU+bh7uuvGOdY5lMl3IwQsCZg4QXVzFCFt9vfasyYHT6uBCkdShV0MnbkoYspoZw4
nENsaJRJ9Tg8taJ34oFNT3KGEeb0PR1reBDLaA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
ipRdwd31PVf0zwtu9CH5jrkJv62froBEP1j2iD3z81M2TUCgkEh1oAC+WzYi1EAu8KJee7pxlwXJ
drsP2aKCDUQkc0Uaj3nWIbLvpJJ6g9mj8yFAGEw55Ni4++S5uVkRHroXn9+OdqllDUngVBWP7LOk
QZLy0NyeQLuPDIkMPZzf3X+Sd/IKbroSg7fDkQqyLkL5jedeDeAM3lcvphYizpp0Mo+1yypU6zWq
o1CSGneU9Njniw/wc/ZZr1WirMKa7ghX/fO4zlg8+Wt+5kjeHeMfnsMj+DAj/I/r2pHVbkr35dCS
yRxj/kQ/hOOAf4UK4QQJs+6XWvS6uMXPmnIAsQ==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
r5jGwyLhLsRw1DCLtlzlPcrM
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
