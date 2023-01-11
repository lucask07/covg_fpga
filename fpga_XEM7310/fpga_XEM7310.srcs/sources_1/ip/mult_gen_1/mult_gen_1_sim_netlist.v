// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Jan  9 15:29:11 2023
// Host        : FDC212-04 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
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
EUYwwh76VCqVQkJEWMwCxxCsfJuhBNEnIWjJVVHV7WiEYJNmWnu5kENxM3o5TGvPVsIX/MPOJHow
JXx2S2jS0Gart4Fye9PN2CpMkqfN+XBGYxXSQQ/yqsFlXcBNVTSif6eNKuaJwKNhW/ljosRzWngl
WILxzgB8fe4I9RzvcMdabeoSkeVLlr4V4fRJ7POSBdnQ36CGqJ/Cu0TCnqt7yzZz81bOYE6nCb3C
TpLz2ebq7hMc2gBmao5GJQIRByACSLS6OOuWzW56bIY3sKAbEtBxqCyBlBd003vIbcmGbB7aCGRl
EU2Fh/8q5lMBmna21Dy8t3QetksjtG+4FPe7sA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
PbdHAsjBYDdvN2yVPfx8rT3m5kF1y+NHsX0jifS8Zk9A+VGcOIszAXUmAdLI/lpjVlA98OOyzCmr
NreSluzv0lg4ZiX1HQqFG4duoNFXPTsCvULOQYNPRGWG694S47ptAR8qyDEyYzXHKPizrmrYa5uh
kjZDCw7vBbWIgQyYNejJ5vk7wYt5b5Zl8UszCXuVAJagLwANJhDNd4rG23WF63Q4gzOmaueddnUN
z3jZ/Hp/TAOwymPcazlowB9tXwsuXSjTWPwOcF+uAjneMFH9GVpCAuaJBHGp0cGT5WNZhKLICyvg
XGTCyL3ifMoi1WAbFKJuZW1KlLcs4pT0M6d7Zw==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
NgvMlMyEma5iiFYY+YSOODYW
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
