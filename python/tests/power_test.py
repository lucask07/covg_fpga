"""Early test file of the daq_v2 board
   Enable power supplies using the FPGA

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu

TODO:
1) DAQ board initialization
2) separate instrumentation code

"""
import logging
import sys
import os
import time
import datetime
import numpy as np
import atexit
# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == 'covg_fpga':
        interfaces_path = os.path.join(covg_fpga_path, 'python')
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

from interfaces.interfaces import Endpoint
from interfaces.interfaces import FPGA, UID_24AA025UID, AD7961, DAC80508, AD5453, DAC53401
from interfaces.interfaces import TCA9555, disp_device, ADS8686, advance_endpoints_bynum, DebugFIFO, DDR3
from interfaces.utils import get_timestamp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply, log_dc_pwr, init_current_meas_dict

eps = Endpoint.endpoints_from_defines

from interfaces.boards import Daq  # TODO: should I instantiate the Daq board or just pieces from it?
                                   # TODO: for now, pieces, eventually the DAQ board


logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'power_test.log'),
                    filemode='w',
                    level=logging.INFO)

# eps = Endpoint.endpoints_from_defines
ADS_EN = True
EN_15V = True
DAC_80508_EN = True
DDR_EN = True
FIFO_DEBUG_EN = False

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply()
atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2)
# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})
# turn on the +/-16.5 V input
for ch in [1, 2]:
    dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
current_meas = init_current_meas_dict()
######################################
time.sleep(2)

time.sleep(2)
# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

# log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='startup_bitfile')


########## GET Chip Instances ###################
uid = UID_24AA025UID(fpga=f,
                     endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDAQ'), 1),
                     addr_pins=0b000)

clamp_dac = DAC53401(fpga=f,
                     endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDC'),3),
                     addr_pins=0b000)

clamp_uid = UID_24AA025UID(fpga=f,
                     endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDC'),3),
                     addr_pins=0b000)

ads = ADS8686(fpga=f,
              endpoints=Endpoint.get_chip_endpoints('ADS8686'))

dac0 = DAC80508(fpga=f)
dac1 = DAC80508(fpga=f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('DAC80508'), 1))



pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

# power supply turn on and check current (AD7961 - 1.8 V first, then 5V)
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='turnon_{}'.format(name))
    time.sleep(0.05)

# +15 and -15V simultaneously
# pwr.all_on()
if EN_15V:
    for ch in [1, 2]:
        dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
    time.sleep(0.05)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='turnon_15n15V')

time.sleep(0.01)
print(current_meas)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
# gpio.spi_debug('dfast0')
gpio.spi_debug('ads')
# gpio.ads_misc('convst')
gpio.ads_misc('sdoa')


#for i in range(AD7961_CHANS):
#    ad7961s[i].power_down_all()
#    ad7961s[i].reset_wire(1)  # FPGA reset wire, resets FPGA controller

if FIFO_DEBUG_EN:
    fifo_debug = DebugFIFO(f)
    fifo_debug.reset_fifo()
    dt = fifo_debug.stream_mult(swps=4, twos_comp_conv=False)

ads.hw_reset(val=True)  # put ADS into hardware reset

ddr = DDR3(f)
ddr.set_index(int(ddr.parameters['sample_size']/8))
flat_buf = ddr.write_flat_voltage(600)  # input is digital code
ddr_readback_flat = ddr.read()
sin_buf = ddr.write_sin_wave(amplitude=2, frequency=10e3, dignum_volt=546)
ddr_readback_sin = ddr.read()

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD5453'),i),
                channel=i))
    fdac[i].set_spi_sclk_divide()
    fdac[i].set_data_mux('ads8686_chA')
    fdac[i].write(0x2000)
    t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_flat_voltage(256 + 256*i)

fdac[i].set_clk_divider()  # default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)
g_buf = ddr.write_channels()

