// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Nov 14 13:16:17 2022
// Host        : FDC212-04 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/koer2434/Documents/covg/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
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
iGcskohuIUuwTVz0jpDeqKUeuN9zltUsojQwU0I3AgIUCZgDNbPuqV6TgaYdJuLxQxMWXnzg+9MN
+aGSPknn0eAi09O2glYtLhfzT9KtDhFMiSX9/jplimCyM7Aav8yg7f/8bciJUNDihqCQGC4jojki
bjSqpAf4cXnvxcGz6zaN76Yi7J29UaYZIQp4fEkuKZRs3T4crkxRhV8b3Z0alnVXpwK4FU+Uyntn
FcmnLIe4AMh+lI+DK5AxMpTLIXzqKfKcBbAXkLuW+zDP9Sn9la6a9dNfKFvLLMl7/bCH/EGx4Y7S
+XmOnDuHVooeEm2pQvUqVCsB3n502GVm2JOTLg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
liElw2Xix6XmaFOOxAcIpefCbRAbq4zV4zmjgXnuhjjxl13/yYVQ3Lym2Utxpkd0xowqodegBDqA
bUIqBzMB4Ztm0ZFMeGLyz8v7SzHdaLFlnn8ZNQ0Sq7CzBT13MKuYoX1ewPmKLdOF0IDOVkoSUiKO
LAmcpRFPe6WAjXGHD5VrwaZj6o6EuGgv6yn4zaNMVHatrD0zTWXDFCvITOirV1aHSK8F3kFiszmn
EXYlIGK7QA4kI5HALbJdTZl6T43UKrFHeNtb4UTwZWpuL8PJb7HYKg7S7N0D1ggXQSVovPA9KY0y
lBoFlZxgcp3KH2rP1ApFH2mzj9jqU/V8lm2mhg==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
+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
34ZRpD9kIx/+fjBRUm/NzyRf
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
