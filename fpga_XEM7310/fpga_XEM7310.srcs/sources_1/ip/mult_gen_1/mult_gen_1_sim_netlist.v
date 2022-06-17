// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Fri Jun 17 11:27:58 2022
// Host        : FDC212-05 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/delg5279/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_sim_netlist.v
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
foKT1YxFvaNkiEHMZ6in2YOeK5IOO5Ec+FNMPeFj/vXSoHPgOdlT3hPF58NZNmPCGkUnoJ+2OJ/D
cHgOTZ0Nm41SrM1LzeCDWm4u71KL9sCwwKFvaruBFsjQNaUnBd6xbRpamBkS2D1TYVy408WnqTyQ
jRO3Q/k5g8XWnzm+xIDY/eGzWKWFMRX7dA2Ye00mlJwsV1sq4teWoiVy61nPkT4Qn+13/ir51ryf
KisZ/2ojmrRlKnbrISd2KdRBUOu5e0DzYn/2MSAfc77jXt4hS4+4GimFMP1F55M5e4eRr3oZJu4s
c+ox2oCIh4btldYiR9HCZ35/CZ4UGaFA9OUaPg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
cPMlR2id/00mBF5eq6403OWIm6KXDadqoPIvE/heeIKNS7i2fZ+tIk8wm0YSVOZBSUHBuJVQ+nXZ
oUt1p4NcAhbG8+WedjeUIIeBq4L1eFgXpwzDQKinEkPBh3RIuKkmYp678oafU8JQR45gJ3SIWR7C
ctjShLTsh6ih7qsz0HJ1yIno4MkvMG2Qdb4L1hxG2toDlOIsYsK/D8N3rghbU3JS3s09F1khxOoM
j4J1gpdIgWdqJlwtDNgrQQj0jVq01gJ1w833dzTU9ADI0i7ayl3KLaOIlWFQ/lbsyOUfYktdmxbG
/EipZAwmdNZBtgAZrKJrPGtFOekfGGxDWjxh6A==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 7200)
`pragma protect data_block
j2UYKvmKcyeo4zhyzqGl+WRM4WNwlKIH1JmDulewJzD/kSLMNn2Bc9bHoiKxfw8bHds1NWp4l0Sz
deREP5FW9OVzg1E23rar//G7RoJI5fkHMq8r/Xtq43cSGWWZHUujxmhLdU8weHloQzwifLL0cGTm
2lSQfnXbSVK7r82aDGd7iSUmegMsdwTrkIj24SL7mC0+Afk4TarcgsXqtFVM6i6Sr0PxXo/w4rP3
jYiOUYEdBnyNA02dOBZU8Mb3ZLI7oHw9HhhUtvvK/Gp3OVZMa4qOuqvQlOZ1aUF0Pqt41qpcUwb5
++kxMHYs/Sb4LPeJCfQFQwY8lCLCNMwiQ4kXi99A1ZcL2buBHpsyhK7Exur6Xq+jPAXz18nGEadC
Eq5xbFCnEjkuQN90SEZ/FxTCoWvay046e5Jfht+JWD1OiScD12zl/qf4lJtCY89NIa+44dv7fkBQ
Y/4iXNquWX3/24J+lKz0j08ZFnL3pEywkm51UHvwzfv72KPKn3i85VZsUwDDmPtZF7Bs4AE2hj6T
ipgSi9at8GFOWWNUTfMhmyUOFA3CxyD832Ba5LanEIQhPUfVrVhLDoUxEvGC4OlUHNLUedRZhB7N
fgtocAbPPyCFCfu3lt/tOzoUygOH36Ji5RJrl4Vl3OxSewtH1hDVBIFD896Dt2xmQf1z1CCh3btH
PHoFAU/mVQUW0jtQ43t0budFrKVpT6SMJ/bWtyxF/DxPfsyzonGcwj5WadsoF4DFZeG98IfGm0qX
8yND/h0ra3iazuCFPVU84oltlxfkBNJU1Nnv4pJQezAZjiHnxR7VYmsokhCVFX13lML2BcU2WmJV
BUBR/dAYcBJvOq3jqlZ4jAfL/gAyfFibjX91TQX/TSEDf3tMyvLoojYgfLIin5fL7v86l4Av1SS2
phz1Yn8xhmEi43oCoPt31+8ETh1JP5FK5iqWPYRK9Vb3T4cVMNrVx+LkWi2wDK+zGWIKWJv5+fBI
RTEg2rWM2NDcKTrmtwJ/yx9RneIRSOzDCxep0OXQgNyKN2XFsa6EabaQhyyD3eJclslde9yfIPFo
cs/PTSJEy2alixuZ0IjeB7TQY2N+8+B1HM+4332Egd9mMD+1ndSBovx9T14QRRYzqqxchzV4Z6ej
Y9eWh1+GSie287bfo0fhRvIn1fZmamdTj8Jk2DUazYZ3vuzBWVwdwRRLsGZISYSyHOLG+We6Fl66
FnUSBvCNWqE67/7kldtW+3u/drPW3K8sbH4VzPqvbX13dpfLQWOCaPmcQbgl6R+U+LgL2FJTO0i7
ROG304Bf/TnYbvjrzgk9I+FpMcxl6c+wOisybRPfngsQekD+LVX1kRtG5KVmHhNjksOuvyW9f78T
gjp1eOplBebk3c5krOWpjH2Zf6MI7TBbHp2q2nedfhi37xRCcPXfzA1hDVzWcCZikkzLBX39aurY
/MX+w6GCG4PhoTdKhQC+NYWVx+Xp9C250cydKsCYil7Xr1Z5Hed5xa2mnZ8DFkI3owMJ5FOcJvu9
vwYunjIPiUbrOFxk2LcfI8mEih0yPUv9KLw7Nr9Z8hFKEijlL44pryyXEbe/hKr7FvDhSI4r1Zcm
cd6JgbTqytIiqjv5FPEJcRMD8S0Xrxs57gwHLRWzuFjTUhzG43Rkec+EZSUv6TCqj0TD/8y8PJFv
3BNKNsSIOMNVQi4dPF3db1p7Ko/RkDmcQNSESgR5yihmP9c4AgEGQLdEvkP7wPmgNz8qT17cbJ5q
ChsWNSxU0eXXJ422bGzKBrtoTxUqVcwTr/ik/vWZxQGISJ7ZXh9s7sLqpTe1OpCQxV8MdIZQwJMi
tfA8nGBx+W7WKDW26TvJ/4ZOVxGLEdr5jOrullhIqfSKnvYd2CVqkH9IkR0tWXzqb61Ckme9y38Z
AqokK9swa5HMdIsNVVB6tYafnJQx88v2p+ho87KkSuL3Y6gWBq/Y5M5idjxH1s4r0YsaGchWvXeQ
uPFpS1T0OuQrI9MBIKYbzXbS5GlobU25FKPEi+rXMpMj7ld8F0yEce1GJ+BnyQeMGtAjIXOmQjmy
Tw6DY9edqkrN5g7fvwkceTOKv7ZkiSitTcYBA53/47XJk64Ft1mvtBpNoJzT3oOhHN6OY6jNCEou
hgzhTiVjkt36lTTBeOCi+jqW0Wd94tTYF64qBO5SH7EHtbqgZzfyMUSZZxTVQqGlLarJ7nPCEjuz
dfvyNFRgvG9Pm7F3csbNqf4ABo2U5Vdhs1+kh6W8+c9Exyn2CmhT6tD8Gr4jUCTiQrT4s5/0TJqQ
50s5wxDoCIC4atyQEeKHK9uX+0y0Oi7F3s31p0Njm2jQiQnv+Xuy+ughP7h3xvuOvp3fNSSyFu3t
8N/QREWFtOmyiBPWBno6FPuerAmOU33YtFykCim86/ySeCd/wPk50f+OO8Ij91l11xuRsbSDfsRg
ZirxEJQEklMXIvA3TJaViMnabOamARvVZIy++tZrt0Fkjx0GhV+NszyXChM8ATqVaMowipKX9myk
YCeFSYAbf17TgoYq/2Tqn/71M6mNnIc3srwzt4Ym+2Fhns3iKup9bIE6KAmqtF+hxKqyeAsDKkl3
QRBz7sVitcYkK3KASLcb1BSlsnR19eLKoEoCjxXG1vJB+H6reFbzxNKl9OQVzW5zCPA3vSDhjnN5
LkIdQItX0urfD7Azodl7l2Q9lf2Vx7qu3MfmK1fJb6BUS3SBGenEeC73OyzwFrHUYk7JFzqn/+PP
pmK//1vSzMmt0Q7TzBa3Hqw6QgLcTzQ/ml+LUZDhEVmDsUE5PHc9qOv2BzYD0Zmiq2a9/FhYrEPD
AJcCa4ktenoBRaVblTDuYcmT28OsVg7Jr+v09V4deXGijYplgnv6A3qZ7TGEZSosR/Yj5mX4z0ei
flsP9p3gC3auvTozbJHssD4zm7fEnAdpECZj8Aga7mpuibIhHGztN4BGAk+GJf+PS85Y8chX1FGN
gnM0TJ5HpiIHGkI6VMO6fFRe/87V4Lk/Et22DGPV8HaPk3iRiKtPIJKTmBP9nX8M/mHtv9yYhZUP
b3pFQkUvuUSoWnHSqPCBt0vvq4KgSihFFPmvQlZoOKermq9BssXOMR5G7cQ1C/WPmupr/oIMtpUS
fAeccfdvjnCsIzGE3/h6KxDQD/fEUatE1HqEL1DISiUv6J2MlYAAxiAqBfkseK7d/kN4XNpwYS2h
dwyQsh93i01EtzVEMilDjH4BO/No9udA6DnQILqtQFwllkdNsw9BwESfKJgF0cgFtv32ZVMvWWGw
kH4uB3rhtlpjRTu+zAW/QbfWSSoe0Fz4Q+3sZtZkcjSnZzsFPWYAvUcl6dNelqJ/O9VCraCrkm+B
oc94v6Jt0Ev29/ztXjllQ9xSz24AEt6ZqDI2zX/a0AR4ShBqZBdKpDobYZFNjQvG2tbogxGtDNOO
KMk9ukk+/VhVQsHrHyYSzMxUzJVuHGWUa4ldDhlsp/VjdSHHgf3RGNE3duI54s41MT+bi98FHNYF
ToV0PUYX/DqQmOO9DS8cHwFk4t/h1EFfw/z1s71WDkBa4vc1s6ksD4gLZNK3eU7qOHiVQnvsIoLF
daeTQ6e51dWY87n4PwDBlvG8YDAZlpVIXPFm7Fa//3OzuGdgjXqrcslercDb2W2MscldW+Eyii+N
U/Bve0JZtO4tKtrtWRlDNun6al+OX0wcKW5n9IsuruID0Ky+CiINGR9Fj7V0Q+bEZtKYJ4fTStzI
B7md3SNQb/tDV4cT0A0ORxhsp5xhVycmjNrkP2b20xOPYY5INvXWB/iKTRwzcBGYt/yYOEr3PyH2
ogFN8G7rYOw8QlhYxT/yEBVTULagBzpqImXg63AAgS2GZLXSXcj/6CPySB7UjNY58VGZmP+9zGIp
xPhNPruxQ1TMXaVXL5DbJZeI7pzW3XtrSLGLOGAlavmTYaXwYQrYjHpWRFODbgVWHqPE5xDI8zyJ
1lvXW9l8K7rc2Q04Oasjp7g8VmuI4MgmbKRNHJrHTLtiRJC35bC2/G1hWe2H1HKp74B9gX6Dwr7v
Bj0hTfapCmETIp6agnMCTOuakYyQnwg9Hs6p4oV8CoYuKAUm0okXSeQZ6RJhrIW64rkRLUWFZgFX
VlyT8sKvk68kjWpeyyzTOLwAaXjeVWFzTTnMYyaUo2MFN6UADjGOUKiLSW5LYLo0lERS/Y90iY0Q
x62fYH86BDebwxPqVzHJr5KZoaCWSYjje6rOtAITXhduCjVGiH+4EK3rj5H4a7nEI046kE+to0Vp
yU9QD81y6sL4NfXw2ZB2a/ILg3Ng22w6vysrCwdWR8oQdMD8tUHFP1NGS//C0GKOyhDlavL2nxme
KzajbazWRYQuNfSdcF0dtxJfhEvj09ol2JU1AB5vFHYougma5Ow8yS6myVwfFhoUeQcc3/VSZFhL
SeTH9mN4NO3K+AhndEKvK1NilFZm1049u714VXNLoGMN0jLjVnrCCJG2Qp5tPStRUZchS5v7S5x/
DVUjDfnTAqSwGLfxcLP/QSZcEyBnk1aNC2kuyGRXPOsv4YRh1Sa+OT2dZgRMuMseH5tYtmXDuCcQ
AQiHiagnMyTMIa+Y/7Zagm9vAw786cMKMG4gNEbYdofkNNTEX5eC8V9+TTn2GXXu6eaIoum+p4XA
bX8WwKmaxSmm1b0BattyI86EXswymlWcIttVTL2YyM87ZRwwmwwlhtMTQ6RlK779s3FxBR5ecLXO
0Ad8a1KD3NC2kd+5y3XLuZ1Z9v6nnayG9CDLZVD+8gYhlaFmYT25WKfIex1dgHE/D1cdHLJ/2LeD
vo0KrsrYjBjHgYMF+Z6FAa13pKdo/ntKhtfwEIw/G6x8OzT8BrKUWt5ohJq4MFaDlyEqTn0Vf6Lf
ESR1d1qz3UOyKUIwtJRmnghzlS5c5HlJeiulF3n531O96fgvz24AmRPslehcWeJ/rpOjlbtkZyrK
oQi90iLowfu15htx3oaO8ELUMpufiexc82jZBm8J3t0bc7pdecwSlD3h6QTB7Ye5aRTtTPlzeVww
q3jDEa5xGfPMsBrkoCxaHhLZIAISwm0ILdei0kaIDXu6E36LjMM4DiN5VfpTFPyZtEOHthQlmy0x
zOm39lpZLPl/4KjxmY2lUo/NdeQ3kEEmHH1oZ0jLLCUg7POIfkO+YvdHhiGUxXeeLPsB6V8Y4vxC
L2b98Hh27HIazis3zhU2vsKJJdV3QckOUk7J6ewBe8egsnwe/YmBc8bWAWVIrbWaWOlbP7iwEo0O
Ep5XbLYl2ZFJyVEp+uhrwNqxaIW7qXle4FjzLg1dypYx2BUXLWkPGudC4xmv1y1fXsBlBx3BFscY
923YQH1i5cGOHWhDsFkvc3E29ptKokXZwuJClAGSfAycDB1thTrbyPnzLDREzC3yodBVjiSFXQh8
eDNp5z+mYy9WLSPVcB5E/ARYhm6R6+mu28vf1MfGMS58Gy4vgI/OqqcWENj/gKCVwKp3SpyEvdXJ
LIeWDFDeRvt3rbyqjNzpkrqBRpJrmQEzfaPyEeVCntlKVTZy7QkjshkB4sSz4zIvXRgVTHA0MWQ1
ZzcHPnTkkiwqQ6OMYEJYDpKVsyEjgx6PJFYwtZ9LwXUo7Eu+b+Z4hhyY45MhOiUha8UUupERN8eD
DLpU3sL0muBOQU2LZ7l+ZeHCVFmlAuAuH2NrLqUmPmOUWIlazy6eyu1jb1FZBHaS8PES3MhFT7B0
PuD7vdVl/7wP3jugE6KsoIUHyhaw9b320T7CIGsdrTVKgWpkoyrKIjzeL8Ytg74pbqMbPE/DrDL6
TUICE4GzskTYX+Rkd304vkZviNN+frfqep4zEttSX93TvXCyLzUWz1drgw4qA1mgQjo4SXr1KKX+
1OwYb0lKElSv4TxUL6MbHhA6Ca1pXVIz9WrFLA0UcrTevb31NGeBh4kqeUno5QN97ZYt9d/7QTju
EV+/tbrBQlP6WtcyoH21+djkRY+A/1L4uvMH8B7pNYJe1cydNPilamD/Pq2SnAUXgG+Pm3qOBHjl
RHYAuWDr0zZWexPouFXksP2onqYcqkxRhvVP9PXkGI2cV/iMdYdI0jo4cipGhFln9NjEMQttHJEI
oHgkEoRd5oZ4rEoY/opJ2KYy7XpeDsN7OxkalBv9x5v4I0bUaUp6Lj6gnW2ZZhHcGs9EqYF3PGVC
ryWzaB/lmtibfFMZJjYopRmMMLmxQ92nRR/vV6rSyajcG42pEp8haF9gLdrf52x+E4X0U/5werAq
W0fMKPYqbLOctkPh1UIUQ43fJjlamWGujG47USB9LfxNqrSIVuHb63PkSM1VgjhY23XTxQWzidEB
yZWSN+JjYdP1kGXBLi3QlLvLX39GvhA3Zs2MQX+hAAnCNwPt1qSpR0QlMUUvdDIFPAFKE2c6ACAu
xA044ybP5Slyd1F43esnKd49557iHddIlB9B6muZLzX8o9ib/6PKjbOUn1r00QAlH+Im4/3Cjpxp
6XiSx8J5xQWB7hP/kJc3eDDtGYN/2gM0pZMAe1mC3Ajv2Esy4qUvY9vc9NElKRgvZ+MywJm3MCAW
hfYko4EUJujlWQluwMvnkG23674n3Uqnlnp/+ZPPCKuLcfj0OETkxgdlZ3Zw2Xe004CojXqNO15y
lJFb+KLoJxibRixgHNyDl1v+uUyACl/c7GLtS9/pKrnRs/E6OeZgSlReGTwXsAWJbhRe71OdBU5Z
2cPXza5SlFdrW6qcApQez6iVdZNhvI7U1YVmp8tuhKfFr8N5adw05X7TYBU+KAWqK2PG73mGvCAu
cFnz6IRLuWgL+kUEiIFlcRHV9h1pvC1VO5yXqnb5RKrlIQKcVeCcjdoSFRXAjHLpP6Ud/djNanBU
y60i5ttMOzwvRqbJx7XVB0/X4zwQ4AM29SE1NL4+SFVFlLu92R2Z0ipJ/PIyLvaDtU7YBSL/KSVW
HpUR5/9RNGIcJSnx+Vi81xmhEHZ6mFgOP0vtFwp5v0rFLltalWevxwMlqcyBVl9AzXUsApQxsAXw
COpJGL+4GeMwtAtpehIsm4dlPKUe8UKvHYRF9Jo7lpUK5rB/ZO91Idsi2NFhb1D6mCLZx/g+U6jA
lOzKKYywzLLsa70QAreAGT0aRiZPAHRngJJ5cQuajx8q6YNuhTK0etLaHl/UQiLzTVWMUELZHC5l
uXoRt2TTE/wlt3Qgb9+5Z2CCL41EtFHFIJMkWKQrjTfGknX8XOeZ4NkV0mxyN/069MiGF5Lte/pC
HbUxUhtZmkQEjaTsnCLHqyAOFOQxYj/+qi2cLBRrsYONb9T0yoD83BWrOmjFvVp0xLKH+92vMmUx
fXyRJsiBLvnrxrvyj4rQVuCOe2FPEDOI2259I1rTfE/9fA/o1fCJdtydzMjeZUpunGfvrmWbIbGQ
r2HnljFE3XEKZKZCGBbnNRVbUqxNmurvPDqIbzEYHpCqhsyP8CHDHvIuvshKlvD6h/yVuwWOPdZ8
U45fEChLAlU8mCEPLC5pNbozwsDpMJtD+9izt+ndstffFXXEdx26eaawAtkrI2E9expnjkBu3WGs
Xr89zsC1LQPDxrSHtURHyJL1bSliJ8cUA3VB1fJVdq50Sy5DL1tZ7DRtZnvc+fB1BV5X5KyxyUUQ
IJsN7Ul+vjtyMnvrfUm9XwTqz2UEl1O2pOhF45YcCsYBNhfsBWKKI+psCcOowvSLMKQ6qYpyI83J
UnRZeImbPdYbsCk0XNpmIm10x0uPz9VyvafFug+V07hye7ArX4IXWhPRUTtXaB9sdBlCWukPHUDy
PXCRKjbE9JF/CYZABeHIXJCHCVfhHqy9TumHVYnSqA33gcDUXuen/55cgJi6Q9r9s64U8eyG9TbV
ndY+gTpW+GipHMoYLHADbn6E3PoZwxV5tRu6IMLbvv9kQAVkmmebu6M7dnOpYGTU8vaFJ5OyBboI
Akg11zjEr4aV5aG7/fszhxT3yhpuHFXh+HLEH4q6mBwoMsjeNLwXyw3kWsxb1uSD2HwqJ2WaRTY7
cckStw/avNqB3V1jxXMcupe9D5BE/IyximjCIGIR4XCnd4trtxBNio+DYhOfNkJeeIeeB9nGR5zU
LjTqd2cFKAztlj8/htWSEjZDj/nB1cBSk9A2r14Bern3KuxaeJjIf7Wf4YShDvb2l96uMKo+E58I
5HAgrpH6/o6TqIYa5rZuc7MxGUIfgndjTq2xG0rDV2rl9bH9nQFSQEMuKSAaCtbt5CgsnjTfuAx6
ZTYFA6sbhg2xLsDTmsjcAye87N2cfEsIqjjZT9FAgb4q9u/WuVD1LFCh6CuRMVWKk/8Jkw/ebo3A
is0RckYocrGwUZcUfBa4cXRd7TfuW9QZSINNEzP5Y0kewuA1kuA9cuHXcwTLfNSeYDx0LzfR+h3q
MlZTOtV8TlRYCC27uwk5LgxqSg9vzbKUMaub/6mxjKYymFWco0Ompt4FOZJqkPY2nAsnxkuIMyIj
vEsgXUsxhl/0fhg4vEnk1UXAXXt4Go7ohYSidF0yqK646ZtHMn4ZIYTJclRsXdQdB3NjYf7naDA6
XIy/40+mRe5aLXuYVOHpMmgwV5BQJW3C6S1jq1iX6nug4JK14NoAsXPyn6boIauCPll7dBKJLuz9
BYadfE+RBS0EARIS4ps2tzqh/vrzxq3jg3eN7+IjV66UgziZFnKcKTAHXt2hJEbUh2GsQ6jOM6jD
tMx1PBjmoewGfDEW4QlvybVkD1yZHAa/hqY3h274t2kXdY5Wp0SLBIVhn9po4OjZQcDxkXMWXfWF
kS7dYi5ErFaV+zAWJ5tlZuXgB8ghoF0oYiX0lb3C6q7wuSyQO8nwacT7NKP4Eg7FoaYiUCZqM6Pd
mi04rd2kgF9EtHnlkXiJxMJ56afmTDaKiU38yryYzsaTbUPQy7MsXhkLEfR3F+UbaNqqRqMRCaQC
fGckPDKL/hJ5lHOfRT8BT3cA2XhPCJqA4ro5OemPGLS49nlCKs44ki7DyfNokhcsXINifi7WSiv8
SwJm2VdQnhmx36muFtGvu/96g0fYhGXPk8mvfB5Yo2HvxxJO+/HoLegvwfUqda1PSaS+8DhfcdPB
gLiVkOXlkgXHFJdvBaGhq4eDzTfAj9CsIoREzxT2lnaEA81qUXNHN66aUxxCat9ASNwh+Lgt3ELY
IZ91U6E1BzmbMOG/4xENu7KFwrl/QcrzyC+/nkW1wiJimz3qCmdyjBuDr5Cso2EKXhKscRltrjcq
C0/BXMSMzSDZLy6GhpMqL6eDoh9dumEXFGM9nSLuQeoryjFNX0SJFXrSpHOUczX4sBJ5e61XV01W
8dSolhoRlMLendNT9pOKDhWk8yGNXzuCOl7f6390Jpqv6cyCobT05Jasnr2RMFwYTYK4xv1tw0Hf
iFNI0MlUbgCtXQ7mfvVeBKIo5g1BXVg7pslHZKw9CNSuess8U8NoyhDyGvA6ZrJC17e3hiyFwCTs
iKQl6Jrr74LrBD95/FKEq5oqzeOrBVzOoLtfO96aMCv+MkDhWoD93Rm5jLr/ZlCZXcDf5/EOnM3L
LTWU+CUidymmy0U6v08LIY8IRL1lPAB3kZw3dziHv3G4Rp0n2vObHMreli6SYb4WlJZBPWglqDt3
ghdDFS56kgzu4VPUJfSpfXfY
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
