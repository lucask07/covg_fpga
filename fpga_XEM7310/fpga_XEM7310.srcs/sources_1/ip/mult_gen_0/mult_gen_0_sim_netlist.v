// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Tue Mar  1 14:13:34 2022
// Host        : FDC212-01 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim -rename_top mult_gen_0 -prefix
//               mult_gen_0_ mult_gen_0_sim_netlist.v
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
(* C_VERBOSITY = "0" *) (* C_XDEVICEFAMILY = "artix7" *) (* downgradeipidentifiedwarnings = "yes" *) 
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
mv1g85GD3aIXQOy1m2bIKRur83Pp97w5o/Nro+3VB52k52hackSQ3jYToR7Z0clDRlXTYBw4srVP
iAOcFrFtVK33vIymGLRYywZFhwMNaeROJ6XlZBEvDweG8hhqpI+Lrf2vUiFTwTlja/cgq4WLWXc2
bhG+nOHBZSO4TC2pu4OjVh4fnnOZZaZSrE9C3pyf/39BqLA9SVltOE240kaIfeOARig+0u4sdo4E
E/OQOu03fi5t9LYaHgBqhgBlfOdNsJB5iXt4HEovf0u2AjyMlq3wbxUM/vK2W3nORRbJc/93xJfC
+vyLOP5ovQeKVt6vlcQns8MK85LVeq5QgkPfXA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
GDVQLsnJYtgL0+Sh5eWJTSTPVDIusTFXNlgTo/luuupZvzsglugZDMoHfyjK96PULZJCE3a6T2FX
zpbPJnie09SPCMFSRmSicDHFJl8wgjMQkHm09SRYWaMY1r+QhGC0OJZtplp4LZVZwkOUsur8f4R/
Iqo8TLgxniiSwwrv8QRydRrdAUmOSIjhnZzltazqJKz8otHqNnlbh5YrkxX8E5+GhxVcOXs/feHu
nAPzHjAf4HgxHc87acki1Puo4EejXzYGrbn8ihSxWYbLYE61k0DOnfo9mhhkhLWmwnzWyDdAji22
ijbOpM3o7T+M3c95YZiLRRDSfTXehodhf78hDA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14224)
`pragma protect data_block
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
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
