Search.setIndex({docnames:["endpoint_definitions_guide","index","interfaces","new_peripheral_guide","peripherals","register_index_guide","utils"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["endpoint_definitions_guide.rst","index.rst","interfaces.rst","new_peripheral_guide.rst","peripherals.rst","register_index_guide.rst","utils.rst"],objects:{"interfaces.interfaces":[[2,1,1,"","Endpoint"],[2,1,1,"","FPGA"],[2,1,1,"","Register"],[2,3,1,"","disp_device"]],"interfaces.interfaces.Endpoint":[[2,2,1,"","advance_endpoints"],[2,2,1,"","excel_to_defines"],[2,2,1,"","get_chip_endpoints"],[2,2,1,"","update_endpoints_from_defines"]],"interfaces.interfaces.FPGA":[[2,2,1,"","clear_endpoint"],[2,2,1,"","clear_wire_bit"],[2,2,1,"","init_device"],[2,2,1,"","read_ep"],[2,2,1,"","read_pipe_out"],[2,2,1,"","read_trig"],[2,2,1,"","read_wire"],[2,2,1,"","read_wire_bit"],[2,2,1,"","send_trig"],[2,2,1,"","set_endpoint"],[2,2,1,"","set_ep_simultaneous"],[2,2,1,"","set_wire"],[2,2,1,"","set_wire_bit"],[2,2,1,"","toggle_high"],[2,2,1,"","toggle_low"]],"interfaces.interfaces.Register":[[2,2,1,"","get_chip_registers"]],"interfaces.peripherals":[[4,0,0,"-","AD5453"],[4,0,0,"-","AD7961"],[4,0,0,"-","ADCDATA"],[4,0,0,"-","ADS8686"],[4,0,0,"-","DAC53401"],[4,0,0,"-","DAC80508"],[4,0,0,"-","DDR3"],[4,0,0,"-","I2CController"],[4,0,0,"-","SPIController"],[4,0,0,"-","SPIFifoDriven"],[4,0,0,"-","TCA9555"],[4,0,0,"-","TMF8801"],[4,0,0,"-","UID_24AA025UID"]],"interfaces.peripherals.AD5453":[[4,1,1,"","AD5453"]],"interfaces.peripherals.AD5453.AD5453":[[4,2,1,"","read_coeff_debug"],[4,2,1,"","set_clk_rising_edge"],[4,2,1,"","set_ctrl_reg"]],"interfaces.peripherals.AD7961":[[4,1,1,"","AD7961"]],"interfaces.peripherals.AD7961.AD7961":[[4,2,1,"","create_chips"],[4,2,1,"","get_fifo_status"],[4,2,1,"","get_pll_status"],[4,2,1,"","get_status"],[4,2,1,"","get_timing_pll_status"],[4,2,1,"","power_down_adc"],[4,2,1,"","power_down_all"],[4,2,1,"","power_down_fpga"],[4,2,1,"","reset_pll"],[4,2,1,"","reset_trig"],[4,2,1,"","reset_wire"],[4,2,1,"","set_enables"],[4,2,1,"","setup"],[4,2,1,"","test_pattern"]],"interfaces.peripherals.ADS8686":[[4,1,1,"","ADS8686"]],"interfaces.peripherals.ADS8686.ADS8686":[[4,2,1,"","hw_reset"],[4,2,1,"","read"],[4,2,1,"","read_channel"],[4,2,1,"","read_last"],[4,2,1,"","reg_to_voltage"],[4,2,1,"","set_range"],[4,2,1,"","setup"],[4,2,1,"","setup_sequencer"],[4,2,1,"","write"],[4,2,1,"","write_reg_bridge"]],"interfaces.peripherals.DAC53401":[[4,1,1,"","DAC53401"]],"interfaces.peripherals.DAC53401.DAC53401":[[4,2,1,"","config_func"],[4,2,1,"","config_margins"],[4,2,1,"","config_rate"],[4,2,1,"","config_step"],[4,2,1,"","enable_internal_reference"],[4,2,1,"","get_gain"],[4,2,1,"","get_id"],[4,2,1,"","lock"],[4,2,1,"","power_down_10k"],[4,2,1,"","power_down_high_impedance"],[4,2,1,"","power_up"],[4,2,1,"","read"],[4,2,1,"","reset"],[4,2,1,"","set_gain"],[4,2,1,"","start_func"],[4,2,1,"","stop_func"],[4,2,1,"","unlock"],[4,2,1,"","write"],[4,2,1,"","write_voltage"]],"interfaces.peripherals.DAC80508":[[4,1,1,"","DAC80508"]],"interfaces.peripherals.DAC80508.DAC80508":[[4,2,1,"","reset"],[4,2,1,"","set_config"],[4,2,1,"","set_config_bin"],[4,2,1,"","set_gain"],[4,2,1,"","set_gain_bin"],[4,2,1,"","write_chip_reg"],[4,2,1,"","write_voltage"]],"interfaces.peripherals.DDR3":[[4,1,1,"","DDR3"]],"interfaces.peripherals.DDR3.DDR3":[[4,2,1,"","adc_single"],[4,2,1,"","clear_adc_debug"],[4,2,1,"","clear_adc_read"],[4,2,1,"","clear_adc_write"],[4,2,1,"","clear_adcs_connected"],[4,2,1,"","clear_dac_read"],[4,2,1,"","clear_dac_write"],[4,2,1,"","closest_frequency"],[4,2,1,"","data_to_names"],[4,2,1,"","deswizzle"],[4,2,1,"","fifo_status"],[4,2,1,"","make_flat_voltage"],[4,2,1,"","make_ramp"],[4,2,1,"","make_sine_wave"],[4,2,1,"","make_step"],[4,2,1,"","print_fifo_status"],[4,2,1,"","read_adc"],[4,2,1,"","read_adc_block"],[4,2,1,"","reset_fifo"],[4,2,1,"","reset_mig_interface"],[4,2,1,"","save_data"],[4,2,1,"","set_adc_dac_simultaneous"],[4,2,1,"","set_adc_debug"],[4,2,1,"","set_adc_read"],[4,2,1,"","set_adc_write"],[4,2,1,"","set_adcs_connected"],[4,2,1,"","set_dac_read"],[4,2,1,"","set_dac_write"],[4,2,1,"","set_index"],[4,2,1,"","write"],[4,2,1,"","write_channels"]],"interfaces.peripherals.I2CController":[[4,1,1,"","I2CController"]],"interfaces.peripherals.I2CController.I2CController":[[4,2,1,"","create_chips"],[4,2,1,"","i2c_configure"],[4,2,1,"","i2c_read_long"],[4,2,1,"","i2c_receive"],[4,2,1,"","i2c_transmit"],[4,2,1,"","i2c_write_long"],[4,2,1,"","reset_device"]],"interfaces.peripherals.SPIController":[[4,1,1,"","SPIController"]],"interfaces.peripherals.SPIController.SPIController":[[4,2,1,"","configure_master"],[4,2,1,"","configure_master_bin"],[4,2,1,"","create_chips"],[4,2,1,"","get_master_configuration"],[4,2,1,"","read"],[4,2,1,"","reset_master"],[4,2,1,"","select_slave"],[4,2,1,"","set_divider"],[4,2,1,"","set_fpga_mode"],[4,2,1,"","set_frequency"],[4,2,1,"","set_host_mode"],[4,2,1,"","wb_go"],[4,2,1,"","wb_is_ack"],[4,2,1,"","wb_read"],[4,2,1,"","wb_send_cmd"],[4,2,1,"","wb_set_address"],[4,2,1,"","wb_write"],[4,2,1,"","write"]],"interfaces.peripherals.SPIFifoDriven":[[4,1,1,"","SPIFifoDriven"]],"interfaces.peripherals.SPIFifoDriven.SPIFifoDriven":[[4,2,1,"","create_chips"],[4,2,1,"","filter_select"],[4,2,1,"","set_clk_divider"],[4,2,1,"","set_ctrl_reg"],[4,2,1,"","set_data_mux"],[4,2,1,"","set_spi_sclk_divide"],[4,2,1,"","write"]],"interfaces.peripherals.TCA9555":[[4,1,1,"","TCA9555"]],"interfaces.peripherals.TCA9555.TCA9555":[[4,2,1,"","configure_pins"],[4,2,1,"","read"],[4,2,1,"","write"]],"interfaces.peripherals.TMF8801":[[4,1,1,"","TMF8801"]],"interfaces.peripherals.TMF8801.TMF8801":[[4,2,1,"","factory_calibration"],[4,2,1,"","get_id"],[4,2,1,"","power_down_high_impedance"],[4,2,1,"","read"],[4,2,1,"","read_data"],[4,2,1,"","write"]],"interfaces.peripherals.UID_24AA025UID":[[4,1,1,"","UID_24AA025UID"]],"interfaces.peripherals.UID_24AA025UID.UID_24AA025UID":[[4,2,1,"","get_device_code"],[4,2,1,"","get_manufacturer_code"],[4,2,1,"","get_serial_number"],[4,2,1,"","read"],[4,2,1,"","write"]],"interfaces.utils":[[6,3,1,"","calc_impedance"],[6,3,1,"","count_bytes"],[6,3,1,"","from_voltage"],[6,3,1,"","get_memory_usage"],[6,3,1,"","int_to_list"],[6,3,1,"","reverse_bits"],[6,3,1,"","to_voltage"],[6,3,1,"","twos_comp"]],interfaces:[[2,0,0,"-","interfaces"],[6,0,0,"-","utils"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function"},terms:{"0":[2,4,5],"010":4,"0x":[0,5],"0x0":5,"0x00":5,"0x000":5,"0x0000":5,"0x01":5,"0x02":5,"0x04":0,"0x10":5,"0x1d":4,"0x1e":4,"0x1f":4,"0x20":4,"0x21":4,"0x22":4,"0x23":4,"0x24":4,"0x25":4,"0x26":4,"0x27":4,"0x29":4,"0x3010":4,"0x31a0":5,"0x3f":5,"0x41":4,"0x44":5,"0x5555":4,"0xaaaa":4,"0xffff":5,"1":[2,4,6],"10":[4,5],"100":4,"1000":4,"1024":2,"1024word":4,"10k":4,"11":[],"12304":4,"128":4,"12824":4,"14":4,"144":[],"15":5,"16":[0,2,4,5],"16384":4,"1st":4,"2":[4,6],"2021":6,"2022":2,"2048":4,"24":4,"24aa025uid":4,"256":4,"256bit":4,"2nd":4,"2x":4,"3":[2,4],"30":4,"32":4,"32bit":4,"34":4,"376":4,"3v":2,"3x":4,"4":4,"40":4,"4096":4,"4294967295":2,"47":4,"4x":4,"5":4,"50":4,"54":[],"5x":4,"6":4,"64":4,"65535":4,"7":[4,5],"8":[0,4,5,6],"8192":4,"8th":4,"9":5,"boolean":4,"byte":[2,4,6],"class":[2,3,4,6],"default":[2,4],"do":[4,5],"final":4,"float":[4,6],"function":[3,4,6],"i\u00b2c":4,"int":[2,4,6],"long":6,"new":[1,4,5],"return":[2,4,6],"short":3,"static":[2,4],"true":[0,2,4],"while":[0,4],A:4,AND:4,And:[],At:4,Be:[3,5],For:[0,3,4,5],IN:4,If:[0,3,4],In:5,Into:[],It:6,NOT:0,No:4,Not:4,TO:[],That:4,The:[0,2,3,4,5,6],Then:6,These:[0,4],To:[0,3,4],With:3,_:0,_gen_addr:0,_gen_bit:0,a3:4,ab:[2,6],about:[0,2],abov:[0,3],access:5,accord:0,acknowledg:4,activ:[2,4],actual:4,actual_frequ:4,actual_length:4,ad5453:4,ad7961:[2,4],ad7961_ch0:4,ad7961_ch1:4,ad7961_ch2:4,ad7961_ch3:4,ad7961_tim:4,ad796x:4,ad:[0,3,4,5],adc:4,adc_data:4,adc_data_count:4,adc_no_timestamp:4,adc_read:4,adc_singl:4,adc_transfer_en:4,adc_write_en:4,adcdata:[],add:[0,3,4],addit:3,addr:[0,2],addr_pin:4,address:[2,4],address_head:4,ads8686:4,ads8686_cha:4,ads8686_chb:4,advanc:2,advance_endpoint:[0,2],advance_endpoints_bynum:[],advance_num:2,after:[0,2,4],again:4,ajstr:2,ajstroschein:[2,6],aldo:4,all:[2,4],allow:[0,4,5],alm_en:4,alm_sel:4,along:4,alongsid:4,alreadi:5,also:[0,3,4],altern:0,ambient:4,amplitud:4,an000597:4,an:[0,2,3,4,6],ani:[0,2,3,4,5],anoth:[0,4],api:[2,4],append:4,applic:3,ar:[0,3,4,5],argument:4,around:4,arrai:[4,6],ass:4,assign:4,associ:0,assum:6,attribut:[2,4],august:6,auto_gain:4,automat:[0,4],avail:[4,5],avdd:4,avoidi:3,b:4,back:[2,4],base:[],basic:4,becaus:0,been:2,befor:[0,4],begin:[],belong:0,below:[0,3,4,5],between:4,big:6,binari:[4,6],bit:[2,4,6],bit_index_high:2,bit_index_low:2,bit_list:2,bit_width:[0,2,6],bitfil:2,blk_multipl:4,blob:[],block:4,block_pipe_return:4,block_siz:4,bool:[2,4],both:[0,2,4,6],branch:3,bu:2,buf:4,buffer:[2,4],byearrai:4,bytearrai:[2,4],byteord:6,bytes_read_error:4,c:2,calc_imped:6,calcul:[4,6],calibr:4,call:[0,4,5],can:[0,4,5],cannot:[4,5],captur:4,categori:0,cell:0,chan_data:4,chan_list:4,chan_num:4,chang:[0,4,5],channel:[4,6],char_len:4,check:[0,2,3,4],chip:[0,2,4],chip_nam:2,chipnam:0,cl:[],classmethod:4,clear:[2,4],clear_adc_debug:4,clear_adc_read:4,clear_adc_writ:4,clear_adcs_connect:4,clear_dac_read:4,clear_dac_writ:4,clear_endpoint:2,clear_read:[],clear_wire_bit:2,clear_writ:[],clk:4,clk_div:4,clock:4,closest:4,closest_frequ:4,cm:4,code:[2,3,4],coeffici:4,collabor:[],collis:2,column:[0,5],com:4,combin:4,come:4,command:[3,4],comment:[0,3],common:4,commonli:3,commun:[2,3,4],complement:[4,6],complet:[0,3,4,5],compon:6,comput:6,concern:5,config:5,config_func:4,config_margin:4,config_r:4,config_step:4,configur:[2,4],configure_mast:4,configure_master_bin:4,configure_pin:4,connect:[2,4,6],consid:3,constant:4,contain:[0,2,4,5,6],containt:2,content:[],continu:4,contribut:3,control:0,convers:4,convert:[2,4,6],convert_data:[],convert_two:4,copi:[0,2,4],core:4,correct:4,correctli:4,correspoind:4,correspond:[4,5],count:[4,6],count_byt:6,counter:4,covg_fpga:2,crc_en:4,creat:[0,2,3,4,5],create_chip:[3,4],ctrl:4,ctrlvalu:4,current:4,current_data_mux:4,cycl:4,d:4,dac0_pwdwn:4,dac1_pwdwn:4,dac2_pwdwn:4,dac3_pwdwn:4,dac4_pwdwn:4,dac53401:4,dac5_pwdwn:4,dac6_pwdwn:4,dac7_pwdwn:4,dac80508:[3,4],dac:4,dac_data:4,dac_read_en:4,dac_write_en:4,daq_v2:[],dark:4,data:[0,2,4,5,6],data_buf:4,data_dir:4,data_len:2,data_length:4,data_mux:4,data_to_nam:4,data_vers:4,datasheet:[3,4,5],date:3,ddr3:4,ddr:4,ddr_norepeat:4,ddr_seq:4,debug:[2,4],debug_print:4,decid:4,decim:[0,4,5],declar:0,default_data_mux:4,defin:[0,4],defines_path:2,definit:[1,2,5],deriv:[2,4],descript:[3,4],design:4,desir:4,deswizl:[],deswizzl:4,determin:[4,6],dev:2,devaddr:4,devic:[2,4],device_info:2,dict:[2,4],dictionari:[0,2,4],differ:[0,4],differenti:4,digit:4,direct:4,directli:4,directori:4,disp_devic:2,displai:2,div_ref:4,divid:[4,6],divide_refer:4,divide_valu:4,doc:4,docstr:3,doe:[0,3,4,5],don:4,done:[3,4],doubl:4,down:4,driven:4,dsdo:4,duplic:3,duti:4,each:[0,2,4,5],edg:4,edu:[2,6],either:[0,4,6],empti:[0,2,4],emul:4,en0:4,en:4,enabl:4,enable_internal_refer:4,endian:6,endpoint:[1,2,4,5],endpoint_definitions_guid:[],endpoint_nam:0,endpoints_dict:2,endpoints_from_defin:[2,4],enter:[0,4],environ:4,ep:[],ep_bit:2,ep_defin:[0,2],ep_defines_exampl:[],ep_defines_path:2,ep_defines_sheet_exampl:[],ep_defines_sheet_templ:[],error:[0,2,4],even:4,evenli:4,ex:0,examp:3,exampl:[0,2,3,5],excel:[0,2,5],excel_path:2,excel_to_defin:[0,2],expand:4,expect:[2,4],explain:[0,3],extend:3,extens:4,extra:[0,5],extract:0,factor2:4,factor:4,factori:4,factory_calibr:4,fail:[2,4],fall:4,fals:[0,2,4,6],fast:4,few:4,fg:4,field:4,fifo:4,fifo_statu:4,file:[2,4,5],file_nam:4,filenam:4,fill:[2,3,4],filter:4,filter_select:4,find:6,finish:4,first:[0,3,4,5,6],fit:4,fix:4,flag:4,flat:4,flight:4,follow:[0,5],fork:3,form:[4,6],format:[0,3,4],found:0,fpga:[2,4],fpga_test:[],fpga_xem7310:2,fpsdk:4,freq:4,frequenc:4,frequeni:[],from:[0,2,4,5],from_voltag:6,front:4,frontpanel:[0,4],fsdo:4,full:4,function_nam:4,futur:0,gain:4,gen_addr:0,gen_address:2,gen_bit:[0,2],gener:[0,2,4,6],get:[3,4,6],get_available_endpoint:[],get_chip_endpoint:[0,2],get_chip_regist:[2,5],get_device_cod:4,get_fifo_statu:4,get_gain:4,get_id:4,get_manufacturer_cod:4,get_master_configur:4,get_memory_usag:6,get_pll_statu:4,get_serial_numb:4,get_statu:4,get_tim:[],get_timing_pll_statu:4,github:[],give:4,given:[2,4,5,6],glass:4,global:4,global_en:4,global_tim:4,go:4,go_bsi:4,goal:[],gp:0,gp_wire_in:0,great:3,greater:4,group:[0,2,4,5],guid:1,h13:4,h3010:4,h:0,ha:[2,4,5],half:4,handl:6,hardwar:4,have:0,hdf:4,hdl:4,header:4,help:6,here:[0,5],hex:0,hexadecim:[0,5],high:[2,4,5],hold:[0,4,5],host:[0,4],how:2,html:[],http:4,hw_reset:4,hz:4,i2c:[3,4],i2c_configur:4,i2c_max_timeout_m:4,i2c_read_long:4,i2c_rec:4,i2c_transmit:4,i2c_write_long:4,i2ccontrol:[2,3],i2cdaq:2,i2cdaq_level_shift:2,i2cdaq_qw:2,i:4,id:[4,5],ie:4,ignor:[0,5],immedi:4,immeid:4,impact:[],imped:[4,6],impl_1:[],implement:2,improv:4,in_plac:[],includ:[0,3,4],incom:4,increment:[0,2,4],increment_endpoint:[],index:[0,1,2,3,4],indic:5,inform:[0,2,3],init_devic:2,initi:[2,4],inner:2,input:[4,6],instanc:[2,3,4],instanti:[0,4],int_to_list:6,integ:[4,6],interact:4,interfac:[1,4,6],intern:[2,3,4,5],internship:2,interrupt:4,introduc:5,io:4,issu:3,its:[0,3],itself:2,june:2,just:[0,4],keep:3,kei:[0,4],kelli:[0,2,4],keyword:4,khz:4,know:[],koer2434:[2,6],koerner:[2,6],label:5,last:[3,4],latch:4,later:4,latest:[],leav:[0,4],left:4,length:[2,4],level:2,light:4,like:[3,4],line:[0,4],link:3,list:[4,5,6],littl:6,load:2,locat:[2,4,5],lock:4,longer:4,loop:4,low:[2,4,5],lower:0,lpf:4,lsb:[2,4,6],lsbyte:4,luca:[2,6],lucask07:[],lvd:4,m_ndatastart:4,m_pbuf:4,macro:0,made:[],mai:[3,6],main:3,make:[],make_flat_voltag:4,make_ramp:4,make_sine_wav:4,make_step:4,mani:4,manufactur:4,march:[],margin:4,margin_high:4,margin_low:4,markdown:[],mask:[2,4],master:4,master_config:4,match:[4,5],matter:[0,5],maximum:4,mb:4,mean:6,mem:0,mem_wire_in:0,member:[],memori:[4,5],meth:[],method:[0,3,4,5,6],mhz:4,mig:4,millisecond:4,minim:4,minimum:6,modifi:4,modul:[1,2,3,4,6],more:[0,3,4],msb:[2,4,6],msbyte:4,msg:4,msp:4,much:2,multipl:[2,4],multiplex:4,multipli:6,must:[0,2,4,5],mux:4,name:[0,2,3,4],ndarrai:[4,6],necessari:[4,6],need:[0,3,4],neg:4,new_frequ:4,newli:4,next:4,none:[4,6],note:[0,5],now:[2,4],np:4,num:6,num_bit:6,num_byt:[4,6],num_repeat:4,number:[4,6],number_of_byt:4,number_of_chip:4,numer:4,numpi:[3,4,6],numpydoc:[],o:4,object:[0,2,4,5,6],off:4,offset:4,often:0,ohm:4,ok:[2,4],okcfrontpanel:2,oktdeviceinfo:2,onc:[0,2,3],one:[4,5],onedr:2,onli:[0,2,4,5],opal:[0,2,4],opalkelli:[2,4],open:[3,5],oper:4,optic:4,option:[0,2,4],order:[0,4,5],org:[],organ:4,origin:4,oscilloscop:4,other:[0,4,5],otherwis:4,ouptut:4,our:5,out:4,outgo:4,output:4,over:[0,4],own:0,page:[1,2,3],pair:[0,2,4],paramet:[0,2,4,6],part:0,pass:4,path:2,pattern:4,per:[4,6],percentag:4,perform:4,period:4,peripher:[1,2,5,6],phase:4,phrase:0,piec:0,pin:4,pipe:4,pipe_out:4,pipein:[],pipeout:[2,4],place:[2,4],pleas:3,pll:4,pm:[],point:4,pointer:4,posit:4,possibl:[0,4],power:4,power_down_10k:4,power_down_adc:4,power_down_al:4,power_down_fpga:4,power_down_high_imped:4,power_up:4,prb:4,preambl:4,preamble_length:4,prefix:[0,4,5],print:[2,4],print_fifo_statu:4,process:[3,4],program:2,project:5,propos:[],protocol:4,provid:4,pull:[],puls:4,put:[0,4],py:[],pypanel:[0,5],pytest:3,python:[0,2],question:3,quickstart:[],qw:2,r:4,ramp:4,rang:[4,6],rate:4,rather:4,read:[2,3,4,5,6],read_adc:4,read_adc_block:4,read_channel:4,read_cnt:4,read_coeff_debug:4,read_data:4,read_en:[],read_ep:2,read_fg_en:[],read_last:4,read_oper:4,read_out:5,read_pipe_out:2,read_trig:2,read_wir:2,read_wire_bit:2,readabl:5,readcheck:4,readi:4,readthedoc:[],reason:5,recal:0,receiv:4,recommend:[4,5],reduc:4,redund:5,ref:[],ref_pwdwn:4,refdiv:4,refer:[0,4],referenc:0,reflect:0,reformat:4,reg:2,reg_nam:4,reg_to_voltag:4,reg_val:4,reg_valu:4,regaddr:4,regist:[1,2,4],register_index_guide_completed_exampl:[],register_index_templ:[],register_nam:4,registerbridg:4,releas:4,remain:3,reorder:4,repeat:[],repetit:4,replac:[0,5],repo:3,repositori:3,repres:[4,6],represent:[4,6],request:[],requir:[3,4,5],research:2,reset:4,reset_devic:4,reset_fifo:4,reset_mast:4,reset_mig_interfac:4,reset_pl:4,reset_trig:4,reset_wir:4,resist:6,resistor:6,respect:[],rest:4,result:4,retriev:0,rev:4,revers:6,reverse_bit:6,right:4,rise:4,room:4,round:[4,6],rout:4,row:[0,5],run:[2,4],rx_neg:4,s:[0,2,4,5,6],same:[0,2,3,4],sample_s:4,sandbox:[],save:4,save_data:4,saw:4,sawtooth_fal:4,sawtooth_ris:4,scale:4,scl:4,sclk:4,script:3,sda:4,search:1,section1:4,section:[0,4],see:[0,2,3,4,5],select:4,select_slav:4,send:4,send_trig:2,sent:4,separ:[0,4],sequenc:4,seri:6,serial:4,set:[2,3,4],set_adc_dac_simultan:4,set_adc_debug:4,set_adc_read:4,set_adc_writ:4,set_adcs_connect:4,set_clk_divid:4,set_clk_rising_edg:4,set_config:4,set_config_bin:4,set_ctrl_reg:4,set_dac_read:4,set_dac_writ:4,set_data_mux:4,set_ddr_read:4,set_divid:4,set_en:4,set_endpoint:2,set_ep_simultan:2,set_fpga_mod:4,set_frequ:4,set_gain:4,set_gain_bin:4,set_host_mod:4,set_index:4,set_rang:4,set_read:[],set_spi_sclk_divid:4,set_wir:2,set_wire_bit:2,set_writ:[],setup:4,setup_sequenc:4,sever:[3,4,6],shall:4,sheet:[2,5],shift:[2,4],shorten:0,should:[0,3,4,5],show:3,side:[],sign:4,signal:4,similar:[5,6],sinc:[0,4,5],sine:4,singl:[2,4],size:[4,6],skip:4,slave:4,slave_address:4,slew_rat:4,slope:4,smudg:4,so:[4,5],soft:4,softwar:4,sort:6,sourc:[2,4,6],sources_1:2,space:4,specif:[2,3,4],speed:4,speed_mb:4,spi:[3,4],spi_control:4,spi_fifo_driven:4,spicontrol:[2,3],spififodriven:[2,3],split:0,spreadsheet:[0,2,3],squar:4,src:2,st:2,stack:4,standard:[],start:[0,2,4,5],start_func:4,startup:4,statu:4,step:[3,4,5],stop:4,stop_func:4,store:[0,2,4,5],str:[2,4,6],stream:4,string:[4,5],stripe:4,stroschein:[2,6],structur:0,stthoma:[2,6],subclass:4,subpackag:4,suffici:4,suffix:0,suggest:4,support:4,sure:[3,5],swap:4,synchron:4,t0:[],t1:[],t:4,take:4,taken:5,target:4,tca9555:4,tclk:4,tell:0,templat:[0,5],test:4,test_pattern:4,text:2,than:[0,4],thei:[0,4,5],themselv:0,thi:[0,2,3,4,5],thoma:2,through:[0,3,4],througput:4,time:4,timeout:4,timestamp:4,titl:5,tmf8801:4,to_voltag:6,todo:4,togeth:[],toggl:2,toggle_high:2,toggle_low:2,tooth:4,top_level_modul:[],tos:4,total:[4,6],track:[],transfer:4,transmiss:4,transmit:4,triangl:4,trigger:[2,4],triggerin:[2,4],triggerout:2,tupdat:4,turn:4,two:[0,4],twos_comp:6,tx_neg:4,type:4,uid_24aa025uid:4,uint32:4,unaffect:4,under:0,underscor:[0,5],uniqu:4,unit16:4,univers:2,unknown:6,unlock:4,unsuccess:4,until:4,up:[3,4],updat:4,update_endpoints_from_defin:2,upper:[],uppercas:5,us:[0,2,3,4,5,6],usag:2,usb3:4,usb:0,use_twos_comp:6,user:[2,4],util:1,v:[0,2,4],v_in:6,v_out:6,val:[4,6],val_list:2,valid:5,valu:[0,2,4,6],veri:[],verilog:[0,2,4,5],version:[4,6],via:4,voltag:[4,6],voltage_rang:[4,6],vref:4,w0:[],w127:[],w128:[],w15:[],w224:[],w255:[],w31:[],w32:[],w63:[],w:4,wa:[4,6],wai:[3,4],wait:4,want:3,watch:3,wave:4,waveform:4,wb_clk_freq:4,wb_go:4,wb_is_ack:4,wb_read:4,wb_send_cmd:4,wb_set_address:4,wb_write:4,wbsignal_convert:4,we:[4,5,6],well:[0,4],what:[3,4],whatev:[0,5],when:[0,2,4],where:4,whether:[2,4],which:[0,5],wide:[],width:[0,2,6],wire:[2,4],wire_in:0,wire_out:4,wirein:[2,4],wireout:2,wishbon:4,with_neg:6,within:[4,5],word:[4,5],word_address:4,words_read:4,work:3,workbook_path:2,would:0,wrap:4,write:[3,4],write_channel:4,write_chip_reg:4,write_en:[],write_in:5,write_oper:4,write_reg_bridg:4,write_voltag:4,written:[0,2,3,4],x1:4,x2:4,x:4,xem7310:2,xem:2,xlsx:2,yet:2,you:[0,5],your:[0,3,5],zero:[4,5]},titles:["Endpoint Definitions Guide","Welcome to covgDAQ\u2019s documentation!","interfaces","New Peripheral Guide","peripherals","Register Index Guide","utils"],titleterms:{"1":5,"2":5,"3":5,"4":5,"5":5,"6":5,"class":[],"default":5,"new":3,address:[0,5],base:4,befor:3,begin:3,bit:[0,5],board:[],chip:5,content:1,control:4,covgdaq:1,ddr:[],definit:0,document:[1,3],driven:[],endpoint:0,enter:5,extend:4,fifo:[],file:[0,3],fpga:[],guid:[0,3,5],hex:5,i2c:[],i2ccontrol:4,index:5,indic:[0,1],interfac:[2,3],lower:5,memori:[],miscellan:4,modul:[],name:5,peripher:[3,4],pull:3,py:[],regist:[3,5],remain:5,repeat:5,request:3,s:1,sandbox:3,spi:[],spicontrol:4,spififodriven:4,tabl:1,test:3,upper:5,usag:0,util:6,valu:5,welcom:1,width:5,you:3}})