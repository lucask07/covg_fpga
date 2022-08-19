// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Aug 19 12:33:52 2022
// Host        : FDC214-01 running 64-bit major release  (build 9200)
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
VVHSwsHgkuAiwoWg6Lepu3Bt9aZ8YPFI0BN6hPSNw4RQ7ZRUehCegrUUMcJzJN3/9UcFgjvIA5Pf
3FhA7sdpfZBbZsfFPBxhHxOrC+FgSWJzg0cXykIFg4zLZ+BNqyyGWkizM1ORBZFDX7BziC2PC9RH
YDDcpFqHQLFxkdHTKO/3WN4Na2W63ans86VQbM8FOSBgJ7TH+/nK29uRKRdC9UWMlAuxWHWxfy57
Agf34zahXoS1JauTq4UtGwWNxZ8SbWZmrANmP8wKtncpFHgjSFI8Ya8PEn/4rorCYX6RCulVtqdK
iaXHvrZTXs33ri2p1WzdPMr9p2xhDByEmgOpHA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
qq47gIHPkL70bXxIbijtruNJ4F6tT3vZTLQ6ZrXWJYXt2oWsstxtEnynAFFIoZNB3fI++d7R0SGQ
5uMQ7jvTPLD88woayhanvEtFVLIP64FwmzLsyW7qoeo81znUCmFzZYRklxpXM93SbbkiuYJ1a6Y6
CxQv3C7FgQ8llNZq+ViP+RM+YR04j7cL9bzmUVPk6K9G/SByYpg/0tbdG+cfKuf/3ECGh42GJhWl
uASzcJ7z5eu/RSHq2l56TTKctuTmgV6E4Nc6LApGov5hCh+cdeeHHV3G6i5TOL3T25KTwl2588ab
tbi6D7RCe6IXRW0rp+yuhwPoyDke5l7X35EzLg==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
dVahfWJ7tO0=
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
