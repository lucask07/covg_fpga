set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0.xdc id:1 order:EARLY scoped_inst:adc_pll/inst rxprname:$PSRCDIR/sources_1/ip/clk_wiz_0/clk_wiz_0.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xdc id:2 order:EARLY scoped_inst:fg_pipein_fifo/U0 rxprname:$PSRCDIR/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xdc id:3 order:EARLY scoped_inst:okPipeOut_fifo_ddr2/U0 rxprname:$PSRCDIR/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xdc id:4 order:EARLY scoped_inst:ads8686_fifo/U0 rxprname:$PSRCDIR/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32/user_design/constraints/ddr3_256_32.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32/user_design/constraints/ddr3_256_32.xdc id:5 order:EARLY scoped_inst:u_ddr3_256_32 rxprname:$PSRCDIR/sources_1/ip/ddr3_256_32/ddr3_256_32/user_design/constraints/ddr3_256_32.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xdc id:6 order:EARLY scoped_inst:adc_to_ddr_fifo/U0 rxprname:$PSRCDIR/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xdc} [current_design]
set_property SRC_FILE_INFO {cfile:{c:/Users/stro4149/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xdc} rfile:../../fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xdc id:7 order:EARLY scoped_inst:ddr_to_dac_fifo_ddr/U0 rxprname:$PSRCDIR/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xdc} [current_design]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:CLKIN1:CLKFBOUT:sys_clk:clkfbout_clk_wiz_0::1:0:CLKIN1:CLKOUT0:sys_clk:clk_out1_clk_wiz_0 [get_cells adc_pll/inst/plle2_adv_inst]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:CLKIN1:CLKFBOUT:okUH0:mmcm0_clkfb::1:0:CLKIN1:CLKOUT0:okUH0:mmcm0_clk0 [get_cells okHI/mmcm0]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:CLKIN1:CLKFBOUT:pll_clk3_out:clk_pll_i::1:0:CLKIN1:CLKOUT0:pll_clk3_out:mmcm_ps_clk_bufg_in::1:0:CLKIN1:CLKOUT1:pll_clk3_out:clk_div2_bufg_in [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_ddr3_infrastructure/gen_mmcm.mmcm_i]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:CLKIN1:CLKFBOUT:sys_clk:pll_clkfbout::1:0:CLKIN1:CLKOUT0:sys_clk:freq_refclk::1:0:CLKIN1:CLKOUT1:sys_clk:mem_refclk::1:0:CLKIN1:CLKOUT2:sys_clk:sync_pulse::1:0:CLKIN1:CLKOUT3:sys_clk:pll_clk3_out [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_ddr3_infrastructure/plle2_i]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:FREQREFCLK:ICLK:freq_refclk:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/iserdes_clk::1:0:ICLK:ICLKDIV:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/iserdes_clk:iserdes_clkdiv [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_in_gen.phaser_in]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk::1:0:OCLK:OCLKDIV:oserdes_clk:oserdes_clkdiv [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_out]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:FREQREFCLK:ICLK:freq_refclk:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/iserdes_clk::1:0:ICLK:ICLKDIV:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/iserdes_clk:iserdes_clkdiv_1 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_in_gen.phaser_in]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk_1::1:0:OCLK:OCLKDIV:oserdes_clk_1:oserdes_clkdiv_1 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_out]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:FREQREFCLK:ICLK:freq_refclk:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/iserdes_clk::1:0:ICLK:ICLKDIV:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/iserdes_clk:iserdes_clkdiv_2 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_in_gen.phaser_in]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk_2::1:0:OCLK:OCLKDIV:oserdes_clk_2:oserdes_clkdiv_2 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_out]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:FREQREFCLK:ICLK:freq_refclk:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/iserdes_clk::1:0:ICLK:ICLKDIV:u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/iserdes_clk:iserdes_clkdiv_3 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_in_gen.phaser_in]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk_3::1:0:OCLK:OCLKDIV:oserdes_clk_3:oserdes_clkdiv_3 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_out]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk_4::1:0:OCLK:OCLKDIV:oserdes_clk_4:oserdes_clkdiv_4 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_C.ddr_byte_lane_C/phaser_out]
set_property src_info {type:PI file:{} line:-1 export:NONE save:INPUT read:READ} [current_design]
set_property TOOL_DERIVED_CLK_NAMES 1:0:MEMREFCLK:OCLK:mem_refclk:oserdes_clk_5::1:0:OCLK:OCLKDIV:oserdes_clk_5:oserdes_clkdiv_5 [get_cells u_ddr3_256_32/u_ddr3_256_32_mig/u_memc_ui_top_std/mem_intfc0/ddr_phy_top0/u_ddr_mc_phy_wrapper/u_ddr_mc_phy/ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_D.ddr_byte_lane_D/phaser_out]
set_property src_info {type:SCOPED_XDC file:1 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:1 line:2 export:INPUT save:INPUT read:READ} [current_design]
# file: clk_wiz_0.xdc
set_property src_info {type:SCOPED_XDC file:1 line:3 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:4 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2008 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:1 line:5 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:6 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:1 line:7 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:1 line:8 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:1 line:9 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:1 line:10 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:11 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:1 line:12 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:1 line:13 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:1 line:14 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:1 line:15 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:1 line:16 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:1 line:17 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:1 line:18 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:1 line:19 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:1 line:20 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:1 line:21 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:1 line:22 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:1 line:23 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:1 line:24 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:1 line:25 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:1 line:26 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:1 line:27 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:1 line:28 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:1 line:29 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:1 line:30 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:1 line:31 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:1 line:32 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:33 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:1 line:34 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:1 line:35 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:1 line:36 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:1 line:37 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:1 line:38 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:1 line:39 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:1 line:40 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:1 line:41 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:1 line:42 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:1 line:43 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:1 line:44 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:1 line:45 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:1 line:46 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:47 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:1 line:48 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:1 line:49 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:1 line:50 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:1 line:51 export:INPUT save:INPUT read:READ} [current_design]
# Input clock periods. These duplicate the values entered for the
set_property src_info {type:SCOPED_XDC file:1 line:52 export:INPUT save:INPUT read:READ} [current_design]
# input clocks. You can use these to time your system. If required
set_property src_info {type:SCOPED_XDC file:1 line:53 export:INPUT save:INPUT read:READ} [current_design]
# commented constraints can be used in the top level xdc
set_property src_info {type:SCOPED_XDC file:1 line:54 export:INPUT save:INPUT read:READ} [current_design]
#----------------------------------------------------------------
set_property src_info {type:SCOPED_XDC file:1 line:55 export:INPUT save:INPUT read:READ} [current_design]
#create_clock -period 5.000 [get_ports clk_in1]
set_property src_info {type:SCOPED_XDC file:1 line:56 export:INPUT save:INPUT read:READ} [current_design]
#set_input_jitter [get_clocks -of_objects [get_ports clk_in1]] 0.05
set_property src_info {type:SCOPED_XDC file:1 line:57 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:1 line:58 export:INPUT save:INPUT read:READ} [current_design]

