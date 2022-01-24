# https://noisyopt.readthedocs.io/en/latest/

# notebook pg 116 says 4 nA per ADC code at 100k

# instrumentation amplifier
def inamp(v, rg=None):
    # rg = 9.9e3 / (G − 1)
    # rg*(g-1) = 9.9e3
    if rg is None:
        g = 1
    else:
        g = (9.9e3 + rg)/rg
    return v*g

# differential buffer to the ADCs
def diff_amp(v):
    rg = 120+1500
    rf = 499
    return rf/rg*v

# AD7961 ADC
def adc(v, v_lsb=125e-6):
    # internal VREF of 4.096 V => 125 uV per code
    # external VREF = 5V => 152.6 uV per code
    return v/v_lsb


def dn_per_nA(rf_tia, rg=None):
    i = 1e-9 # calculate dn / nA
    adc_v = diff_amp(inamp(rf_tia*i, rg))
    return adc(adc_v)
