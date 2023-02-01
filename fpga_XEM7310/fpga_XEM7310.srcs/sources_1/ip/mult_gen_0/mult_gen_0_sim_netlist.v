// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Nov 14 13:15:13 2022
// Host        : FDC212-04 running 64-bit major release  (build 9200)
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
lL54m6fl1598I/Vr6W7AR0IgHsjM+zEiSujcxgDhf0oa8okCWIH5l5DuSCL+wko0wE6qd7tgtnG5
wVdDQbW5cwbIVTq/HgsY2tZkXD1EzjiOdlMbUHrYZ/1SexDnZzb3CmUuAaa+W9VjCwotappeuQoY
2XCyJnMyoNZwLrHAT5uuYWTTH84eGZOcwqp8KZPOuOz9H3/mkRCmwBorjmoOdb9YfP+k8OpZanwE
E6fz9jq2928/rwIQH1UD4LmrD9zV6KiGaiPTD0kQDy259j967FXDL5gBMHkmQsKbEg9za2JGiPLq
E7IhPPGeMszTMLBJb4cVCrf6CX+hVwXQgtw3Wg==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
n1ri/erDhy8nPeojKO58V54sSR9AZNAUV/G0UK3E3ZksSqzOATV7gt5TXxAk0WLt/OP9X41NOQy9
+2SJWu+ZiacAvl32onsoub1y19QySFNumXC+a57tNhrRTf+42xRllzry/l8MAFdhrQs2wXS/iJbm
6VAi4oY1FsPXD5rHerqChoo1GLki3LnT7O1dT6uZTGJFIyKrnw4VoVwVyLdrH8ESM9C8G0NvWaV7
wCzuXqcHmRVD+Tdcf9Wo+3jdVQs74o6rFd9zcDwiGjkEy+Rtwo4V+LyMC9eKtNG4GIKO0klW1YxF
ks1uuZhmoE6JQSJpwhIF/9P9p9+Q/+qLS5r3Xw==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14224)
`pragma protect data_block
5nvcZ0r5tdc1REoMqbA00Zq5G3Y7l+A0tVPTVxCgB/hfLE0Zd8/+JR5h5P678KfwkAVtPGKtidBT
PXCUZZ1J+FoqM+OA/Ep6MExe88INi5DzIY4IZdcVyvj5HFB9XYikkHx2i8hSKYU1tVCWwBfSNyga
BfZy0+bFF+ZznySOSDNf3w+iOcFV/32IAh3/4a8RuTW77pxXBJtcnriLM5BqPZ9UQzxKaiD6vdL7
nGMzyVwVLlxlVC6kcu71STN/3bjqr8vy9LXKiVLdf8bYcDus765e1w8o6UhQjO6VK7RYDvnXfgHw
MPPAzzflqDZ+oGIiVM5fMSXxyEcNsjfMgr0JklV71nCo9pNjCakDxiaYk0+oqtjPMD4eVQl+gknt
DuneewLGMEScTXjCn0I/T+AIQ8LEU2NmyWaAPNQJyqUEs8//Sb+ZmO7MU+AJZ0gL/9VrF2K6kR9H
sltg5rli/CVQNMNArWutvFmYdVEhnBbPh16a0WpVNWFI4NdxczI1kokWAtVQ7Azc0aiCbmWICBl1
LW6oOLs8El3YnYFOBfbzNNO2z10ukyeWPyQVMIPAd2kUhRUpOlSPXDzf0vmAMT3JEnR8HMqFnsab
Y1RuyMFxzpvRgcL27Y2oKrVLwZFiw1rR9n4K2CplyWeM11sa/pfL2aW7NLRodq6uv9LhKysmhCAt
ZC7RL0MhshOdqRpxXX+0kTWmvO36k+q9L/W+xuarPb76PWs2qib0J+6Uvijwfq9U4sxJWzcETcB6
4tHTkLFY0qUnLOPilqAKj3Adg8Z4KCaDP6COKXr4OnryKjDGZ6YlKpJDSS1xtAgzCwERaD1Aq/GD
NpdNgHtkH7i9u+Qr5m9+u4KN4RjaB21zXrh4mnjMie/+GHBaHLHNrcbzp3yuaeSXuCW7KShFqvt7
f7j40s7O3RiL2sDPvrioOfCsDVjbwELXna+SiGpHdFaRHuygOHngg5kMUPgN/Yi3eVrCFFuelfQI
Wd6wVXUz14um1B7mh9GONOuqd4rz8p6xbNi+9tlgukfbLmUwktyGnMXegJpZvxjd8sf352QakA+k
IAbfYJMpf2SMgcWG448lpHaxvAwzF7JqPLar+I7/TUstVVYuVnxsvSthr7HHc5dcoxDhinQGsI6w
dpO8b8ujdNhID2w5uCoSkf5tlrg8ZPoQrYgY5BZXMtKqIWLDY/PGsYfdaXei41vKGHCe4dQA3lL/
bEh+yyNKCLQ/CxehnADn66OSfgcLTaudl1xh99/wbfgWfzua7P+f6yEMZybNEZzIAAK9j7atasw9
VTW2gu0u1i60HuCwnjKPOAecZMu7sHt5zdScSgtcEy3LcpeYN0VeoOzibyb+thwbtRO00UIPOncB
FngTiQvlZs6nwTf/kPuK/8vRAOANvMYopjXPuFNB5TqeIpQ5NdB3El9GYWK04jYoetqCzfx5IcWO
AQQQe/5F8qkn35mQQwGnHk27Kl7iB1YEoHeP0QxsSahL1mh/ugfDO5oVA+5cdBdyi0Suo+mRbrOY
EqiL9fWyI08BqNyHX3AOFkl9cArXBG9yEdz3ZdP5gk0YO7UBBJowJpRSu9PHQkvAtsrvXf6dzQGi
hkqgpN/QeHPVmlbNRelKyqbO6TfOHXNUdQLy62XFBrzVKALguyllxC/TnLVAmeLU4X/z9VG4Mqf8
R7aMSWN8M+SMDKvYVSSiFkUn7muUiK53SOiaG4LjVRoiBQgLfYRpxNrRbH5aVMiVlf3b0zrGZE4/
ehc3gTNDlPTUIPEDg68wrxyk/bDuGq0sMJ2lb65vYPwRwoiCMLHa2wGQJ2vstC2+bLV/7uuKGdSf
smB7ciLNCvGWJgjdKwhC8aX2Jj2MqtV4V+/iPV5xYrLup+0T8zEKgYqnTM5dfwb3U1AhTioe9fa6
slrpAdWT3FSwQadwu1sV3tN/p+7ILMO3OPvfEkEa+enY43zN6BDH4cWxjmJSBr5a0LSDxqvor/kt
4suGzydVUwTbU0XXN/esvD9S6FG979sOAjYtX2HZMPAOTzZfSoyfOjnoqqNcbYQy6nCWqWpmj6cQ
80bbU7bsJajewhJnIL63NlCByzdczKIftQI9HHG5593x1GInEbaNKMa7kEAX1pPs+jgrKRLdHUax
qMhAVoLrVz7B4qE/ild12sq/SGPbmCux3M78CWx+/b7C3I7zfwYarCG/fnr0MkOWbdo2ki59ZIkE
J1L5NbDozwCfv2g9Oju8Cr2Qj1dZ7DcJz4/WXasiPP0krKBFK3+Bg9KozreqTrwDFBV/h/htFrOv
1XzfKaGkkUwoNK62MBhtvpAd3m4U2gw6aRxn0qlhRRkDwmVfErXY04gAvMZNevRJD5qxj8svKBu/
pBmHuPYjQEPojRdj0ug/eSvJ7PK7e4p78BlKJFiWJGikMXe76eH+4gD0vo1XtaOnoVCEVz0FJv9R
uaWEDMRxIhF9RjwzMUdYw9ugAu14asMq1maclLi82sRR888NR1vrlGydELkduYtdQyCYoNEmdIck
WY96z8Chf/aMZoqjlNv0SZL1AHC7+EPXVVFLUmtD4MUOIf+xU7BO7qqIKTV0CDLoilHds12xFUdS
Db+6/h9tAqL6yrFOsHLPTsGQJLy+JriUOy4SGV0LuvkFDkJ3ljdFAlrGq0Om2jt95zxn747DyV8R
8HQTAZk++6u61spKY8+lem8KGnWJpVyMt5qz/nnI/jee7IkbAIhNmRnu+Mt4btl9GzAituJ/G9ag
U/teRVvFYRVkZDZ5TPzgMVuaMQAUNken5TB3QdTBDJ3Djg4Np7bWnS4K42onKdWUe5bLXDwNi7xJ
aU7/vSHaa3qv9UIuHq+fbKOYfvM3IdYaDmcGgM0f7pEUgKNNklKEdCMzF91KTncctO2GuBsxwTLF
gD5bkuFa+eYAmCQjAg10yOD9t6TTtWkGVRowWY0BlJVwWSsv8s/vxEqoCB2mHzn6FsP17foK/Ww6
XsIwuAVA+bCZ0Mghh6vQfEysAm4eHs6qwPCV68jjAo+VVAdCHKHpehhJS22EeqQHGgdJCMl4aDbK
vhk96OA4NUywbjxXM9ndkd4NPwLAVW85RaokxjcYini/3/Zy39Ypi1zhwe+qv6k0LwknHKCumXip
j9/YzEWCBovu+OZsfJyC39pYbJxC02yPWnJdO/biFjKdxyuAD3NsT7BRfvpNV2TVEtM0CmI8mspc
Oli2iD3XFm0Y5vLBWb3ndGK/IcrKxNEjcXhpSbsT5zDuyqn71uwPD+fFGXhJAaJTSQRLYkIij6Vi
1GNuaTy+sI0Xu//HbIajRHogHXPnkuWLpwRhsgD8udcDwswA7VsIB7q6xpaNlKZG7gnUDw3kk5fz
+HXrJsX008oFxkRdHBR4TxSxILW9bJ7QwkzdkCepHQ0cPgqDGvR5Vy0fGLibTvVyi13dmLlzFiG7
OSg0ZPk5dMaC1KzBcubw3zMoFqP8wkvJ+4rmzrBHWCJEan9+jWki1uX8F+yl2Twf4bRuVfEn6ZiR
5qS5lIPig58ebYUdDsEaBgwL6spvQcNtP7L9mmiG5bwQvyJ9WIeFq77l5trbaiR6zsoW5nbCTiFj
AR3yQVz31CLRgwXFC5STLPFbaMAMEh7V1hhIO4XXz8lv3XO8P8NL0aZhZQXolIUmoQTgYRHJq4Nf
s9nmC9Keph5AVvj5c10kAm7EKHLWw1Hf+a9y1xUgD3ccqWjj5a42Pi6C8A53IzNODBNFqvcWQPDh
6nSmrB8aJNvTa4R5kCjX3kS4e6eXLubCQ3ZTSajeUBqNc6NSU4mJjAljikPUl9GbPWYIfnoZ+1hZ
8ZVPAd5uo/xoiRzjpZM7Cyj5RZ1WWded6cx6Bxm4WFPZPsBEUWK2RZ5yYf1dXW/EMTH6N04zgPuD
g1HKm2h91u+qBdfndS4doUxWo0hvvg3DQw4JIs2ngY7guMk0TZ9CH+ugOLGZCUdITUWdIhwE8gfT
bde5bL4FsOL5QDylrv7PI1Kk1iU9ACj7lCE2zmHQ7ecFvx/trQ0dRzh9OrXPlTnKrkxbRIEducM8
o8cGT/Scf58fjweOjJusj04MXWCThzqy0Vx2GZECUl3XO7IBc+DI6FLc4Qkte4jVMohwOGgF6Dqq
3PU7UAK0w6Ue84V2T/EXqfLwQcj3SSw1Sc3nWQhU7JeB4NHM9GVxgnj1i34DppNHTkxJYjUQWy62
5iEzlbvwxB90MIUU1+EIlWN7MOA40W5KWummsXZv8h3aTIKSRQ5rhlJvEgZle6U04ORakDkV5/Bm
oXWznAhcGl2DL09uKMmxuMT4xRYi7gAeIB0XfhQ4XEbOpVHwKmxAWMTvvLDmoCJQPpe05O75ASfj
jefBWaC7871AEc5k8vHUpn0uOBomkpf/l1nBSMIacGTloz2kiF+gdO9Fwheknb/JJnDBsZh9YKfW
JJhPJ5lEISw4URNdZ9jumOSCSA1/Xim9rgYqkLfLK6SaV1EFhtpKBua+kteuQXgHUjEsX2ak6Zvx
1hJ1bERBoEK0uU4xaAWM61Q1vQxut1fJvvTLNuy70fQ1MIhZdaRk6a4cFlIgUcx2rRvJ5Dzamx8Z
A/Nq32AB1d7LWUQqHWklUNWvkPfNHYQUcDMUYuAA7GEWhDscwwy1Zv/WVv6WviuXsqIm9of0M3Ji
l6UWRSsQGvXsgrt6BWQCLcCvHe+7IpqyyJn/A3dSyh8Ji76PuhwMBWDuPKsZ6Ah6lVFAmo4qDPXv
QVrvmyn680/0/UVAfx3ftnfmDXANFWXib+34MiBs84SjvVjV1NxCB0jlznfmawg1eWP8uOqLAa6S
pzrHDYLjFBA7PZFlWiY7iZ6DAd5LlbcSSiCW2fXkbSJl6TUi9DEPn0h8Ba9AU+hKyBt2WFXJ7mif
SsAQB7nkDANJRG/PFbxTsKOXXPnxznsDGA4QtVjTWHmsu5cl5vTFS95bl/VN/k3RP5tnk7TmfV3Y
xXSgqUUIIhe5JNMvvEBTGVLatBGD/mhdx6KP8i5Nr9QBUuIb3zMPrHfoqacSf3KFGpXHXm8sEhHd
mK6se/XKet2MHBeYVqIO8IsSkSek+ZmNYeu4zJRXsxLdHVNo/OxZLqf8ASkX5GDVIatLPpxuaJVf
TWngmHLPKn1oRun5C4ylCYBrVwfkdgJSeUESf69im4JdWaC3Htfi9+bMoVM/IqgbdFFEdahh7/55
5QKET24CVKnomrAAPAbPrQI2RFCc7eUYzR1u9H7Rql/nGoFj1hj6V184zQjSd6NZ2PkGlGkIUhNV
tANG6AKzFBN05R7RQRSEorac65MXz/7W5ALVSIEB2Tq8yav9xzhTW0qYCIUpMQ3F2jtA/s0TIPu7
eKYOOQ11b0EZDnIJQujqcLzkKrfg/YQAn+46242RHtTvXP8N34y2Gw16le7LKlvmUKpjsFXeM+kc
RIBWIYexR/0FvKKBfEb+l11dpunJsoixOQAQDAF6eb2cPrqI5U7pgM5qCIJN9+wXkXRr58zJ3cSr
oyiBvItXtudWir6RUNvOD9uK10aqWpdYSmF/xNOzQh6l+yWlT50f4sBoGkxIg4Of4Bzj8ARi03Jn
fSghWwPqLNBJMBxpxol3tkrkgO+Jb5aAlqeFEBk59BAoWLz8PtqEIZLICzETFgyTpcEFxP9XWMsp
RvmqSL2QmubR12O7F5mr9nFQz1de1pKiRVbJree8Lpz2EIXvhUGZlWeJEUO4y+/CXVvUkX8tDgb3
3VbT38nm7Atl8J8c5GB7rvJCumq+nd9NXjF2Yn0+Vi29ELg95o5hdvDHSoq5P/1IVa/28CsktOY0
VD/e/PqS3sCk6Hb6D1fOye0T1dSMwjnj56cMVvwwxXUX1gxpyxtpbSbr4Yi9+1GCu/8dKJSQ9sTG
7/Yf5DUehwxf3X/wtQMk/2kC5qjWBpFpyQ+FHMIfuZUV9A8bBUREPufTDGV5unX1hAvmtSdkdR+w
OzZ0DJytMJi+em2jBxO5kfWrp2P1BzJTi8SaiZ7NLVWUfpyDniIqpbAbw8v+HUxMmXb9IZdHoA6A
prAsKaPlf66CS7dCB4SBN6lwrOvBXBUN63mhxAvx3WITa0n18OkBcAdBc0fDbz9/++tIHZHGcUBA
eayBohk8Yl0At5YffNDf5khb0CJBLcYf6iMLQpWmue78+hrYFiw1CvqLQcgbiSbNWR5ftQ5ETqqZ
89xNJCv4MxTY3xkeCUHm7g6boDgMmSJDEksvjZGfCX5F+lQblzCazzJObAhzcuPkjKc2M9iQV4Sk
4JcTrLqdVvIUNQ18iI4JzXhqlNjb6rv7DUNSnsgbYdF2f9xC989I7zgY57qdKxWR/0aJbintYs1b
hWAL+yfSIDxZv5jcYG3tMgUg99oNg/VYEuD5LUObuICFfCtfwv9VvA7u/86cf5AoFA0bZdY1ZzXM
xLbWd1KMvONPmlWI936BXg/e+Djepjq5tYNYEhoITeAWiIwkpiDfAg8SYJZCvl7Irn9/uPCBIeL8
O3a2bxfYgWstdpzYMswQPv0wQtgw1RELLpcXzcDsbFzRkWE4CA1CEas/5KtbS0/VyXcU3dqpRr2f
XAN1E8ML4nN4sRUUsEFTJHkGJq0woAiGqKXaIHSg1WRhql7ILsQCeKxkbChVenHqqCTYs4lDxZwz
5n7B92+ZdscthC6Z1WCGDr7LVVUAQ3OhAa6kjM9ubaS0J35uRBRADXoRAvn8N5TLblzXyNNmY18q
H9jSG0QpDtecfL94LZtzBEnIv9rb3bKlTprBBB80fh+gQDZ8kpPjC05ENTj4QtP3Z5OcnVmOKt/r
aJpjf9G/20RBazn7oL/Qnrg7xxPY4++TnCa5JNL0ixm1Mj3UbrZWApaLGW0SsdDMXWUE5T/OSAXZ
O+p8k3oVFPEZsc/jizqS/HyBisYRxRkzoDXmP3rrz6p+1AZqROhywJq64eo2Cs99k+ZFseTTq30l
Ev98XTQKcOZyiHyEkPEjjNSmQBD7NwoPx9yEXnAshcsVoEEpB4PhkFXPPfjs4tqkdklOVro1ih2Z
VjL4WZYTLjgqzMNkVUta7rYAwh5W94DljwPHqe0TRDeuxV4kJG4HIZkh8patHCfVMDUBiS9K8+rX
hDhxv6RViEFliTqwtCCpQglAXdXp9HamC08EJ4t4U0Ruw1b3chF4VjiEfbGwfA9obg272kTw1tYA
BiE6Y56SLbwY4oJFrIH9i2qfZ3juuQsvs61jnlkDbDn0QJQzq5Jop5sY5nGCQV4x+NmN2cR0j2gy
DwP8aIgQSNp11melZJ9l9aDMER+VMVkkhaejoYKOC0F8U0vvzDdUW/gerqJIXS2ygcswsxXypjZD
Zms8On0ZP7cuXj0igAjS6jDUI/2KfgX6NkXK6K2ZMczGXIQCrOO8aFrmFYkYDyycz1cVcjgEIL3h
0xhUV0qta4ZZbRpSc3gJa3QOS6ea48wMPPrnNpCl/aontZtj00XMXtWNA5E2qhwxXIp9D+eVvuBA
vJWrPe6f9xqvuVkagLkbiMSKoX7pKNiPzrSLqohLGTa6zUoWilZz5gOj52mgUHbI2mOI1nxgZm9o
s1k6i/ADN/uUSTgFmNnw8FfpGjDCBA/FweG7OUuuHr36wMQjnRgsRErZTxLsTPEE5T7e6Rrku12g
9aZoI+p2w5y9EsXRMf7mz/26PXOCc3ujjzWQivSvr8uPtqlm7RhORbit8Hb8/4rY5Nqc/3EXzXnQ
Jtv0ZDEwTGdbb/GUZakDc8KcZEZizlbBuTEKDMwEmVZb7qzElKscEvHCHmHtpe5WHV869aKPEGNB
4VCERn0xSpjanKZHTPwIF1AMk+HGhuq0B+3/WuyezuRrZTKHimmjwhHHlkS5mW0giF+PUsQGu1te
0BPkP/y1XKno5XSdE9sWMkI0xx9O+iJtLbRPHZwL5uLRiyBEHYAv0veswvEoI9Qu6mV/BJoXnGZV
FPF59pNsH6oCObfWiXqMUuSaOAnkAPvpIcQkbtmm1GzFSv275dXturTf2LmZK58x8LOFcK/YPHDg
ZB7kzt+G4X/nPetRW8GJxoiwRBEysIk0kGV4w/mqHZKmDl3lUagXsooiE3jfEN5GqWFn5b7yys1L
27d4KxE2GaDOAxFEPZAdpKQ5/eW+OJ/Bl8j3UyE3HbCxrE3jRCddgV1PCpgrcg5UhsgQqdAGPCQO
GRdNdz8vyrxEN5c1rzW27/BQAfIbsBZ59RJ9dU9l+uLh932MPlZi8GKhX25T6802GGnVM5SgV87q
mJVex7OR/b/IuXls5bhLhaeo/tU1iwPMBzU0VjtPt9wvyurWnmY9UICGSOlX+yJLi3IUC8PmHhZN
a0qYoLyjqTrL3xUr3peu4RFl7xCKbvrqRQxCX+sCNpZOKGdCmI2hizmwQohYdvdCPa/IPsQh2a67
GdSrviFelZn7vgttBPmElCI5QbUN8TAeM9b80cApEYNFf2v8l/pLM6w2vtHrC8EeXaYR2XNyDI0A
hRKTNj/zOz28hwFVfFN80cPzWbBJWLH5kNuEtdL92YdBl2UJApR2G2yi0TBOvl1tbOgAzMh6vUeu
hIv7OHi+gLASzIvScj6lNZo+kSwI7SKWpFduWAUrGMLWTEqW1YHMTrfy20six4fYnB8/C8RYLo5a
hTP37PDP8WIGmLpcLMWBMr1XLZ392+xAhfBwBpLjwqHZS6O8dxIfdfHaQustpUYNEwyPjqmOWJft
njGZK77SSWLi+WsBkjRwwsn5WNK6hzUVvZZ2hYhv1AlihwClDnNeX3hHJzc6nsk57Q6sKkH/26zM
GsDr8UlzreYHLVucVFKjIgeIL1tTCr2yMtAsgpufn+tE+v1uCRRGOhFlEqS9x1GkQHCs8ej6UP3G
CmUyWB+WBrGEVcDIaa4LX8rvA8CdaeYUqyEZkvBzmjqdyQSQ+MUbO/Mf3YI5BWiIzzvFZyCstGf7
uHK+sTlAc1jPRPpWvIrxlSl3PaAns1jvKOc4weLWOlA8IRPQgFtzWsUbpABNeNfSrKpWQzbJhLuy
+WYAsBmeA1UI2oXo8EmqEbaAIQX6np2yJQ1npkPu/+zJH/NDdwhFFeYmpZKmhxx+5g7bp0SavanD
BlqrSinWe+NRirbW2b3z3ns5cMew0IxSUhB/BevXFpECNT7hCKJYFKAV1Aej8LjTfW5vqfyqLPhW
Qok0QaGKfKoSHYsPclrBUVW9YD3RhlRGNj+S06YgoDQeO17Fe2OHIpC3MdSeBcC10TbLdhyCtuzY
xy9/t+fTdQBPO0P8pYZm/uVgZ2Ayj0zVS5nqPrSCPIdA3QgCfTNZFrBcrj/rbWR+E+D1y6TCn0lP
Z8LtH7OLOyaGjM3wrlZazms5brZZjIMprDdJ6phC15hdvWDwlBi0Lq1DulNGUqqc7LPUo58a88zQ
i8NaIwW7wMdPA3dLpnssfjDOhmOKMjcZcGAT7wzgZM6F88H40/PwiQBAn6XuSKQIG4O1MLTlpewK
qRkBmdYUni98Q0PEcBzaCtqkcQn29Fm7Nzls2Sbsuof0n+5C9WU+aLmVUV4BakHMEijgxl8zlvhJ
6hh8LPMfMM3wwZrggbzOCf5nXFetJcSovKzh/mkKKJm8E0pg2cXjjUB4kNdYin2yhxCgljB6Dsui
iPJPXDxyRDs110nl587Kd0de+tfn4Vg46BsYILiMMaNsTKcTT6898lgMfSuw7BdmkDrsUqwotDCI
pRrcbisbgQqweV5c2S5kxfZ1bljHNJfDe5btFXOzFo0C1BKkQ2frm1YIp+psq3mHOa2YkmBZt7q7
Hos5NgO/eQla4V+DVBOH+2GQjvANT8NqxxSU5cVoSqKhlhLG9c5Ck61LYgi8BibjRaZDdfmINy34
tQOV6srONKt6KHDpBAqheNe3xaEaaatIHzpJhvWGwv3B1ygQntdBl/nMl2zcJunxKYXHK4Bv7NGS
10ZCN0TexfToNdGgXG2RUugHQG86F0zJfQl9gerAQvUcNhelPMCSl+hhQnw7m4x3k8kLek8lKyjY
O4hlSDmr72v7Fnx3gpuC/PCV1N15lMmSxCBN6epdFErKyGSrujK9wD5WVlQ1lxNjfuu3amdwNj/M
w/7ZU+zKqORVYA9ttwyJb/ZxVcFOA8Xhum96vBUN42IyiY7j4c/gZilVYsOS7P8CNl/rDLMG7miB
TOCHgYdBfPvaX7VAWGJP+325tqEYPXyxXdCfvE+CrgckChkOc1RI7XYmvNEBH8J/y6crCtEz074j
rdkL1K4HFep6hEHvFQ1s88FAQg+Cj9ncXmm29nxRI36IgyWFrKTyxJ74nwLpwDfQiRvMrtgaKNXq
bvvsK0YcHUMONYEna8RxGZnlGyDXU8j0DOOe9iRMwZQzhgN5AyDyDK6+PB2vrE05cAzcPhT4LfoD
/ogEqpZ14up/386OULJ77OBamxHDEW3VUaZKpG+c5RsAOhG8wrrYjCN5ORlHTMBl3DFvRo01m50Y
0FnQjkgRcOLh9BVi5QoH/hoNwpjn6vPZo4pviT8bqi4entU0lnWmH5XqfjTFHcL4AcvLOiLe0q/H
3BVjhuPiYtJM+pBw+X/QX9eZZw83HHYNVF54I1gmogj6lRaqN4qgSpU8rkHc7GZVZdiZ9FKhSwkS
fMurl+vj8DBIyBvo7r/RjHuz0MofYJZheLYKnhKZZtdJIz8k1MPdMuQBtDOPirETIokY1kM+K1xX
HuNBAwwz6iwZAfbUfBypolkiuwrW8qtLsvUh+TEBewOgCRnNEweuoKPQycaFEpmfEIx5BD6BYkjg
6yWQc42GLZ0IbGTAattPvizEBGx0dOfyHAo2aZDXJjV/NkOp97s8ONBtqJW68YH7crfUbxjyY9iQ
KkmkgVB16+r8pc/wOt6CQF2cI+mZaKlOAx2wHjR0UuUyCaDdxiBWr3PAh1MUOQgEFjZJTLwSiAbA
nPnywKEs1Lak0Kt+7c5nw2MaWup8ayp4zGHbvfp00wN9E/VWUe9v8dNnCJ6nNl9zhG4ssDSvp3sD
+AaCZZg9WHUlbZ7MKHT7EZ0so3ozCIhv7TkrjfqZF4eHxbca9f6y7zJGfHxnB2UKw0/LcDLWdOsb
CrbDIlwDUQDpXwvR7B+aqLuG5lxhPo2BXufXVwnSCRaXA49xUba2xuu5oOhKTnG4OhuPyTuyxpux
Q0XqpA1dlpPXo8rJxM+zsMiAIZEctu6hu/arIbz8getCVMyjrvgSoc7ntyG7x5Ple83EkDClsJFA
/OTx+aD4usfq02dfUdCT2tfJNBVCR+/My5VlFS94MOpcXBXOI3KU646l4dHYIxoB5I9ZDCfsx71X
rwVBMtp8gaWvmlJVrmBBXq7UII7XRQYt3CHe4nusXHPy2ea7IZ/pFpS0uuAtqKT/wWPzJ8iRRCNx
ZAnqnCK8MpD4kauUdpLOLGX5Y8dqU4y168UvUtLcINYa663K62JPNaJPQZi339P+o5gfQzLR+Bea
NQvRycVCz8w2TIrVTk9ByaTawfGPfJog37TBedc+RUZnkXBO66RUWOaA4bQie8mrTMfyt9mdb8eF
7mUF8MhuR/gDdNCn/CCiKMtUzZC8P1nvs7Z/Ghx7VCVU/hTh3EOz9FGpoEs5sxKWwNekyl1SQAKL
Rg1WaPo6A9DhjXIeU2LCoy/IYBnbojnyALC7vhGoNlW0FUBR2BwEy7yuTA3iSew7SUKQIzruFXGJ
xMcBilSyEmjVDd/KdB80Od/rjBwZEN80zdpNfCppaaN/wsHhwX+dhxUGVTFBY4AM8ZrY2Rhki0+K
8mcPamDawoz6Ey9UK4/WIVkSQwF4r50lpi+terWPdkNBzm+I8Ru+weXMYgPo37CGn9SuET9Sq3wv
KuHXIUyVugv+pIsWj21TyJBzoOPQmfMNYWmIq0/mKtY3blrqi3jfGUfwMO4ztdOVORRlk7RPaZMi
2UFAhWuekKk0VBbuDL2uyDfml8Kc5IEOT0L9kTEr4gbaJBocln9F3xI1aTL+hUF4CwERW4WGg6NK
Lw9qaVyIhEtaejRersQalzv035ELgW89RlUuiQFbBWKlOOCzGy+MbF/coEqIkC3522yKcthLz9AV
E34o533Cr+4rZ1+5kKFSUHUoXK7Ffj8eM87STw5OlrPCf6Vanf/qSvCQ1AzQ50/S+L/8KkZmzw12
aqjwteD8VIFQhB2vmgVnF8fv1087SEhqmy9/4HBK0GoJCIMbUzpJc0PjNF3c/E8650D4d8WvcAyg
MaKIvXs+Gx33PchL2VlB/+Rt3vDHI1XcK3EGQf0VIjJBjK9e5OUY5iOd5LI7FVwDsGGSxwv6yUxf
flj3d+J0iNcQ6Foyz8dWPw2BF8dOV9aemzzyDciN01Ckaex/MSwM1IzoPhb0J5JosAMSDEdQes+Q
VB3GQjI37hIbSDYUtIMod3/9raeWunvPBzBS2m3VfUM+L/b+VwjZd+xXEQKFEjm6Rh3LOAjtqehd
rLZSsWE4wmwCJUobeTo4c3aDSgUpUenzE6EY3iOFsQFWT30Gqmtu2TwLrECwXQcvOMP1kDOihs6x
NaeeOCRwFfxmWVJwrR7kBJNGq22KD/K9H7WwKt5lHHLyX8YHYohTAM6Y2V/IFcZP7QNcxwYRfheu
sidEkMd20aAPVFu4GDFkdS6Bn328viIlS285FQaSQNqHi0UNuNsmIqW7mqXgvFQm2fuxKbACbf0m
jbJ+HLvNeWP1k1oeSbJBEPKomVQUMIffxmHOhCn8NSqzI8z5v/QBKOf7Sv9TOQ8arHZWB3I1FWaV
hcWtBFDfUzZ/NREERZih5mC0hWSi3TY155vuAcZfbbE4VVS0lQhN+alZBkx38FEXqzK4uBbgKcRn
im3sBxq/xcQNC7acTz6Pzjlq67KzVimuJP6ewRl8yVE6nV5kfdy4vBRvas1Dl2vhtrko5Br5lNJp
9V3AogPuQcOnjF5Ebg1vlBDnVUyBdHe4hQoXvg2KnPm3dItUoluW+5RGXd2uhT1e1TWRuZmYGIB0
BcTna1IoIUxvKKMAVK5+MTqaPmqUU3GAPuLXmKcMaVhZViGFBMDa8IbROgAB5pVW+8YqIkNs7k04
UueTyhz2cEQGqXm8KBN3I2lfz0/HGoQ+yEK3kfZ7ViOE7bPho1KVhINbA/4tjIEWCs/B+FWuqJpa
ldWbA7SuO0MIMfflUBAWcsseHWu+LxVwgZxnuNKZ2iR+ZqHYKVvMYXdLA1xIlR4EiRTJKyobRFV6
Nc3w2zFlZVPq9xGBBQFKeZycopU+i9YxgrTOyxsXkV/SLWDM7RrjcZuGASaZYBAri0TOhUSgDvQm
yAgQJ9/J4O3OWnZhKgkoOg10LXKWy2XKa7T7qpYcY1sYv6Y5TxIqRNwpaC3R1jcsU8kJBMs2lMZJ
kDSm+0IoySTx7YfalIOqjRNSuDdDmOEcGdzqzQRqOF6LIUi0ZazMEe+kTcC813NJTmFRzc1xJ7K7
LYILhs0daITwkXAhj7zn92azFz0uGsoqZGSePidHv5eBllNJCLomGnnsbDRAYXkWFFGqUPh8MuCY
10uuQgceRWktCrJe58/Aj6ryMYayuBKdlYFck90pTdv9BgZ4Jp6ieh0WuChGPi1SKvVo99mdY/19
u+UdcsYIB1GDQ43YtMAwA5HDNaDipFZ1iW2cggdp7pqP8iLj1G2vhJWDNVCNSzb8zzEj9f3d89/q
k8GPzU/4m5X9FcArboN6NaU/MwGwCKDTRCLfooh0It0RsR/iwBXsm+qVS2CBHF8sHbRQqFU6p6Kc
+u8dXYdnAN78LqPXXNbFeQ6sejciSHLPWJ8hXzxlqktrwOBeQEdgXOSik7uiJ7zxJATg7uCeZX85
NlogVklVyQmRzkfvK77HZ4j0hKHnIaRepq4B2hFs7+wf5geEU0vGP8rFZZQIvNBJQdwnLWh+cqIh
AXEd2Phj8RvRB8novefRhkqMHkO9o5KDqbCYK2UAdMGigvQcNobbqH6w4mK0MaMuM4VKPVcZa/Qi
ncbPRVI3J1mYqN1lNJZ5inq4JJgunCNZMeriFA6ukjs2Fj6VbLd100KMgcDH2pBdw9UiX60ooz5l
Ygxj4ZdPVBUeiD/pH41/RDiq/ikO4KJYtZq0yDNucZDMr/FSffYzPkbFws8NRA1yNHHyU3hvsfGu
+Rzvpto6bW3yiGEorDbXTudV0bJYpTs6x664nZAFJu1tKiz6ta7zDzQB9bEdiP+cOBGijbqHwyUw
pvr1aHQ1iQHrN3yURm8jlAHBntPexTpRpd+87MOZ52VNzI14eNpORJ/cuVr6X6GWQe05GnqlBYng
XfFjF+OHM1ctkpyS2f+S/kxJDV1JGmdUuszsPtOgX67RCrzwoPhf+NETtx3Qv/QPSMa/Z/0cioFY
Trrrt6MH6pamqHrpble7CN6UXTr2eQlImMFtaU8WbV94irS1WWrW4T9Mx9c6xEnO1T6ljy51UIF0
9/X28k8qBpJeuQF334xy7bbHUfNMTeKfx8mQrzd6vi/nZqEmDpd0+axWlrn4u/67VbkwPT/WgrmZ
iHokZ64+P7Ei5LA/gg+azSeC6xWKMPy1PzYyTDZTiQzTL3FtBlM6FLOgidNqUDvUdeIExfv2E3Y5
N2i2tUWfabYKAZxCwybg6HgzUbTQn+3SL/54b3GteMrDxkegqIhTfD+H64XzCU1tJku62MFvbHxP
ahGmp9DChqT+imeOuCZAB95iEPPh93mEDdfTATwtz7yiDvKe4XtgiNueY4QSNmzAqXBaoUhrE5Q1
25gj3Dv3i8sFH/DlssmYn1RX+VR6L50HwM0FXCJspSfRH4tC0BVxdoAZ/bwlf452oC1OVaoAIqgb
5hEll15Xz+e/WGVwzrTzFk6zjvgKFwi9FlNdEiHJNVOFQBspT0yTsswJ+8DNG4UYJBEF1Kiyx6pe
BkEHEbTG1DOGz0QgiYVwwWDmkUnaKyE+Eei2FOZ/9uxAm23/c0hV40KzLNOCcL8VeF8q4u0l8Hq5
8gGDlgPf0/IbdXncvCYrCOpj74Ff6yISQlzyMnSS+65dzSuyEbnVllMjrLFljs7Ty9X66BKtxRNm
1QapDULMERKWbu5Rln3NXyDzDxd0b6CsGiBgh6CeLnFjn8H7vC5+ikranjL6TCj9E0MWfljKAAPL
seupojq6XEUMfzZxEleLgRisDn9i/msaOGCGZyOE97uDpaIKA8xE3tt3WqYsEp8dybf2Ay5ZTB9t
B7MzmqBeI4ROs/ma9imvn+NqVOZbTUYMP2Z6PDKd6tAxOCmuFr6sDTQ8gKmbP73xfJYeyg2YzxS6
qijRDxSm3Ebu+v10K9FHZwtEe3ATM0zku+PTaAI7YR1Q/c/BfGrmlvAUSYiNr7t3ZTHoiGSeixKF
TaIXcS5gZ0RNKMynhC3Y1jiY6/0CNSsEZIoZq/VMu6ZajhKo2g94hPZws2vMP3kqhJBiY4AhqrJq
mbL44/MbI2jD6p1EWckIxVlmAb3wufZHhb6EfkRwzBtHKusTXmD01IevF6Ekl6IKQyPgUK7zgLH2
6npIpvs5UM7a9eSKCBcuVAOvMwPhCRgG8EwvE6gJL+Q3gXIq8wHoxbsNeXIyDZ0HEMGi7g2DyyE8
uhCQFjZKrnJfpkuBGDGLU5ANigY0SFdcPFFWc8z/+haAwIPPhfVH4zheK/tYnf2NLyhmh0eTbR92
Rg5SV1S+Ls36tWTVCmPzWS+rsZ6A4aj8/Y/lK7eiCzin5hBtUEoYqBoQE/VACZJ2+wLT2IeBXOy4
juDr4UkZ854lheQUqVPofbELHy5+FK0fRhdsAqOXbU5KvbBqTpXIJ15gnP6ZKl3aiyX8rvY6+l50
foyfc7WhU559gdNYDrFXmlRah81ymfU7FsK3pZTMVfL3R2UZPZZJanjMIllK3S6ifoM4cmiogUr+
pJihnA6YczdfhgRluR6WFO8e1JdscSlQlOxJdjLnMr3N8ervCui/YFHYlley27uJ/mofPvkWspNV
mnV6xoqeiwi6eZg28ntyTvVL9WCxm0jyb9QzsTP2RSCVzg9lA6PSVy94mGE5hQXMxCROaobZpcfl
HkTcRJ8ZAUEpkVxWw/O5I5JdXEtzwRbjfevd4DA53YbECnOZNFOVA0RuRc0Wwq2uvC2uR6tBd00n
EjUiwDYjPL1jOms444k66VtpmTpiKnwogucZWcBDj8y+/wl+PmfuvY0iFAIVKTTQeNnFrnBBcT5O
cb4y+2t5Pd3raDfNVgRzcpnb2D2JoOsCWt+2JUe03rSLIEwmBLYswNhINXTkK7U4SzMI6IidjGN7
w6RP9EXdJoOnd4/Kl8yLqXffwKL4+wDgCzxv1JaK4Dwa6OS//fLrSGpKkIW5cRM7PdtjKMjB3Ex3
hB90wF7uUnxRtL4hMgtF8kLT1LkRuaq7wxE/BdWMWWh/L3r5B6euo+XQBEbm5lyCDqouMoVE1k9v
qYQJcQ5aIrisPQul6IQH6ilVb1AniHg+PR+HTkdmxJ/N+PZgwdqF/2W24NjXK9Fz5dFzq2GWiL1H
3RAizUe06OFEqqxtJZ+3tEDlu65NYFHQ3040vBv2dSnEO7le5X2C4/6iKHzZ8oNPZnOTE8uKeSNZ
jr20O0rCW5Sgo98HMEkBLoCeY14D5Zu7gWneJigR0qyfyoO8R4E/mM2S7+JmI+IAcVJrxbOf5r72
sUPz7UoUpDKB6lZ0PjNrKyTtEC8SiY80ThMs12TybNiXP8UvSIboPga42ZmoSVhra9FWlKpZinhz
ehxK5KjF8/zHG9fkI7PHAqeY2L3hnnv6O6FM47eMqJfIEO5zxCjZM+7BtvLBhn9AaDhoU5J9jkZM
S2/dvPSHVLxZzWC3t+z/n2tybE6TOMMfjh9FcixkNNVe7e6jTPxsEOzmFMr80Ea+NZ60qEzL1zRi
bPG2zVA1e0Y3rd3tlxM4+qMuUINRGcIu1QGOiIKhOfHLz/nly+b2bOxrgLVTz4WvodG8jopbDhds
z2Ns/M62VIclu5b2tR+MBaeg2h7rlYw3coM38vkyfEdF+934V3J1RCLccThC6NU+VbydcVT9jHfa
bCNwlXn15/SE7cXFpywEZx//UAxfqL1HzNSZRUe4uCFDnZGRUwXGfGtkZdfPt2a/Z8loDtThuVnX
nIopqlCR4lRaJPiLnAjoZXO8fUKxL2pZgw8a3WL72zm4kBMsdE2OiSIq8qgbXHWapJu0BfuHQ8kP
ElcRAZbYFASa7Ha9iiZJBIpGZdH1eJyJX7nwq/KCBQ7g8odt7/eANleowGGX7QVcAyL7BzPF9F4v
5eVGPktFuleaWCKsFyTc6Me3WpFkLq/4NXGhAPCaldRXK0OJNJX7hdpXdjR5xvy31Z1RJYQkO/RX
vvjIYV1bgX0cGKW1UnuUagBF9qmiexnjbEZUhSVYC3DIs+udXK9grXy5ctrsFCaNn9x1Bv+F6oKZ
YVrU/ENmHVVdclpTOxVjYs/YGs08R7tGYmjDuxsQQpuL1Ql5eN1gf6SLK60rxMSrToeVLBIfypsb
aEzifulh7t6UHvYP70v419zvuxHJwoLPgeWxLFb26yeNydifOZPtxFAoVSBMIUITNHw4uKM2KrA7
llus1T+ZvdN1SXeV01NFpWV7sEJ6Mw4aoux9KV6aa7OpPf4W8T3yP+bN8hT5TTgf9urWtkSuyEnP
sIdrWVz6CoZfPmmCqX5AkZiAdPgw0+n3KCmOrDoagBRTQoN4KH78aBNnqR444h20Fv/8KVDqmBIV
0nfRtdiL5hIzV4W6ndEvlJq36LRB08RJK9mSw8RMt9LTZp59oVdB1v7BJifWPB0DAa6RPv1KHdIQ
rdvtYbds+qm74my4JkbNe6pdmuotsdJ6ZqlIec6eqSs9Lly6qEEDBrVeV54Q4Ry4kgTIYofzLIDQ
LvCBX0NiP9BbMkKQCTB+z+glWFAQav05iGSx2WMQ8040B8P3MZlDdsvtnfhH/uJfnp1d5TiKoLfR
CeQdfU5LM5Xtxc1TSny0uNWSKqEb5o+gV1tgDhF3qIppeTN7tGKzdQEqW4qb70FX10mlOxVVlDJA
qdj6BRdFWVn7XqNUFuAQRHvI3XyLTwIyD2ER3LeVnfnPCxdCOjVRDdHLwZw99eaggPG8Y8LalDQ5
0unUpFjGgiQxW4NHGXceBV7cHPmNNOTkUqlZ43P6LJSP8D/6r1KxpaOXhNcPrIXnuMTF1IeiARdJ
fBp1MJxmUaAvvLUPjheO9Vjozu9xgEYvLZ5jPwIV28rQKfdjmiP893KbyUPa5Wu9Q9ajfSo1PGnP
bmoSxwn1iyqmk79XSVlDMpltYpDL9EJpkkqUk2IyxSEdgGXGnLghHtwkhaNyx/I7RgSOFzqi52Fm
0x4P3fdvmJmUDfatcpHtcwqWvr1Govi/D5nwY3BBRCrpiUFVmFHJiRnStFvEEWdV+U/3Pck+ow1R
6bsOBXOBRQvJKLGLfoRfqbNlZzh6D7eB+Wo5ByFgsfVdBPXlMibotm3lRqIUy5E8NkW1W60vhaq9
JpIkNSwLVbCKkmpBfJTvnL/epbE+SmutOzEAqVxe0q5gi3hTykKjSAv9v0LpWK9A5hMKtQ8o/Yzx
+p/AIKiSVqCMWderOqj9AeeEuDP/NWvQU715UQQ1FG7w4TKQwcE65nTbLJiaoQ+GE2rJ3yoNRQQ7
rZPbUiCvAo+tXLDwRUlZIJ1zPs9mIYybVCZZvk0loKsHfY3fun1leAPYWsXmo8NCidzFb4KK9T+H
tpK6jvaYdKYFdZ6C+7bP8mWD754P2YNVu3mlvfgAJWvxfpiT+2cmcorX+w9uYBK7Pup5guiRnqhl
a2M9jR9fKAOllOUyCTLNPj8/dS7Ma0LgYS2uFCfOppJYpwlKmWYYd2su
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
