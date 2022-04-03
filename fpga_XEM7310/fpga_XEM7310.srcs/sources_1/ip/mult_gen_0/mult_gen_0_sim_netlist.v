// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.2 (win64) Build 2258646 Thu Jun 14 20:03:12 MDT 2018
// Date        : Sat Apr  2 14:38:59 2022
// Host        : FDC212-00 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim {C:/Users/stro4149/OneDrive - University of St. Thomas/Research
//               Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_sim_netlist.v}
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
Fb9e4Z06ECeSxP0S8+TUSpf9DxioNCQ75eRX5HaeDRMhmSM6UYjuqch+AzvrZPqU41dCJBwuCZfK
BP9PHHxSE9FQp8hOZ0EvF440tICQAJ15bnJ4iNlETtZnSZqqTznBpp7FabuT5VtV9fEYu1XzXso3
yUKmBdXkkub5CvFYLXkEsvYjARhJbNit15VTZD/kxYKJFUe4nK9F2yXEzp25FGya2hFkgRcI1S1p
lOSCZ5WGjWhGWXfqFPa8ac3/pKjXNQz3QlYT2QCBHOUqZahFSPKJrj/aLpGUKwnYvBqZCreSTUb3
1qcaQ16ZKN7yz4xnjwpdxXSJF2poNFc+H2AzOA==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
X7gxuHlUKRONO2REyP5nRzil+FcR1Ljz1zetygNGXIIMEcWBYVrkKxAqJ3rNljP8X1Qj1qBppz81
GAqpLRWxEqD+HVp0irVtw0D5BJOOkSzduCpqv9XHeOHDt/FpfFelYenvk3bsmxIA6X1gn0MREXSB
zq2rTJ1B7sGgoQT/WtRXEhjXAq/EdV0Ae0+3FUUBpqp9gFOMAaGRjj3fWLUxHXI0heMrz6JN/E07
yywe1PhdO2jXKZ/0MPBYLTh/HJZeWnW4bCAkub3qRsRsIFayUSjmurZTiD5KmLEfNFo3nZNsr9Ct
KfDIEaz8yR5yeHqriualkQA/hIpcCUhLoPY4ug==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 14144)
`pragma protect data_block
eWV7kMGOdxoWkOnwAd/FKh+r5unHsGSjG2vaa/+bbiy/wIGU2tyC5yE8ReQ4N7dOHuAwibNzGTIT
koEh0IDjSna0Ly/dS7EKkmzkmLXEo1z+3z3oxbP+eCZC8JM2aYsN+fHVrxBnGXobA+Au30l/U4NE
Er6v3z5nrzrLoCandeTKF5d6xmPjmVhAeXM1K4LCPQxhn5eZ7GvIQrbenX/UYJrQ6G6s/dYyW+6f
kRvpBXo96E5OY64RmiYyktcsCtouk9eJXasnz68ddJPojiiCUBb70LKsP8ZNO6RRW42Gws+w+Glp
2fGf9WTFAB56vBS0r0GgPYuoexoBQUmhw6xNizA6cgfLEwk4FC7KnSuvDIp9CBgGRhP464DB9JA0
sND+wvnpPkZuqEY90wLSfWKJSxxf3K/osOnkpOrPJ88R2xMqg5XnIYCXJK8l+0FyVX75c0kU9Cwc
B89J+AVAcPoWg2qTB1DTAK/edllsO8AnUK56cK+9x84PDkM/BKEZGWfler7CgmeXnmbUpMQ5L5+q
kj47Yr4reGadpkpWMOsNQZyXnuVkcjSW8lTWcoelyxLTLYsBiHitMdKdwNBJxhYAoCsuQOQlRRlY
SZVxnYMa5mTrFH9yXmXOdBrn5hpxhk3tC8SFAFsrQaatkzwSK7IckdgjbJ24vPG3DLhWlrrc4Sl9
WCvb5ROB3bxbeQKv/odgTOooapRN7jwQW02iWJrzSh12WdAab7NHvj4shLjOFZFICP8x3ZMAdpEr
JfqrjBJu3XvX1M2YLsK8nznuMm27Wu9pAu7dYPFO0LbvBqXa5zeTKhgcpSHQz51xGdNRsy7L5SQm
fGhqgqYfcbpe3p1nLBOcGx11oZAOr+QBd4lhknDvW1qT8qyXBWmPTX9iJDZnrKHekiAGDDI5J4aB
aZquLi34hAZNVeFeKIpJL0uQaPGTGAMBuA7NoO7z6EDQTIexRNqmX9nEDw6dWvl3Hf3rJF7oOvuG
PMCQp8POtJnFp5j3QdzbmVr5mQWIJhpJPNJJZur8vbiQhjQyLkEPSlTL5ur7OXkVpPLaB/6MAur8
OknXuoQcS9qU43zgiIrctRNvYVTjv9+dXA2bxbZwhvEoiZO8hF+VD3CfMkEUTx7vR+2LVtKAPQ1n
WGgnEtYhVjhAwOeQ5t28x1WO/wKQ8KjV48vJNa/baLl8BSA/GzNWo8hGnYoCSA+icSG6wZ/bDIFG
p8JwTe9fNFNpfsYQae2mz0DowJifBM1OfbrtzFCM4J66kRdtnQkMMRn8I+ZVqIw30tt477E+Un/N
88gC+5/PqyP+I6OEa+fiYSH0jPW2VtJNxoQNNaet5vd8douEB7KQTg2xzDDkcT1gyXIUxVah+qAH
43Tqn4uIcB8XHwsK0YxLyLjfQ1nNeaBeGOulpWg8/crYYlRwPV39woA2n7ugfodIWB0rwq98LSb2
MBcAMRs0xaYPtdrNwUlii012XnaB4lynBeYE5vdqZTP2OzlFiJy8bvUuYW2jr5bUDtPwPXu70j5f
Dxb+X8/4ga7J+xy5Vku7ulFYwq6hG5+LQZHdoVE+LB2BNKjqFJomhgHNefrg9iNwXAKR4EjXfD+0
eWHnl/LERiaq2cJXMeivvP63IHl519cYDT0ejZjAyUVqUm/yMqMNifywyDQw208kYXCo+VUiI9F6
KbRQehUE7Mt+Z8IsqOemBCWFDjrbCpenLmGdRzoKrjlEH+xN/+EDK/hb5kH4nFXbXp/J4bgfUEr5
EfVEqMhvxn3Qzc5pgu2EV8es6Kuk6OeY9P41OLPNpC5D6jOFakN3IHGRY5fWHYAI5TiahxA3dVKk
wW684kZHvHkswpiNHmLy42nuKpupdDedZ+UDDeiho0nHuxQPdtwrRchkZq9r12TwhSUvTZcXYMnU
1eEhZRudbtKCyT0ZYEUH6a9ExPtTKVP07XNLPetwUX9kVwXggtzR8lVBnaNkiMJwC/EOMdBXISnQ
k365B8+LILsOH1BkMwc3XpouzwHYFcn9H+Kd/eBufEDbg16EciyPWgNb/AMEqsnicDZgsYVi3/Jh
ZZz0zyr20O0N6i81Mdo+k6UlLyERCs3fpv8Cv28SqS0JPQgvJxAMY/9N8r0Om3v/Rrnci0Yvn7oe
Y29mhvb9EjyrxnEwV6oYqNQaf4djEZ5Dk3NjydLI94ihMasmGfn1Zskmasas3EseRrWBq+dX5NgP
ZnL49msSL7+JnNrZe9x8SHYYtCWyIZSSe2nDCeGtiRME+Wc2rOzxBp2o1VbotUb2LUlKmi7jJXoe
n24x+nw43/IWb39L+LzEzNL2UpdkKLgd/BK11Aj72HiDTqmYiz7Qjdg64D095nhTHLbbigyZBDmx
yl3ZiQShg6hWLppgtCtci1p/ITGbg1LVk+OD54jaBlNi1yEzOEPJn9mp9FHUbwcsV5tiN6kyE3Vl
hIKF28jX3VninRX9tL5EzA4MNrBWrg3J3eBXgbujdF3qtYScl1CN8R/0ARuZIZmWfoBMCb5MECsk
QHQeqdvQHkx2F7a3vTAuMG0/WQP2PacYDyTTFxgi/APWuoozmhoPijAFz2tD+6XRm2IzW9EpAqnt
67EXOEyNiVcweFpq6T673OIgLVfKyGdMQ6v+fhqq3c1ni+/q7T6eYN7K4N1CESYqpw5G9V0OVj+A
C+xtLiBg673xdpl+axA6P/qfU9bC3kLgH0KFh6nOyMG/cYcPSLaSrZWFQqoSqWG78/tdZZykvU+4
eagc6YpevQJ/5XVspV1UlmctZHphYtL8rHQvJXTlmlyUoGwk97F2Zt8rKAA8TErZjRLX2IqA6Y6C
hAYQN84wFaM3JrLSiAAPeuAtf3J4zkTij35DxINDVbUXX/RMkC0SVgivlsBeQtDFhAmZm1W+07RQ
7U7a6E1yvkIUwuysTMnvgBAyGtIBTEvbatUZ/90ayR6xGfowMX2UQT4o6CHEzWStrRqxyWxa8tJ6
2JdncTCJDHT17EcOFe3piQJHB4t+4Hy/TpD7M7g+lPcM2AiTFdJ2dIxgnPjPBqGgVrsOhU9RN1vo
qSOUO5sOCjKhtqZqwQCy37+I+u8CDm9vuk3tlWPOK8GKRDrCQh/YTT5h3XctjpMuwr90XmkZapVP
7+JhkXjgxdk/PqYIsIC8yZVUiG8QuH5AcfjmBetFeqJRRiQD79qaqmbMt4+gtxyxtMtR6FmHdxsE
EAtes335O9x2/8/amq3HU0dhC4jPql2+kidCZRfoDYYjeKCGJrOy+4unND7n7V+LA98SaEEKkVjc
0ukdRPzZzuhcfyEjXE1FVs+eik+x+PL15MI54jmRn5AJDAYITyg/h4HhLAOGdSIjNlJlibMaMLEi
VMCi0Kek9E9EbPUwU8kqVPoI3/IG5+Gu1nQm9NiosjKUmKDQ2Rdvt5KsShwQnxPTTY8ascdTCwDz
/7V+GOmgDhuXzmXHaBzJP2srEySdIlZr50EYEmjteQfxStohV/ffR5bfEOwk2Fgr6VEDaV8s9iCE
UY6yAbDPCJdTvEA72Eb/DxzeNAxxURJC2LFYGznfrtO/456ZHf3K+3LFZnrdx3BM3fBG1nT9GpLR
xWQ5moDWDCOZ4p/+EL2kPvqYoe+u+dLYEOfbpMbtnHifqsmOxPfIEPOICJBo9n3TDEcGs8lf8DKb
9YIAfDDdvXeELUL+2lT7GqlWgZTEBDN8NgPf3ZW/E5/Qw5/7HY2YltyTos2zg2cZH0GVoP9RLQdO
ktnQ2It03IylZ4VTPoeXnbjmlLodRb0rxvvmOOHT9mER+H0dAS7NzTeVdxAfG2ENttdVqxG0x2f2
dejuLHYFgJA6l3fVUDaaLqkznIUMMcEOG+/mwLOPmBiiR4iT/Py2vSUsiLJsB4HjF8hmb5ovQzlz
dnjbPPb0FUk0ywVXHvFXLkyIVuwI+jw7TqDANXx1aR7w7UyW2lNhe2/t2jtM1WEB6GyhkKqGRRge
7epXfbsnLTPUznsk6GX0xrWfhT3A3vV1yICVI3hNM4V8bkmF6TPrslWwMqlUilj8UDOss6gHJi3A
t0XmcJv6KpihjbG/NNipIOd5UzwUUPIXpeEMJjT5eAp5ihp4TTdXBqFMDhnvyE99FverA1YEKUvI
27eOU95htnNjYCqAuyqqASfu7R2PzsBNab7JjVnZO6i3QozmN2qzpU52ZVkguR9xyT2f5LXmQcw2
BMHXJODq0bECVg762hj6GcUdqDCIvKtAVzgso/g9Z7EJaiQ/Jy1h8G/HfbmkANfsfHlkyc4NLWJA
QdeUDX7+dj/DRxBHLDuYWtqYGALXPSaz/MLysAZnanBLM2Yob0yqQt08LVRhEranZHTWvdbnCSEL
sFZcsIRGyYhy7CVKehySvBUhWgJMwzadmHz88UBUbletnW8ykgGYq+RYilWLUTXT6diLToyb+jOZ
29TP1HN337g87QXPUkht8DjLDfzMhbCf9IOWECsVuCB+3VcQ6N104RBxryCfNK1afTKEotrX9hCL
WnJFF2Kf7acgocu3KWzuC0eYW9WFo5zUfI7ZMnm2otZNfGDM2jvrljcURg/l9MnWAbGJmrzv2aaN
R4kCro6RwpJ1CTkieBFHykTIzXedpGLgUkmqNyf6IDgSt1PAEo/KoRmmx/myk1LsBx25t4Acf7O7
vguK6ZXEX6blMKWWIMJoKt1HKSomGHegiNisHmzR+1rGCexSLPR7Ubik5S+6bbnXnLLb5okQmxRb
jMS15OegoIjyMaxSEFZ0Q2BQc/2+yqxh+9kur0DZkGuSiM1dw+36dV3L5hhqiplmIjgD4bYysM+b
xzYP/fO2VUFzhxn7rHPK1JHlnt6Fvfbg7hmvkLna9jzEpKq/cakiN6kJK9ydsoYHMaA4Wt+EiV5f
1hRk3qwS4XRxsDXxGqQTzBZzO09hPAQq02TNE+nOOBx45AE+fv73hpBud/PtaA4h2ZlMrU4yabJs
hW6PQ5wMP9EeJDAV8M3rWiuMvFXH0Rv4r9SliCvwHBfPfIlSs+O7pwbXyCw6WCKngJgj7KEKEp0W
G4KBEwe19UNEBk26dWk1ggZTaDrOrrWzUiweU47lcbKjXZ1QVrABEXpgM0o8INQ3Q6QnTkle7Voo
oWlqeEtcSyJD+UYeKRtTXU9SrN2yVPiyXXU5EHxKgNSVgmRwWlHMwMyxvSEyE0EgE87ba1je/AU6
+zYcFwon+zvRhNReEVYaKxyN/aI93qZBLNOcCHgxI3fEyX1a5/jXlzVXrq9YkrzdxR6tsF8T2jo/
kgFhrbN8UGgqXuCMCpeoIBq9t0/c0GfE4SdTJH6tzOxq58R2jI4QZM52eu/9P5vTa6JtVBe8SZo0
CAmgFdA/D15ZpCbguqNRCOkz6YkWaFmZZ1ckr1omHQDoIwGTcCNJvAZsxzOMwdfxcFM/TW4eNGAz
1YC9orxge0SIbN/Uiw47/1KfJFGvHaSUfxiF3ifj1jetNS6vbNjL1vjmnoGJZzWl7oGaoUdGuGI4
fY52wJG2SosglXSGvfkBRcmFSNfzkmtrSZ4okC0ddFgyrvaBV9mPEaZmjPm2AXGr11WitOX0M+0z
vXyjpWwIjdQz2V9JONKyCZAczwu+YoVZOq9Q7lQAtWc7PIwhviDJKuf2J79TntP6i9tjH+XAl8XR
67uYHSPq4FfbIpHNnUdzoX2wN4/mEsh0UXlY7jpb/wPBZxF7RPO82ECZ0coHmBCu5BlEdrETy5FE
ZhGrAjtuGDqYz5AbStG2gaiMNOb0jsAT95u5iUc/hHQkEdMgw1oSiyEIDp4TBXq0XbF4smi/Ab7p
fyusJU3h2/lTC/j/8FHm1bMTTXuNweXun6EcN1SSUoWJh61/NE/uf+v/McMc3B+3qzVEi8HqKpQg
rVEIFs44nHlZa7CwGnIwe6/5NueoncXaykOCfSAjCNDET1G1b/Wg0zcz71Iz1/8RAkHbBiiYW17U
pMF4MNKBXPeZz/yTHcjXsIOBgTRU/n/8S0Elsoaas/xYsY9XELtnk7TTibYSHUGTvqkr+0pvWnfj
vSKwOIgn+9hedYuGWnqFxNik8dCFXPj3hctmBGaDAGe+VTL9W1ksIaHUKDP8qP0QiZ5qUNlhyBEd
ZBT+adB56JxDTe+1qs9vScPtxCTHrAfcsaZ2OBopnljHX/x79QaDmjjUATVodRnnoCu53LNDxlzF
S+YyiqtQGoLFOuNXt5alAHGLcfC5imiOqhUbs6dyiK/mn76HMe3NQFt17H/JFHtWvr1ROV9kt8l8
cPbEXbAnT6D6Kf9HdtvrY7GuuhAlSexntMuLs4tdbNYmRmJq/TrzDX2e1olPXd435xMX71Ho7FPg
YiKUfrS4Z7G96SXvBaf06bs2AAxl9wPmZud114PDUw1CHzBHRJNUsaVAYHzUimOHCA7NFpXJ0oTM
GIBVBmdLgdpP25DmwUZc+f5cAexa4+0UpnJPFTdthCpjrN3xfYPaazr5YghEgFcWVBmLzF5tmOqn
OT3cTdFPChMEJLMCaHeF5r051M8AziFCOjPu52u9ZyfeGK+VQxBMV9kWmGtAzyiLBtrhy0qNLOX+
9l17oLNfBOmFnM2HQ5NgOHqbYaoJysT12E4HdlkOjAovelyK0XqUa03EypQrxxT6YMh+5TVssdBM
qXK24IcXRWh7C//wkhfiCOnomipo2OjPVIQRs3plj3n88Jz1SMwXPhHdbHHqw/6vt/8yXOTQYBl1
wr7OFOrFZNn2GMWgsKtBK9TkFh89UjP263B9X96xVIbqFQgniqaqPNGA4rUW/lEUQOX1UnGoVNsa
XurhU+CQE3cbO6ed9+TTxcsVRd2bbdHYmYr/0OV7LTKu1jQkA1vhYYybQ0GzM644OAK3uRlZwdWL
T+0rAr1eSbYLewrTdCvPfq0IVwUp86KkhBIUnxrTTT4UL1G75FqB1cfMOH/5VSeOqCI6lT3fA0qL
AGhXsCsi9b5G/4cT7gDjRjHc8MrrJ4OA7gaX5MyqVg/MbVggO7KWpT9N2/SLRcgwrauO8Bf3enax
7mI1s83DsURgNzQpxV7MkvXrAeodyatTTgd6Ikceg9VYgu6Cq7RUMkUXj15J9cNTDxnz5RMeRjDQ
r3EQVcesft7yZpaeUu5ETrotHN6w1+XwP/b6w4YWKVv3s1d19W4NWbRVWab7ZUCeL+cEnIzG13jy
TDvnGojvLe96wKqMB28I6FUC4ghs6Y5RSdJDkOngQdDhGNlf4f9FJNanlJ0j0Awf7MaZN5oc7ArO
UMpyZ4hU2T8ZJxRL2h+y+O/oGkmwWdpo8xFaWqw9QBLjtQp33M8XxP3YcQWTZqmWxx/8AYQs0abZ
+RkA28RBy2PCPTx6SAvAmrZk1vg6XtHHQN63ONYbueBaoSEnQHRxZsH/A0WDUGhR/8AziWSvE6Nf
Ml1azMiO6HaU+4yb2+bLsd4hwy5U09c8JSnt69s6TnDTpfDqcIK1Gd8snmjjCVXgEPobT0Uf7L7N
3Z0WYgdTytCwx8Jl73ajRvAphYQ4q9CHubr/pdghIDEpYmSUOayLVTZl8Bz7Ee8lLSdkYLq+9az/
oXW+jJwHMi9hNmqR8yyUOMP6QuBiljqRRmpG1SbcYfXX/qLp7q/2ImL1QCEL2VvYsPPpFQ5/Tu0l
eIuRdoSy8bb7T2vRkP3dgNRtEvkkKnc+hi4ZY4r6N3coyHWCR3lWUXvD5l310+5TKlKe8cchLdm6
Vu6p74uDXHCSpYWjmNN6z/UWW5jgRB8Y1+NW8XSljo5bEi//4XswLPzSkepPvjCk1sEmXAqkNKS4
rVLyC/o7n+4NlPCLwjk8Td/kq+nOsa2a2zNyQothYtm9Lxxxl0rX6S4afXLuJtQhw7UHQK8NMnNO
MJ52llxtkbfDLQmS2dq4ROsM0ZEmA2iDvVLOVKVZr4o5sAtZlr/OYWV+gc8QLQy0XHokJRHfWJFP
529qsbcFk30U/QrtUmG1ed9qTCRqBVbirsbQXpk320Jkl8/SmzbIZExbr8pWq6FwDR+kuBFOlwVs
3sKTT2MNO5l1tnFijG1lX7YScq/DWOUFzZ2uVTOrrVNe+//ZmcntocsGXGhu1HzVyY8lKOf9mCKq
zZbtlFmvMlYKnUAU+FPya+7gfqqVG4OFUvxVuz1JKOHIJABOZSGGWmr979si9Bep4IT+pLdr2R6+
5jLYlVKx+bgwXvbMapBRRzF9Zl+GHK7zxKBx4WtGPBN7Rn9nRCedGSoEVMWRzzMyoH+dWq5NTpSU
Gs6n9p9demmaYzV7renKhLK4ckackYBLn53u9D2R3mfwy9RSiqHtiYee1A17ekOQsfzXReaf2BEk
yi43bOLiZoMa8eL3s0m3ICDtmzBGRlxEhjqKpPXmV5FW4xRyK/z9MmCMAIt3RKFpQp6MsqmE7phs
/aBkeXwqt4VHHxjkyMjKcss0XdblbeNWx3qXyqiSf7zbC9u0lB43VTpYY2tmFj39S9WlJgnGpNG3
Z1kpvrb7Kpz8Z3pCikmnVzJCEwZZbS2KL8Jtc/gIV3YqlVpzJAb10xN/6QTjhsgvLXKp9GXFzPNV
ihRCZ6zhMigGFg7MHVdP57b3n8eZGUzCMkWiFOBgyAxPUzkKTGEw+CQD7RKvtKzPh7p8mzDlLlQZ
xq2AGPUs7evkcz7YhB34kTKwgtM8we0+wMhr/Q5GRlDbouXVV/8TkXx2cUyRrk31jhbUn7hY50de
993bq8rI3ksaJpFyFaiGrTOGyVY8mK8j0dr8x47lqHTVucsoTIAL0FyBkNlZPD/ytfLjze/4Q0dR
aFqQQXv/68r5BuTOFk6CGMTKlqZzpJJBjHgDPLT3xznTtuJ+Z0kscA9FPAe1Jl37PUw8zqaV5eB/
4d/QaKIi1wkIwNo/jMF1YOWk05Jgo2/nBokGSjkv0sKsgKtIo7rqhQogwert5fy4YbWNJoNVDRFf
3z32cP9nUcwh6Xfl3M61iOEQHQW8h5Tz/MQxfAz5O3u2+vBUlLneas1te6ja0ztlCl5mxHRvrHO4
mWIfWLTac2C3yh0ZjX75OGqC8kaMDg0bEJOlxECNXvaN1egfV1xKurozAEiGx0OUa3ntU05GZDPI
MZFfdyoTLu5iodUNWeb1HGrr6r/01eq3Q4DkbwvQ0URvdfJjEuASHLJf+NdfHVveRkoOk7dGA0+d
rPJMJ2hAVa1Ld7qci+IMK8PZeW5m0Wg1miwSXDPmfNac+lFdHLmFG8pfOHtqpAnEiX7zBcxIPeo6
moq0LI4gUvhxwADrFRtdwmppcjpYhjFKHRkJ1OhRX0RB9aLCZhkWw4zJfaExrlqZglTRFUzM/g/o
UkZNGnE+VQA69IVfY/hHbgaJz+jtx/6yW+Oap/KobwINWi+wqDlkccdxrFjLc3ILrBcpGCeFRT8v
J4ld7AqEy2JWy6Bg4ba+24dx7uu7PmW8iCAjO3z08Ec90Fyu95AkMYcC1QDL2OzG9t3kBefR2mNh
JvlSloxrZNCMPelHNbRZAu1j5EM09VMxLIeWWvruJ5ZWOKVuOkH1UYOw1YwUEYoRhbrst36wZjNQ
fk30o28EXc59YhlQCQEVC+iw4eahkZHRGUH0MJEm2792ol5Ga2JU29wug5rBDoV1HKCt9xUJ2O1c
3N7CKnJZpqss/WvW0zPq0vHPh57Sqz6U6YZnNwEBPC9WZRfPlLxeelxBzxEOTaSZbBDRmbDelS9W
iABNLygRn9Pu57MeTjw6FlprvUAGYZAU6ouoWzbCCRBT56GI0A08RYy0X07A73nr89tyxOPv8Kw7
vdVAazwT9vUDb2vhsmB+KFqPjESKTtyQbuKkOM/d2OGX7F7OroyB6ChGQ1SjCsEL6q+3SIfIF1FW
qhqqZRc8b7y1zyLAYEs+8qccLDM/2cGdcEu7azEHKkS30fJlL/+BXI2o7lj7THA3engrfvJTH1Lc
ROKujVCLlmmnCSRxPtNEr3IU7nVN+sKfhhUZXMyl6rppSXdv52RrEap2E/9+Ofooe/PIDv+ZeGkB
WePh27mJvH0ndQ43J9W64/LBg7GJKuL/e8syww6dotCWUH7s4v2zDsBjL+jwfCVlySDBpJPcr+EY
nDgRYS4hQDPmi4QrmsIVzxZls/0YzL01JPEBvTtGpRNOeX/Npks+KVLzAjs/qtU2MVxngSDzh1+/
cIZeNZU3/OCi/slrH1NJk3SEqrHcBRaPlwjq160tIFJlJR5J4Wusp3n+h61txT1qGCcuUHsDUqSN
064WI8HpoMlxpKapdHJZtpC5HvcBG8CRJILbKVMCG3hXkSKLl2t1ctMPyMpzgwm5nhrLJ6vhHUvx
dk0GrZ8e/PQHpxx1MJKl4YoQgwtC7owZGHMN3i/OxGg+EWwczuJc5goDUK4pmoVufY1AzgWoe49m
XjnooPe9m6NBUkSYfVEuDgyxjYvzAFrJFfPORz7ZsvounJH8uKkIIdg+KmPykbjI/+Nje7Mjemgc
XnwcI4bfUWKhyMzmWDz/snpJLeRJwTlLC0OPIYEZeygyj+ikRNFDpsAm1FK5mEyxk3uPWITqYnFe
loYxYmQiwAHnBdR8YALshPvv5nMD9rEXnVjy3MAJk9zsNzXVhZmpdYj5J16lJS5FMhK7MbvAWv4x
A2SREdcOCVhtle9h8UctWAmPGX6355s0AHt6e2j4ppylribUkm+8HCwWOdb9FdICirriEhTi8tFy
XOE6cSqCM+kzDYNEo6GWjuS18iUum9VO2q0xHMcel3tPqcLc3envh3ZHvxlKPtQWlDoU/P42OS3O
7cuR9K2XlC3Ho2KkQ6ZgjSrKkRtw8lQ/syKDEWOptiNdy5XvA1oWriCkEPMSr3oBR9Fc9r5PK1dX
NoqS0ImaGkapZ16sE2MpL4bgyf0vmf3GhKQh5R4GOrZBEjFkeC3MuggsZu9CTG7emfc7rYr5EqZ6
sk06E3gn9mTPxGPV8JFL7mHzBsGbwhNaKREVDu7I3gBnUNADZf9EnrdxPmAuRPn5vn2D8wT+Z2kc
Ec9rHtf3WEUN0DgBAmK+MZkFd4CPvYC+XL++xmpt1nKsnsPo5OJrubj1Cpb8eTHjn1sy9JGA9Aqo
XFZxQDtdj5DBK7Ld33rQWWVkBj46k2MTlJvt7SP9nHnaUCe/ae16hGfxznc/fJvdS6G40f90/jnh
f1Myk8ZxBb14kKFE+85CPzrhlHiOWwpUFIoYTt6KWtZc2QqUabxDkvBztA25nh9AVDZnzlJ7GcWl
LihuXJHtdogYJOgBVpmQT8nFU3Ah5Td/Bov8SHx7Q6YzF1dtJr7G/c/8lbj7Y6fXtQd6IiYT965K
V4KlcSX2x8Yz2a7PTQZi5SilLIJGDVCG+ZK0S+DdqQ8GxyIEp1hBQuM8m/9J4wSe4CAOgW328g9D
qN7xBI2svSTnUAxp8JvFKX7qn/6/MhzXQFcMdZKvYGuRZJXVxjDKy9nNq1kIHZpsY6cfFlf+OX05
1wCKxfRhqH89Fqcmj3DvysfeGnJnHaKut9xfsJIs2NEy3Rq+nDagna9RgAQhHsmOVkYGyGkt4zNt
8TSKyPOXR/HnQh8uoKtfCctCLKNC3+DJucoTUJh0QWyHpwiLo2054+elrsOb8/xrYfErAjJAkg2e
1iUsY9Aw7XoefJKi9FMk7L7DY/6JU+AZ1bGq7P5CWDrBsg5tSL4OUORPwSxRG66/gigHSAIB0Vdj
5umlOnPc7o+9QABNF/wkdNfpn3VyXd36+PbItQj23zp49S+UiRotxBIQeLxY2fm1jhAJhlbZ3cKd
uS0ddWQ56OZMTUpLOntnuZMTT8hv4/bGkjrwrX/A28X+yHj/HBlf9ASSRGR0Iwp/lAHsgK8BibSX
7cJm7rLMkfV6C6nhrnA8QjVykcDgZH1woqVoubenz5mfxcJ0K7XqI7YnuqJIgUkyQIzMADWHrs/z
A5zsQx514nZ58LuvCUjF8xC6w/vkbTHjEGCPtAPU+UJ+BMprc2YaoIKKVPTEBIVuKm53Kwieb2yd
QTDuGnlH4iF08h6VwB3qGbpuc2v+hV4y4+aFOxKHnVFOaWLGct+dDO6kAJQzQ13v+1VBwgAdaExm
/qs99Qi1WbqO108Nwz7hNJ0uY1zzA17KikfNyXF00ep7iPLj9iTtsSeeJJV91xGnLXQToiylrGRb
1+fmN0lGKSGPFmQ4seE9H3uFUmRGUYg2fxkF40FKHihRw4uogVityjkjQDgNeWaGjNH+x2FahPZE
uFkHsqA789Kdbo2PIEE8k9V4264rk2bYAjopu+vpes5lAbMktDHxs9eQzu6TADORnuFypJZJF1dI
kMlbS2NcogZ/7nd4e7LrAiGimrZCyrPD0UfxUbobhmC+4FUN5DUQQWzYDg468Qif82VfB3RaRhI3
rNs1955ViK6t/RW7EhD3km04gv627X0EdRaiOMrhQwZbFbmfyLZgxxVL7Zfu8qVtQuUTvJJYEy1K
quCZdbKqe9QiJJs7VWSTdQ1ELBvJyln9uhJ0IbMG1xOssRD56O6M4Oxmej6/Q3l2l9j6aGHSdODF
H11IfmjQyF0hf7WSY6447A833WUkJgHVfBpioQ1Shf3kepuYMIxXQqOF6cnu2ohTzlXJ2r5Gkfo3
Xnb8NsSJfxkWk3p1p8ULNwBjxRqp5746EzCPq/dopuD2Xno6EnNxetb/YyXCV3HMjlzP8Qb4lk7g
TjimvXGhilfb/0fcisCWy/QoDaaHakOp9b2dJ5zmmBKEOz88C2cZlVr8SxQsMkkA2GKVjfOMFKTt
4YM/H+z54n/cSWzHaR8L8gPxr328S96zmNXpzXFjIj1GTfGliobTJWAIeDuMxM1Cnmfm+bkJ71C7
dr3qXJidrrZ/6V+zemwXmb8WPc5ohkruwNxpZW0F/mP41kiD2hQFyyb5Dh8shsRLW/Sq1q5S9ASf
rzHGf7vGByJ6ukW9lNmHiCiKBXo5UNLXDTPvrGISZtPlj+nnNG1l2MNfEvd3z9/vVY9QWNx2E9QC
GE/d4Zf5V5zgbokNUZAH4G8GII1BZtnTkh0Kb9supjW6p2in75r8YAm+ea6fvBP38lhPb0Vieo51
8BCJzIeSZg80ERy3GPbaWD5iwjEYbCv4C5TUTAcyMcvDen5Ms7vsdaiTPc36uE46W9kPNzXAhq6W
tMCb9qSnz1Z2uHVz7la1qZf8plKWsKIBUKviQHEfjoBwjCzGGi5leAvrQ9GedPtBlqWGxZRHcHIH
lv6dPq7OG91z4TZqqpdIy8uLrIeJBMIjSWd+y2ocZs111Cohs3deVXFpYh5tJLTZHIis/4ee4oQt
aPa6xhvdZA5+qjvwjgNx+44t1MR5jdgC3XXjbkSAyjFngcXlgOxfh3zFUyESc9D4rlPXYBE+DE2R
EixzomPIEwdY9hpbnKp4RL788Vl+QjFNusEUi9JjUPNHV1dlYsADBcRcwyWQqSOy+9kwKj9I/oDL
A/J4jBjAnfkoO74wengjUD2uDMk6nOrj5F0YrknbW2aKH5d2ND88iL+8AC1Mm5oJfZ7Z7CGQhnqo
BEs74gXaVh4UBSbRFAhu3xn2nY4WKqvaOfEdbm4T1PlK7XhBoPprTJdCyFYD3N1NoLM0sO3uN6RL
G2dpf045V5OTDiiOFYaEqhKTqulNqC5ryF1LfkuoKb4BD3T3u0e2MxOYOuKBlqs2wcCZ8Jx0rfAB
rkaXyrGF/X1h8TSsY3bnyR7T15f/GbA0zUSpgjBfMarJAvek3JBpgZDtSCriCP7k6ombEGMr7m2b
cHxQJhL6xbdjfajYbFynr7+rT0US0TgOYbqG3lqjxYLdVqgipANruchEaHOMO5sa2EyDXaDckVOt
JUsnuTNr9CZ+aNdGv26EAOgPz1qicHsfrqhUPM/2khb2DoObgfUZXQez0s5wUtLvxEgcQU5/Al7o
cJLygC8hy5Oz5kJBd0cgq1ZEUctOI910ZWZdHMkyB8V8tsdSYJpEGzpaa/jALuj8I0CDazv+vC5N
2kNqYvnk05ZaBWYUJE0InqHF8fgFm0gG/aUjUnHtniXJyRcLLja9FZLIIlmPwEVxCoDsdjyRvWVu
nISrwK4aBLo0hO7tCgHTjXHR07EwJVNb71k5gG03bhnGcrhFo9Pkbg93WidsqGY0/4ndYtv5jnzh
H7xAJWbNPAsU/pmOKRmeDj5I0PnL6S6wrP0gK5WBcAXEV1p4xMi6KifBsTDlZ2fFiTHxTuZtSuRN
SZj9RXrFmDDp2xvpBKqTmqtaXT0g7IHzjJ0/rSlwaiy9zRM5QgDng3RIi6NCT/11SsOgV45kbAbd
gS5eGH1982vyziF9D795aY7dltWXxBeKaY+FI0BDadpw1YimAgPCTutgDaNaqTodkD/jOo8qVnzq
6Hv8t1xfjMSi8Nklfl8cipSulcKee9+SaMdpDr2zlgfTYfKLjIAaFNHWAkU6qHqL/kQjz2o+7WnX
XzdM5oXsgu0uFrvndCiAPcCwad58pZ6127uHm1xLAtYWe6R3T4NOhS2knoxY7jbt8bopfRh/+xeB
jak6FdqjO0rXcX9JTRyc7NDXPg7RF6AdOs7BFek4tVCaakgFtXgXa68oS95PYUfxO4ZwnPvRIRId
mIcTceIGB6TJCIqvIimCNKSmjV0GuzXViwfAzW1nAnDWHiY2EOz2NEIIKJGVW4p4jmneT572LRSY
gLhVxKqQRi35Zt/9nNWS259LGtxbncqNVtewwlxQAy+OlEYH2X3lRz8X4ATM28F173ypbkjP/qvH
mnOhslEQh5gUxnwFVoiz9WL17Fu8eude7N25S8heHjLEkObeG5yA+Yg/UI+7zijFTzA03BgRBUgN
3lLT6zGIVLAquPavIZo3hdSZOeeBz2rxGNvVV/ACV93/FS4SMI96Qp9CG++0M+ajl5e4kXJkC2UF
Yxtb/2m+zPPcC8V+AViO3pMTZ40XjsK05/Wl0cj4RMz4GGeK9y1c8iKAI0aLO+F9usGMgXDIPjz8
R6RaQxsIKVtGVbVt5zW643X5J7GCKatIzEmNPADasFJN18XIh3AaZQPyC29Vs5+tY9AQWc0HQ1u+
Dxpiql184Yge2etrFOh2wDLE6NSlBRaN2RaeIo9Fpheo7vVZPSI4vj4mTN4NQEUC9zfCQaV6IoCy
AMswNUbuc+2ZFLyzCyLjwK69gsLBiMUfA30Q3uwARCc2U3ManrZkOq7xxTKECfaJlkg9ElZNj7We
HMtAr08Rh7ZFwsKXjHERXmoXtxRf89Z3MeBl2VIlYEc7P98AhZy80MkDO/yHdSzAuJ3+7KEMc0mH
xpRVZ/WRrs9XSay3Y5cPjWNrmf6geiy7KUyca/Qw/YFJQuhUWt7EkIPwhkNpKWcQM7CDRtXmWhs9
XcMfNTmyq9J+IkxDSE7/ZWydXM/RJNMtbyU8wPh3SWySviDJjLQSQB+UOD0r8K10A4LHotYE3Za0
rAC87IOlWcqkUbR5ZYrVmiY5+6nEAGMqiN1ysycwyZT/Z6iQav22Su3GPVkA0gLR9fAzC3OaXQ2R
LtFt8kXATSx1IEBlJSVxtXpTjrHFfsICcuqky3ymCP5oDYY3+oAooFMl/ENfCljL56n8Z5SwkiT0
XYFaspK+Eo5ytoVmiO3IARzujTcQZ9Ys3LX9aHeXPgrSzUvn5lqai7s3rkDez7wvRCmqSSc4Ibkm
YyMzDKh+mV8PWUPb+fzlGccyzs+kPkrWE7mVAXgtbaqwrymJX+CGGtMsTI392DbWtXueJ7AEDIeP
Jf9ooEHgmzeEkheSE+95kxJhAQEmBBkmRnmIglPA17gOG76KZAYq9thDQEge6NziI26RDioi5HtS
nIdt3Sk8JvCIZMV/xxu9UK/c8f2cVyJQg1ergIchJdwELdrnbe92o1ckcOG9K9G3YCAkD3G9e22t
hbDILOlhOiJ4ZNm3pR6iOMyLpqaApLV7vkyhpo/uF0metzsEPMoIU2hP+e2h3x94pSolfskPymqS
okJ280Q/OcixDq19by/16l11zZx98FqLRr8knUdwoFQ7Vi1RBUGEGEoSYOfFoasHjn5jGPRDC9yD
Y93pM9P9YXJ27lWyPAg2AGEoCxw/bulGZV0HAZulTAjuQVspw6pzNUkPZuAraKQHCzQIENU+C5sQ
GC97fj2kq5JHJZ+re8yUnkF6B9rR57KCBHx1ictMuXSfXc3VmC2kO3KqT7pafPQA3wW98L2vsEkm
ff0ZteJ3HRhBV80DtxVR4IrWYBQFMLKAVdiwj6hAS/yuQtE9Z/iAl7MJ//c5oTqCojbNbjReAC4g
t7mwYCHv/rx+XqPv+ZN8xWlNNbZ0xDcEFnjPTJaMlydFRXN0IQez57MasmpccvgQ0+GfiGeXaRQf
XVjy7j4gnWwabDUoEUWoMY3jcV7bamb3wZpImTuR/1vf6DaKUqUmBFS05PivydCFi57iELOJrsd5
tBFAV03VL9lPLts9hHkvYos7dWEkXRj6A8QHheNJKHp1LTbOFlEJxR1FLHXOddbL8A/TQiUa5Iww
9YFcL/1d+AvKPZ94ikOeKukjHwzv26V4lgoZqoow+/TrqCqtCoOdz+BGtF238oJZ9+phjcOvp1di
C4DmowsGVr1ly22B/9Ae/HnaSPrfz6FL9T8pE3ol3fduvSnEgW+I7A9hM3xVKJvVdGJhYgWoC89H
5Yq6l2GKStwOLQBkKQQkZz7sEc7u+s6ObhOf5AWZ5RyV9MrhUI96MUfxyVpUeQI0FkJOnYBlXK/4
3CfiJvoh+R6SiIuyQ1D2ZIlbd1Ffga4l5JYKjVsdKwyijJf2gEXp25bL5mITil9ef+n6Tea3dOna
ATjmhDaIPJlwAGiUJ3xKtwTinZcbIAn42ff/10yKFugMz+TrOpRHTtygNjGFEy695xTp9CHHVVx6
kKzDn49gbo3jLS0FJXMfhpdLsq7JzbaQ/EaJDuZm7NcxPxOOjBfMenMZCeIEwVCzevPPSYq6wZMo
UYjyUubxevXgEQmlYkzhYW3MtnvzLZ034B4+ka9+N2x9xGW5CaVWAso8qy9N/u/s0oy0CtfCSzWc
YWpaY17YREjyzWa9xRvWLFwm43o8sLXGGP9teTOB4BgHY57Fr7hw0BUc1Cv/E4K/SLA/VIaDrdAP
QSmNgWQq0IuXX+x8mRWaIr12QC6+R+RPNHGPCaucDgbUJhWVLHP6NnQ7a0x4Cc8L5W4+y5UBurbT
zNrqS7QMnwF/bxeVxO5von0POOCSOnNHa85T/3cjnuv882WrCQSQGkLwEAAIPGdmZcGmxDFf1hSb
CADSlsDe3f0uZXm+270dpFVeZ+N/Afj4dLZR+uHWupSuffjt5IHzHhlayOMKH3BFO/7OytnCbAfL
eGDlR2egbTkBKiprX/i9OcYMtLTmLEECZuQfIerUuoIEJu8NagQOvzGvGQV1V/ZQyVthYf4Pfjxx
xqNOJYaCHjwR7SSmQDuX9HzDOZhe2yg1SdYVunbYIitckrFrz19RxBYYMgKzk7bX9t9Sur1yiG0K
O8EF0jYgbqBjRUCZ7iJxqA9mCkoZ6OSbsEO+qlanX3aNznRErP7SOEKtf7YJWmwI3Anutg9Tz+Xq
YRY0VzYctUl+ExZIP72EI3wg+rV8g8hO5EZ1zFUv9P+KtMHjPpa4G9CENJFGCUOVtc/DsWbXWd4F
7PI4NS6Ev5AsCDyKHnBbFtjPNiioxIO7EJf9KoNOSRIYy0m/gFYAwpLFKG1MDBazKu+qlYWiuhuE
pW1qJLZGEvN2Z92fOXl2TKCcKcpkuU9wUMKdOv4XVlJ+UeQeB/t3WwMtvpBN5/7xI3FL5l/ckbaG
cSlFkwy18Ju4I2LIJfk4oX13nyQadZz/VBLBVjBvWLnyF1NWtW9eh7F829TBCkG3mPx9c33mNbQX
uZYVeYqUeyLY4qdtFQRsZYaTW2DzRuwUu6VXBa40aqH51OrJ3xBVrC/QWmkVPx//tAUGRHVQHdrF
lPInqV9147FceLj/rW+QKJoRIWtyWM7brey6OQzpe6JcQgiXT6X0fg1CSVBTm+Y8x1dDvaBcxdVS
leuXHs3LqsOodvtjHzuna5pa/er3HSCBCK3yuc1wGROSdMc4fP+dHIAyyAZgaAXz4YVAho9hPM3m
L3mY5d2PsS31EhmrHKbsqUTiTEj7seTDidIYDCtnC9fP9FYD6PjRnNXeAgJDv//SIj6b4MRYlZaU
FN5g6no2DZxyAWJaoJ+S8gM0Ida8LTAbHewKBYdprmBwz/KjVFNUm//8rlwShtv814z2YdHsFT8R
60CjXkID1G1nrlQ/mzMz3LRADfjso0rKdLKLpYjyeRKXmR21EounmS52zPqbpPx6sjBAGNeSfS79
q0HKeiyBA/7gZ8nZCT7SgivafehmJsHRO1g+DVqFRBKjjNcExenL8jvWwVbYNcsgPIYUFa/KjBLN
U9rZeKtQZVPfDD+8H3FbnNseqNTc0ko30YDS/s2UZCOKvrGL+CdDJeI204KtquBYFtz4znz+OpHR
/862uiQAA795s1j6iKOC6dopoXWzSySP96yi8Ps2ISmvwOXRQIu5nkveUA6rx11zDlS5E6t86Jrv
PVAsia4iUT+rJ6JTARHTuKj63mc+UeOlvl2mUkxb0Dnnh1jPxYb+CHmdXKqQRLkfqMbMpUQ5tl8t
nh/56cLV+M2hg68lQWg2mitqUDyVYEfSTqSNndf2OqWsFv0d1iXQE+9cDGzazFxNpCbKIm5kZXTT
+55xnMcDtGIqDMnhVFoAOrGn80JWASScfHQpx/sxtFe9b0IfT3fYBtwX/kayV3re59KNvM+sYG/E
r7SrSp67N7Cd5m4BexRaXFUxiV2zYvHqSFjW8KjTR/z06eZo7ynF0l86Q9QtJ8HI7fXDw+9BIyoF
9YCMlFPsJZAoCpYBh0l0JZ7z2/lVUTwkvk7ssmBtjbag21HLn0To1HPhe/+pbaPl8rZbACAzeBHm
joXimAPkOzQ=
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
