// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Mon Nov 14 13:15:13 2022
// Host        : FDC212-04 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/koer2434/Documents/covg/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v
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
UTeoyaWF07oaoHZ1cRwdvI+Qdau5hGnmbJBp31MZMbOiO1j26/RxzgpfDYjZ6LAVyoPHDSzZpz4f
NFOhV6zmwCL6L6q+pzBPQdY/2KD+AfLJvLk7doyStFJ0qrpl2/KIYZGJFWfoSsVZ9ab3ScPcguKT
EC1/i9no45mFKyXNRfnJVq6Qqj93/2oJ9vhEYVWooHmdkRrMmqLo7VpfInvq2c/kYUELxxR6YNkC
ax2YftF3OToJvAQu1e0G7owwCFwkqvuKe+9nO80lm4JqVG4UXUesIzZSh70FX4xg4tMrd9VZJx5c
S8O2U1FcEfwWEnzKeKDir9NpNTW4MZzrTku47w==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
LtgVtD13x42qPaNdAvDpZ6WQeqftmK2ZqJmewuv8YJ+lLjR16zV31TClc7WVKZbBVYCXcHxCdnzP
cwC7qewHMmz+PDrIQBXWROJWr+SrDWSqux5QHkVfiD5YE46lC1k2OCbsi+WkvNdHvGlPcBbjhnL0
4Jj1h09PsHdmy3BrGhWmAzK4Q+nP5ZLZZ34y152WOGYqT0FAe1UHea7t303+mQLf6qHBY7fQj5r6
L5tnOO1gJUV295qU7id0NpqJEHjJKzfT21yOzPXd+HDIIGGQ/KuF68gboGrU6XGpcy8DMXsI/nAZ
I1w5MR7rVWsq2YiOByyyjdJACj2JF1vyqM4tAA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
jCRGnzm1uqSFzzP2MgcYs3BZtriO6iqo2OpR34hqtNSuEeJAz6gyhrCz4dpYUOh88wBA+9BoKTO6
v8zlF1tABpjW4ZrRcNK1jLYnl4+GVKEQN+z0Z0mRSu0Vl7NrV1kDvwgckyx+TaaFHNOSlLXc8i6q
61rjpSXsuSxqEQTZLe15X5Qj/vKYRz9WMGgZUEJ4QHbAMMzJvu1piS3WJq5avgZYpXAN5PnC+yS+
oJp09ttu1kRcg8SMyrQZHYvXtCsBHpVpDPt7yVqBKP/MFHrsqsQ3ywAqY9GJ9tRCTqoKDC7WGAa7
JUleswqLnCRltY1EeR2509TWVLenUmUwl1we5J0eoD1hnba8j/O53KZV34/VeKM6snPHjSzenHqu
A0WsoxF2n2gjOJ2VZSpE3awDLy+cLxCy7/VXR/G3jOggLVXLlJVpWkQnZm1x2EsHH0wK7lf1vLGJ
rSPfJ6HIvXOVu7Y/zU0UCO5ljgJEUoJCc7L2VYIRFNBpkUj6OSIUGMhkR0LZuiCSf2lNTAK1hG7X
QDWqVIg1i2EJYSIAlR3UyUozIoFyQvVIvBjNa1q0sAWaJBuJUCBLmF6CI4ekxjMgNu0dJ2w9golC
QsVmD0vI2ycxLA8/iX1eiafOrSyVRPj6ksPIZYVxuC906EA3Xr4+M/aaRWC8hZ8z3semAxYi1hPX
wiBA/aLYtE5t9/Ct8Z9Zb8VBKWAXeakMkTiwPr+MkxgIGfgm5CmK90sZASVRtoB4grVX3iA1lZF3
192mXtttaScufqgT/jvBavxkNdsthxK0c4t3wIThifu/L8UhszrNoByIlM829fejsFxX86VOC/s1
4p6JenqmrThEe6AqvGYgZithTdTlSDhH++0o4AT6b39vOivcDaFLpqm6oAfSxBk0H0t7QBa3ofaw
8EWlFeAjWloRrX0GbRLtRJly/Xu3lBK0cJ1hrPubjSXRlykabkzJjcwL5Yz9VsultqOUHcLXzKC/
UshewtfW77AwqdK2WK9T+osR1nSsIxsPn0bQ4NpjpZlDQqP2vBcr0ag9K9RXt9r5GmQx1abKAvMa
rI82rHNI0ms1LOS3lqqQj91kSUJXg+JPBN3tvqOxALUIoL0Y58OmcGLskc1EgMKZ7IQw/iTw60/Q
Ol/ep8tuZzbJtuzGvAQ7Do6UQVO/pms5Y5ZRGqCDKAVsbrvscRxIaCmqbHQ3o9H8HgpwLjwB5YHU
dmFfPLotnj6W2duzBaw8jaNBbFOqY0DidnXTbZkcSjpR+CTGNgTXx43D7QqX0o4ogA6bBKRr5ml2
eoeoDYWDNcCf3mMuxGyNUw1nzbVfMOUA9Xcc8wHAqcqOkNpeuRHM/U1Zi7oy7Nu5zyUS02dROMv5
ElnVpD/LHxdCZ1Q8BlgbD/j6RPSZguSpi2CZ7LG+CvVi3Jr7HBMwK/21y8zs9wPfiZIg2eo/wm1b
FQl0OyB6ZUv8gnDR+N0JXp/LlGmZbMC5dyZf1AavJ+4a9KBTARAtYU0AHRsYgvmMcdThqB5mM4Tm
/sycBCRQPi9tDnO7qe0vrixfc+CXsYa7kYnGnlkSQpmvITy4PcNrWR0LhgDkInEzzhm2ShH6BJF2
VRU6yau2QBMkhabu1w6XTIITtD720yhbAwKbhmowf4sNqAuJ/hyt0nhOeQX4EXKkr7+ESxIN5n1J
3dXIfIeT1oKhJP8YKeH08hYWjmbJ9C2l2EkHwYRTl3rahrwTtS7hQXY/vHIGLKBudHNM+Mh08CgT
56G+BqfPZ5NPT2aAzEBW1wtbGx/Pk7va6LrdjG9vvveJqawWwiaiRey6LGK7JjkB7Gx1pd9ZV5Im
H7CDC0uxBHQUFp6SYZHZ+biHHkYCmLNobCD5e7SrYTXuIk/X68F9DMk3KVOElggwsdLRK3JoaClN
Oo+TTpjjU1egnKRulPavUJRaR1+YDb7p+p7Z35hiCyU9wr5O7gL7zvIKoVuECCnc62kdlH5pzbdb
xl++S6KxqevflRz2bAsLY0urk2SI40yTx34iE209ddvSsaFT4rRosrT/D8Qi361gLXmG7bJV5BDp
OB0L7dXcp/r94hQXo3uYUM5oIQKPQW8E6MOjPZt5wYQixJFoi3EtptzYyPGRDvpc4Xu46Y79KaeD
X/DgBCy/ZlmEj3Bae+vI1SMSrBaGzuX4aQ+pUUNRnwX6QZe4TxQSU5+9KVFRDB273Db4KvViny2I
AnKhyUI0Vc3AxOLjDYHr9qBifZOHU496Q40NA8Mu3ilJ9PFcHk0oEyTHB895yp8RhlEHdc78EozI
34djtMZUSi9ZGd2VTW4aLg/V5WhWk+gAabIDM9LG7xx3SoFFb1pkFL2XNSj3gq+S0MOQbY1b03ff
m9FXJVJVUAJ34DvG4qgwq4ardr0dX/5SroCmMUD8jyp1MvH72TFcQDrF4S7SzCHVZOrQFAATDWVm
fOnQ0ynszpOKAzWb022bfrlE6FL5MzicIh2B1EIjir0CfgmmtlwBn5P5xZX3W3c2oZCkdWX9BK8e
xiaUhhSr5iLwPoyZsVZ+Rxqrpb9qxnuDbFCOnkejvRYY6Pp7LmsBWs0m3QUfOEWYZi86sMU3t6vM
N0fjoderd6TLsh/F5k/y7H2mrsLeCSDj3cGGfKDsYbZ/3LMUDsCGwli9BpMGk5egA55061KLc6Ot
TACaLBpalfsld2UJ3L4m1qLoTq2jrHpGusn4jKPDfF0hHv9wuF8JO38M/dKcPaLxqUyk3XXhb32P
HwE75byZbLnNKqyS8R51S3AX9UhPuEIQ4ZCeMllVpEQvET9IjETdI3R4P2oJxtdx6HzCCxcFgu5o
30Hwgui3LKoeFSzWDQfYqzDLKu91S7qKRpeFNQa5zSSxzl+zrKQMos5tB/hhcvURbZ4OvlMgXPB0
vXOsgT7L+EK5y923NNGyzSlgYpyZEwudsHizjyWqn+MsKLq6gH1tnQ9FsniijAGmvdON//vd00bR
nzLAHN9Ikjl/vkLN0mPFTZ9TKTN7PZvsr+zDgBt99R6qAq+iyQWgpFs1FVOJliujOsPnhwVLFU15
NffHmJr1VnhpqGNQE2GuhACScMvOr9GjjSV+6an+rC63aRAzd6S7Uw2eo4nTDoeQfzVJ2AWxnyfb
ZeajYMxDnqsIvsHAEh+pAhJOfcYsLqdZRHu9Pu1/09na6+wBDthFYdMUd/4XnZjwLu0sBBv0tls8
IMuC2QHDSO4DUi5dQJlFNxpxE3n4z65QPTaoA+je5QoCz9XDH9YrWfeH4amZ7/wKEJhDQo14EAH/
0ZQdGFAs6QqpxOcbQYR6YtF054UoHRNbjin5ym4i8CtAj+8S16gWVeLTn3UcpB/+5MEOtd3KCZok
eZkQr8+LP4jCiAauc20vR5O8+zGV62m4zwZITKLfhOw6DTNUZMQqsh811MAjk+SL12eTNdlPGJHN
+n54lbXdpu4Vb6O7gW0662WCjDtB5HCgIA51nL2IhYr/iUjB+/ZIjHDCOsh8eONpWpd+HwNf79Oc
woIS8J8N607IsOdJGxTXKviy0WIN48dOSRHfMAFgQLAewkm94LxRp5ylazSpQDnXd087QWPhjoFC
wNYpqUQpUkdnU2MxMNPC6mY+E1L0nsc0leQkRXDXPHbl8b/GaqHif0H+X8rQPPUxXC0dDsruTUCL
go/M+IOErYdpnyTNmNIIUZ+bVDopO40brdiuBfUIXnUDva0kqOoRwi28dcrRF8efS+v5PLTIKsA1
Qhl/IzFwy9mZrXA5B57Bg4Ye8gdKunjmF7dZvA32nwwP6MyrV75whQmwEwt0lw9TB2MC5Q7XLuuf
eOV328nMzGF2wLitI5MzyS8lLIiI2BbQPKVcR1gHmjhqh+puEqWrtcJeBbnjbNHOjHrlQpALo9EK
1LawELywUAJtALgxPh1lavXXN4ik1QJ2hTts5Fj+kTzENu3e5mv25iqn/tsm/YE6gBVqmptl12+p
DYrpRzRtjM0h7c0bbidmw9Tynto6gBPu+8bYCfQclQGdSJiU6DJ5JWP5yQ939GzgrvsBDOLUVHxj
qrds3A5VxgdBp/26d0gF/VB9XKqWHYpcIM6trfSFz229/aKAK8ZnSOxBKjVYLeu++HjJzhLiOk8T
9EbVM3ximMfLD2lhjy85fmKl8n7gYnONHrX+vqiidWA2zvTVY2civJzrLnt3V2ne3Xesd4wdMpip
c7hTDi8DQjsJi3z5qUulxD1w4fzZ/dIeCxyRKGDqlHdlXwaHvORlBZDE5Emoywk0ufITp5fEi/QQ
j3eYHUyRrpuUDxueQ5cxmKPMo3p83CA7f72YxpRLJxCGl3m3hjp8vlRZosxZD4goW/ix0PK9ffiT
RRzYrW+vchoORdIlce8qZ4Wj+Sy0aEY3kqMWT/eWBTn9ZfS7Bu2H/HcOV8zl0H5ERwjY6Ht07IE2
cO/TQqh3e4jZGZQ1RgUxYYiC/w/eaTuYjrm1HkNy+8nT/UEhM+jYiIuWb2Sw6gL/uYmFQV/9hzKQ
fdvHI+c5/UwOECsPenFt9qhvM4jQyVOAZw8sZlCsBK+RyhYOy2B1vsnIRTxoZ1+R2ul6yULdVvdS
cydIBuQKLfEB5voWiVYAwEl2xC7oB0vAFrlAEnNIMt9ZUcnnq84DQmBHCalsI24cscl0atqM0tS+
kTmItg01L6gVJeNNJV8QDPAC8IMT2BHuwf2HJvP+ztix76qx0sTkOrriu428lyWSr5ZV0GTY0NUP
dZBDdBOciyOimtzKzoz+7/1SXwn82hLcg15IR7ZovzAawZZqUP7pshwMiZZlqheReVVF17LYfYus
nMSlbMbSBNr1+5ofarErA0/mE4AEu0+VIWFG5CTyD2rDyXQmJr4bFWbJX6sEUZQrbaF2IFzZIXXO
2yZCp3APmNF3buim0jPnXO2059YZr9yKZHyuKTbiAXaocfXtW5uSY4Ag1TSat3XNY54zhAjssIda
UiQySvGD0ABELi/d6H98jkoQNW/YVmfWSugOx1GHdAUfSLNLaKaKEo4heR4ZZ2sSwwOFWA2mKMWr
RaXD9uTj2m4KzJRdp/Wo69t+6OEQXSZ3yqCYPnLDmE3Nn5Gezn9H8K5OtWwjIG8jNnWsZSNH+4Vb
UCY7oEvjAUntJRx+xgg3UnAz26GpfS6AeBEhYvWnQGrIw7vU5vRrmkVVCGF6/QD0Dp6hF3wbsgjB
W8G3rjQ40a/vqNLko83zfrbMnV17cb9C5MA089i318eO3fp3T39RNegKVfkPe8nUz+p30NfpJopL
kztwgMRRj46EwCvo5FHVoKV4pIKaP0zcmMe8YAAF6ifvsKHTndyyYK6up2dknc/4Hfjw69BJQfGl
3knJ5CU4yQekQp+J2OnzrfgHMCARw+JE4Hqa5olOAMROah7xLMHFZQ7DVCDiZzPFt1quABsO53vp
ai4ur9oHYnou77nbcCHXNpf7BIOnmFbQrCvjWgUhZs80iiAdzriiPf6fl4DZdyzl1qKyir394/pX
6qFwvEhlvWIGg2PiA25W7l+TQ9fEFobTKoAwtB8e4K8DYV67WBKFmT1WyObb5hBji3ul5L3+GM1p
rsMyw+qZPO8WzkMryQgceuW3fN0KVjwvPLcK1XSdtl034Zt2/vBJ1q3Mdaqu5Cu8Gz2HladusHu9
BxbUzhxlPI9VdlpMQ1Lx62RyyozSoEzmRSrsAr3qGnKlU47JAMzmgGwKXCsgSwNRx+UMfPfECJox
uH0Z+pXHjNKg836/r3ioJ55s52Ylr+356U1TlgcAiA5OogsRukQYrt5azdGnfCFPSNcDTNcpI6A/
iD93XA4eeITpsubqEWN98mWaVSiAoEHl45Hg+JisDvyw6Pqu7+LTiU49h+sEJ6/XPwr0xCPQStIk
PBv85VY99dWd5SiWHzRNd0/DWo9X030n1xmpB2EVqETLVW5BEO0eVndUeL1ZYK8RNSzYEpSdRD62
RSaYm5SKRZ/jjEM2JGy1THeX3gaEyxNe95NZVY4GVix/BpV2K01m03TWkaKE1kJcrodHf/zdruDy
ct84/bBgQdctQDDaW/QUcxrzQ7/43mJZdo7rJGbFw25yga2I/cfGAGEBmLx9rwb573PejIpXot0g
G2eRH0ji/kf+PPqeobv+fD85oOmAQMs3cgDHmUN/j2f2CC+NNrkFznzENhW9C1EHVdmWglMQiFte
yYRAERQKzi/BaDYdgkEHiOrS0C/HiT9pEZI93NtlAYxOp2jqypPk8Hr2+ap5FPv8rdMYyl4FDkHC
o/HIvi1QWlyH1XPNdydivT+qlPO1iQ1nR4YTnMiGipVGg1mZm/Xv4CE7nVv2D7nDOr6fYBUB0RKY
5bMkymI3r+Dc8pNpxUOuqhqUkhCIlwQr8v6iAd7G+fFETNmLGK1s8OGNYYEXaXO2tOHFtgAdS7GW
KbO779wKMTY7Qhr3KQ/lBafuTEHmPW+QVPsfhlzz/IHSwNPr7AOYFC2He6TIVzKpHSl4J51GIMv5
Mr2MU7aK3nYjDRoSVs76MYmmpQGYNeoq2bw9m1+pNupqJVJxDjnn3THxA9oY2jJksPy0TCWIdDz0
GFkZ6f1t2P6hEZ+uwB/C2TxQ6vEuMaUi45EkPtjpLlBi/j4q4y9VPgmKQQxBmXIfjp5nRT0A05AA
ztDqYqYQc2GQZVEf9PmNIADrKv7dz2mQNuAUsY/N4xcOW5gneTk6LuchDVETy16zEUc0VInEoAfS
bTS5cZRjdaYZeQ/45Ra8IO+5D+8NX54SkZvB3xVVRwjs/UuPPEz5ChP7c1ybnBCFmmwMzmVwkgu2
QGzpRFNDZ1lWzj75FuqbkkgPMKGAPMn0JqVSf94aCie/cyS6FWTnqOdDzO0vdxbbnzanOC5gR0q9
yY07P02Ate/8nCXWD21+txO3Rrv5cs6cdVMC/BmHN2UTKol2Of92Z8JIDVNJ32FLKRYvVoc7LDxM
J0ZJvOEItz3mRwZiXvy18efT+cjVwtbmZfb4OYp4Ow/Rj19j/W59HO+GP2bYLveEw6m6Be8IKN2R
Zrx6xbWsLT3EgaPqTHshCbhIQlpURJQBitn2ni7vZE+SO6pbk2IA0GODZCcpNiVgGXJur+RIK+iK
Pu1uznUgyz+FO2YSxxTXOVmyZ29NZNH4tlaeU3PtipJgBdjNNIQZEENqToHLi9PCEAKXGxjnZvuA
u2nrg1zX9rfHVxTTfysE/FQaSnnCvpZ/NP97fRHuZA3ZbSkfR85sM8iEVDY7OG33ziCp5Hpvbq7+
v0eEanxMwXw/Q52Ps5/iIANbENsBElmH8l5gPN5RaSQ5Td1+gsvWgZE+4GiKx9bIOUdl7gu533ol
pZ4n7qc+h1OdwX3BlnwldUnBKJ2jKsurO2x9+h+yRUAW5++jY333saoCQhazhPBFSineLEquhZsl
jp0XSUELkwB91A5tRqzFvrG2klIjDh5so9J4LONMxgmGYFqYHeZsrrY2BPBsLy0mJB39u4YfpQmS
D3uO+DaLkd2akMiGaZvanN0OZDp7u1bSTyMh66ya1ofjK/hyfRZMlfXnO/h310q5T27nyGMBOt8Q
iTkKU4+WPmw51ZDZ7Vps6OhcZh5sM6ODa3IQwTb7Noy75Jceu6HNNqI5hhjW+XHBkkayrYPkLd+K
JFPMy590VJ3KqeDnOS7Y3rRfixAwYjYkWInNN6upNDDBEwenilIjR/8YTtdQnX1UmYqNkXuO0RCO
pPkIkso7dfQKGXTLZ5qoumMnKba7ACN7Lwia4jBbdUFmxJUptIVyRkbIrzHejG2488IdhfpG6hEz
FJvSN7b2vxz5qK22rQ2mUS5W5U5KXX41z6Uce4vOWSn4M7lnOndRzAJHiWLVh/PYpole4dIi2CEQ
3pbcTb8/7f1haqP/rJS1Sh0NO6pYpBDbL3CzhQPcq7GAYUu0u1fLAtX02kRY+YqJZtcunM6eUMpt
5pBi4FKZVvGlHUG6irM9kjgSbE6Iod9xIiPVCkZX4KBdCD3+L+z7wvA2FTIHoleSBpJgeoACpkmW
kBknmyCEJwB6K+FH8KedC7Rwr0UCXILjMh8rFEVVgJKNdjLEOQ9vOhRjc/08JPpGa64eaIpS6ANQ
sdGG0xCz08vaVbehACbngWuLoi5O6ZHFshcbeV9/IP6WEBAEwlCOAYjxBNYgC+cSS9c1bE2CfB7f
5iBY76WPWW6nD4bz6eITdzleW36jd7CR+yEe2qFV1JhG+V2odE4qsnd3zj5gSdq8rDcfo9V61+Gr
EpGoEKJ3+zaoxBSqMGCvkzzRyAFxtxxlfSxjXTdxQOgZpG50Fd/4vB3cmrXV4uq9jzyq16KmLoFy
xZaPBDp+pxUj9OJB2JRYILqNvE+oUfq61U+V9vRcLNlvbzppflIh8VHZVbQVfpSgSDjIIw+WpGTN
Aj98i15v9f8WySrRW4Fi85KS9wWttLDXITZVhl/UcIiL+jmIBWAaOJYrSpDPjSyG450cRHjzG3h3
OI74i0r8P7Lb4PK73nS06Jb5iI6ADqgE0JALF0P6BU7m3dKtXrFOSZ2bYktTR78abtRjucgbKCH/
7CsDhGPCpto6fSzBMlbYi3Ot5aDBiC9NN3XkZn/N3KbtIf3WWiPKQ9/3jnH8ecZGMcQCGa2doiho
gzDMABXQS6XBWo5jHPVlErbNQKy53OzoDnTtib1Dk5ful1Xrgr6gr/x1aaR8n0oNwe6G1OCFfD3l
LR+C67rQI3L6t8+GdP+2fePdioC/HPzGe4dpS7SbGI+tgL8xfpzCp+fHY85L5JSrihvOxAvYZ7sw
E5PHSIUtbyjanK+KCYmNasWj5gx0X9FoRc0wnCQDIBbRMNBTEZcK3SuuhqeSpS5Q+inCBd/WQxzQ
PNioBJbYlIwFQARsY9iUkIMQg2fNw5va8IdD9UXrew2oapJTWbVXHEiXkuQAAPvNxE1NR2yG/xjp
tn5L91CwOqYlb1g8gtP3wVm/HPx9gXzRz6fLYdFLciiVPJ4V7NT0TetVG69HEAA7Wwmf0GCcTclI
WwslBkeCDIDpT6QVzEQy0DgZ5blO5vxNibFtK4QstKohSIf1s3l0Ew+yI9ONn0TH4T3DSIibaGZW
1w3jeIsKzIU8pbVM3Wr/MnvT4ccu42f+pyWH30vCdLUnYXbYFeC8FslcXa6Pf6h1ZqhCS+4eeiMS
2x764LI0oepg94Z1c0cL0lAp6Ne6IwLQdwuffGFcrJRJGkk6S7efJNCumJTdcHENGHx0ijWRdljy
7vdDKtesiQznC4+o/0Vqe5TkeBQfSUP+R4O0RUBQDz3w95C9khHvVn5sp1saaSmOe/viLzuzC/yN
qSejSVN8sysxZJBeTl/7ogzHbckHO08bxGybq7iIt8rqRaTKlfRLtQGPsMa+U8ImSw2vpLDdj4Is
UMcmVO6t1StqZ3CP5pQbUR2+LwAEDRSqzy7W+2H0kJiqcfTZlEqAYteE8WupJAIMTaLMy1eELKxd
BQrfLaLueBEP3QrhvuN+JifsvyM5yo+Tg04VWPgHDIlDOTSNxciwZMVAyW0T3s7qvIXoPx2LtaY2
7dovrygnOcE3gIlh8BuQd+beAGKQpmwF09AzyDiff9eGa4IkMcOKQD7ZBj+yWFCgH6r65efYqjzb
e+w9bL9H1nZxQG28CtCh5vNFnWUj9PWd2Klm+tvjYqeBX4OYygGXFRN9KmVELMr5uCONX4VQW0zI
IjMsiwOxIbh3UCNV8keTx7nNektP708X+Buayy5hYYrbBLB/SuEJ/G2guBdfqq42ScnrvYLJgYMz
Zj8P+NkIGh0FOxlsrBdtSLVOeU7eOPKz9ADz+PNxwin68DOFkN3FwIy7ZLHR8wT0omwEDYrhnzwO
1W8nQx1Ocwi3Qc8kGONw9x26y3FqClg4JLDuTsGEUf/owMaBncJFy2VV6N28BJMc3isnGF1ExLZ5
An3twZXI04UIA2s7cYNnkwvcIfgds3kFtYztfI/dQid1D8aKSCDy3ZXdMRTrjg9WpbAqHqIsqWED
1581trIC/eK3o2tCWQmbYA1Lk2woYK7t/tjOAFxfYnyubvqsQJ7TJkqqrvQma/xOUlQ49r3/yOMq
kxTFa0Xi6Hi8PVNkXQp2rG1lG/EafAfTYz9AeG22z1qQ0Y8xHuB7XnawpSwLTGwtV1YUAbrHGyKC
B3kzuLIVkcKaLDvxWokkpTuc3BgrPZcEY+sMyTYeWPxdzr6G97kmalK00Gb+FRSD+5U1iNdnC38k
gu1Cps3ofJH2vYp2tTuwKoU55s7IvffkdmuKygee456Au26ed8E3/LIX5DmKE8epotNTGlEXswVP
dxnmQzDDy+x9qHO6SeQMp6g6GetrD1h1tbtYG955RkeOd3aYCFf+ErpJH9w2aBeUqeaQ2fym5ENq
S4SawOX7Azr/WtuO+TrsRk6LmlHKBcJ1rEbHNTZgpiIOoNcGLU+8Y/hMTttueUR0B+UklE6NeKFL
zP1AbeDK1rmeGSjiUW05LQJ0+y+8e611WC8+g3B0UpqMRKxUp68eDCpRwzQp/H1DpmxxWqVxSvkF
VuvXi6hUD1ZVHv5XnRacE6z+l9Z00H/Q/2DvhdmHGS4fjEQLGkFwpF0yprlfwI9KlP32UaMhIr2a
n/8IDkMTbKA0DjULC8cGN36gfBgFoKU9hYtlNiVhlNVuSsO0rGJVaIkrSaRElqFGVb6GL+v8Oknj
qn7WEzSwWmk3buJTP+faomJpcehgG9cDwwC+55sm91WDEIH+UNjSglYR578vbNk+HDwimChDLuJv
WNXGyQjoCeAlJqePIDxswOoXRgr2wQw1LyHpPrzglh/um4nAZoVro0OXRERdhPoT2IJGe5umop6o
Gz/QlxUmtL8NMnW0ux/Mdto8gZH3bOODlFS4FbzaQF2TrsGcCZy2DgfI9xSyDYYjmob5jaIBPlw5
RGH1xRjCdJ4yh+zFSqe3vsqd6Dm3AKcRZxkiQ4R0Ul4upRDlITXOimIvgi6crYoT/8EcqIF0zGp3
UpvxYslCMVD69wHwLNDF5LHAW45fhDJFE+Ia31J1crc1g3Pr4mI0VGOGi4ib/6FEUprGCn2wkZ3c
UghpLn9v6GxJfNW/d86pYL9CrTQtdGahwvQPdCwLLsOod+N3bxexig15NylDe+NTOgClZY1re65G
r7e3g8E+LY3+7D77w7+nSp2A02i4ZBl6fPOJJMSjFrZHJIsOVQh+POSG8ibgc0v7BvKEQnBGkr0q
HEl2RzNTN3mS7fCeZ9rFQJGbpjs2NsH4VI+rDciux8HpNm9HG8lmOsi+R7VaHqRW+eAQEgSDGcCB
I5d46nNYIOIzOenH18VDMwhFZdI73iE30DoVyUW26krIV2C9B3CYr2z3ubPpKgiyWRr264gHk0aJ
7iOZ+/A0f4AsK/bLL1QnY9SfvKYD1oBDhF22JwCoLo/PssHleobQqUPlyXwRMIeqpIBCJ2wX3B1w
UJC597X1S2FtPfmjAx+dZN1UwWebyhXm9cDfNX3cS42QDBsgaV9XfS4J6qCd223NXPtkqKnAnODo
ZXan+MVlwhHmHaKko3WXbrc/wTMn5hLw56ZdlrAs2evJCPij0liTTHC+iOVb22beecl5opWpbvH1
n6SC4b3ea4tb2qI0YaRr8eDjYhSuA34IvFftxcJBc1oX8qtmEYfy5xGdiq5fznW/b83hgCXpRsgc
/yo9aXodsgEGI7oYZNKcSj8RgXi0MOy9VvBCM9vD79bx7ylzQSxJdchlEH2hQwi3DeRfwkSo3zrB
NuFJAE4kgihGWIlyqjWRlGpDO49oVqNCnnkwUo1sL/auVenGrJNzzHWDcp0unAv7jrLK00kcgF7z
mqDo0tdwo/SBGAPh0p0LTb3I/Gvv4W8gdzhQ2pROHw29kZo+OXwnBF08Hg5J5YtqKklOdhYR3qX/
1R4/Ffpfc63bhOtv8tKORQthBpPatCr+C3oUY+CRqwECcR7ioisgBUWMqD6uD+VEfjs064h/gEXA
IR6orCQGp14jOwQSgorZV1x4Ak4IaqZSn0AnxsAwpeJjdhx0FmXiMaILUmnGd95i3klNO3ES+prS
QdsIkbFD84a567Z67AnIIAOXs+enRH4/kiqFxB7AY+ocuK5ure22veek8gnsKkWb3+GLeivqFEnO
DYIMqxs/lS1au3NeIa6OAzDgAiCajd+iBjJTMVjpva8dNxUfwg3D5wSeEtjbdieFV5HizzuFrvKQ
imD30/Kw1uTo7rkAGJKKUsQ7Sdds+FvuyRB56iXWyISRszVsUR2t8nXlm2L2XT2PHqcEBsw/5ldJ
CuDADMN7Q4rXQFbUAMeBGgw4kI+p0cj5U/0BjBbnQLUcd/gaY2EowheU+m7VGCDEn17OtlFjkngh
zL5b22TptASfC0toTxvqJKkUgh6EPQIfVwMt3S55EhYzvRZ4IVCASSQzr2PnYpJaQK7FZglEr0fK
dEHuXMbyd9GO/UBShvEDHCgGcNeszT2RuIoHUifkTUtzYYqjnUeReAfE1dHMdBGjlQ67Ns0MSmlV
4NdBsl/udHo1idYTAsYdNNqnXugdg6khv17SZEhUqIyvOcH2THMGNAgtcKmL2tPASHSBBnr5MDe7
NMlHMggeklF4cDC2RwRxM3R0REtSy0DCNCu3/1eBQIGtSYQ9yZkV91AUzdqR2sPNRhatqi5CIf6U
mYyCMLCkUtWwjTxJHmM+Vy6RYtQwJCY55VTQdpyOkAUNQqzNYa6UdCB/i14t3Qz4HKeRsBf0HeXD
GM4rJtl1OOo6W7vjj/MCuNS3680Ucy4wOgM8mT9Uw4soLpRnv+QSTKNpXKh7/UbauqhOM8Ijo3Ct
D/xUHkN0kC5Cw3rVMzc9/ptZ1L6Q25ndDW7DeU9eR321XJzVip4reVGWCDA/xARrinJNXr5Vz8eO
lRya4JDkXI058Q63CW8bED3YRVqO7GA0wpNEosH+cafdowm5I7yUuSD27Q2Jesq/BEGaqq7h9hQL
SHvM0BeOx6ANqBntAjZsYFb1Mu5/rguX7o531g4neA7zzJ4VzN4Vn88wLUkZ8yalbCG4HR0Lp6SU
MFv13PZgnRIUvrU79gP/kHf6l4DVXq5tUej7z4vHzFLrkyaDVDP8V/88N9tdp4QKy4cw5UkV6WaQ
O3j7AZfKfcqew2LaVDcpLd+rNY0mEUe5aFT3SIhBRPjhi2+c3tNvgSS32p8ONeSI9kmFQ9UMb0qE
GCgFBFJs6JA26BC+rm3c5BRsaLw2rDQk9FKa+Hqpxo+ygfvtbCieT4VzGh1KrM+M1TX+0BDjTZZO
eplG+nI5UKZabLA4rkm2D0zy1ytwDBpsJNoIbR4zElNBSjNfk3o3HcZ0Oq8UfWwbTYP48MidrA4u
u0MJlw+DzDxvmSQL3nvuCy0WUYwOocFoePqM+ra9iolb2DWruzpEXba5ERmg1larcDeLXKAH7vkq
Mvzl86awFt6019MBHXy4kG739cASuSwUBU8JAXo7COFeXOXcFNl7PpUXdZUhgjalGFeWIzibpSzA
3qRbeCuuaAlD1EWkZU9vRU0/YJmFEFK3Ig76+d4PWEk3k0jBxYc9Mn8oTsBoh9PeEyRyLK/mDbnK
YCVXWugiX5AuVKdYEVitpZHGNi78OYWArdnweJ84SUB2LeNqgFaVnPJjou2m4lLHJK/0gHWHcxqG
bIrh5tYXow8oRNP8o662QFkXaPs1A5LK6TK1TlpZ5dA6kuYf5MoDjqJQ4yHTKZ952/D+of24NBMW
JvJOLoEGtKq6qnJb/RQJHQ8Pp5x0iCVXo7Q76yyhJkg39If+0OtJ2WPhKebz4b8IhvJP+63jmEjZ
YN15rrEi66hfnS9Go6OM7KrbEkmgcs5Uy5/eDUHr6na88+UQy8T/jSTznd7AQBZsLEUpcjeQHKwM
SiAhmSRoi1lukMVhZH8/v9yAlkMVL0P1LPBIvM86Y3DnJk9XyzF1MCPee8VZ6N8ceKEoDVMObJp5
I91ISPvz43I/mEyFI6cXqseEsJRh/ZZyhgEWVNu6SNLb00MnuXukyujEZRtDvqDm8dC7+zNAc6ge
WnVV1dnO8YdlOj0bCA821k7tBAD58ctntaOBM9ZnedvKHbDY4+WH9EN1CCKYhXiC0JahrbCBxMB0
Hh2D2Q+gd0FKPfdwgD22qVaPkUgGw/hkObfN/FwOx5z8FmXCeoIJkj8UoSiy8u4ZNY5yjrdrOk2e
uZvJZXJZ9E0stHdgXNoBWCagt0b3ooJRIDURODab0Re3Tzq++xBlrN7rQDWzMJBPNEilWAxAvh3L
KkXlPiEL6nm//spKxAl4stjrgqpRP6yWREWDu8IVfpOpbJrlVrJup+bZ8BgRhD7QX9J1caGmy6H1
IEMIOQPHGSMGb8yLuPl1sN2CZxuJ6mlPtyD3M09vn6/soHKtrwrIFWy+Ri3aFfUkNurV3MXl30QU
MwQAOeqYV0RDR+jusjXwGmAw7EBf/97ZRAqi20//5M/sRr8xIAhin4Au5ZWcdbI2INP4feJRCiKt
2ms18RFAAfayK7D8HRLvzPZr3gQb3IHOJWvuKw3KCXp3NcVmIvpGnC2lOTLRsWKQwrNBP6UXGl8M
srk14T2YbhTf/GUUCDFnFuMEamCbDbQO7fueaZc3UWGrdf0DfgMrkW4Xim9SGfpdRqJQCiJH1oJb
uNAvgFHXWjE5LmeNxtOaazCo6QeUgNmzVDx4/QBc0i5GXmVmZ8KUER6f31c8YlJyCoyEaQDNDx/k
NwlPizDLXkerVBeY213AzWUhtZ9jGjEqKFtLmMxBiYO6tRjFkEikXUNVpeeXuzyYSeHCIcJx04yh
L02WGKp8ek3JvpC/ipgVnpUnqETbTpUJ4mCGva7VwC0hgf5ld2+kQuIzl7qvXqtmZw1Qoav1tCln
w9npTJqmYIEYeKxMaEFYaeLdpV/b/BQAEnRXh5s5TJ9hzFnkgS1NEnM2Lx2fMd5oaSwd8l1naV4A
+EB125NZnghVDjoYvlXFsarmKoWfgipBJZIXW6FBRwgG3EHY1eTTr+NKDB2UcDn1TNPy+a0sUJsn
C9BD1Nu+j2+31ll7b3G9wkTDL6zTipHt1140+DC5L7jrcsSSMWHBA9yF497uqJLxIKEMpo2OWUEd
kWie5+TVb8vCay2li9jm9hNd/I3Ryq9EZIJTDZqNcO3M5PfUVExLP7bcS6JLniCa5amV/3CM4cqo
4G86r+lfWUZO7iUySn8+UZPkRx32YcZxy1lRvo8HzZpa9e5JLj6SJxE+FWOmNCC8H6n+vANsipGj
Al9OfVxJRlVTpc4TjkZsigQVxnJaNifubt0rj0ickmlV69hMpxZC0zX3Y+TbBzGjz9t44WoQx7Me
qZOJKupf2aHtralQYI+b+m4F5WWM5693aE17Ugx8ZK03tEONOHl2XHs4qLlHi3HLzkD2+Wp5ZPM7
0PIE/Af+rywdcw9RAmV8v8kkbh3wz9PMH/xaWNZLcD2Dw7BNIdKiR8B6uRSLvJ3zuQ6ert2XGRRp
8CgWWy91roEbQ5qbtiLNOVu/LVMc3jNkIHiWgvjfuBr7WamNQH9vRIsmQBqrMeYgdAeEvHH3H9al
z6qeawGnr+0Rd9EwWqaPoQrmz1ODHKT1O3H1rY6AXxnHvtp1hsmIOo9hma0pCUhggbGV06AChXl9
leDiTWjUlvyfuYR+05TroIAARWRp1+ZLBU9f8P4GdTXo8DM+n8v+gB6veiOiDrtBppDLCBQfVx58
4weIbnsCyUxlPL2RbZmfIC6+/yW/BCoQ4YJvFP91duhzmehSBdCQgSf3tJMIln4BKhZqgPaZsgr4
X7meApbEmAjcHcJDFB5h4wA5T8/YqKmdJl0dAopROBXB5n9Wdokn9HTQGDJdaCbuOLxhhdur2ZM6
3C+3LKWHuJTngsVb6BywvDMv+8fcrWTLNF+jvUXEDnSlZNQa51zqdo9fdbdo6zixa4qdrZiEYvUa
1HpcW/4xtlEPr9Mf5g5MHEs1UhgHdYKGdgVqLgOv6bO8h0xnUfnGCMUfwWIsUZr4sXIw9IokYb9m
kt6FHRp6REaa03ZiE7F0h3ITbKcwO6v1jRz4OUMtkbN53JZz4Ybb7gbI4O3RYlRxXGxaTklMCaHR
i8WDmxf6n2DpP7gbewOtUKSv+TKvKsGh6Ms+hQ+B4UFPlOhNlDDMFCZ1D73f14nC7/B/VNdXjvqV
k/esTFsABOkVbejCIjPAGTtCKWkRwqkgOSE0vvkeZCs5/HFE+0f+sjMtBVD9lkekgNjqwmzlQj6e
BJzAK6veUmL24RYW1CfFGRNvS7BAU5QPcDYvkMqCegrBr76VRy8ZZEktyAzRi/gnmwVeQNAWmtqR
MT86hS+RzzkLkhikkCgL6ZNk23zLy6H/BsI+ja6sHl4x7IJMxC5RkxmT7G0my3gw39i5BBxherSJ
7nMVRkCs0X/S4t5rjUKHNGSDeuZiWP86+wOTsPXMYliCdj30eg+aUTIynaBFy72zYEPbPMwmGnsi
akxxXOFrF+4ubq7Adm7i9ggEPxmKwqt1mwrTOO6QmNQAO76yA9cseezyNylLAGLr+kQE9dw/oZjC
QnGw1gP76qnmZuBvGT/cRzVLhCRsiCs2NMd72X2afwQ+j+r8C0zy6bIOzFoX+6OFqQ0z7ubBmJTv
2cGS1EJcz0mSqKe50zxGqgxThO9gBS2mUv/GrHnhIkSoyxfWX5NPBY3csobnC236YHNmWev10Zp1
yYI6gTPIZtq7xH5XinekYEpc0oKR4BF2pkvxcf5QVgRMaCafq+XWV/b9Re7T1rU31BorqhfqtmLY
WF35Dpsiwbe9Rx0nw7rC4nCiEGaSmB98X0SZQ9DELqzO+yVQet+yyBAvuv8skjUbKG3vzZOFODrJ
KagW7ONqwTNy/plm9o2XhPICUklYnBVb20luKrqrPLL9pNdVkNQQ0A3Z6p/YWX9Sqy3RS7GMW7fK
C/mXxqm0+geLKt4YPoqOZP/e7VbYLf+jSY5SdlfX8DAtorJmgSBW6t7Xk01YFGGHIP8ja9sY+Ahe
/leScnzWe2Kg+ijFLox+NgZdiYXsbBmV+ZhtAo0qinMridS3SujCJM6IKdozgxOtxnWDJQ0vO5tD
nBuQgSbJ0h8b75DSc1JJJReJVABuslkR1+6ZL0ANFsiZRbE2so2pRLMkgdeiiGOiqlK+2RF6Bar9
9eF3cv4gS/HgVkxLZEBiQwjpVYCu/0p6Oi3cUpRJnuEWBs2dpXD2hBns2/avGbvBXunVCLNy+1y+
zAaNksG4h34utoLL5j5W8/W/uLOGA/ZJlISAOwxgV9N5cODK/gB8dxOQ11Jqxoa6iHO35N+6HSVL
5gMA5NT7m/+TQEx3ptMKhMdbZxjMxW4WpmGltmT+7BqHwSlgOwszAlIn35OAkg63h7yiJCfkCPhR
qTHNik1cOg3i3TAEz5MEXsfYamK4M3FVznCDRDm1u3Hvnk/20LxFM2h1MAtuyLKVKPbURSdCyMKV
X77OS3M89GXt7vIHXllAnMPYpMKY8F7ut9g00MOdtexUUHqRiFR01uzUezCyRpx/p6+jze5No0xK
yZns6vXni+U4HE5PyUmIadno9I3Wfnvp7n2kexRI3lpfYkAWfdPlFq69Fmj5THR3bbd22Ior7Vvr
qWrNvXR5pOcVE7rHCDYbMPj9i+7flp9XHWFT2Tod88u8Mzdd4oNJOnC6gsMQNbUNJeLeIydeSJ5E
nFjmvbvSDpBeVrGR7N8R6ao4B6+PQsCIBgZmbzHsMzJZ7CIC2cz0ZSdAfMXwVlvyHTM8nU970v5m
oHuCLhcusQ6EZxFZe7MKd3o1LzgUarygOBKgHJrfITWzYXicqDWnBIfnaLSD3qhFTWc1D+Y8XUs1
wm2Z655Uy/ilH+Bd1lnM5SwfbZwIvnR8tNRk1+zksIXZCi/igRf0eErNdCTARnEfy3aWijLiUgKl
TRetRRFnr4ZvAauIQ3dckKqDP5tnP73NJ/SxeEQT2rEGUtX1XNotwJ8+7xtfFN0S683TdYPd4+S+
IsHxLX+mxSIOhA6jQHdJ2Nmlch1HVpt8TwbkGY6fHK1SvuD+QodPK4aVZ6l9LoyML60azmXaJch6
O+zEHVRPNxqiGuoalzzv3jK4gF9M3H2rvQiavxn6Q4NtDeLqXni5qkkIpzSvGymHJOaUxZ9rPQge
w0wM0oRH/86PLZqvcmYgcH1swe/XcL5vcYOlQKWPtSdm+smJrChY/HJkZwoAtQgh0R9hnmVWoRFL
UpRFm3q6Znanlg+GJ/Gtfb/IauCdk6oYHGjzpLFGanvl1602zBfu3Ej6wDE17Ud+NpF5LTRHX18S
uJyPpZFHrymz7nUcJAh1mI6H8Ay9ilmYes7z2iKklWvqKsVGc13bgVL5fC7cjUQhz005kXDcNfb6
rS4JPQlpCbeTri4WLsKN1FtoEUv90h3f6TkEL0jGP7mrdafba6n9BoICDk9HRMNN6q9Fmf0mDpvq
oCbrykykc6N+6FiKAaZT3VFernBTIZjGR9TQih/Nl/Id3oNb415t4gcAouxX6PW7D5YU0FqR2s+E
I1xqNpaeQ0lh4P6PGcmZJoEE2xYlYDgWUbx5zmAh2o93fAJn2wsZPcWgFFmiq0mCkSx2oq3ZK3w4
jCkZMtEBAQB5AH7rYW6/DEruzrE4t1VjM+6wb8+M0UH6gZFncw8HFZB6DCwsmXpoQbhxW7GlpEam
6Ufde/5ToGHlUNcgt0GpzaUa+cpytafx3tsFGXJEoXP8QaN7kQP4dXK4+lhAu6l2O/ygRmaUzX7a
mv2Csh3HWyNBGKm6fkX3ZDxetNdfwF79hxBK/aKJQrm6UObomToIkUQd3j3iNij3gBlwhWfXdV4k
OL/UQ7jBoxo/RkDiP6ldan2u3Wi7zGIvU2GNuv8h4j529kursX9nbqxJP3EKs1T6xNHsCVjN7S8M
KlOCw00guhI=
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
