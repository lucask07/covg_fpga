// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Aug 19 12:33:51 2022
// Host        : FDC214-01 running 64-bit major release  (build 9200)
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
Os5q5tRbAd2zChTqufPiyG1E/ivNzKSqVciC4jYPgynGxMwMBn6E4QRpzM4bLVNh2YSgth1nX+wP
RrDhNtQIkd0kEVGXStaqQ27rEyFKVR5/ueg9Z9FePlcoCG/Cr9FiTKmsG9O875mX9kaKPBoWN0uS
Nc7Nbu0B6wtyoVOzmeAFAhw6KIM4LCjp14qUmc5o2ClL7+eEmaT9tvy9YVaR0dLtu7EYIoTTNUW2
f6+ekw6oQaEQ7JmslZZDbkIHKdTg2whcK19ZoTAOHDxKIRx2Jn0Lz58TwS6+eWwvZSshrSriBZcz
FaVgFxOmzLby6dgpQVR6GujQfP78ZusdRwpKKg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
u/VCu2GqjpvkZLLemx53m62FKtEJSTttmTT17yhfmbilHB18mkIRjrhLUE0Bz3TtAuqwSnJSpy6o
UB8+tNeQ44KcPkkQ37fwvnT2N2SGjj1fDH5sG1c4EpljsWnx1KCuxOpUkSCoHZZHYuzMdCspsVWa
CgmkVpop5JJzVljSpjtq08ExVTNzDVY2/9oMW3gByg+AxlrduwkhijqNMu5yGoTEfgISZ6hvUluq
79yyBr+C1aLOTc010di7S+AflUoSmQhDzfKCTa8BAgFcNXc1vH/E1iN6sw4UvCyTM1yIw/Y+3ra9
VKLoj4Apv+FrEd9hPHCB8vZYa8ZDNJS5R4ld6Q==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
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
nkwqTd1dcR5zDEdkm4nHPizS
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
