// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Thu Jul 14 10:50:11 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
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
b7cERm7Me+3ck3fZ0qve/t3p4SF82kA1ULuLytBCjZb1hbNQo8CdPVBzGVVGDYfbQOPouj/LWwEw
viR/OmElKfUfmCTYy44Xn31vVK4x5mW/HRhupe2xJ0UJBWhyMnip32Z5Vyk2GOGwV2Ax1mTV807O
CEW1VePQkj4vPDg/7uVRFRr9LcL1fXc7fE1q5fDYm4ZPpf3gfxgZ6quhLUmZ0yYfdVVTUyK60UYF
8yfm1vsnrlsWujpZJ9KovY9F0Uk11eDUKRb7JOzAB/fnO4hCsLgqRhUoHEgnkz1qBVzzP+dbMMe6
tZbH6GQ5e7ULK+H+yVBuhUxTLcqmfmqBRy18/Q==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
V/phOjTo1xg3RbeATZ1O6n5ExfwVC+Qc3PNJva4e1LmYeoiFTJC5dWtpthLh+bz1vMpMu9JnrAR8
DPwlOySdLtMV0x+l5wbp9pQYhhXD/GPTviwtJsCPBiJvEs3gyIwLNHCmpbfbJvg9eAk6uYy/QTga
2G3/OkZdFGNrFl2GfwFBmTXFzR3Z5BKcfAtln2arSyt5QnneBTqu3K3VxU2DLTmduWqmDGt2kqBC
kZi60opSmbdePwC42eSrYy0/aKo9TMPqCOIQ2qdvHuMJf3WUG8ALuhhZdPN6TTArq8zgcnjNxluZ
Py2D/BgftQhide8ZfeZziIKO/u+MAWHxrjn05A==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
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
dmrExnm9Lqs=
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
