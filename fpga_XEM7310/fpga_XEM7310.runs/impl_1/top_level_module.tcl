# 
# Report generation script generated by Vivado
# 

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
proc start_step { step } {
  set stopFile ".stop.rst"
  if {[file isfile .stop.rst]} {
    puts ""
    puts "*** Halting run - EA reset detected ***"
    puts ""
    puts ""
    return -code error
  }
  set beginFile ".$step.begin.rst"
  set platform "$::tcl_platform(platform)"
  set user "$::tcl_platform(user)"
  set pid [pid]
  set host ""
  if { [string equal $platform unix] } {
    if { [info exist ::env(HOSTNAME)] } {
      set host $::env(HOSTNAME)
    }
  } else {
    if { [info exist ::env(COMPUTERNAME)] } {
      set host $::env(COMPUTERNAME)
    }
  }
  set ch [open $beginFile w]
  puts $ch "<?xml version=\"1.0\"?>"
  puts $ch "<ProcessHandle Version=\"1\" Minor=\"0\">"
  puts $ch "    <Process Command=\".planAhead.\" Owner=\"$user\" Host=\"$host\" Pid=\"$pid\">"
  puts $ch "    </Process>"
  puts $ch "</ProcessHandle>"
  close $ch
}

proc end_step { step } {
  set endFile ".$step.end.rst"
  set ch [open $endFile w]
  close $ch
}

proc step_failed { step } {
  set endFile ".$step.error.rst"
  set ch [open $endFile w]
  close $ch
}


start_step init_design
set ACTIVE_STEP init_design
set rc [catch {
  create_msg_db init_design.pb
  create_project -in_memory -part xc7a75tfgg484-1
  set_property design_mode GateLvl [current_fileset]
  set_param project.singleFileAddWarning.threshold 0
  set_property webtalk.parent_dir C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/wt [current_project]
  set_property parent.project_path C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.xpr [current_project]
  set_property ip_output_repo C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.cache/ip [current_project]
  set_property ip_cache_permissions {read write} [current_project]
  set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY} [current_project]
  add_files -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.runs/synth_1/top_level_module.dcp
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/clk_wiz_0/clk_wiz_0.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_ADS8686/fifo_ADS8686.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/ddr3_256_32/ddr3_256_32.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w32_1024_r256_128/fifo_w32_1024_r256_128.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w128_512_r256_256/fifo_w128_512_r256_256.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_256_r128_512/fifo_w256_256_r128_512.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_w256_128_r32_1024/fifo_w256_128_r32_1024.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/fifo_i2c_pipe/fifo_i2c_pipe.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_0/mult_gen_0.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/blk_mem_gen_0/blk_mem_gen_0.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_1/mult_gen_1.xci
  read_ip -quiet C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ip/mult_gen_2/mult_gen_2.xci
  read_xdc C:/Users/delg5279/Documents/covg_fpga_project/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/constrs_1/xem7310.xdc
  link_design -top top_level_module -part xc7a75tfgg484-1
  close_msg_db -file init_design.pb
} RESULT]
if {$rc} {
  step_failed init_design
  return -code error $RESULT
} else {
  end_step init_design
  unset ACTIVE_STEP 
}

start_step opt_design
set ACTIVE_STEP opt_design
set rc [catch {
  create_msg_db opt_design.pb
  opt_design 
  write_checkpoint -force top_level_module_opt.dcp
  create_report "impl_1_opt_report_drc_0" "report_drc -file top_level_module_drc_opted.rpt -pb top_level_module_drc_opted.pb -rpx top_level_module_drc_opted.rpx"
  close_msg_db -file opt_design.pb
} RESULT]
if {$rc} {
  step_failed opt_design
  return -code error $RESULT
} else {
  end_step opt_design
  unset ACTIVE_STEP 
}

start_step place_design
set ACTIVE_STEP place_design
set rc [catch {
  create_msg_db place_design.pb
  if { [llength [get_debug_cores -quiet] ] > 0 }  { 
    implement_debug_core 
  } 
  place_design 
  write_checkpoint -force top_level_module_placed.dcp
  create_report "impl_1_place_report_io_0" "report_io -file top_level_module_io_placed.rpt"
  create_report "impl_1_place_report_utilization_0" "report_utilization -file top_level_module_utilization_placed.rpt -pb top_level_module_utilization_placed.pb"
  create_report "impl_1_place_report_control_sets_0" "report_control_sets -verbose -file top_level_module_control_sets_placed.rpt"
  close_msg_db -file place_design.pb
} RESULT]
if {$rc} {
  step_failed place_design
  return -code error $RESULT
} else {
  end_step place_design
  unset ACTIVE_STEP 
}

