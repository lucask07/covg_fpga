// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Jan 14 10:57:47 2022
// Host        : LAPTOP-RK0H8TS5 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/iande/Desktop/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
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
bYVIHXivE7r//PliA5cXlst2romI7Btk7MzDP74sSARc4qXkScgVOoALnbhz5kO6l2SGmfTIxDnN
YkSkhy4ldjhxtDcaRJzHxpugbu5zfamnRCsPth8e5urfSThBK6P6x0eLskWxAPiga6uIQwi6G+rk
8jvQBi5u2qpFHFFgrWRh3wkUAgV8FSsm8hbQzAnecJDk2lvHoZzFMMQ2ys0ixBcCBNsmxNWegMJt
sa3xTc44ldya1EsD96bPhwCZwkeLK3My6QX+6fbSNB/es+ms458aTpCAOdjRBOMOweNNVZVFaKkt
HZUa8unIfHwSAuouelVBCZZUo/pFyWbaQKXulA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
NJqZtSBDhpcjPAD3MpS5dfrR6zUfNge5fLZS7iy87k9fQamlMrJ4eJsPU56xuFB/1HDCeNDqs+O/
TsnpgceAosol0WvZ2J2nnklWIp9zHj+mPTtvBCsvDU+AXUvWaFwzrdd8qoxfZ6KQwZwhU33kBQxp
rmVmUMIZtudRA+aL5IYGDd9pWMqM/fO759JiPB292f19bacqABN7V57BDoCvBg8SYzdufu9kGsAi
e2lNoMHOg/IWhIKw25Gc2cnP8X0QhXmjAhJtiT233M8Lf3I/Brk4Mf2Y59FzZF/oBeKMIaDd6Z7I
3kcMLD4KHaxvsOnLPG4vpc9AiYYYmsyp/eWOYA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
fxilkai9yV0=
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
