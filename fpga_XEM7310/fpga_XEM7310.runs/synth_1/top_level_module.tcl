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
set_property webtalk.parent_dir C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/wt [current_project]
set_property parent.project_path C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.xpr [current_project]
set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY} [current_project]
set_property default_lib xil_defaultlib [current_project]
set_property target_language Verilog [current_project]
set_property ip_output_repo c:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/ip [current_project]
set_property ip_cache_permissions {read write} [current_project]
read_verilog {
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/timescale.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_defines.v
}
set_property file_type "Verilog Header" [get_files C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/timescale.v]
set_property file_type "Verilog Header" [get_files C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_defines.v]
read_verilog -library xil_defaultlib {
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_slave_model.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/mux_8to1.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_shift.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_clgen.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/WbSignal_converter.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/spi_top.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/one_second_pulse.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/hbexec.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/top_module.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/okWireIn.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/okTriggerIn.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/okBTPipeOut.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/mux_1to8.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/top_level_module.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/okWireOut.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/okTriggerOut.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/iande/Desktop/covg_fpga/SPI_Master/read_AD796x_fifo_cmd.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/XEM7310-A75/okLibrary.v
  C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/imports/XEM7310-A75/okCoreHarness.v
}
read_ip -quiet C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_generator_1/fifo_generator_1.xci
set_property used_in_implementation false [get_files -all c:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_generator_1/fifo_generator_1.xdc]
set_property used_in_implementation false [get_files -all c:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_generator_1/fifo_generator_1_clocks.xdc]
set_property used_in_implementation false [get_files -all c:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_generator_1/fifo_generator_1_ooc.xdc]

# Mark all dcp files as not used in implementation to prevent them from being
# stitched into the results of this synthesis run. Any black boxes in the
# design are intentionally left as such for best results. Dcp files will be
# stitched into the design at a later time, either when this synthesis run is
# opened, or when it is stitched into a dependent implementation run.
foreach dcp [get_files -quiet -all -filter file_type=="Design\ Checkpoint"] {
  set_property used_in_implementation false $dcp
}
read_xdc C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/constrs_1/imports/Downloads/xem7310.xdc
set_property used_in_implementation false [get_files C:/Users/iande/Desktop/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/constrs_1/imports/Downloads/xem7310.xdc]

set_param ips.enableIPCacheLiteLoad 0
close [open __synthesis_is_running__ w]

synth_design -top top_level_module -part xc7a75tfgg484-1


# disable binary constraint mode for synth run checkpoints
set_param constraints.enableBinaryConstraints false
write_checkpoint -force -noxdef top_level_module.dcp
create_report "synth_1_synth_report_utilization_0" "report_utilization -file top_level_module_utilization_synth.rpt -pb top_level_module_utilization_synth.pb"
file delete __synthesis_is_running__
close [open __synthesis_is_complete__ w]