start_step phys_opt_design
set ACTIVE_STEP phys_opt_design
set rc [catch {
  create_msg_db phys_opt_design.pb
  phys_opt_design -directive AggressiveExplore
  write_checkpoint -force top_level_module_physopt.dcp
  close_msg_db -file phys_opt_design.pb
} RESULT]
if {$rc} {
  step_failed phys_opt_design
  return -code error $RESULT
} else {
  end_step phys_opt_design
  unset ACTIVE_STEP 
}

  set_msg_config -source 4 -id {Route 35-39} -severity "critical warning" -new_severity warning
start_step route_design
set ACTIVE_STEP route_design
set rc [catch {
  create_msg_db route_design.pb
  route_design 
  write_checkpoint -force top_level_module_routed.dcp
  create_report "impl_1_route_report_drc_0" "report_drc -file top_level_module_drc_routed.rpt -pb top_level_module_drc_routed.pb -rpx top_level_module_drc_routed.rpx"
  create_report "impl_1_route_report_methodology_0" "report_methodology -file top_level_module_methodology_drc_routed.rpt -pb top_level_module_methodology_drc_routed.pb -rpx top_level_module_methodology_drc_routed.rpx"
  create_report "impl_1_route_report_power_0" "report_power -file top_level_module_power_routed.rpt -pb top_level_module_power_summary_routed.pb -rpx top_level_module_power_routed.rpx"
  create_report "impl_1_route_report_route_status_0" "report_route_status -file top_level_module_route_status.rpt -pb top_level_module_route_status.pb"
  create_report "impl_1_route_report_timing_summary_0" "report_timing_summary -max_paths 10 -file top_level_module_timing_summary_routed.rpt -pb top_level_module_timing_summary_routed.pb -rpx top_level_module_timing_summary_routed.rpx"
  create_report "impl_1_route_report_incremental_reuse_0" "report_incremental_reuse -file top_level_module_incremental_reuse_routed.rpt"
  create_report "impl_1_route_report_clock_utilization_0" "report_clock_utilization -file top_level_module_clock_utilization_routed.rpt"
  create_report "impl_1_route_report_bus_skew_0" "report_bus_skew -warn_on_violation -file top_level_module_bus_skew_routed.rpt -pb top_level_module_bus_skew_routed.pb -rpx top_level_module_bus_skew_routed.rpx"
  close_msg_db -file route_design.pb
} RESULT]
if {$rc} {
  write_checkpoint -force top_level_module_routed_error.dcp
  step_failed route_design
  return -code error $RESULT
} else {
  end_step route_design
  unset ACTIVE_STEP 
}

start_step post_route_phys_opt_design
set ACTIVE_STEP post_route_phys_opt_design
set rc [catch {
  create_msg_db post_route_phys_opt_design.pb
  phys_opt_design 
  write_checkpoint -force top_level_module_postroute_physopt.dcp
  create_report "impl_1_post_route_phys_opt_report_timing_summary_0" "report_timing_summary -max_paths 10 -warn_on_violation -file top_level_module_timing_summary_postroute_physopted.rpt -pb top_level_module_timing_summary_postroute_physopted.pb -rpx top_level_module_timing_summary_postroute_physopted.rpx"
  create_report "impl_1_post_route_phys_opt_report_bus_skew_0" "report_bus_skew -warn_on_violation -file top_level_module_bus_skew_postroute_physopted.rpt -pb top_level_module_bus_skew_postroute_physopted.pb -rpx top_level_module_bus_skew_postroute_physopted.rpx"
  close_msg_db -file post_route_phys_opt_design.pb
} RESULT]
if {$rc} {
  step_failed post_route_phys_opt_design
  return -code error $RESULT
} else {
  end_step post_route_phys_opt_design
  unset ACTIVE_STEP 
}

start_step write_bitstream
set ACTIVE_STEP write_bitstream
set rc [catch {
  create_msg_db write_bitstream.pb
  set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY} [current_project]
  catch { write_mem_info -force top_level_module.mmi }
  write_bitstream -force top_level_module.bit 
  catch {write_debug_probes -quiet -force top_level_module}
  catch {file copy -force top_level_module.ltx debug_nets.ltx}
  close_msg_db -file write_bitstream.pb
} RESULT]
if {$rc} {
  step_failed write_bitstream
  return -code error $RESULT
} else {
  end_step write_bitstream
  unset ACTIVE_STEP 
}