# UID
read = uid.get_manufacturer_code()
default = uid.registers['MANUFACTURER_CODE'].default
if read != default:
    print(f'UID MANUFACTURER_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

read = uid.get_device_code()
default = uid.registers['DEVICE_CODE'].default
if read != default:
    print(f'UID DEVICE_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

# check to see if i2c is consistent
i2c_repeats = 100
read_test = []
for i in range(i2c_repeats):
    read_test.append(uid.get_manufacturer_code())
    if read != default:
        print(f'UID MANUFACTURER_CODE FAILED\n    '
              f'(read) {read} != (default) {default}')

unq_sn = uid.get_serial_number()
print(f'Unique SN: {hex(unq_sn)}')

# TODO: error in schematic note
#       should be "high-Z or high will enable"
for bit_pos in range(eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_low,
                     eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_high + 1):

    f.clear_wire_bit(eps['GP']['CURRENT_PUMP_ENABLE'].address,
                     bit_pos)

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='ipump_disable')

# desired I/O expander:
# DAC gains and current output select
io_0 = TCA9555(fpga=f, endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDAQ'), 1),
               addr_pins=0b000)  # DAC gains 0,1,2,3
io_1 = TCA9555(fpga=f, endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDAQ'), 1),
               addr_pins=0b100)  # DAC gains 4,5;
                                                  # ISEL1[3:0]; ISEL2[3:0]

io_0.configure_pins([0x00, 0x00])  # set all pins to outputs (=0)
io_0.write(0x0000)  # set all pins to zero --
                    # minimizes the DAC gain and should lower current draw

#TODO: check bit position of pin 13  P1_0, DAC2_G0 (accessible by DMM)

io_1.configure_pins([0x00, 0x00])  # set all pins to outputs
# ISEL = 1 gives voltage outputs
# ISEL = 0 routes Howland Ipump out
io_1.write(0x00FF)  # set all gain pins to zero & all ISEL to have the voltage output
# TODO: check ordering of the io write; seems correct

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='io_expanders_0')
setup = ad7961s[0].setup(reset_pll=True)
time.sleep(0.05)

# enable ADS868 and remeasure current
if ADS_EN:
    ads.hw_reset(val=False)  # release reset
    time.sleep(0.01)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='ads_release_reset')
    time.sleep(1)
    ads.set_host_mode()
    ads.setup()
    cfg = ads.read('config')
    chan_sel = ads.read('chan_sel')
    range_a1 = ads.read('rangeA1')
    ads.set_range(5)
    lpf1 = ads.read('lpf')
    ads.set_lpf(376)
    lpf2 = ads.read('lpf')
    #ads.setup_sequencer(chan_list=['FIXED_A', 'FIXED_B', '5A', '5B'])
    ads.setup_sequencer(chan_list=[('5', 'FIXED')])
    ads.write_reg_bridge(clk_div=200)  # 1 MSPS
    ads.set_fpga_mode()
    data_ads = ads.stream_mult(swps=4, twos_comp_conv=False)

    # ads.hw_reset(val=True)  # back to reset
print(current_meas)

slew_rate = 16
clamp_dac.config_rate(slew_rate)

# Write voltage
voltage = 0b1111111111
clamp_dac.write_voltage(voltage)
print(f'Voltage = {voltage}')

# Power on, wait
clamp_dac.power_up()

if DAC_80508_EN:
    # these DAC signals come out before the bipolar amplifier
    for dac in [dac0, dac1]:
        # dac.reset_master()  # TODO -- I don't think this works?
        dac.set_host_mode()
        print('Setting divider...')
        dac.set_divider(0x8)  # XEM6310 worked with divider of 4, XEM7310 runs twice as fast so divider of 8.
        print('Configuring Wishbone...')
        spi_ctrl_reg_val = 0x3218  # Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        dac.configure_master_bin(spi_ctrl_reg_val)
        dac.select_slave(1)

        dac.set_gain(0x01ff)
        print('Gain changed')

        # Write 0xff to 0x03 (CONFIG register)
        dac.set_config_bin(0xff)
        print('Outputs powered down')

        # Write 0x00 to 0x03 (CONFIG register)
        dac.set_config_bin(0x00)
        print('Outputs powered on')

        # Write to all outputs
        voltage = 0xffff
        for i in range(8):
            if dac.write('DAC'+str(i), voltage):
                message = f'Write {hex(voltage)}={voltage}V SUCCESS'
                # print(message)
                logging.info(message)
            else:
                message = f'Write {hex(voltage)}={voltage}V FAIL'
                logging.warning(message)
