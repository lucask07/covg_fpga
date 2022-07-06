"""This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453. This is repeated for
feedback resistors of 10K, 33K, 100K, 332K, and 3000K. The membrane current
(Im) is graphed against time with all of these responses together.

Biophysical poster: https://uofstthomasmn.sharepoint.com/:b:/r/sites/COVGsummer2022/Shared%20Documents/biophysical_2022_poster_covg_v1.pdf?csf=1&web=1&e=gbUPQi

June 2022

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

###################################### 


# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("host")
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

