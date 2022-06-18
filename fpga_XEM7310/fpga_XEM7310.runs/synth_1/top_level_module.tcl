# 
# Synthesis run script generated by Vivado
# 

set TIME_start [clock seconds] 
proc create_report { reportName command } {
  set status "."
  append status $reportName ".fail"
  if { [file exists $status] } {
    eval file delete [glob $status]
  }
  send_msg_id runtcl-4 info "Executing : $command"
  set retval [eval catch { $command } msg]
  if { $retval != 0 } {
    set fp [open $status w]
    close $fp
    send_msg_id runtcl-5 warning "$msg"
  }
}
create_project -in_memory -part xc7a75tfgg484-1

set_param project.singleFileAddWarning.threshold 0
set_param project.compositeFile.enableAutoGeneration 0
set_param synth.vivado.isSynthRun true
set_msg_config -source 4 -id {IP_Flow 19-2162} -severity warning -new_severity info
set_property webtalk.parent_dir C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/wt [current_project]
set_property parent.project_path C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.xpr [current_project]
set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY} [current_project]
set_property default_lib xil_defaultlib [current_project]
set_property target_language Verilog [current_project]
set_property ip_output_repo c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/ip [current_project]
set_property ip_cache_permissions {read write} [current_project]
read_verilog {
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/timescale.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/spi_defines.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ep_defines.v
}
set_property file_type "Verilog Header" [get_files C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/timescale.v]
set_property file_type "Verilog Header" [get_files C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/spi_defines.v]
set_property file_type "Verilog Header" [get_files C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ep_defines.v]
read_verilog -library xil_defaultlib {
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okWireIn.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okWireOut.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okPipeOut.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okTriggerIn.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okTriggerOut.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okRegisterBridge.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okBTPipeOut.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okLibrary.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okCoreHarness.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/top_level_module.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/realTimeLPF_readwrite_coeff.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/reset_synchronizer.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/reset_sync_low.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/mux_8to1.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/spi_clgen.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/WbSignal_converter.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/AD7961.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/hbexec.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/one_second_pulse.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/spi_top.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/SPI_Master/spi_shift.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/spi_controller.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/clock_divider.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/spi_data_gen.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/general_clock_divide.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ddr3_test.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/XEM7310-A75/okBTPipeIn.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/spi_fifo_driven.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/read_fifo_to_spi_cmd.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/LPF_data_modify_fixpt.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/Butterworth.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/src/okDRAM64X8D.v
  {C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/Example Design/sync_reset.v}
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/src/i2cController.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/src/i2cTokenizer.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/src/mux8to1.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/mux4to1_16wide.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/mux8to1_32wide.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/dsp_filters/Butter_pipelined.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/global_timing.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/i2c/src/i2cController_wPipe.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/dsp_filters/mlhdlc_biquad_fixpt_folded.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/dsp_filters/mlhdlc_biquad_fixpt.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/spi_fifo_driven_filter_test.v
  C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/LPF_data_scale.v
}
read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32/user_design/constraints/ddr3_256_32.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32/user_design/constraints/ddr3_256_32_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0_board.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_i2c_pipe/fifo_i2c_pipe.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_i2c_pipe/fifo_i2c_pipe.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_i2c_pipe/fifo_i2c_pipe_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_i2c_pipe/fifo_i2c_pipe_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/blk_mem_gen_0/blk_mem_gen_0.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/blk_mem_gen_0/blk_mem_gen_0_ooc.xdc]

read_ip -quiet C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1.xci
set_property used_in_implementation false [get_files -all c:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1_ooc.xdc]

# Mark all dcp files as not used in implementation to prevent them from being
# stitched into the results of this synthesis run. Any black boxes in the
# design are intentionally left as such for best results. Dcp files will be
# stitched into the design at a later time, either when this synthesis run is
# opened, or when it is stitched into a dependent implementation run.
foreach dcp [get_files -quiet -all -filter file_type=="Design\ Checkpoint"] {
  set_property used_in_implementation false $dcp
}
read_xdc C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/constrs_1/xem7310.xdc
set_property used_in_implementation false [get_files C:/Users/koer2434/Documents/fpga/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/constrs_1/xem7310.xdc]

read_xdc dont_touch.xdc
set_property used_in_implementation false [get_files dont_touch.xdc]
set_param ips.enableIPCacheLiteLoad 0
close [open __synthesis_is_running__ w]

synth_design -top top_level_module -part xc7a75tfgg484-1


# disable binary constraint mode for synth run checkpoints
set_param constraints.enableBinaryConstraints false
write_checkpoint -force -noxdef top_level_module.dcp
create_report "synth_1_synth_report_utilization_0" "report_utilization -file top_level_module_utilization_synth.rpt -pb top_level_module_utilization_synth.pb"
file delete __synthesis_is_running__
close [open __synthesis_is_complete__ w]
