// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Jun 17 16:20:27 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
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
D+kscNigM/259NtWsHFET/6Yi1MFKCVqW84z3FDh2VnOf+wnyxvWpsdiKtL7yi0Q/Nwwmy2LE9uh
c4YbTplYD5zK2uhTlK6f72X0Zx4YqwDUK3QAGn5x4cGKOowUf9CVG+IVABkopXYz6epUfwjzcnDU
4i3Mrsaw4Iab6LL16uCXLT3OX4ipaCAylL9en+G7kAvtKxNsjc13cjSyQ/4W/Bk2sgyNG6sKY3xB
Qg7lbPys37fZA75yeSwDqHEetzHRpmCLGBEXmETcaQ2hn9QVqM5ieBKdQWKPGb4WSHnbz4XHqSYK
gmK5G6zmUCZRQNdKwQdJPx9moZlk6dROIVqshg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
KLmQYtebsWZtV3x93sN0ntZb2OTmvtdlOywSSvmBBZYOaPsPWguKH+Ck26sOe93A6G1hhpnMVFR5
aiWvX2kFsIh4/jgA4NrI5lC2QoKCR143SO4idRqHgZmSeqaLmD6un2Thp94pIpjkuzKWisS5Sg+3
ONx3S3EAXURYdguKbCAdPu+hR2c5Gp84IOvOvgKeUecKEkvf+q7nmb0++OVeu3uzjdHGiQtGmz53
3zpOTj+lS2PnSVFb1B9pREQ50RK2QUPnc2TEVzY972oMe8Q4RonB7DlMY+xEaa/OQFFdgZD5goVs
PPXYY7mc2MKhT2kbDbFAYDCDJQQYG595Og6lGg==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
bUjrJiGprs5H8Qvnfwx8YjB7
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
