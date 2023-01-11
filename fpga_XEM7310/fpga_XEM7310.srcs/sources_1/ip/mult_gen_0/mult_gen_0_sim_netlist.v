// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Jan  9 15:28:25 2023
// Host        : FDC212-04 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
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
Lep37/BHq7C42alwFcV3Dt7U+TjUthv+aQUrPdSUV1mtlXKpSA6eGI1V//sMX3g/pYqGLPEOMdMV
T5Vodoa88SDGDfwrinoysxQct2QHdDCen5PQ2BSZasBFk+PN5eqoNaGBL1kFoZphQ4Mvafsj0xs5
wg3i89d7QbSN/Xk96H3DaxcnKh3gmAPankhz0U34FLD2o01V3ROejQe/O1On0dDJlpzzHNzCYy9O
MHXbJgDa1nZNGcZVwj3TQw5f6gnky9VudgpleWLm4d7BfcmZjNlfvY8sfQajZKQ6YwYsFXst4rft
dJmxc15+yauO3YnjfORIV8lMJV1s/wCK4RsedQ==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
YQfObSdnG6t0aTC+Udl3TUHDIscWkcP3TCqutYmzt6QYxHSFgABQLd7F0jJ8JGrSVrHrRkXc8jLj
OlKqhqvQjsr6nyra50DzyA6n59cQtQ43W0lhBtJvhEr4r8u4nwlbTrTbbTUhxL3Y6FeNH0cFGAQZ
xsc2KdN6X0nBO/nL/w41xvLWJXUqWCbtB0PWdfZcHaKcVRX1hRiszHMmmRPFZ8c4zBYmtcwesSxe
EDN3gqP02Yylfa9vDois/pIJBB7iKw1DXDUoqy5lYzZeLURdi0tFqofrZaA1qVf7NUc71SX8cyHJ
826ZkIElyA6m+yQ0e+X8CFiZl/DAQayqDOeUew==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
SRt/kEYwWyE=
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