current_instance adc_pll/inst
set_property src_info {type:SCOPED_XDC file:1 line:59 export:INPUT save:INPUT read:READ} [current_design]
set_property PHASESHIFT_MODE WAVEFORM [get_cells -hierarchical *adv*]
set_property src_info {type:SCOPED_XDC file:1 line:60 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:2 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:3 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:4 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:5 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:6 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:7 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:2 line:8 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2009 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:2 line:9 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:2 line:10 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:2 line:11 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:2 line:12 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:2 line:13 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:2 line:14 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:2 line:15 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:2 line:16 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:2 line:17 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:2 line:18 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:2 line:19 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:2 line:20 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:2 line:21 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:2 line:22 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:2 line:23 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:2 line:24 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:2 line:25 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:2 line:26 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:2 line:27 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:2 line:28 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:2 line:29 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:2 line:30 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:2 line:31 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:2 line:32 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:2 line:33 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:2 line:34 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:2 line:35 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:2 line:36 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:2 line:37 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:2 line:38 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:2 line:39 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:2 line:40 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:2 line:41 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:2 line:42 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:2 line:43 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:2 line:44 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:2 line:45 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:2 line:46 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:2 line:47 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:2 line:48 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:2 line:49 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:2 line:50 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:2 line:51 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:2 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:2 line:53 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:2 line:54 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:2 line:55 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:56 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:2 line:57 export:INPUT save:INPUT read:READ} [current_design]
#                         Native FIFO Constraints                              #
set_property src_info {type:SCOPED_XDC file:2 line:58 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:2 line:59 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:60 export:INPUT save:INPUT read:READ} [current_design]
# Set false path on the asynchronous reset port (rst) to the inputs of synchronizers
set_property src_info {type:SCOPED_XDC file:2 line:61 export:INPUT save:INPUT read:READ} [current_design]
#set_false_path -through [get_pins -of [get_cells -hier -filter name=~*rst_wr_reg2_inst*/arststages_ff_reg[1]] -filter {REF_PIN_NAME == Q}] -to [get_pins -of [get_cells -hier -filter name=~*rstblk*/*] -filter {REF_PIN_NAME == PRE}]
set_property src_info {type:SCOPED_XDC file:2 line:62 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:63 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:64 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:65 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:2 line:66 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:2 line:67 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:2 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:3 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:4 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:5 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:6 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:7 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:3 line:8 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2009 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:3 line:9 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:3 line:10 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:3 line:11 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:3 line:12 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:3 line:13 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:3 line:14 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:3 line:15 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:3 line:16 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:3 line:17 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:3 line:18 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:3 line:19 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:3 line:20 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:3 line:21 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:3 line:22 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:3 line:23 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:3 line:24 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:3 line:25 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:3 line:26 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:3 line:27 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:3 line:28 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:3 line:29 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:3 line:30 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:3 line:31 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:3 line:32 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:3 line:33 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:3 line:34 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:3 line:35 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:3 line:36 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:3 line:37 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:3 line:38 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:3 line:39 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:3 line:40 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:3 line:41 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:3 line:42 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:3 line:43 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:3 line:44 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:3 line:45 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:3 line:46 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:3 line:47 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:3 line:48 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:3 line:49 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:3 line:50 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:3 line:51 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:3 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:3 line:53 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:3 line:54 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:3 line:55 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:56 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:3 line:57 export:INPUT save:INPUT read:READ} [current_design]
#                         Native FIFO Constraints                              #
set_property src_info {type:SCOPED_XDC file:3 line:58 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:3 line:59 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:60 export:INPUT save:INPUT read:READ} [current_design]
# Set false path on the asynchronous reset port (rst) to the inputs of synchronizers
set_property src_info {type:SCOPED_XDC file:3 line:61 export:INPUT save:INPUT read:READ} [current_design]
#set_false_path -through [get_pins -of [get_cells -hier -filter name=~*rst_wr_reg2_inst*/arststages_ff_reg[1]] -filter {REF_PIN_NAME == Q}] -to [get_pins -of [get_cells -hier -filter name=~*rstblk*/*] -filter {REF_PIN_NAME == PRE}]
set_property src_info {type:SCOPED_XDC file:3 line:62 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:63 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:64 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:65 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:3 line:66 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:3 line:67 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:2 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:3 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:4 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:5 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:6 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:7 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:4 line:8 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2009 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:4 line:9 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:4 line:10 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:4 line:11 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:4 line:12 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:4 line:13 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:4 line:14 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:4 line:15 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:4 line:16 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:4 line:17 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:4 line:18 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:4 line:19 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:4 line:20 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:4 line:21 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:4 line:22 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:4 line:23 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:4 line:24 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:4 line:25 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:4 line:26 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:4 line:27 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:4 line:28 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:4 line:29 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:4 line:30 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:4 line:31 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:4 line:32 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:4 line:33 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:4 line:34 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:4 line:35 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:4 line:36 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:4 line:37 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:4 line:38 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:4 line:39 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:4 line:40 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:4 line:41 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:4 line:42 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:4 line:43 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:4 line:44 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:4 line:45 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:4 line:46 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:4 line:47 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:4 line:48 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:4 line:49 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:4 line:50 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:4 line:51 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:4 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:4 line:53 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:4 line:54 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:4 line:55 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:56 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:4 line:57 export:INPUT save:INPUT read:READ} [current_design]
#                         Native FIFO Constraints                              #
set_property src_info {type:SCOPED_XDC file:4 line:58 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:4 line:59 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:60 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:61 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:62 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:63 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:4 line:64 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:4 line:65 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:1 export:INPUT save:INPUT read:READ} [current_design]
##################################################################################################
set_property src_info {type:SCOPED_XDC file:5 line:2 export:INPUT save:INPUT read:READ} [current_design]
##
set_property src_info {type:SCOPED_XDC file:5 line:3 export:INPUT save:INPUT read:READ} [current_design]
##  Xilinx, Inc. 2010            www.xilinx.com
set_property src_info {type:SCOPED_XDC file:5 line:4 export:INPUT save:INPUT read:READ} [current_design]
##  Thu Feb 24 10:58:33 2022
set_property src_info {type:SCOPED_XDC file:5 line:5 export:INPUT save:INPUT read:READ} [current_design]
##  Generated by MIG Version 4.1
set_property src_info {type:SCOPED_XDC file:5 line:6 export:INPUT save:INPUT read:READ} [current_design]
##
set_property src_info {type:SCOPED_XDC file:5 line:7 export:INPUT save:INPUT read:READ} [current_design]
##################################################################################################
set_property src_info {type:SCOPED_XDC file:5 line:8 export:INPUT save:INPUT read:READ} [current_design]
##  File name :       ddr3_256_32.xdc
set_property src_info {type:SCOPED_XDC file:5 line:9 export:INPUT save:INPUT read:READ} [current_design]
##  Details :     Constraints file
set_property src_info {type:SCOPED_XDC file:5 line:10 export:INPUT save:INPUT read:READ} [current_design]
##                    FPGA Family:       ARTIX7
set_property src_info {type:SCOPED_XDC file:5 line:11 export:INPUT save:INPUT read:READ} [current_design]
##                    FPGA Part:         XC7A75T-FGG484
set_property src_info {type:SCOPED_XDC file:5 line:12 export:INPUT save:INPUT read:READ} [current_design]
##                    Speedgrade:        -1
set_property src_info {type:SCOPED_XDC file:5 line:13 export:INPUT save:INPUT read:READ} [current_design]
##                    Design Entry:      VERILOG
set_property src_info {type:SCOPED_XDC file:5 line:14 export:INPUT save:INPUT read:READ} [current_design]
##                    Frequency:         0 MHz
set_property src_info {type:SCOPED_XDC file:5 line:15 export:INPUT save:INPUT read:READ} [current_design]
##                    Time Period:       2500 ps
set_property src_info {type:SCOPED_XDC file:5 line:16 export:INPUT save:INPUT read:READ} [current_design]
##################################################################################################
set_property src_info {type:SCOPED_XDC file:5 line:17 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:18 export:INPUT save:INPUT read:READ} [current_design]
##################################################################################################
set_property src_info {type:SCOPED_XDC file:5 line:19 export:INPUT save:INPUT read:READ} [current_design]
## Controller 0
set_property src_info {type:SCOPED_XDC file:5 line:20 export:INPUT save:INPUT read:READ} [current_design]
## Memory Device: DDR3_SDRAM->Components->MT41K256M16XX-125
set_property src_info {type:SCOPED_XDC file:5 line:21 export:INPUT save:INPUT read:READ} [current_design]
## Data Width: 32
set_property src_info {type:SCOPED_XDC file:5 line:22 export:INPUT save:INPUT read:READ} [current_design]
## Time Period: 2500
set_property src_info {type:SCOPED_XDC file:5 line:23 export:INPUT save:INPUT read:READ} [current_design]
## Data Mask: 1
set_property src_info {type:SCOPED_XDC file:5 line:24 export:INPUT save:INPUT read:READ} [current_design]
##################################################################################################
set_property src_info {type:SCOPED_XDC file:5 line:25 export:INPUT save:INPUT read:READ} [current_design]

