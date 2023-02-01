// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Nov 14 13:16:17 2022
// Host        : FDC212-04 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim -rename_top mult_gen_1 -prefix
//               mult_gen_1_ mult_gen_1_sim_netlist.v
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
(* C_VERBOSITY = "0" *) (* C_XDEVICEFAMILY = "artix7" *) (* downgradeipidentifiedwarnings = "yes" *) 
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
PpqKWNeTI4GGvL17n2+V6VxOHyYSyH8w2KPHrhYFpVgOdVceo/0aov02ajQ3ETUUGM+HKTS4hmmf
3l9AncvjY3sr/Ffebvcil7ph6I1vJzEpy1HaOlJON7ITqws9yTJsNJXOwSvE/bnwJv+1vfZCiAqX
LtfD+AhDpSUuCXf8PKIcPhohRbYfFbAmYNyWmtawxgleFh3V4zmc4Dcn44qqzvP2AGClOIj2tuB+
YvHUhQjhBqVYdDuJVZEZcFLIGD47tXJL1OO7Zyl6GGEmZSIR3zPWEZaVPoOb7Pkdx7nvFlD7Rsjs
Z7SjQWWNjSiJwauOm+LlOogfdk1uLEAJMaH8ZQ==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
PKXRqpQfSdHxS6fcKUJdQ8e0bCqE86QjouGgB0pMRuIBeAuzSd4JcYRS/UzBOBT8yrNYWKWtVjv+
aU4M7SXtiqo+zBJxog8GtCNJuwKspiAjCc5b/nBtydlmHLRnd7aLf+MVTQMkJ6X1NYjgOaLMinPd
wS+/NIAwVerunMtWqRKuOr5GS5AapjfsM48oPXIKP4hlwqDv5M/P6Uv5g8GQSICc95h7HuMqDvlv
O/1ToXWa4vM2ou1hzfUcMDVAEAAmI7nMR/R7CXY1l49p4u6anzmxrJqfKBekls+mxZ/jwyLOCyj4
LrQ1v8W+6yc8+32rJxY6jwUSKjoy2ejawi4ubA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7232)
`pragma protect data_block
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
RdRLy9BkG8rcaKA=
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