current_instance -quiet
set_property src_info {type:SCOPED_XDC file:5 line:26 export:INPUT save:INPUT read:READ} [current_design]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ck_n[0]}]
set_property src_info {type:SCOPED_XDC file:5 line:27 export:INPUT save:INPUT read:READ} [current_design]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ck_p[0]}]
set_property src_info {type:SCOPED_XDC file:5 line:28 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:29 export:INPUT save:INPUT read:READ} [current_design]
#create_clock -period 5 [get_ports sys_clk_i]
set_property src_info {type:SCOPED_XDC file:5 line:30 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:31 export:INPUT save:INPUT read:READ} [current_design]
############## NET - IOSTANDARD ##################
set_property src_info {type:SCOPED_XDC file:5 line:32 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:33 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:34 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L17P_T2_A26_15
set_property src_info {type:SCOPED_XDC file:5 line:36 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[0]}]
set_property src_info {type:SCOPED_XDC file:5 line:39 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:40 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L14N_T2_SRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:42 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[1]}]
set_property src_info {type:SCOPED_XDC file:5 line:45 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:46 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L18P_T2_A24_15
set_property src_info {type:SCOPED_XDC file:5 line:48 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[2]}]
set_property src_info {type:SCOPED_XDC file:5 line:51 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L13P_T2_MRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:54 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[3]}]
set_property src_info {type:SCOPED_XDC file:5 line:57 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:58 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L16P_T2_A28_15
set_property src_info {type:SCOPED_XDC file:5 line:60 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[4]}]
set_property src_info {type:SCOPED_XDC file:5 line:63 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:64 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L13N_T2_MRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:66 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[5]}]
set_property src_info {type:SCOPED_XDC file:5 line:69 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:70 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L17N_T2_A25_15
set_property src_info {type:SCOPED_XDC file:5 line:72 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[6]}]
set_property src_info {type:SCOPED_XDC file:5 line:75 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:76 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L16N_T2_A27_15
set_property src_info {type:SCOPED_XDC file:5 line:78 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[7]}]
set_property src_info {type:SCOPED_XDC file:5 line:81 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:82 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L23P_T3_FOE_B_15
set_property src_info {type:SCOPED_XDC file:5 line:84 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[8]}]
set_property src_info {type:SCOPED_XDC file:5 line:87 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:88 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L22P_T3_A17_15
set_property src_info {type:SCOPED_XDC file:5 line:90 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[9]}]
set_property src_info {type:SCOPED_XDC file:5 line:93 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:94 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L19N_T3_A21_VREF_15
set_property src_info {type:SCOPED_XDC file:5 line:96 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[10]}]
set_property src_info {type:SCOPED_XDC file:5 line:99 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:100 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L24P_T3_RS1_15
set_property src_info {type:SCOPED_XDC file:5 line:102 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[11]}]
set_property src_info {type:SCOPED_XDC file:5 line:105 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:106 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L23N_T3_FWE_B_15
set_property src_info {type:SCOPED_XDC file:5 line:108 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[12]}]
set_property src_info {type:SCOPED_XDC file:5 line:111 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:112 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L20P_T3_A20_15
set_property src_info {type:SCOPED_XDC file:5 line:114 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[13]}]
set_property src_info {type:SCOPED_XDC file:5 line:117 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:118 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L19P_T3_A22_15
set_property src_info {type:SCOPED_XDC file:5 line:120 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[14]}]
set_property src_info {type:SCOPED_XDC file:5 line:123 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:124 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L20N_T3_A19_15
set_property src_info {type:SCOPED_XDC file:5 line:126 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[15]}]
set_property src_info {type:SCOPED_XDC file:5 line:129 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:130 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L22N_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:132 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[16]}]
set_property src_info {type:SCOPED_XDC file:5 line:135 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:136 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L19N_T3_VREF_16
set_property src_info {type:SCOPED_XDC file:5 line:138 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[17]}]
set_property src_info {type:SCOPED_XDC file:5 line:141 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:142 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L23P_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:144 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[18]}]
set_property src_info {type:SCOPED_XDC file:5 line:147 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:148 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L23N_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:150 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[19]}]
set_property src_info {type:SCOPED_XDC file:5 line:153 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:154 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L24P_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:156 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[20]}]
set_property src_info {type:SCOPED_XDC file:5 line:159 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:160 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L20P_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:162 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[21]}]
set_property src_info {type:SCOPED_XDC file:5 line:165 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:166 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L22P_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:168 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[22]}]
set_property src_info {type:SCOPED_XDC file:5 line:171 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:172 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L20N_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:174 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[23]}]
set_property src_info {type:SCOPED_XDC file:5 line:177 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:178 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L16N_T2_16
set_property src_info {type:SCOPED_XDC file:5 line:180 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[24]}]
set_property src_info {type:SCOPED_XDC file:5 line:183 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:184 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L14N_T2_SRCC_16
set_property src_info {type:SCOPED_XDC file:5 line:186 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[25]}]
set_property src_info {type:SCOPED_XDC file:5 line:189 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:190 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L17N_T2_16
set_property src_info {type:SCOPED_XDC file:5 line:192 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[26]}]
set_property src_info {type:SCOPED_XDC file:5 line:195 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:196 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L18P_T2_16
set_property src_info {type:SCOPED_XDC file:5 line:198 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[27]}]
set_property src_info {type:SCOPED_XDC file:5 line:201 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:202 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L13P_T2_MRCC_16
set_property src_info {type:SCOPED_XDC file:5 line:204 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[28]}]
set_property src_info {type:SCOPED_XDC file:5 line:207 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:208 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L14P_T2_SRCC_16
set_property src_info {type:SCOPED_XDC file:5 line:210 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[29]}]
set_property src_info {type:SCOPED_XDC file:5 line:213 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:214 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L17P_T2_16
set_property src_info {type:SCOPED_XDC file:5 line:216 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[30]}]
set_property src_info {type:SCOPED_XDC file:5 line:219 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:220 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L13N_T2_MRCC_16
set_property src_info {type:SCOPED_XDC file:5 line:222 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dq[31]}]
set_property src_info {type:SCOPED_XDC file:5 line:225 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:226 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L10N_T1_AD11N_15
set_property src_info {type:SCOPED_XDC file:5 line:230 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:231 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L9N_T1_DQS_AD3N_15
set_property src_info {type:SCOPED_XDC file:5 line:235 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:236 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L1P_T0_AD0P_15
set_property src_info {type:SCOPED_XDC file:5 line:240 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:241 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L2P_T0_AD8P_15
set_property src_info {type:SCOPED_XDC file:5 line:245 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:246 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L5P_T0_AD9P_15
set_property src_info {type:SCOPED_XDC file:5 line:250 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:251 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L10P_T1_AD11P_15
set_property src_info {type:SCOPED_XDC file:5 line:255 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:256 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L8N_T1_AD10N_15
set_property src_info {type:SCOPED_XDC file:5 line:260 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:261 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L2N_T0_AD8N_15
set_property src_info {type:SCOPED_XDC file:5 line:265 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:266 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L5N_T0_AD9N_15
set_property src_info {type:SCOPED_XDC file:5 line:270 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:271 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L4P_T0_15
set_property src_info {type:SCOPED_XDC file:5 line:275 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:276 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L1N_T0_AD0N_15
set_property src_info {type:SCOPED_XDC file:5 line:280 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:281 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L7N_T1_AD2N_15
set_property src_info {type:SCOPED_XDC file:5 line:285 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:286 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L9P_T1_DQS_AD3P_15
set_property src_info {type:SCOPED_XDC file:5 line:290 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:291 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L7P_T1_AD2P_15
set_property src_info {type:SCOPED_XDC file:5 line:295 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:296 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L11N_T1_SRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:300 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:301 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L12N_T1_MRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:305 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:306 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L12P_T1_MRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:310 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:311 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L6N_T0_VREF_15
set_property src_info {type:SCOPED_XDC file:5 line:315 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:316 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_0_15
set_property src_info {type:SCOPED_XDC file:5 line:320 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:321 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L6P_T0_15
set_property src_info {type:SCOPED_XDC file:5 line:325 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:326 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L11P_T1_SRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:330 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:331 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_25_16
set_property src_info {type:SCOPED_XDC file:5 line:335 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:336 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L4N_T0_15
set_property src_info {type:SCOPED_XDC file:5 line:340 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:341 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L8P_T1_AD10P_15
set_property src_info {type:SCOPED_XDC file:5 line:345 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:346 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L14P_T2_SRCC_15
set_property src_info {type:SCOPED_XDC file:5 line:350 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:351 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L22N_T3_A16_15
set_property src_info {type:SCOPED_XDC file:5 line:355 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:356 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L19P_T3_16
set_property src_info {type:SCOPED_XDC file:5 line:360 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:361 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L16P_T2_16
set_property src_info {type:SCOPED_XDC file:5 line:365 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:366 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L15P_T2_DQS_15
set_property src_info {type:SCOPED_XDC file:5 line:368 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_p[0]}]
set_property src_info {type:SCOPED_XDC file:5 line:371 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:372 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L15N_T2_DQS_ADV_B_15
set_property src_info {type:SCOPED_XDC file:5 line:374 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_n[0]}]
set_property src_info {type:SCOPED_XDC file:5 line:377 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:378 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L21P_T3_DQS_15
set_property src_info {type:SCOPED_XDC file:5 line:380 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_p[1]}]
set_property src_info {type:SCOPED_XDC file:5 line:383 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:384 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L21N_T3_DQS_A18_15
set_property src_info {type:SCOPED_XDC file:5 line:386 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_n[1]}]
set_property src_info {type:SCOPED_XDC file:5 line:389 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:390 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L21P_T3_DQS_16
set_property src_info {type:SCOPED_XDC file:5 line:392 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_p[2]}]
set_property src_info {type:SCOPED_XDC file:5 line:395 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:396 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L21N_T3_DQS_16
set_property src_info {type:SCOPED_XDC file:5 line:398 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_n[2]}]
set_property src_info {type:SCOPED_XDC file:5 line:401 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:402 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L15P_T2_DQS_16
set_property src_info {type:SCOPED_XDC file:5 line:404 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_p[3]}]
set_property src_info {type:SCOPED_XDC file:5 line:407 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:408 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L15N_T2_DQS_16
set_property src_info {type:SCOPED_XDC file:5 line:410 export:INPUT save:INPUT read:READ} [current_design]
set_property IN_TERM UNTUNED_SPLIT_60 [get_ports {ddr3_dqs_n[3]}]
set_property src_info {type:SCOPED_XDC file:5 line:413 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:414 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L3P_T0_DQS_AD1P_15
set_property src_info {type:SCOPED_XDC file:5 line:418 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:419 export:INPUT save:INPUT read:READ} [current_design]
# PadFunction: IO_L3N_T0_DQS_AD1N_15
set_property src_info {type:SCOPED_XDC file:5 line:423 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:424 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:425 export:INPUT save:INPUT read:READ} [current_design]
set_property INTERNAL_VREF 0.75 [get_iobanks 15]
set_property src_info {type:SCOPED_XDC file:5 line:426 export:INPUT save:INPUT read:READ} [current_design]
set_property INTERNAL_VREF 0.75 [get_iobanks 16]
set_property src_info {type:SCOPED_XDC file:5 line:427 export:INPUT save:INPUT read:READ} [current_design]

current_instance u_ddr3_256_32
set_property src_info {type:SCOPED_XDC file:5 line:428 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y11 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_D.ddr_byte_lane_D/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:429 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y10 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_C.ddr_byte_lane_C/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:430 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y9 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:431 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y8 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:432 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y13 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:433 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_OUT_PHY_X0Y12 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_out}]
set_property src_info {type:SCOPED_XDC file:5 line:434 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:435 export:INPUT save:INPUT read:READ} [current_design]
## set_property LOC PHASER_IN_PHY_X0Y11 [get_cells  -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_D.ddr_byte_lane_D/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:436 export:INPUT save:INPUT read:READ} [current_design]
## set_property LOC PHASER_IN_PHY_X0Y10 [get_cells  -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_C.ddr_byte_lane_C/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:437 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_IN_PHY_X0Y9 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:438 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_IN_PHY_X0Y8 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:439 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_IN_PHY_X0Y13 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:440 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_IN_PHY_X0Y12 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/phaser_in_gen.phaser_in}]
set_property src_info {type:SCOPED_XDC file:5 line:441 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:442 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:443 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:444 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y11 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_D.ddr_byte_lane_D/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:445 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y10 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_C.ddr_byte_lane_C/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:446 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y9 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:447 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y8 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:448 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y13 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:449 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OUT_FIFO_X0Y12 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/out_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:450 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:451 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC IN_FIFO_X0Y9 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/in_fifo_gen.in_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:452 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC IN_FIFO_X0Y8 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/in_fifo_gen.in_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:453 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC IN_FIFO_X0Y13 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/in_fifo_gen.in_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:454 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC IN_FIFO_X0Y12 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/in_fifo_gen.in_fifo}]
set_property src_info {type:SCOPED_XDC file:5 line:455 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:456 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHY_CONTROL_X0Y2 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/phy_control_i}]
set_property src_info {type:SCOPED_XDC file:5 line:457 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHY_CONTROL_X0Y3 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/phy_control_i}]
set_property src_info {type:SCOPED_XDC file:5 line:458 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:459 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_REF_X0Y2 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/phaser_ref_i}]
set_property src_info {type:SCOPED_XDC file:5 line:460 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PHASER_REF_X0Y3 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/phaser_ref_i}]
set_property src_info {type:SCOPED_XDC file:5 line:461 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:462 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OLOGIC_X0Y119 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/ddr_byte_group_io/*slave_ts}]
set_property src_info {type:SCOPED_XDC file:5 line:463 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OLOGIC_X0Y107 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_1.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/ddr_byte_group_io/*slave_ts}]
set_property src_info {type:SCOPED_XDC file:5 line:464 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OLOGIC_X0Y169 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_B.ddr_byte_lane_B/ddr_byte_group_io/*slave_ts}]
set_property src_info {type:SCOPED_XDC file:5 line:465 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC OLOGIC_X0Y157 [get_cells -hier -filter {NAME =~ */ddr_phy_4lanes_0.u_ddr_phy_4lanes/ddr_byte_lane_A.ddr_byte_lane_A/ddr_byte_group_io/*slave_ts}]
set_property src_info {type:SCOPED_XDC file:5 line:466 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:467 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC PLLE2_ADV_X0Y2 [get_cells -hier -filter {NAME =~ */u_ddr3_infrastructure/plle2_i}]
set_property src_info {type:SCOPED_XDC file:5 line:468 export:INPUT save:INPUT read:READ} [current_design]
set_property LOC MMCME2_ADV_X0Y2 [get_cells -hier -filter {NAME =~ */u_ddr3_infrastructure/gen_mmcm.mmcm_i}]
set_property src_info {type:SCOPED_XDC file:5 line:469 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:470 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:471 export:INPUT save:INPUT read:READ} [current_design]
set_multicycle_path -setup -from [get_cells -hier -filter {NAME =~ */mc0/mc_read_idle_r_reg}] -to [get_cells -hier -filter {NAME =~ */input_[?].iserdes_dq_.iserdesdq}] 6
set_property src_info {type:SCOPED_XDC file:5 line:474 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:475 export:INPUT save:INPUT read:READ} [current_design]
set_multicycle_path -hold -from [get_cells -hier -filter {NAME =~ */mc0/mc_read_idle_r_reg}] -to [get_cells -hier -filter {NAME =~ */input_[?].iserdes_dq_.iserdesdq}] 5
set_property src_info {type:SCOPED_XDC file:5 line:478 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:479 export:INPUT save:INPUT read:READ} [current_design]
set_false_path -through [get_pins -filter {NAME =~ */DQSFOUND} -of [get_cells -hier -filter {REF_NAME == PHASER_IN_PHY}]]
set_property src_info {type:SCOPED_XDC file:5 line:480 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:481 export:INPUT save:INPUT read:READ} [current_design]
set_multicycle_path -setup -start -through [get_pins -filter {NAME =~ */OSERDESRST} -of [get_cells -hier -filter {REF_NAME == PHASER_OUT_PHY}]] 2
set_property src_info {type:SCOPED_XDC file:5 line:482 export:INPUT save:INPUT read:READ} [current_design]
set_multicycle_path -hold -start -through [get_pins -filter {NAME =~ */OSERDESRST} -of [get_cells -hier -filter {REF_NAME == PHASER_OUT_PHY}]] 1
set_property src_info {type:SCOPED_XDC file:5 line:483 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:484 export:INPUT save:INPUT read:READ} [current_design]
#set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *temp_mon_enabled.u_tempmon/* && IS_SEQUENTIAL}] -to [get_cells -hier -filter {NAME =~ *temp_mon_enabled.u_tempmon/device_temp_sync_r1*}] 20
set_property src_info {type:SCOPED_XDC file:5 line:485 export:INPUT save:INPUT read:READ} [current_design]
set_max_delay -to [get_pins -hier -include_replicated_objects -filter {NAME =~ *temp_mon_enabled.u_tempmon/device_temp_sync_r1_reg[*]/D}] 20.000
set_property src_info {type:SCOPED_XDC file:5 line:486 export:INPUT save:INPUT read:READ} [current_design]
set_max_delay -datapath_only -from [get_cells -hier *rstdiv0_sync_r1_reg*] -to [get_pins -filter {NAME =~ */RESET} -of [get_cells -hier -filter {REF_NAME == PHY_CONTROL}]] 5.000
set_property src_info {type:SCOPED_XDC file:5 line:487 export:INPUT save:INPUT read:READ} [current_design]
#set_false_path -through [get_pins -hier -filter {NAME =~ */u_iodelay_ctrl/sys_rst}]
set_property src_info {type:SCOPED_XDC file:5 line:488 export:INPUT save:INPUT read:READ} [current_design]
set_false_path -through [get_nets -hier -filter {NAME =~ */u_iodelay_ctrl/sys_rst_i}]
set_property src_info {type:SCOPED_XDC file:5 line:489 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:490 export:INPUT save:INPUT read:READ} [current_design]
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *ddr3_infrastructure/rstdiv0_sync_r1_reg*}] -to [get_cells -hier -filter {NAME =~ *temp_mon_enabled.u_tempmon/xadc_supplied_temperature.rst_r1*}] 20.000
set_property src_info {type:SCOPED_XDC file:5 line:491 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:5 line:492 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:2 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:3 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:4 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:5 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:6 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:7 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:6 line:8 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2009 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:6 line:9 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:6 line:10 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:6 line:11 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:6 line:12 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:6 line:13 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:6 line:14 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:6 line:15 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:6 line:16 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:6 line:17 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:6 line:18 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:6 line:19 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:6 line:20 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:6 line:21 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:6 line:22 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:6 line:23 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:6 line:24 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:6 line:25 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:6 line:26 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:6 line:27 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:6 line:28 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:6 line:29 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:6 line:30 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:6 line:31 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:6 line:32 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:6 line:33 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:6 line:34 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:6 line:35 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:6 line:36 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:6 line:37 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:6 line:38 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:6 line:39 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:6 line:40 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:6 line:41 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:6 line:42 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:6 line:43 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:6 line:44 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:6 line:45 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:6 line:46 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:6 line:47 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:6 line:48 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:6 line:49 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:6 line:50 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:6 line:51 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:6 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:6 line:53 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:6 line:54 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:6 line:55 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:56 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:6 line:57 export:INPUT save:INPUT read:READ} [current_design]
#                         Native FIFO Constraints                              #
set_property src_info {type:SCOPED_XDC file:6 line:58 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:6 line:59 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:60 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:61 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:62 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:63 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:6 line:64 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:6 line:65 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:1 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:2 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:3 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:4 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:5 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:6 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:7 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:7 line:8 export:INPUT save:INPUT read:READ} [current_design]
# (c) Copyright 2009 - 2013 Xilinx, Inc. All rights reserved.
set_property src_info {type:SCOPED_XDC file:7 line:9 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:7 line:10 export:INPUT save:INPUT read:READ} [current_design]
# This file contains confidential and proprietary information
set_property src_info {type:SCOPED_XDC file:7 line:11 export:INPUT save:INPUT read:READ} [current_design]
# of Xilinx, Inc. and is protected under U.S. and
set_property src_info {type:SCOPED_XDC file:7 line:12 export:INPUT save:INPUT read:READ} [current_design]
# international copyright and other intellectual property
set_property src_info {type:SCOPED_XDC file:7 line:13 export:INPUT save:INPUT read:READ} [current_design]
# laws.
set_property src_info {type:SCOPED_XDC file:7 line:14 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:7 line:15 export:INPUT save:INPUT read:READ} [current_design]
# DISCLAIMER
set_property src_info {type:SCOPED_XDC file:7 line:16 export:INPUT save:INPUT read:READ} [current_design]
# This disclaimer is not a license and does not grant any
set_property src_info {type:SCOPED_XDC file:7 line:17 export:INPUT save:INPUT read:READ} [current_design]
# rights to the materials distributed herewith. Except as
set_property src_info {type:SCOPED_XDC file:7 line:18 export:INPUT save:INPUT read:READ} [current_design]
# otherwise provided in a valid license issued to you by
set_property src_info {type:SCOPED_XDC file:7 line:19 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx, and to the maximum extent permitted by applicable
set_property src_info {type:SCOPED_XDC file:7 line:20 export:INPUT save:INPUT read:READ} [current_design]
# law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
set_property src_info {type:SCOPED_XDC file:7 line:21 export:INPUT save:INPUT read:READ} [current_design]
# WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
set_property src_info {type:SCOPED_XDC file:7 line:22 export:INPUT save:INPUT read:READ} [current_design]
# AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
set_property src_info {type:SCOPED_XDC file:7 line:23 export:INPUT save:INPUT read:READ} [current_design]
# BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
set_property src_info {type:SCOPED_XDC file:7 line:24 export:INPUT save:INPUT read:READ} [current_design]
# INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
set_property src_info {type:SCOPED_XDC file:7 line:25 export:INPUT save:INPUT read:READ} [current_design]
# (2) Xilinx shall not be liable (whether in contract or tort,
set_property src_info {type:SCOPED_XDC file:7 line:26 export:INPUT save:INPUT read:READ} [current_design]
# including negligence, or under any other theory of
set_property src_info {type:SCOPED_XDC file:7 line:27 export:INPUT save:INPUT read:READ} [current_design]
# liability) for any loss or damage of any kind or nature
set_property src_info {type:SCOPED_XDC file:7 line:28 export:INPUT save:INPUT read:READ} [current_design]
# related to, arising under or in connection with these
set_property src_info {type:SCOPED_XDC file:7 line:29 export:INPUT save:INPUT read:READ} [current_design]
# materials, including for any direct, or any indirect,
set_property src_info {type:SCOPED_XDC file:7 line:30 export:INPUT save:INPUT read:READ} [current_design]
# special, incidental, or consequential loss or damage
set_property src_info {type:SCOPED_XDC file:7 line:31 export:INPUT save:INPUT read:READ} [current_design]
# (including loss of data, profits, goodwill, or any type of
set_property src_info {type:SCOPED_XDC file:7 line:32 export:INPUT save:INPUT read:READ} [current_design]
# loss or damage suffered as a result of any action brought
set_property src_info {type:SCOPED_XDC file:7 line:33 export:INPUT save:INPUT read:READ} [current_design]
# by a third party) even if such damage or loss was
set_property src_info {type:SCOPED_XDC file:7 line:34 export:INPUT save:INPUT read:READ} [current_design]
# reasonably foreseeable or Xilinx had been advised of the
set_property src_info {type:SCOPED_XDC file:7 line:35 export:INPUT save:INPUT read:READ} [current_design]
# possibility of the same.
set_property src_info {type:SCOPED_XDC file:7 line:36 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:7 line:37 export:INPUT save:INPUT read:READ} [current_design]
# CRITICAL APPLICATIONS
set_property src_info {type:SCOPED_XDC file:7 line:38 export:INPUT save:INPUT read:READ} [current_design]
# Xilinx products are not designed or intended to be fail-
set_property src_info {type:SCOPED_XDC file:7 line:39 export:INPUT save:INPUT read:READ} [current_design]
# safe, or for use in any application requiring fail-safe
set_property src_info {type:SCOPED_XDC file:7 line:40 export:INPUT save:INPUT read:READ} [current_design]
# performance, such as life-support or safety devices or
set_property src_info {type:SCOPED_XDC file:7 line:41 export:INPUT save:INPUT read:READ} [current_design]
# systems, Class III medical devices, nuclear facilities,
set_property src_info {type:SCOPED_XDC file:7 line:42 export:INPUT save:INPUT read:READ} [current_design]
# applications related to the deployment of airbags, or any
set_property src_info {type:SCOPED_XDC file:7 line:43 export:INPUT save:INPUT read:READ} [current_design]
# other applications that could lead to death, personal
set_property src_info {type:SCOPED_XDC file:7 line:44 export:INPUT save:INPUT read:READ} [current_design]
# injury, or severe property or environmental damage
set_property src_info {type:SCOPED_XDC file:7 line:45 export:INPUT save:INPUT read:READ} [current_design]
# (individually and collectively, "Critical
set_property src_info {type:SCOPED_XDC file:7 line:46 export:INPUT save:INPUT read:READ} [current_design]
# Applications"). Customer assumes the sole risk and
set_property src_info {type:SCOPED_XDC file:7 line:47 export:INPUT save:INPUT read:READ} [current_design]
# liability of any use of Xilinx products in Critical
set_property src_info {type:SCOPED_XDC file:7 line:48 export:INPUT save:INPUT read:READ} [current_design]
# Applications, subject only to applicable laws and
set_property src_info {type:SCOPED_XDC file:7 line:49 export:INPUT save:INPUT read:READ} [current_design]
# regulations governing limitations on product liability.
set_property src_info {type:SCOPED_XDC file:7 line:50 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:7 line:51 export:INPUT save:INPUT read:READ} [current_design]
# THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
set_property src_info {type:SCOPED_XDC file:7 line:52 export:INPUT save:INPUT read:READ} [current_design]
# PART OF THIS FILE AT ALL TIMES.
set_property src_info {type:SCOPED_XDC file:7 line:53 export:INPUT save:INPUT read:READ} [current_design]
#
set_property src_info {type:SCOPED_XDC file:7 line:54 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:7 line:55 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:56 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:7 line:57 export:INPUT save:INPUT read:READ} [current_design]
#                         Native FIFO Constraints                              #
set_property src_info {type:SCOPED_XDC file:7 line:58 export:INPUT save:INPUT read:READ} [current_design]
#------------------------------------------------------------------------------#
set_property src_info {type:SCOPED_XDC file:7 line:59 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:60 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:61 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:62 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:63 export:INPUT save:INPUT read:READ} [current_design]
################################################################################
set_property src_info {type:SCOPED_XDC file:7 line:64 export:INPUT save:INPUT read:READ} [current_design]

set_property src_info {type:SCOPED_XDC file:7 line:65 export:INPUT save:INPUT read:READ} [current_design]

